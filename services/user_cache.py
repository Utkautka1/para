"""
Сервис постоянного кэширования пользователей Telegram (username -> user_id).

Сохраняет соответствия юзернеймов и цифровых Telegram ID на диск (data/user_cache.json),
чтобы при перезапуске бота кэш не сбрасывался.
"""

import os
from typing import Dict, Optional
from config import USER_CACHE_FILE_PATH
from core.logger import get_logger
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("user_cache")
CACHE_FILE_PATH: str = USER_CACHE_FILE_PATH
_USER_CACHE: Optional[Dict[str, int]] = None
_USER_CACHE_MTIME: float = 0.0
_USER_CACHE_PATH: Optional[str] = None


def clear_user_cache_memory() -> None:
    """Сбрасывает оперативный кэш пользователей."""
    global _USER_CACHE, _USER_CACHE_MTIME, _USER_CACHE_PATH
    _USER_CACHE = None
    _USER_CACHE_MTIME = 0.0
    _USER_CACHE_PATH = None


def load_user_cache() -> Dict[str, int]:
    """Загружает кэш пользователей с in-memory буферизацией по mtime."""
    global _USER_CACHE, _USER_CACHE_MTIME, _USER_CACHE_PATH
    try:
        current_mtime = os.path.getmtime(CACHE_FILE_PATH)
    except OSError:
        current_mtime = 0.0
    if _USER_CACHE is not None and _USER_CACHE_PATH == CACHE_FILE_PATH and current_mtime == _USER_CACHE_MTIME:
        return _USER_CACHE
    _USER_CACHE = sync_load_json(CACHE_FILE_PATH, default={})
    _USER_CACHE_MTIME = current_mtime
    _USER_CACHE_PATH = CACHE_FILE_PATH
    return _USER_CACHE


def save_user_cache(cache: Dict[str, int]) -> None:
    """Атомарно сохраняет словарь кэша пользователей на диск и в память."""
    global _USER_CACHE, _USER_CACHE_MTIME, _USER_CACHE_PATH
    _USER_CACHE = cache
    sync_atomic_save_json(CACHE_FILE_PATH, cache)
    _USER_CACHE_PATH = CACHE_FILE_PATH
    try:
        _USER_CACHE_MTIME = os.path.getmtime(CACHE_FILE_PATH)
    except OSError:
        _USER_CACHE_MTIME = 0.0


def get_cached_user_id(username: str) -> Optional[int]:
    """Возвращает Telegram ID из постоянного кэша по юзернейму."""
    clean = username.lstrip("@").lower()
    return load_user_cache().get(clean)


def add_user_to_cache(username: str, user_id: int) -> None:
    """Добавляет пользователя в постоянный кэш и сохраняет на диск."""
    if not username:
        return
    clean = username.lstrip("@").lower()
    cache = load_user_cache()
    if cache.get(clean) != user_id:
        cache[clean] = user_id
        save_user_cache(cache)
        log.debug(f"Кэширован пользователь: @{clean} -> {user_id}")

