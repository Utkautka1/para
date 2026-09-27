"""
Модуль локального хранения подписчиков бота.

Сохраняет и считывает список Telegram chat_id из файла data/subscribers.json.
Обеспечивает атомарную запись через временный файл и fsync.
"""

from typing import Set
from config import SUBSCRIBERS_FILE_PATH
from core.logger import get_logger
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("subscribers")


def load_subscribers() -> Set[int]:
    """
    Загружает множество ID подписанных пользователей из файла.

    :return: Сет с Telegram chat_id
    """
    data = sync_load_json(SUBSCRIBERS_FILE_PATH, default=[])
    return set(data) if isinstance(data, list) else set()


def save_subscribers(subs: Set[int]) -> bool:
    """
    Атомарно сохраняет актуальное множество подписчиков в JSON файл.

    :param subs: Множество ID подписчиков
    :return: True в случае успеха
    """
    ok = sync_atomic_save_json(SUBSCRIBERS_FILE_PATH, list(subs))
    if ok:
        log.debug(f"Сохранено {len(subs)} подписчиков в {SUBSCRIBERS_FILE_PATH}")
    return ok


def add_subscriber(chat_id: int) -> bool:
    """
    Добавляет новый chat_id в список подписчиков.

    :param chat_id: Telegram ID чата
    :return: True, если пользователь был добавлен впервые
    """
    subs = load_subscribers()
    if chat_id not in subs:
        subs.add(chat_id)
        save_subscribers(subs)
        log.info(f"Добавлен новый подписчик: {chat_id}")
        return True
    return False


def remove_subscriber(chat_id: int) -> bool:
    """
    Удаляет chat_id из списка подписчиков.

    :param chat_id: Telegram ID чата
    :return: True, если пользователь был успешно удален
    """
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        log.info(f"Удален подписчик: {chat_id}")
        return True
    return False
