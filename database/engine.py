"""
Движок БД, фабрика сессий и создание таблиц.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import DATABASE_URL
from database.base import Base
from database.models import Channel, User  # noqa: F401 — регистрируем модели у Base


engine = create_engine(
    DATABASE_URL,
    echo=False,  # True — логировать SQL (удобно при отладке)
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    """Возвращает новую сессию. После использования нужно вызвать session.close()."""
    return SessionLocal()


def init_db() -> None:
    """Создаёт все таблицы в БД (если их ещё нет)."""
    Base.metadata.create_all(bind=engine)
