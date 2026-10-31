"""
Менеджер автоматизированного резервного копирования базы данных SQLite и снимков Redis.

Выполняет:
  1. Горячий онлайн-бэкап SQLite (WAL) через SQLite Backup API
  2. Инициирование асинхронного BGSAVE в Redis
  3. Упаковку в сжатый .tar.gz архив с ротацией (по умолчанию 7 дней)
  4. Отправку архивной копии в Telegram администратору
"""

import asyncio
import os
import shutil
import sqlite3
import tarfile
import time
from datetime import datetime

from aiogram.types import FSInputFile

from config import ALLOWED_USER_ID, BACKUP_DIR_PATH, BACKUP_RETENTION_DAYS, SQLITE_DB_PATH
from core.bot import bot
from core.logger import get_logger
from core.redis import redis_client

log = get_logger("backup_manager")


def backup_sqlite_online(dest_path: str) -> bool:
    """Создает консистентный снимок SQLite без блокировки читателей и писателей."""
    if not os.path.exists(SQLITE_DB_PATH):
        log.warning("Файл БД %s не найден для бэкапа", SQLITE_DB_PATH)
        return False
    try:
        with sqlite3.connect(SQLITE_DB_PATH) as src, sqlite3.connect(dest_path) as dst:
            src.backup(dst)
        return True
    except Exception as exc:
        log.error("Сбой онлайн-бэкапа SQLite: %s", exc)
        return False


async def _trigger_redis_save() -> None:
    """Инициирует фоновый снимок Redis в RDB файл при наличии подключения."""
    if redis_client is None:
        return
    try:
        await redis_client.bgsave()
        log.info("Инициирован фоновый BGSAVE в Redis")
    except Exception as exc:
        log.warning("Не удалось запустить BGSAVE в Redis: %s", exc)


def _create_tar_archive(staging_dir: str, archive_path: str) -> bool:
    """Упаковывает файлы промежуточной директории в .tar.gz архив."""
    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            for item in os.listdir(staging_dir):
                tar.add(os.path.join(staging_dir, item), arcname=item)
        return True
    except Exception as exc:
        log.error("Сбой сжатия архива бэкапа: %s", exc)
        return False


def _rotate_old_backups(backup_dir: str, retention_days: int) -> int:
    """Удаляет архивы бэкапов старше заданного количества дней."""
    now = time.time()
    cutoff = now - (retention_days * 86400)
    removed_count = 0
    for filename in os.listdir(backup_dir):
        if not filename.endswith(".tar.gz"):
            continue
        filepath = os.path.join(backup_dir, filename)
        if os.path.getmtime(filepath) < cutoff:
            os.remove(filepath)
            removed_count += 1
    if removed_count > 0:
        log.info("Ротация бэкапов: удалено %s устаревших архивов", removed_count)
    return removed_count


async def _send_backup_to_telegram(archive_path: str) -> bool:
    """Отправляет сжатый архив бэкапа администратору в Telegram."""
    try:
        file_size_kb = await asyncio.to_thread(os.path.getsize, archive_path) / 1024
        ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caption = f"📦 <b>Автоматический бэкап системы Para</b>\n📅 <b>Дата:</b> {ts_str}\n📊 <b>Размер:</b> {file_size_kb:.1f} KB"
        doc = FSInputFile(archive_path)
        await bot.send_document(chat_id=ALLOWED_USER_ID, document=doc, caption=caption, parse_mode="HTML")
        log.info("Архив бэкапа отправлен администратору %s", ALLOWED_USER_ID)
        return True
    except Exception as exc:
        log.error("Не удалось отправить архив бэкапа в Telegram: %s", exc)
        return False


async def run_backup_pipeline() -> bool:
    """Оркестрирует полный процесс создания бэкапа SQLite и Redis, ротацию и отправку."""
    os.makedirs(BACKUP_DIR_PATH, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"para_backup_{timestamp}.tar.gz"
    archive_path = os.path.join(BACKUP_DIR_PATH, archive_name)
    staging_dir = os.path.join(BACKUP_DIR_PATH, f"tmp_{timestamp}")

    os.makedirs(staging_dir, exist_ok=True)
    try:
        await _trigger_redis_save()
        db_snapshot_file = os.path.join(staging_dir, "para.db")
        if not backup_sqlite_online(db_snapshot_file):
            return False
        if not _create_tar_archive(staging_dir, archive_path):
            return False
        _rotate_old_backups(BACKUP_DIR_PATH, BACKUP_RETENTION_DAYS)
        await _send_backup_to_telegram(archive_path)
        return True
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)
