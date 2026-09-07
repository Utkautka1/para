"""
Модуль локального хранения персональных контактов преподавателей.
"""

import json
import os
from typing import Dict
from services.docx_parser import TeacherData

CUSTOM_TEACHERS_FILE = "data/custom_teachers.json"


def load_custom_teachers() -> Dict[str, TeacherData]:
    """
    Загружает кастомные контакты преподавателей из JSON.

    :return: Словарь преподавателей
    """
    if os.path.exists(CUSTOM_TEACHERS_FILE):
        try:
            with open(CUSTOM_TEACHERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


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
    os.makedirs("data", exist_ok=True)
    with open(CUSTOM_TEACHERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_custom_teacher(last_name: str) -> None:
    """
    Удаляет преподавателя по его ключу-фамилии из JSON.

    :param last_name: Фамилия (ключ)
    """
    data = load_custom_teachers()
    if last_name.lower() in data:
        data.pop(last_name.lower())
        with open(CUSTOM_TEACHERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

