"""
Единый модуль логирования платформы с поддержкой распределенного трейсинга.

Предоставляет настроенный логгер с выводом в консоль и ротируемый файл logs/{service}.log.
Поддерживает контекстные переменные trace_id / request_id для сквозной корреляции логов.

Каждый сервис пишет в свой файл (api.log, bot.log, worker.log, solver.log): все контейнеры
монтируют общий ./logs, а RotatingFileHandler корректно ротирует файл, только если в него
пишет один процесс через один хэндлер. Поэтому хэндлеры — синглтоны процесса, общие
для всех именованных логгеров, а не новый файловый хэндлер на каждый get_logger().
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

# Сервисы с собственным лог-файлом; всё остальное (pytest, скрипты) пишет в logs/app.log
_SERVICE_NAMES: frozenset[str] = frozenset({"api", "bot", "worker", "solver"})

# Хэндлеры процесса, общие для всех логгеров (создаются лениво при первом get_logger)
_SHARED_HANDLERS: list[logging.Handler] | None = None


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


def _resolve_log_file() -> str:
    """
    Определяет лог-файл текущего сервиса.

    Имя берётся из LOG_SERVICE, иначе из entrypoint (`python api.py` -> api),
    чтобы не требовать отдельной настройки в каждом контейнере.

    Возвращает путь вида logs/api.log; для неизвестных процессов — logs/app.log.
    """
    service = os.getenv("LOG_SERVICE") or os.path.splitext(os.path.basename(sys.argv[0]))[0]
    return f"logs/{service if service in _SERVICE_NAMES else 'app'}.log"


def _create_rotating_file_handler(formatter: logging.Formatter) -> RotatingFileHandler | None:
    """
    Создает ротируемый файловый обработчик журналов с ограничением размера.

    Защищает дисковое пространство сервера от переполнения при активной отладке.
    При ошибках доступа безопасно возвращает None с предупреждением в stderr.

    Возвращает экземпляр RotatingFileHandler для файла сервиса или None.
    """
    log_file = _resolve_log_file()
    try:
        os.makedirs("logs", exist_ok=True)
        handler = RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_BYTES,
            backupCount=BACKUP_LOG_COUNT,
            encoding="utf-8",
        )
        handler.setFormatter(formatter)
        handler.addFilter(_TraceIdFilter())
        handler.setLevel(logging.DEBUG)
        return handler
    except (PermissionError, OSError) as e:
        sys.stderr.write(f"WARNING: Не удалось открыть {log_file} ({e}), логи идут в stdout\n")
        return None


def _get_shared_handlers() -> list[logging.Handler]:
    """
    Возвращает хэндлеры процесса (stdout + файл сервиса), создавая их один раз.

    Раньше каждый логгер открывал свой RotatingFileHandler на тот же файл: при ротации
    один переименовывал файл, а остальные продолжали писать в старый.

    Возвращает список хэндлеров.
    """
    global _SHARED_HANDLERS
    if _SHARED_HANDLERS is None:
        formatter = _create_formatter()
        file_handler = _create_rotating_file_handler(formatter)
        _SHARED_HANDLERS = [_create_stream_handler(formatter), *([file_handler] if file_handler else [])]
    return _SHARED_HANDLERS


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает синглтон-экземпляр логгера для указанной подсистемы.

    Проверяет наличие уже зарегистрированных хэндлеров во избежание дублирования.

    Возвращает логгер, подключённый к общим хэндлерам процесса.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    for handler in _get_shared_handlers():
        logger.addHandler(handler)
    return logger
