"""
Конфигурация приложения. URL БД берётся из переменной окружения DATABASE_URL.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Загружаем .env из корня проекта
load_dotenv(Path(__file__).resolve().parent / ".env")

# Пример: postgresql://user:password@localhost:5432/bot_db
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/telegram_bot_db",
)

# Telegram Bot API
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Канал, куда бот постит новости (username без @ или ID вида -100...)
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "aliccomputer")

# Google Gemini API — краткое обобщение текста перед публикацией в одно сообщение
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
