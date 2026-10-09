"""
Модуль атомарного и безопасного ввода-вывода JSON-файлов.

Гарантирует сохранность состояния при рестартах и сбоях:
запись производится через временный файл с последующим os.replace.
Асинхронные обертки используют asyncio.to_thread для предотвращения блокировки Event Loop.
"""

import asyncio
import json
import os
import tempfile
from typing import Any

from core.logger import get_logger

log = get_logger("storage")


def sync_load_json(file_path: str, default: Any = None) -> Any:
    """
    Синхронно считывает данные из JSON файла.

    :param file_path: Путь к файлу
    :param default: Значение по умолчанию при отсутствии или ошибке
    :return: Распарсенные данные или default
    """
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Ошибка чтения JSON файла {file_path}: {e}")
        return default


def _write_temp_and_replace(file_path: str, data: Any) -> bool:
    """Записывает данные во временный файл и атомарно заменяет целевой файл."""
    dir_name = os.path.dirname(os.path.abspath(file_path))
    os.makedirs(dir_name, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as temp_file:
            temp_path = temp_file.name
            json.dump(data, temp_file, ensure_ascii=False, indent=2)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, file_path)
        return True
    except Exception as e:
        log.error(f"Ошибка атомарной записи в {file_path}: {e}")
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return False


def sync_atomic_save_json(file_path: str, data: Any) -> bool:
    """
    Синхронно и атомарно сохраняет данные в JSON файл.

    :param file_path: Путь к целевому файлу
    :param data: Данные для сериализации
    :return: True при успехе, иначе False
    """
    return _write_temp_and_replace(file_path, data)


async def load_json(file_path: str, default: Any = None) -> Any:
    """
    Асинхронно считывает JSON в пуле потоков без блокировки цикла событий.

    :param file_path: Путь к файлу
    :param default: Значение по умолчанию
    :return: Распарсенные данные
    """
    return await asyncio.to_thread(sync_load_json, file_path, default)


async def save_json(file_path: str, data: Any) -> bool:
    """
    Асинхронно и атомарно сохраняет JSON в пуле потоков.

    :param file_path: Путь к файлу
    :param data: Данные для сохранения
    :return: True при успехе
    """
    return await asyncio.to_thread(sync_atomic_save_json, file_path, data)
