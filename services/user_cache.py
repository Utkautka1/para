"""
Сервис постоянного кэширования пользователей Telegram (username -> user_id).

Сохраняет соответствия юзернеймов и цифровых Telegram ID на диск (data/user_cache.json),
чтобы при перезапуске бота кэш не сбрасывался.
"""

import json
import os
from typing import Dict, Optional
from core.logger import get_logger

log = get_logger("user_cache")
CACHE_FILE_PATH = "data/user_cache.json"


def ensure_data_dir_exists() -> None:
    """
    Создает директорию data/, если она отсутствует.
    """
    os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)


def load_user_cache() -> Dict[str, int]:
    """
    Загружает кэш пользователей из JSON файла.

    :return: Словарь username -> user_id
    """
    ensure_data_dir_exists()
    if not os.path.exists(CACHE_FILE_PATH):
        return {}
    try:
        with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Ошибка при загрузке user_cache.json: {e}")
        return {}


def save_user_cache(cache: Dict[str, int]) -> None:
    """
    Сохраняет словарь кэша пользователей на диск.

    :param cache: Словарь username -> user_id
    """
    ensure_data_dir_exists()
    try:
        with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error(f"Ошибка при сохранении user_cache.json: {e}")


def get_cached_user_id(username: str) -> Optional[int]:
    """
    Возвращает Telegram ID из постоянного кэша по юзернейму.

    :param username: Имя пользователя
    :return: user_id или None
    """
    clean = username.lstrip("@").lower()
    cache = load_user_cache()
    return cache.get(clean)


def add_user_to_cache(username: str, user_id: int) -> None:
    """
    Добавляет пользователя в постоянный кэш и сохраняет на диск.

    :param username: Имя пользователя
    :param user_id: Telegram ID
    """
    if not username:
        return
    clean = username.lstrip("@").lower()
    cache = load_user_cache()
    if cache.get(clean) != user_id:
        cache[clean] = user_id
        save_user_cache(cache)
        log.debug(f"Кэширован пользователь: @{clean} -> {user_id}")
