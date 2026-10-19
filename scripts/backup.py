"""
CLI-скрипт запуска процесса резервного копирования данных Para (SQLite + Redis).

Использование:
  python scripts/backup.py [--retention-days 7]
"""

import argparse
import asyncio
import sys

from core.logger import get_logger
from services.backup_manager import run_backup_pipeline

log = get_logger("backup_cli")


def _parse_cli_args() -> argparse.Namespace:
    """Парсит аргументы командной строки запуска бэкапа."""
    parser = argparse.ArgumentParser(description="Para Automated Backup Tool")
    parser.add_argument("--retention-days", type=int, default=7, help="Количество дней хранения архивов")

    return parser.parse_args()


async def main() -> int:
    """Точка входа запуска резервного копирования из командной строки."""
    args = _parse_cli_args()
    log.info(f"Запуск создания резервной копии Para (ротация: {args.retention_days} дней)...")
    success = await run_backup_pipeline()

    if success:
        log.info("✅ Резервное копирование успешно завершено!")
        return 0
    log.error("❌ Резервное копирование завершилось с ошибкой!")

    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
