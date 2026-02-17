"""
Парсер новостей про Манчестер Сити с sports.ru через RSS.
Используется RSS по тегу клуба (тег 89039) или фильтрация по ключевым словам.
"""
import re
from datetime import datetime
from typing import Any

import feedparser
import requests

from parser.base import BaseParser, NewsItem

# RSS по тегу «Манчестер Сити» на sports.ru (тег 89039)
SPORTS_RU_MANCHESTER_CITY_RSS = "https://www.sports.ru/rss/tag/89039/"

# Запасные URL: общая лента футбола или вся лента — фильтруем по ключевым словам
SPORTS_RU_FOOTBALL_RSS = "https://www.sports.ru/rss/football/"
SPORTS_RU_ALL_RSS = "http://www.sports.ru/sports_docs.xml"

# Ключевые слова для фильтрации новостей про Манчестер Сити
MAN_CITY_KEYWORDS = (
    "манчестер сити",
    "ман сити",
    "manchester city",
    "man city",
    "сити",
    "гвардиол",
    "guardiola",
    "холанд",
    "haaland",
    "де брюйне",
    "de bruyne",
)


def _text_about_man_city(text: str) -> bool:
    """Проверяет, что текст относится к Манчестер Сити."""
    if not text:
        return False
    lower = text.lower()
    return any(kw in lower for kw in MAN_CITY_KEYWORDS)


def _image_from_entry(entry: Any) -> str | None:
    """Извлекает URL картинки из элемента RSS (enclosure, media_content, первый img в summary)."""
    # Enclosure (тип image)
    for enc in getattr(entry, "enclosures", []) or []:
        href = enc.get("href") or enc.get("url")
        if href and (enc.get("type") or "").startswith("image"):
            return href
    # media_content (MediaRSS)
    media_list = getattr(entry, "media_content", None) or getattr(entry, "media_thumbnail", None) or []
    for media in media_list if isinstance(media_list, list) else []:
        m = media if isinstance(media, dict) else getattr(media, "__dict__", {})
        if (m.get("type") or "").startswith("image") or "url" in m:
            url = m.get("url") or m.get("href")
            if url:
                return url
    # Первая картинка в summary/description
    raw = getattr(entry, "summary", None) or getattr(entry, "description", None) or ""
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw, re.I)
    if match:
        return match.group(1).strip()
    return None


def _parse_entry(entry: Any) -> NewsItem | None:
    """Преобразует элемент RSS в NewsItem."""
    title = getattr(entry, "title", None) or ""
    link = getattr(entry, "link", None) or ""
    if not link:
        return None
    summary = ""
    if hasattr(entry, "summary"):
        summary = entry.summary
    elif hasattr(entry, "description"):
        summary = entry.description
    if hasattr(summary, "replace"):
        for tag in ("<br>", "<br/>", "<p>", "</p>", "<div>", "</div>"):
            summary = summary.replace(tag, " ")
    else:
        summary = str(summary)
    # Убираем теги для чистого текста, но оставляем длину полной
    summary_clean = re.sub(r"<[^>]+>", " ", summary)
    summary_clean = " ".join(summary_clean.split())
    published: Any = None
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            published = datetime(*entry.published_parsed[:6])
        except (TypeError, IndexError):
            published = getattr(entry, "published", None)
    else:
        published = getattr(entry, "published", None)
    image_url = _image_from_entry(entry)
    return NewsItem(
        title=title,
        url=link,
        summary=summary_clean,
        published_at=published,
        image_url=image_url,
        raw=None,
    )


class SportsRuManchesterCityParser(BaseParser):
    """
    Парсер новостей про Манчестер Сити с sports.ru.
    Сначала пробует RSS по тегу 89039, затем при необходимости — общий RSS с фильтром.
    """

    def __init__(self, source_url: str | None = None):
        super().__init__(source_url or SPORTS_RU_MANCHESTER_CITY_RSS)

    def _fetch_rss(self, url: str) -> list[NewsItem]:
        """Загружает RSS по URL и возвращает список NewsItem."""
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Bot/1.0"})
            resp.raise_for_status()
        except Exception:
            return []
        feed = feedparser.parse(resp.content)
        items: list[NewsItem] = []
        for entry in feed.entries:
            item = _parse_entry(entry)
            if item:
                items.append(item)
        return items

    def fetch_news(self) -> list[NewsItem]:
        """
        Получить новости про Манчестер Сити.
        Сначала пробует RSS по тегу клуба; если пусто или ошибка — грузит общий футбольный RSS и фильтрует.
        """
        # Пробуем прямой RSS по тегу Ман Сити
        items = self._fetch_rss(SPORTS_RU_MANCHESTER_CITY_RSS)
        if not items:
            items = self._fetch_rss(SPORTS_RU_FOOTBALL_RSS)
        if not items:
            items = self._fetch_rss(SPORTS_RU_ALL_RSS)
        # Оставляем только новости про Манчестер Сити (для общих лент — обязательно)
        items = [
            i
            for i in items
            if _text_about_man_city(i.title) or _text_about_man_city(i.summary)
        ]
        return items


def _fetch_rss_url(url: str) -> list[NewsItem]:
    """Загружает RSS по URL и возвращает список новостей без фильтрации."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Bot/1.0"})
        resp.raise_for_status()
    except Exception:
        return []
    feed = feedparser.parse(resp.content)
    items = []
    for entry in feed.entries:
        item = _parse_entry(entry)
        if item:
            items.append(item)
    return items


def get_latest_man_city_news() -> list[NewsItem]:
    """Последние новости про Манчестер Сити с sports.ru."""
    parser = SportsRuManchesterCityParser()
    return parser.fetch_news()


def get_latest_any_news() -> list[NewsItem]:
    """Самые последние новости с sports.ru (любая тематика)."""
    items = _fetch_rss_url(SPORTS_RU_ALL_RSS)
    if not items:
        items = _fetch_rss_url(SPORTS_RU_FOOTBALL_RSS)
    return items


# Ключевые слова для фильтра «про футбол» (общая лента → только футбол)
FOOTBALL_KEYWORDS = (
    "футбол", "футболист", "футбольн", "гол", "голев", "матч", "чемпионат", "лига",
    "клуб", "сборн", "тренер", "переход", "трансфер", "апл", "лига чемпионов",
    "убек", "бундеслига", "серия а", "ла лига", "football", "goal", "match",
    "premier league", "champions league", "club", "transfer",
)


def _text_about_football(text: str) -> bool:
    """Проверяет, что текст относится к футболу."""
    if not text:
        return False
    lower = text.lower()
    return any(kw in lower for kw in FOOTBALL_KEYWORDS)


def get_football_news() -> list[NewsItem]:
    """Новости о футболе с sports.ru (только футбольная лента)."""
    return _fetch_rss_url(SPORTS_RU_FOOTBALL_RSS)


def get_football_news_fresh() -> list[NewsItem]:
    """
    Всегда вернуть список футбольных новостей, по возможности самых свежих.
    Сначала — футбольная лента (самая свежая по футболу), при пустоте — общая лента, отфильтрованная по футболу.
    """
    items = _fetch_rss_url(SPORTS_RU_FOOTBALL_RSS)
    if items:
        return items
    items = _fetch_rss_url(SPORTS_RU_ALL_RSS)
    if not items:
        return []
    return [i for i in items if _text_about_football(i.title) or _text_about_football(i.summary)]
