"""
Обработчики команд и кнопок бота.
"""
import html
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import CHANNEL_USERNAME, GEMINI_API_KEY
from parser.article import fetch_article_full_text_and_image
from parser.sports_ru import get_football_news_fresh
from utils.gemini import summarize_for_telegram

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4096


def _escape_html(text: str) -> str:
    """Экранирует HTML для parse_mode='HTML' в Telegram."""
    return html.escape(text or "", quote=False)


_sent_news_by_user: dict[int, set[str]] = {}


def _get_next_unique_news(user_id: int):
    """Следующая уникальная новость — только футбол, по возможности самая свежая (лента футбола, при пустоте — общая с фильтром)."""
    news = get_football_news_fresh()
    if not news:
        return None
    sent = _sent_news_by_user.setdefault(user_id, set())
    for item in news:
        if item.url not in sent:
            sent.add(item.url)
            return item
    _sent_news_by_user[user_id] = {news[0].url}
    return news[0]


def _get_full_text(item) -> str:
    """Полный текст новости: со страницы статьи или из RSS."""
    full_text_from_page, _ = fetch_article_full_text_and_image(item.url)
    full_text = full_text_from_page.strip() if full_text_from_page else (item.summary or "").strip()
    if not full_text:
        full_text = item.title
    return full_text


def _build_one_message(item, body_text: str) -> str:
    """Одно сообщение: заголовок + текст + ссылка (влезает в лимит)."""
    title_safe = _escape_html(item.title)
    text_safe = _escape_html(body_text)
    link_part = f'🔗 <a href="{item.url}">Читать на Sports.ru</a>'
    return f"<b>{title_safe}</b>\n\n{text_safe}\n\n{link_part}"


async def button_news_man_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получить новость: полный текст → обобщение через Gemini → одно сообщение (без картинок)."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id if update.effective_user else 0

    try:
        item = _get_next_unique_news(user_id)
    except Exception:
        logger.exception("Ошибка при загрузке новостей")
        await query.message.reply_text("Не удалось загрузить новости. Попробуйте позже.")
        return

    if not item:
        await query.message.reply_text("Не удалось загрузить футбольные новости. Попробуйте позже.")
        return

    try:
        full_text = _get_full_text(item)
    except Exception:
        logger.exception("Ошибка при загрузке текста статьи")
        full_text = item.summary or item.title

    # Обобщение через Gemini, чтобы влезло в одно сообщение
    if GEMINI_API_KEY:
        try:
            body_text = summarize_for_telegram(full_text, GEMINI_API_KEY)
        except Exception:
            logger.warning("Gemini недоступен, обрезаем текст")
            body_text = full_text[:3800] + "…" if len(full_text) > 3800 else full_text
    else:
        body_text = full_text[:3800] + "…" if len(full_text) > 3800 else full_text

    message_text = _build_one_message(item, body_text)
    if len(message_text) > MAX_MESSAGE_LENGTH:
        message_text = message_text[: MAX_MESSAGE_LENGTH - 3] + "…"

    try:
        await query.message.reply_text(
            message_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception:
        logger.exception("Ошибка при отправке сообщения пользователю")
        await query.message.reply_text("Не удалось отправить новость. Попробуйте ещё раз.")
        return

    if CHANNEL_USERNAME:
        channel_id = f"@{CHANNEL_USERNAME}" if not str(CHANNEL_USERNAME).startswith("-") else CHANNEL_USERNAME
        try:
            await context.bot.send_message(
                chat_id=channel_id,
                text=message_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception:
            logger.warning(
                "Не удалось опубликовать новость в канал %s",
                channel_id,
            )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start — приветствие и кнопка «Получить новость»."""
    keyboard = [
        [
            InlineKeyboardButton(
                "Получить футбольную новость",
                callback_data="news_man_city",
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.reply_text(
        "Привет! Нажми кнопку — пришлю свежую футбольную новость с Sports.ru. "
        "Каждый раз новая новость.",
        reply_markup=reply_markup,
    )
