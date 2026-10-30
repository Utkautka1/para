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
    Синхронно считывает данные из локального JSON-файла.

    Проверяет физическое существование файла перед открытием, перехватывает
    синтаксические ошибки JSON и повреждения файла, предотвращая падение сервиса.

    Возвращает десериализованный объект (dict/list) или default при отсутствии файла/ошибке.
    """
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error("Ошибка чтения JSON файла %s: %s", file_path, e)
        return default


def _flush_json_to_file(temp_file, data: Any) -> None:
    """
    Сбрасывает сериализованный JSON на диск с принудительной синхронизацией.

    Вызов os.fsync гарантирует запись буферов операционной системы на физический
    носитель до того, как произойдет переименование файла.

    Ничего не возвращает, генерирует исключения ввода-вывода при сбоях.
    """
    json.dump(data, temp_file, ensure_ascii=False, indent=2)
    temp_file.flush()
    os.fsync(temp_file.fileno())


def _write_temp_and_replace(file_path: str, data: Any) -> bool:
    """
    Записывает данные во временный файл и атомарно заменяет целевой файл.

    Использует os.replace для POSIX-атомарной подмены, защищая файл от состояния
    гонки и повреждения при аварийном завершении процесса или ОС во время записи.

    Возвращает True в случае успешной фиксации на диске, иначе False.
    """
    dir_name = os.path.dirname(os.path.abspath(file_path))
    os.makedirs(dir_name, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as temp_file:
            temp_path = temp_file.name
            _flush_json_to_file(temp_file, data)
        os.replace(temp_path, file_path)
        return True
    except Exception as e:
        log.error("Ошибка атомарной записи в %s: %s", file_path, e)
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return False


def sync_atomic_save_json(file_path: str, data: Any) -> bool:
    """
    Синхронно сохраняет структуру данных в JSON-файл с гарантией целостности.

    Выступает фасадом к _write_temp_and_replace для явного вызова в синхронном
    контексте и скриптах инициализации.

    Возвращает True при успешном сохранении, False при ошибках I/O.
    """
    return _write_temp_and_replace(file_path, data)


async def load_json(file_path: str, default: Any = None) -> Any:
    """
    Асинхронно считывает JSON в пуле потоков без блокировки цикла событий.

    Делегирует синхронный дисковый ввод-вывод в asyncio.to_thread, предотвращая
    задержки обработки асинхронных сетевых запросов и вебхуков Telegram.

    Возвращает загруженные данные или значение default.
    """
    return await asyncio.to_thread(sync_load_json, file_path, default)


async def save_json(file_path: str, data: Any) -> bool:
    """
    Асинхронно и атомарно сохраняет JSON в отдельном пуле потоков.

    Сочетает неблокирующее выполнение через asyncio.to_thread и безопасность
    атомарной подмены файла при конкурентных обновлениях.

    Возвращает True при успешной записи, False при сбое.
    """
    return await asyncio.to_thread(sync_atomic_save_json, file_path, data)
