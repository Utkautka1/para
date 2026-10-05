"""
Модуль локального хранения персональных контактов преподавателей.
"""

from typing import Dict
from integrations.docx_parser import TeacherData
from utils.storage import sync_atomic_save_json, sync_load_json

CUSTOM_TEACHERS_FILE = "data/custom_teachers.json"


def load_custom_teachers() -> Dict[str, TeacherData]:
    """
    Загружает кастомные контакты преподавателей из JSON.

    :return: Словарь преподавателей
    """
    return sync_load_json(CUSTOM_TEACHERS_FILE, default={})


def save_custom_teacher(last_name: str, full_name: str, link_info: str) -> None:
    """
    Сохраняет или обновляет кастомного преподавателя.

    :param last_name: Фамилия ключа
    :param full_name: Полное имя
    :param link_info: Данные ссылки
    """
    data = load_custom_teachers()
    data[last_name.lower()] = {
        "full_name": full_name,
        "link_info": link_info
    }
    sync_atomic_save_json(CUSTOM_TEACHERS_FILE, data)


def delete_custom_teacher(last_name: str) -> None:
    """
    Удаляет преподавателя по его ключу-фамилии из JSON.

    :param last_name: Фамилия (ключ)
    """
    data = load_custom_teachers()
    if last_name.lower() in data:
        data.pop(last_name.lower())
        sync_atomic_save_json(CUSTOM_TEACHERS_FILE, data)
