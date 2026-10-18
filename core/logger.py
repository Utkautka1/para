"""
Единый модуль логирования проекта.

Предоставляет настроенный логгер с выводом в консоль и ротируемый файл logs/bot.log.
Использует RotatingFileHandler (до 10 МБ на файл, 5 бэкапов) для защиты диска от переполнения.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from config import LOG_BACKUP_COUNT, LOG_MAX_BYTES

# Максимальный размер лог-файла и количество архивных файлов
MAX_LOG_BYTES = LOG_MAX_BYTES
BACKUP_LOG_COUNT = LOG_BACKUP_COUNT


def _create_formatter() -> logging.Formatter:
    """
    Создает унифицированный форматтер строковых записей журнала событий.

    Обеспечивает консистентный формат таймстемпов, уровней логирования и имени
    подсистемы для удобного парсинга в консоли и grep-фильтрации файлов.

    Возвращает настроенный экземпляр logging.Formatter.
    """
    return logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _create_stream_handler(formatter: logging.Formatter) -> logging.StreamHandler:
    """
    Создает потоковый обработчик для вывода сообщений журнала в стандартный поток stdout.

    Позволяет Docker контейнерам перехватывать логи в реальном времени через docker logs
    с фильтрацией уровня INFO и выше.

    Возвращает сконфигурированный экземпляр logging.StreamHandler.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    return handler


def _create_rotating_file_handler(formatter: logging.Formatter) -> RotatingFileHandler:
    """
    Создает ротируемый файловый обработчик журналов с ограничением размера.

    Защищает дисковое пространство сервера от переполнения при активной отладке,
    сохраняя до 5 ротированных архивных файлов по 10 МБ в кодировке UTF-8.

    Возвращает экземпляр RotatingFileHandler для файла logs/bot.log.
    """
    os.makedirs("logs", exist_ok=True)
    handler = RotatingFileHandler(
        "logs/bot.log",
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_LOG_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    return handler


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает синглтон-экземпляр логгера для указанной подсистемы.

    Проверяет наличие уже зарегистрированных хэндлеров во избежание дублирования записей
    в логе при повторных импортах модуля в рамках одного процесса.

    Возвращает настроенный логгер с потоковым и ротируемым файловым обработчиками.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = _create_formatter()
    logger.addHandler(_create_stream_handler(formatter))
    logger.addHandler(_create_rotating_file_handler(formatter))
    return logger
