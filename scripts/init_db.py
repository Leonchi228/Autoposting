"""
Скрипт создания таблиц в PostgreSQL.
Запуск из корня проекта: python -m scripts.init_db
Либо: python scripts/init_db.py (из корня проекта)
"""
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from database import init_db


def main() -> None:
    print("Создание таблиц в БД...")
    init_db()
    print("Готово. Таблицы users и channels созданы.")


if __name__ == "__main__":
    main()
