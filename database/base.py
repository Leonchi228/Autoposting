"""
Базовый класс для моделей и общие настройки.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс всех моделей."""

    pass
