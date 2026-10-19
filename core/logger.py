"""
Единый модуль логирования платформы с поддержкой распределенного трейсинга.

Предоставляет настроенный логгер с выводом в консоль и ротируемый файл logs/bot.log.
Поддерживает контекстные переменные trace_id / request_id для сквозной корреляции логов.
"""

import contextvars
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from config import LOG_BACKUP_COUNT, LOG_MAX_BYTES

MAX_LOG_BYTES = LOG_MAX_BYTES
BACKUP_LOG_COUNT = LOG_BACKUP_COUNT

_TRACE_ID_CTX: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")


def set_trace_id(trace_id: str) -> None:
    """
    Устанавливает идентификатор распределенного трейсинга в текущий контекст asyncio.

    Позволяет связывать события между сервисами bot, api и solver.

    Ничего не возвращает.
    """
    _TRACE_ID_CTX.set(trace_id)


def get_trace_id() -> str:
    """
    Возвращает активный идентификатор трейсинга из текущего контекста.

    Возвращает непустую строку идентификатора или пустую строку, если контекст не задан.
    """
    return _TRACE_ID_CTX.get()


class _TraceIdFilter(logging.Filter):
    """Инжектирует контекстный trace_id в каждую запись лога."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Добавляет форматированный префикс trace_id в объект LogRecord."""
        tid = get_trace_id()
        record.trace_id = f" [trace_id={tid}]" if tid else ""
        return True


def _create_formatter() -> logging.Formatter:
    """
    Создает унифицированный форматтер строковых записей с поддержкой trace_id.

    Обеспечивает консистентный формат таймстемпов, уровней и подсистем.

    Возвращает настроенный экземпляр logging.Formatter.
    """
    return logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]%(trace_id)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _create_stream_handler(formatter: logging.Formatter) -> logging.StreamHandler:
    """
    Создает потоковый обработчик для вывода сообщений в stdout.

    Позволяет Docker контейнерам перехватывать логи через docker logs.

    Возвращает сконфигурированный экземпляр logging.StreamHandler.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(_TraceIdFilter())
    handler.setLevel(logging.INFO)
    return handler


def _create_rotating_file_handler(formatter: logging.Formatter) -> RotatingFileHandler:
    """
    Создает ротируемый файловый обработчик журналов с ограничением размера.

    Защищает дисковое пространство сервера от переполнения при активной отладке.

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
    handler.addFilter(_TraceIdFilter())
    handler.setLevel(logging.DEBUG)
    return handler


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает синглтон-экземпляр логгера для указанной подсистемы.

    Проверяет наличие уже зарегистрированных хэндлеров во избежание дублирования.

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
