"""
Сервис аутентификации и разовой регистрации одногруппников группы 1-КПД-3.

Отвечает за:
  1. Проверку принадлежности пользователя к группе (ALLOWED_USER_ID или реестр).
  2. Разовую фиксацию цифрового Telegram ID при первом нажатии /start в ЛС бота.
  3. Сохранение привязки в data/birthdays.json и постоянный кэш user_cache.
  4. Защиту от несанкционированного доступа посторонних пользователей.
"""

import os
from typing import Any

from aiogram.types import User

from config import ALLOWED_USER_ID, BIRTHDAYS_FILE_PATH
from core.logger import get_logger
from services.user_cache import add_user_to_cache
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("classmates_auth")


_REGISTRY_CACHE: list[dict[str, Any]] | None = None
_REGISTRY_MTIME: float = 0.0


def clear_registry_cache() -> None:
    """Сбрасывает кэш реестра одногруппников в оперативной памяти."""
    global _REGISTRY_CACHE, _REGISTRY_MTIME
    _REGISTRY_CACHE = None
    _REGISTRY_MTIME = 0.0


def load_classmates_registry(force_reload: bool = False) -> list[dict[str, Any]]:
    """
    Загружает актуальный список студентов с in-memory кэшированием по mtime.

    Исключает дисковый I/O на каждый callback, возвращая срез из RAM.
    """
    global _REGISTRY_CACHE, _REGISTRY_MTIME
    try:
        current_mtime = os.path.getmtime(BIRTHDAYS_FILE_PATH)
    except OSError:
        current_mtime = 0.0
    if not force_reload and _REGISTRY_CACHE is not None and current_mtime == _REGISTRY_MTIME:
        return _REGISTRY_CACHE
    _REGISTRY_CACHE = sync_load_json(BIRTHDAYS_FILE_PATH, default=[])
    _REGISTRY_MTIME = current_mtime
    return _REGISTRY_CACHE


def find_classmate_by_tg_id(user_id: int) -> dict[str, Any] | None:
    """
    Ищет студента в реестре по его сохраненному Telegram ID.

    :param user_id: Числовой ID пользователя в Telegram
    :return: Словарь с данными студента или None
    """
    registry = load_classmates_registry()
    for student in registry:
        if student.get("tg_id") == user_id:
            return student
    return None


def find_unregistered_by_username(username: str) -> dict[str, Any] | None:
    """
    Ищет студента по юзернейму, у которого еще не зафиксирован tg_id (None).

    :param username: Юзернейм пользователя без префикса @
    :return: Словарь с данными студента или None
    """
    clean = username.lstrip("@").lower()
    registry = load_classmates_registry()
    for student in registry:
        uname = student.get("username")
        if uname and uname.lower() == clean and student.get("tg_id") is None:
            return student
    return None


def update_classmate_tg_id(clean_username: str, tg_id: int) -> dict[str, Any] | None:
    """
    Атомарно фиксирует Telegram ID студента в birthdays.json и кэше.

    Выполняется разово при первой авторизации по совпадению юзернейма.
    """
    registry = load_classmates_registry()
    updated_student = None
    for student in registry:
        uname = student.get("username")
        if uname and uname.lower() == clean_username and student.get("tg_id") is None:
            student["tg_id"] = tg_id
            updated_student = student
            break
    if updated_student:
        sync_atomic_save_json(BIRTHDAYS_FILE_PATH, registry)
        clear_registry_cache()
        add_user_to_cache(clean_username, tg_id)
        log.info(
            f"🎉 Разовая фиксация ID: {updated_student['full_name']} "
            f"(@{clean_username}) -> tg_id={tg_id}"
        )
    return updated_student


def bind_student_tg_id(full_name: str, tg_id: int) -> dict[str, Any] | None:
    """Привязывает Telegram ID к студенту по ФИО для студентов без username."""
    registry = load_classmates_registry()
    target_clean = full_name.strip().lower()
    updated = None
    for student in registry:
        if student.get("full_name", "").strip().lower() == target_clean:
            student["tg_id"] = tg_id
            updated = student
            break
    if updated:
        sync_atomic_save_json(BIRTHDAYS_FILE_PATH, registry)
        clear_registry_cache()
        uname = updated.get("username")
        if uname:
            add_user_to_cache(uname.lstrip("@").lower(), tg_id)
        log.info(f"Ручная привязка ID: {updated['full_name']} -> tg_id={tg_id}")
    return updated


def is_authorized_user(user: User | None) -> bool:
    """
    Проверяет, авторизован ли пользователь (Администратор или студент с ID).

    :param user: Экземпляр aiogram User
    :return: True, если доступ разрешен
    """
    if not user:
        return False
    if user.id == ALLOWED_USER_ID:
        return True
    return find_classmate_by_tg_id(user.id) is not None


def process_user_auth(user: User | None) -> tuple[bool, bool, dict[str, Any] | None]:
    """
    Основная логика аутентификации пользователя при входе в бота.

    Политикой Варианта А разрешен доступ только проверенным студентам
    с подтвержденным tg_id или главному администратору.
    """
    if not user:
        return False, False, None
    if user.id == ALLOWED_USER_ID:
        return True, False, None
    existing = find_classmate_by_tg_id(user.id)
    if existing:
        return True, False, existing
    return False, False, None

