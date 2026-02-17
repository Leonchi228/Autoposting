"""
Получение полного текста статьи и картинки со страницы, поиск фото в интернете.
"""
import logging
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Bot/1.0"}


def fetch_article_full_text_and_image(article_url: str) -> tuple[str, str | None]:
    """
    Загружает страницу статьи, извлекает полный текст и URL картинки (og:image или первая в статье).
    Возвращает (full_text, image_url). image_url может быть None.
    """
    full_text = ""
    image_url = None
    try:
        resp = requests.get(article_url, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # Картинка: og:image или первая в контенте
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            image_url = og["content"].strip()
        if not image_url:
            for img in soup.select("article img, .post__text img, .content img, .article__body img, [class*='article'] img, [class*='post'] img"):
                src = img.get("src") or img.get("data-src")
                if src and not any(x in src.lower() for x in ("pixel", "tracker", "1x1", "blank")):
                    image_url = urljoin(article_url, src)
                    break
        if not image_url:
            first_img = soup.find("img", src=True)
            if first_img:
                image_url = urljoin(article_url, first_img["src"])

        # Полный текст: ищем основной контент
        body = (
            soup.select_one("article .post__text")
            or soup.select_one(".post__text")
            or soup.select_one("[class*='article__body']")
            or soup.select_one("[class*='content'] article")
            or soup.select_one("article")
            or soup.select_one(".content")
        )
        if body:
            for tag in body.select("script, style, nav, .ad, .ads, [class*='ad-']"):
                tag.decompose()
            full_text = body.get_text(separator="\n", strip=True)
            full_text = re.sub(r"\n{3,}", "\n\n", full_text)
        if not full_text and soup.find("article"):
            full_text = soup.find("article").get_text(separator="\n", strip=True)
    except Exception as e:
        logger.debug("fetch_article_full_text_and_image %s: %s", article_url, e)
    return full_text or "", image_url


def search_photo_by_query(query: str, api_key: str | None = None) -> str | None:
    """
    Ищет подходящее фото по запросу через Pexels API.
    Возвращает URL первой фотографии или None. Требуется PEXELS_API_KEY в .env (бесплатный ключ на pexels.com/api).
    """
    if not api_key:
        return None
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query[:100], "per_page": 1, "locale": "ru-RU"},
            headers={"Authorization": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        photos = data.get("photos") or []
        if photos and photos[0].get("src", {}).get("large"):
            return photos[0]["src"]["large"]
    except Exception as e:
        logger.debug("search_photo_by_query %s: %s", query[:30], e)
    return None
