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
    """
    Сбрасывает оперативный кэш реестра одногруппников в памяти.

    Используется при модификации файла birthdays.json и в тестах для сброса
    сохраненного снимка реестра и метки времени mtime.

    Ничего не возвращает.
    """
    global _REGISTRY_CACHE, _REGISTRY_MTIME
    _REGISTRY_CACHE = None
    _REGISTRY_MTIME = 0.0


def load_classmates_registry(force_reload: bool = False) -> list[dict[str, Any]]:
    """
    Загружает актуальный список студентов группы с кэшированием в RAM по mtime.

    Исключает дисковый I/O на каждый входящий запрос или команду, возвращая
    кэшированный срез из памяти при неизменном файле birthdays.json.

    Возвращает список словарей с данными студентов группы.
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
    Ищет студента в реестре группы по сохраненному числовому Telegram ID.

    Используется фильтрами авторизации для мгновенного сопоставления сессии Telegram
    с конкретной записью в академическом списке группы.

    Возвращает словарь с профилем студента или None, если ID не привязан.
    """
    registry = load_classmates_registry()
    for student in registry:
        if student.get("tg_id") == user_id:
            return student
    return None


def find_unregistered_by_username(username: str) -> dict[str, Any] | None:
    """
    Ищет запись студента по юзернейму, у которой еще не зафиксирован tg_id.

    Позволяет определить студента при первом запуске бота по совпадению @username
    из академического реестра до момента фиксации числового ID.

    Возвращает словарь студента или None, если совпадение не найдено или уже зарегистрировано.
    """
    clean = username.lstrip("@").lower()
    registry = load_classmates_registry()
    for student in registry:
        uname = student.get("username")
        if uname and uname.lower() == clean and student.get("tg_id") is None:
            return student
    return None


def _find_unregistered_student(registry: list[dict[str, Any]], clean_username: str) -> dict[str, Any] | None:
    """
    Ищет неподтвержденную запись студента в переданном списке реестра.

    Изолирует линейный поиск по юзернейму для соблюдения лимита длины функции.

    Возвращает ссылку на словарь студента или None.
    """
    for student in registry:
        uname = student.get("username")
        if uname and uname.lower() == clean_username and student.get("tg_id") is None:
            return student
    return None


def update_classmate_tg_id(clean_username: str, tg_id: int) -> dict[str, Any] | None:
    """
    Атомарно фиксирует Telegram ID студента в реестре birthdays.json и кэше.

    Выполняется разово при первой авторизации по совпадению юзернейма, навсегда
    закрепляя аппаратный Telegram ID за профилем одногруппника.

    Возвращает обновленный словарь студента или None, если запись не найдена.
    """
    registry = load_classmates_registry()
    updated = _find_unregistered_student(registry, clean_username)
    if updated:
        updated["tg_id"] = tg_id
        sync_atomic_save_json(BIRTHDAYS_FILE_PATH, registry)
        clear_registry_cache()
        add_user_to_cache(clean_username, tg_id)
        log.info("🎉 Разовая фиксация ID: %s (@%s) -> tg_id=%s", updated["full_name"], clean_username, tg_id)
    return updated


def _find_student_by_fullname(registry: list[dict[str, Any]], target_clean: str) -> dict[str, Any] | None:
    """
    Ищет запись студента в реестре по нормализованному ФИО.

    Вспомогательная функция для ручной привязки аккаунтов без юзернейма.

    Возвращает словарь студента или None.
    """
    for student in registry:
        if student.get("full_name", "").strip().lower() == target_clean:
            return student
    return None


def bind_student_tg_id(full_name: str, tg_id: int) -> dict[str, Any] | None:
    """
    Привязывает Telegram ID к студенту по полному ФИО (для пользователей без @username).

    Позволяет администраторам связывать профили студентов, не имеющих публичного
    юзернейма в Telegram, с сохранением в JSON и локальном кэше.

    Возвращает обновленный профиль студента или None, если ФИО не найдено.
    """
    registry = load_classmates_registry()
    updated = _find_student_by_fullname(registry, full_name.strip().lower())
    if updated:
        updated["tg_id"] = tg_id
        sync_atomic_save_json(BIRTHDAYS_FILE_PATH, registry)
        clear_registry_cache()
        if uname := updated.get("username"):
            add_user_to_cache(uname.lstrip("@").lower(), tg_id)
        log.info("Ручная привязка ID: %s -> tg_id=%s", updated["full_name"], tg_id)
    return updated


def is_authorized_user(user: User | None) -> bool:
    """
    Проверяет наличие прав доступа к функционалу бота у входящего пользователя.

    Предоставляет доступ главному администратору (ALLOWED_USER_ID) и студентам,
    чей числовой tg_id успешно сопоставлен с реестром группы.

    Возвращает True, если пользователь авторизован, иначе False.
    """
    if not user:
        return False
    if user.id == ALLOWED_USER_ID:
        return True
    return find_classmate_by_tg_id(user.id) is not None


def process_user_auth(user: User | None) -> tuple[bool, bool, dict[str, Any] | None]:
    """
    Выполняет комплексную проверку статуса авторизации входящего пользователя.

    Определяет права доступа: авторизован ли пользователь, требуется ли первичная
    привязка и возвращает профиль одногруппника при наличии.

    Возвращает кортеж (is_authorized, is_first_time, student_dict).
    """
    if not user:
        return False, False, None
    if user.id == ALLOWED_USER_ID:
        return True, False, None
    existing = find_classmate_by_tg_id(user.id)
    if existing:
        return True, False, existing
    return False, False, None
