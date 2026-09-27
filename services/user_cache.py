"""
Сервис постоянного кэширования пользователей Telegram (username -> user_id).

Сохраняет соответствия юзернеймов и цифровых Telegram ID на диск (data/user_cache.json),
чтобы при перезапуске бота кэш не сбрасывался.
"""

from typing import Dict, Optional
from core.logger import get_logger
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("user_cache")
CACHE_FILE_PATH = "data/user_cache.json"


def load_user_cache() -> Dict[str, int]:
    """
    Загружает кэш пользователей из JSON файла.

    :return: Словарь username -> user_id
    """
    return sync_load_json(CACHE_FILE_PATH, default={})


def save_user_cache(cache: Dict[str, int]) -> None:
    """
    Атомарно сохраняет словарь кэша пользователей на диск.

    :param cache: Словарь username -> user_id
    """
    sync_atomic_save_json(CACHE_FILE_PATH, cache)


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
