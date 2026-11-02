"""
Сервис аутентификации и разовой регистрации одногруппников группы 1-КПД-3.

Отвечает за:
  1. Проверку принадлежности пользователя к группе (ALLOWED_USER_ID или реестр).
  2. Ручную привязку цифрового Telegram ID старостой через админ-панель.
  3. Сохранение привязки в data/birthdays.json и постоянный кэш user_cache.
  4. Защиту от несанкционированного доступа посторонних пользователей.
"""

import asyncio
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

# Реестр пишет только процесс бота (привязка из админ-панели), поэтому хватает asyncio.Lock
_REGISTRY_WRITE_LOCK = asyncio.Lock()


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


def find_classmate_by_fio(fio: str) -> dict[str, Any] | None:
    """
    Ищет студента в реестре группы по ФИО из журнала посещаемости.

    В журнале и реестре ФИО могут отличаться отчеством, поэтому совпадение
    засчитывается, если одно имя целиком содержится в другом (как в лидерборде).

    Возвращает словарь с профилем студента или None.
    """
    target = fio.strip().lower()
    if not target:
        return None
    for student in load_classmates_registry():
        name = str(student.get("full_name", "")).strip().lower()
        if name and (name in target or target in name):
            return student
    return None


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


def _bind_in_registry(full_name: str, tg_id: int) -> dict[str, Any] | None:
    """
    Привязывает tg_id к студенту прямо в файле реестра (синхронно, для to_thread).

    Читает свежую копию файла, а не кэш: при сбое записи кэш с уже
    проставленным tg_id открыл бы доступ, которого в реестре нет.
    Отказывает, если tg_id уже закреплён за другим студентом — иначе один
    аккаунт получил бы профиль, ачивки и посещаемость двух человек.

    Возвращает обновлённый профиль или None (ФИО не найдено, ID занят, сбой записи).
    """
    registry = sync_load_json(BIRTHDAYS_FILE_PATH, default=[])
    student = _find_student_by_fullname(registry, full_name.strip().lower())
    owner = next((s for s in registry if s.get("tg_id") == tg_id), None)
    if not student or (owner and owner is not student):
        return None
    student["tg_id"] = tg_id
    return student if sync_atomic_save_json(BIRTHDAYS_FILE_PATH, registry) else None


async def bind_student_tg_id(full_name: str, tg_id: int) -> dict[str, Any] | None:
    """
    Привязывает Telegram ID к студенту по полному ФИО (для пользователей без @username).

    Чтение-изменение-запись реестра идёт под блокировкой и в отдельном потоке:
    две параллельные привязки иначе затёрли бы друг друга, а файловый I/O
    блокировал бы event loop бота.

    Возвращает обновленный профиль студента или None, если привязка не удалась.
    """
    async with _REGISTRY_WRITE_LOCK:
        updated = await asyncio.to_thread(_bind_in_registry, full_name, tg_id)
    if not updated:
        log.warning("Привязка ID отклонена: %s -> tg_id=%s (не найден, занят или сбой записи)", full_name, tg_id)
        return None
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
