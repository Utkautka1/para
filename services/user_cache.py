"""
Сервис постоянного кэширования пользователей Telegram (username -> user_id).

Сохраняет соответствия юзернеймов и цифровых Telegram ID на диск (data/user_cache.json),
чтобы при перезапуске бота кэш не сбрасывался.
"""

import os

from config import USER_CACHE_FILE_PATH
from core.logger import get_logger
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("user_cache")
CACHE_FILE_PATH: str = USER_CACHE_FILE_PATH
_USER_CACHE: dict[str, int] | None = None
_USER_CACHE_MTIME: float = 0.0
_USER_CACHE_PATH: str | None = None


def clear_user_cache_memory() -> None:
    """
    Сбрасывает оперативный in-memory буфер сопоставлений юзернеймов и ID.

    Используется в unit-тестах и сценариях изоляции окружения для принудительного
    перечитывания структуры кэша с файловой системы.

    Ничего не возвращает.
    """
    global _USER_CACHE, _USER_CACHE_MTIME, _USER_CACHE_PATH
    _USER_CACHE = None
    _USER_CACHE_MTIME = 0.0
    _USER_CACHE_PATH = None


def load_user_cache() -> dict[str, int]:
    """
    Загружает словарь сопоставлений username -> user_id с проверкой mtime файла.

    Служит высокопроизводительным in-memory кэшем, инвалидируясь только при реальном
    изменении файла на диске другим процессом или воркером.

    Возвращает словарь {username: user_id}.
    """
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


def save_user_cache(cache: dict[str, int]) -> None:
    """
    Атомарно сохраняет словарь сопоставлений пользователей на диск и в память.

    Использует sync_atomic_save_json для защиты от повреждения файла при рестарте
    и сразу обновляет отметку mtime для синхронизации локального буфера.

    Ничего не возвращает.
    """
    global _USER_CACHE, _USER_CACHE_MTIME, _USER_CACHE_PATH
    _USER_CACHE = cache
    sync_atomic_save_json(CACHE_FILE_PATH, cache)
    _USER_CACHE_PATH = CACHE_FILE_PATH
    try:
        _USER_CACHE_MTIME = os.path.getmtime(CACHE_FILE_PATH)
    except OSError:
        _USER_CACHE_MTIME = 0.0


def get_cached_user_id(username: str) -> int | None:
    """
    Возвращает цифровой Telegram user_id по текстовому юзернейму.

    Нормализует имя пользователя (удаляет префикс '@' и приводит к нижнему регистру),
    предоставляя быстрый O(1) поиск без обращений к API Telegram.

    Возвращает int user_id или None, если пользователь ранее не взаимодействовал с ботом.
    """
    clean = username.lstrip("@").lower()
    return load_user_cache().get(clean)


def add_user_to_cache(username: str, user_id: int) -> None:
    """
    Добавляет связку юзернейма и ID пользователя в персистентный кэш.

    Проверяет наличие изменений перед записью, предотвращая лишние дисковые операции
    ввода-вывода при повторных входящих сообщениях одного пользователя.

    Ничего не возвращает.
    """
    if not username:
        return
    clean = username.lstrip("@").lower()
    cache = load_user_cache()
    if cache.get(clean) != user_id:
        cache[clean] = user_id
        save_user_cache(cache)
        log.debug("Кэширован пользователь: @%s -> %s", clean, user_id)
