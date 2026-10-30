"""
Точка входа микросервиса решения домашних заданий (para-solver).

Инициализирует подключение к Redis, восстанавливает зависшие задачи
и запускает рабочий цикл run_solver_loop под защитным семафором.
При завершении работы гарантирует корректное закрытие клиентов.
"""

import asyncio

import config
from core.bot import bot
from core.logger import get_logger
from core.redis import close_redis, init_redis
from core.redis_cache import recover_stale_hw_tasks
from core.telemetry import setup_telemetry
from integrations.deepseek import close_deepseek_client
from services.solver import run_solver_loop

log = get_logger("solver_entrypoint")
_SOLVER_SEMAPHORE = asyncio.Semaphore(config.SOLVER_MAX_CONCURRENT_TASKS)


async def _shutdown_resources() -> None:
    """
    Корректно закрывает соединения с DeepSeek API, Redis и Telegram Bot API.

    Освобождает сетевые сокеты и предотвращает утечку ресурсов процесса.

    Ничего не возвращает.
    """
    await close_deepseek_client()
    await close_redis()
    await bot.session.close()
    log.info("Воркер para-solver корректно остановлен.")


async def main() -> None:
    """
    Инициализация системных ресурсов и запуск воркера решений para-solver.

    Восстанавливает зависшие задачи из очереди обработки при старте.
    В блоке finally гарантированно закрывает соединения с DeepSeek, Redis и Telegram.

    Ничего не возвращает.
    """
    log.info("=" * 60)
    log.info("ЗАПУСК Сервиса AI-Решения ДЗ (para-solver)")
    log.info("  Модель DeepSeek: %s", config.DEEPSEEK_MODEL_NAME)
    log.info("=" * 60)
    setup_telemetry("para-solver")
    await init_redis()
    await recover_stale_hw_tasks()

    try:
        await run_solver_loop(bot, _SOLVER_SEMAPHORE)
    finally:
        await _shutdown_resources()


if __name__ == "__main__":
    asyncio.run(main())
