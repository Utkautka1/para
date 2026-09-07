"""
Единый модуль логирования проекта.

Предоставляет настроенный логгер с выводом в консоль и файл logs/bot.log.
Формат логов содержит время, уровень, имя модуля и понятное сообщение.
"""

import logging
import os
import sys


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

    # Создаем директорию для логов, если её еще нет
    os.makedirs("logs", exist_ok=True)

    # Форматирование сообщений лога
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Консольный хэндлер
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    # Файловый хэндлер
    file_handler = logging.FileHandler("logs/bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger
