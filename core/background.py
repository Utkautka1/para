"""
Запуск фоновых задач «выстрелил и забыл» без потери задач и ошибок.

Голый asyncio.create_task(...) без сохранённой ссылки опасен:
  1. event loop держит на задачу только слабую ссылку — сборщик мусора может
     уничтожить её посреди работы
  2. исключение внутри такой задачи никто не забирает — оно всплывает лишь
     как "Task exception was never retrieved" при сборке мусора, без контекста
  3. при остановке сервиса незавершённые задачи молча обрываются

spawn() держит ссылку до завершения задачи и логирует её ошибку,
drain_background() даёт задачам доработать при остановке процесса.
"""

import asyncio
from collections.abc import Coroutine
from typing import Any

from core.logger import get_logger

log = get_logger("background")

# Живые фоновые задачи процесса: сильные ссылки до завершения
_TASKS: set[asyncio.Task[Any]] = set()


def _on_done(task: asyncio.Task[Any]) -> None:
    """Снимает ссылку на завершённую задачу и логирует её исключение."""
    _TASKS.discard(task)
    if task.cancelled():
        return
    if exc := task.exception():
        log.error("❌ Фоновая задача %s упала: %s", task.get_name(), exc, exc_info=exc)


def spawn(coro: Coroutine[Any, Any, Any], name: str | None = None) -> asyncio.Task[Any]:
    """
    Запускает корутину фоновой задачей и держит на неё ссылку до завершения.

    Возвращает созданную задачу (ждать её не обязательно).
    """
    task = asyncio.create_task(coro, name=name or getattr(coro, "__qualname__", None))
    _TASKS.add(task)
    task.add_done_callback(_on_done)
    return task


async def drain_background(timeout: float = 10.0) -> None:
    """
    Ждёт завершения фоновых задач при остановке сервиса, остальные отменяет.

    timeout — сколько ждать доработки задач (секунды); вызывать из shutdown-хука.

    Ничего не возвращает.
    """
    if not _TASKS:
        return
    log.info("Ожидание %s фоновых задач перед остановкой (до %s сек)", len(_TASKS), timeout)
    _, pending = await asyncio.wait(set(_TASKS), timeout=timeout)
    for task in pending:
        task.cancel()
    if pending:
        log.warning("⚠️  Отменено %s фоновых задач, не успевших завершиться", len(pending))
