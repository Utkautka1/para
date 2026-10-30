"""
Модуль персистентного хранения подписчиков бота с поддержкой SQLite (WAL) и JSON-фолбэка.

Сохраняет и считывает список Telegram chat_id из реляционной базы данных SQLite.
Дублирует запись в JSON для обратной совместимости и мгновенного восстановления.
"""

import os
import sqlite3

from config import SQLITE_DB_PATH, SUBSCRIBERS_FILE_PATH
from core.logger import get_logger
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("subscribers")


def _query_sqlite_subscribers() -> set[int] | None:
    """Извлекает активных подписчиков из базы данных SQLite."""
    if not os.path.exists(SQLITE_DB_PATH):
        return None
    try:
        with sqlite3.connect(SQLITE_DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM subscribers WHERE is_active = 1;")
            rows = cursor.fetchall()
            return {int(row[0]) for row in rows}
    except Exception as exc:
        log.debug("SQLite пока не инициализирован для подписчиков: %s", exc)
        return None


def _update_sqlite_subscriber(chat_id: int, is_active: bool) -> None:
    """Атомарно обновляет статус подписчика в SQLite."""
    if not os.path.exists(SQLITE_DB_PATH):
        return
    try:
        with sqlite3.connect(SQLITE_DB_PATH, timeout=5.0) as conn:
            conn.execute(
                """INSERT INTO subscribers (chat_id, is_active, updated_at)
                   VALUES (?, ?, datetime('now'))
                   ON CONFLICT(chat_id) DO UPDATE SET
                       is_active = excluded.is_active,
                       updated_at = excluded.updated_at;""",
                (chat_id, 1 if is_active else 0),
            )
            conn.commit()
    except Exception as exc:
        log.warning("Не удалось обновить подписчика %s в SQLite: %s", chat_id, exc)


def load_subscribers() -> set[int]:
    """Загружает множество идентификаторов подписчиков из SQLite с фолбэком на JSON."""
    db_subs = _query_sqlite_subscribers()
    if db_subs is not None:
        return db_subs
    data = sync_load_json(SUBSCRIBERS_FILE_PATH, default=[])
    return set(data) if isinstance(data, list) else set()


def save_subscribers(subs: set[int]) -> bool:
    """Сохраняет актуальное множество подписчиков в JSON-файл и SQLite."""
    ok = sync_atomic_save_json(SUBSCRIBERS_FILE_PATH, list(subs))
    if ok:
        log.debug("Сохранено %s подписчиков в %s", len(subs), SUBSCRIBERS_FILE_PATH)
    for cid in subs:
        _update_sqlite_subscriber(cid, True)
    return ok


def add_subscriber(chat_id: int) -> bool:
    """Добавляет новый идентификатор чата в список активных подписчиков."""
    subs = load_subscribers()
    if chat_id not in subs:
        subs.add(chat_id)
        save_subscribers(subs)
        _update_sqlite_subscriber(chat_id, True)
        log.info("Добавлен новый подписчик: %s", chat_id)
        return True
    return False


def remove_subscriber(chat_id: int) -> bool:
    """Удаляет идентификатор чата из списка получателей рассылки."""
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        _update_sqlite_subscriber(chat_id, False)
        log.info("Удален подписчик: %s", chat_id)
        return True
    return False


def is_subscribed(chat_id: int) -> bool:
    """Проверяет, подписан ли пользователь на персональные уведомления в ЛС."""
    return chat_id in load_subscribers()


def toggle_subscriber(chat_id: int) -> bool:
    """Переключает статус подписки пользователя на противоположный (Toggle)."""
    subs = load_subscribers()
    if chat_id in subs:
        remove_subscriber(chat_id)
        log.info("🔕 Пользователь отключил напоминания: %s", chat_id)
        return False
    add_subscriber(chat_id)
    log.info("🔔 Пользователь включил напоминания: %s", chat_id)
    return True
