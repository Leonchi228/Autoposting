"""
Запуск бота с автоперезагрузкой при изменении файлов (для разработки).
Требует: pip install watchdog
"""
import sys
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Установите watchdog: pip install watchdog")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import subprocess


class BotRestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.last_restart = 0
        self.restart_delay = 2  # Минимум 2 секунды между перезапусками

    def on_modified(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith((".py", ".env")):
            return
        now = time.time()
        if now - self.last_restart < self.restart_delay:
            return
        self.last_restart = now
        print(f"\n[Автоперезагрузка] Обнаружено изменение: {event.src_path}")
        self.restart_bot()

    def restart_bot(self):
        if self.process:
            print("Останавливаем бота...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        print("Запускаем бота...")
        self.process = subprocess.Popen(
            [sys.executable, "-m", "bot.main"],
            cwd=str(PROJECT_ROOT),
        )


def main():
    handler = BotRestartHandler()
    handler.restart_bot()
    observer = Observer()
    observer.schedule(handler, str(PROJECT_ROOT), recursive=True)
    observer.start()
    print(f"Следим за изменениями в {PROJECT_ROOT}")
    print("Нажмите Ctrl+C для остановки")
    try:
        while True:
            time.sleep(1)
            if handler.process and handler.process.poll() is not None:
                print("Бот завершился. Перезапускаем...")
                handler.restart_bot()
    except KeyboardInterrupt:
        print("\nОстанавливаем...")
        observer.stop()
        if handler.process:
            handler.process.terminate()
    observer.join()


if __name__ == "__main__":
    main()
