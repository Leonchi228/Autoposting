"""
Базовый класс и общая логика для парсеров новостей с сайтов.
Конкретные парсеры (по одному на сайт/источник) добавляйте в этой папке.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class NewsItem:
    """Один элемент новости с сайта."""
    title: str
    url: str
    summary: str = ""
    published_at: Any = None  # datetime или строка
    image_url: str | None = None  # ссылка на картинку из новости или поиска
    raw: dict[str, Any] | None = None


class BaseParser(ABC):
    """Базовый класс парсера. Наследуйте и реализуйте parse() для конкретного сайта."""

    def __init__(self, source_url: str):
        self.source_url = source_url

    @abstractmethod
    def fetch_news(self) -> list[NewsItem]:
        """Получить список новостей с источника. Реализация в наследниках."""
        pass
