"""
Модуль локального хранения подписчиков бота.

Сохраняет и считывает список Telegram chat_id из файла data/subscribers.json.
Обеспечивает атомарную запись и обработку возможных ошибок ввода-вывода.
"""

import json
import os
from typing import List, Set
from config import SUBSCRIBERS_FILE_PATH
from core.logger import get_logger

log = get_logger("subscribers")


def load_subscribers() -> Set[int]:
    """
    Загружает множество ID подписанных пользователей из файла.

    :return: Сет с Telegram chat_id
    """
    if not os.path.exists(SUBSCRIBERS_FILE_PATH):
        return set()
    try:
        with open(SUBSCRIBERS_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception as e:
        log.error(f"Ошибка чтения файла подписчиков {SUBSCRIBERS_FILE_PATH}: {e}")
        return set()


def save_subscribers(subs: Set[int]) -> bool:
    """
    Сохраняет актуальное множество подписчиков в JSON файл.

    :param subs: Множество ID подписчиков
    :return: True в случае успеха
    """
    try:
        os.makedirs(os.path.dirname(SUBSCRIBERS_FILE_PATH), exist_ok=True)
        with open(SUBSCRIBERS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(list(subs), f, ensure_ascii=False, indent=2)
        log.debug(f"Сохранено {len(subs)} подписчиков в {SUBSCRIBERS_FILE_PATH}")
        return True
    except Exception as e:
        log.error(f"Ошибка сохранения файла подписчиков: {e}")
        return False


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
