"""
Модели SQLAlchemy: Пользователи и Каналы.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    pass  # Channel объявлен ниже в этом файле


class User(Base):
    """
    Пользователь бота.
    id — Telegram user id.
    Подписка и каналы связаны через subscription_expires_at и отношение channels.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
        comment="Telegram user id",
    )
    subscription_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="До какой даты действует подписка",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Связь: у пользователя много каналов (id каналов получаем через channels)
    channels: Mapped[list["Channel"]] = relationship(
        "Channel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, subscription_expires_at={self.subscription_expires_at})>"


class Channel(Base):
    """
    Канал пользователя.
    Хранит id канала в Telegram, источники новостей, стиль публикаций и владельца.
    """

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_channel_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        comment="ID канала в Telegram (например, -100xxxxxxxxxx)",
    )
    news_source_urls: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        default=list,
        comment="Ссылки на сайты — источники новостей для парсинга",
    )
    publication_style: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        comment="Стиль публикаций в канале (описание формата постов)",
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user: Mapped["User"] = relationship("User", back_populates="channels")

    def __repr__(self) -> str:
        return f"<Channel(id={self.id}, telegram_channel_id={self.telegram_channel_id}, user_id={self.user_id})>"
