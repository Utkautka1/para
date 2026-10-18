"""
Модуль локального хранения персональных контактов преподавателей.
"""


from config import CUSTOM_TEACHERS_FILE_PATH
from integrations.docx_parser import TeacherData
from utils.storage import sync_atomic_save_json, sync_load_json

CUSTOM_TEACHERS_FILE = CUSTOM_TEACHERS_FILE_PATH


def load_custom_teachers() -> dict[str, TeacherData]:
    """
    Загружает переопределенные контакты и ссылки преподавателей из локального JSON.

    Позволяет старосте и администраторам оперативно вносить Zoom-ссылки и контакты,
    если они отсутствуют или некорректны в общем вузовском DOCX файле.

    Возвращает словарь {фамилия_в_нижнем_регистре: TeacherData}.
    """
    return sync_load_json(CUSTOM_TEACHERS_FILE, default={})


def save_custom_teacher(last_name: str, full_name: str, link_info: str) -> None:
    """
    Атомарно сохраняет или обновляет контакты преподавателя в файле.

    Приводит фамилию-ключ к нижнему регистру для регистронезависимого поиска
    и использует sync_atomic_save_json для защиты от повреждения при сбоях.

    Ничего не возвращает.
    """
    data = load_custom_teachers()
    data[last_name.lower()] = {
        "full_name": full_name,
        "link_info": link_info
    }
    sync_atomic_save_json(CUSTOM_TEACHERS_FILE, data)


def delete_custom_teacher(last_name: str) -> None:
    """
    Удаляет переопределенные данные преподавателя по его фамилии.

    Возвращает приоритет исходным вузовским данным из DOCX при удалении
    кастомного переопределения администратором.

    Ничего не возвращает.
    """
    data = load_custom_teachers()
    if last_name.lower() in data:
        data.pop(last_name.lower())
        sync_atomic_save_json(CUSTOM_TEACHERS_FILE, data)

