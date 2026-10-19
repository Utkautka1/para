"""
Модуль оркестрации задач решения ДЗ и управления циклом воркера.

Извлекает задачи из Redis-очереди, исполняет пайплайн DeepSeek
под семафором параллелизма, контролирует подтверждения (ACK/NACK)
и обеспечивает graceful drain активных задач при выключении.
"""

import asyncio
import os
import tempfile
import uuid

from aiogram import Bot

import config
from core.logger import get_logger
from core.redis_cache import ack_hw_task, nack_hw_task, pop_hw_task
from core.telemetry import trace_span
from integrations.deepseek import solve_homework
from services.solver.payload_extractor import resolve_task_payload
from services.solver.telegram_reporter import notify_task_error, send_solution_to_telegram
from utils.doc_generator import create_solution_docx

log = get_logger("solver_processor")


def _build_temp_doc_path(msg_id: int) -> str:
    """
    Генерирует изолированный путь для временного .docx файла решения.

    Использует UUID-суффикс и идентификатор сообщения для предотвращения коллизий.

    Возвращает абсолютный путь к временному файлу в системной tmpfs.
    """
    token = uuid.uuid4().hex[:8]
    return os.path.join(tempfile.gettempdir(), f"solution_{token}_{msg_id}.docx")


def _cleanup_temp_file(path: str) -> None:
    """
    Безопасно удаляет временный файл документа, если он существует.

    Предотвращает утечку дескрипторов и переполнение дискового пространства.

    Ничего не возвращает.
    """
    if os.path.exists(path):
        os.remove(path)


async def _handle_task_failure(tg_bot: Bot, task: dict, msg_id: int, error: Exception) -> None:
    """
    Обрабатывает исключение задачи: регистрирует NACK и уведомляет об ошибке.

    Логирует контекст ошибки и ставит задачу на повтор либо шлет алерт при лимите.

    Ничего не возвращает.
    """
    log.error(f"❌ Сбой обработки ДЗ msg_id={msg_id}: {error}")
    retried = await nack_hw_task(task, max_retries=config.HW_MAX_TASK_RETRIES)
    if not retried:
        await notify_task_error(tg_bot, task)


async def execute_single_task(tg_bot: Bot, task: dict) -> None:
    """
    Обрабатывает одну задачу: решает ДЗ в DeepSeek и отправляет документ.

    Генерирует .docx документ, отправляет в топик решений и подтверждает задачу (ACK).
    Создает span OpenTelemetry solver.execute_task для трассировки.

    Ничего не возвращает.
    """
    msg_id = task.get("message_id", 0)
    doc_path = _build_temp_doc_path(msg_id)
    attrs = {"hw.message_id": msg_id, "hw.file_unique_id": task.get("file_unique_id", "")}
    async with trace_span("solver.execute_task", attributes=attrs):
        try:
            img_bytes, prompt = await resolve_task_payload(tg_bot, task)
            solution = await solve_homework(image_bytes=img_bytes, text_prompt=prompt)
            await asyncio.to_thread(create_solution_docx, solution, output_path=doc_path)
            await send_solution_to_telegram(tg_bot, task, doc_path)
            await ack_hw_task(task)
            log.info(f"✅ Решение ДЗ msg_id={msg_id} успешно доставлено в топик решений!")
        except Exception as e:
            await _handle_task_failure(tg_bot, task, msg_id, e)
        finally:
            _cleanup_temp_file(doc_path)



async def _guarded_execute_task(tg_bot: Bot, task: dict, semaphore: asyncio.Semaphore) -> None:
    """
    Исполняет задачу под семафором параллелизма для защиты от перегрузки.

    Ограничивает число одновременно решаемых задач в DeepSeek API.

    Ничего не возвращает.
    """
    async with semaphore:
        await execute_single_task(tg_bot, task)


async def _drain_active_tasks(active_tasks: set[asyncio.Task]) -> None:
    """
    Корректно ожидает завершения всех запущенных задач при остановке сервиса.

    Предотвращает потерю выполняемых расчетов DeepSeek при перезапуске контейнера.

    Ничего не возвращает.
    """
    log.info("Остановка цикла solver_loop, ожидание активных задач...")
    if active_tasks:
        await asyncio.gather(*active_tasks, return_exceptions=True)


async def run_solver_loop(tg_bot: Bot, semaphore: asyncio.Semaphore) -> None:
    """
    Бесконечный цикл чтения очереди задач и параллельного запуска решений.

    Извлекает новые задачи из Redis и распределяет их по фоновым воркерам.
    Контролирует максимальное количество параллельных задач.

    Ничего не возвращает.
    """
    log.info("Запущен рабочий цикл очереди решений para-solver...")
    active_tasks: set[asyncio.Task] = set()
    while True:
        try:
            active_tasks = {t for t in active_tasks if not t.done()}
            if len(active_tasks) >= config.SOLVER_MAX_CONCURRENT_TASKS:
                await asyncio.sleep(0.5)
                continue

            task = await pop_hw_task(timeout=2)
            if task:
                active_tasks.add(asyncio.create_task(_guarded_execute_task(tg_bot, task, semaphore)))
        except asyncio.CancelledError:
            await _drain_active_tasks(active_tasks)
            break
        except Exception as e:
            log.error(f"Ошибка в цикле solver_loop: {e}")
            await asyncio.sleep(2)
