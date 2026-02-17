"""
Точка входа для запуска бота.
Запуск из корня проекта (с активированным venv):
  python -m bot.main
  или
  python bot/main.py
"""
import logging
import sys
import time
import traceback
from pathlib import Path

# Корень проекта (папка, где лежит bot, config, .env)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Чтобы находились config, parser, database при любом способе запуска
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _pause_on_error() -> None:
    """При ошибке пишет её в файл и держит консоль открытой 2 минуты."""
    err_text = traceback.format_exc()
    print("\n" + "=" * 60)
    print("ОШИБКА:")
    print(err_text)
    print("=" * 60)
    log_file = PROJECT_ROOT / "error_log.txt"
    try:
        log_file.write_text(err_text, encoding="utf-8")
        print(f"\nОшибка сохранена в файл: {log_file}")
    except Exception:
        pass
    print("\nОкно закроется через 2 минуты (или закройте вручную).")
    try:
        time.sleep(120)
    except KeyboardInterrupt:
        pass
    sys.exit(1)


if __name__ == "__main__":
    try:
        from telegram.ext import Application, CallbackQueryHandler, CommandHandler

        from config import BOT_TOKEN
        from bot.handlers import button_news_man_city, cmd_start
    except Exception:
        _pause_on_error()
        raise

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    def main() -> None:
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN не задан. Укажите в .env или переменной окружения.")
            return
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", cmd_start))
        app.add_handler(CallbackQueryHandler(button_news_man_city, pattern="^news_man_city$"))
        logger.info("Бот запущен.")
        app.run_polling(allowed_updates=["message", "callback_query"])

    try:
        main()
    except Exception:
        _pause_on_error()
