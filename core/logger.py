"""
Единый модуль логирования проекта.

Предоставляет настроенный логгер с выводом в консоль и ротируемый файл logs/bot.log.
Использует RotatingFileHandler (до 10 МБ на файл, 5 бэкапов) для защиты диска от переполнения.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Максимальный размер лог-файла (10 МБ) и количество архивных файлов
MAX_LOG_BYTES = 10 * 1024 * 1024
BACKUP_LOG_COUNT = 5


def _create_formatter() -> logging.Formatter:
    """Создает единый форматтер сообщений для консоли и файла."""
    return logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def _create_stream_handler(formatter: logging.Formatter) -> logging.StreamHandler:
    """Создает консольный хэндлер со стандартным потоком вывода."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    return handler


def _create_rotating_file_handler(formatter: logging.Formatter) -> RotatingFileHandler:
    """
    Создает ротируемый файловый хэндлер UTF-8 с лимитом размера.

    Защищает диск сервера от бесконтрольного роста логов.
    """
    os.makedirs("logs", exist_ok=True)
    handler = RotatingFileHandler(
        "logs/bot.log",
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_LOG_COUNT,
        encoding="utf-8"
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    return handler


def get_logger(name: str) -> logging.Logger:
    """
    Создает и настраивает логгер для заданной подсистемы.

    :param name: Смысловое название компонента (напр. 'schedule_parser')
    :return: Экземпляр logging.Logger
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = _create_formatter()
    logger.addHandler(_create_stream_handler(formatter))
    logger.addHandler(_create_rotating_file_handler(formatter))
    return logger
