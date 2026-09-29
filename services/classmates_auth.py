"""
Сервис аутентификации и разовой регистрации одногруппников группы 1-КПД-3.

Отвечает за:
  1. Проверку принадлежности пользователя к группе (ALLOWED_USER_ID или реестр).
  2. Разовую фиксацию цифрового Telegram ID при первом нажатии /start в ЛС бота.
  3. Сохранение привязки в data/birthdays.json и постоянный кэш user_cache.
  4. Защиту от несанкционированного доступа посторонних пользователей.
"""

from typing import Any, Dict, List, Optional
from aiogram.types import User
from config import ALLOWED_USER_ID
from core.logger import get_logger
from services.user_cache import add_user_to_cache
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("classmates_auth")
BIRTHDAYS_FILE_PATH = "data/birthdays.json"


def load_classmates_registry() -> List[Dict[str, Any]]:
    """
    Загружает актуальный список студентов из data/birthdays.json.

    :return: Список словарей с данными одногруппников
    """
    return sync_load_json(BIRTHDAYS_FILE_PATH, default=[])


def find_classmate_by_tg_id(user_id: int) -> Optional[Dict[str, Any]]:
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


def find_unregistered_by_username(username: str) -> Optional[Dict[str, Any]]:
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


def update_classmate_tg_id(clean_username: str, tg_id: int) -> Optional[Dict[str, Any]]:
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
        add_user_to_cache(clean_username, tg_id)
        log.info(
            f"🎉 Разовая фиксация ID: {updated_student['full_name']} "
            f"(@{clean_username}) -> tg_id={tg_id}"
        )
    return updated_student


def is_authorized_user(user: Optional[User]) -> bool:
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


def process_user_auth(user: Optional[User]) -> tuple[bool, bool, Optional[Dict[str, Any]]]:
    """
    Основная логика аутентификации пользователя при входе в бота.

    Возвращает кортеж: (is_auth, is_just_registered, student_info).
    """
    if not user:
        return False, False, None
    if user.id == ALLOWED_USER_ID:
        return True, False, None
    existing = find_classmate_by_tg_id(user.id)
    if existing:
        return True, False, existing
    if user.username:
        clean = user.username.lstrip("@").lower()
        new_student = update_classmate_tg_id(clean, user.id)
        if new_student:
            return True, True, new_student
    return False, False, None
