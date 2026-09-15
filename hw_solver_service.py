"""
Модуль отдельного микросервиса авторешалки ДЗ.

Изолированный сервис-воркер, запускаемый в Docker-контейнере para-hw-solver.
"""

import asyncio
from aiogram import Bot, Dispatcher
import config
from core.logger import get_logger
from core.redis import init_redis
from bot.handlers.user.hw_solver import router as hw_solver_router

log = get_logger("hw_solver_service")


async def main() -> None:
    """
    Точка входа микросервиса авторешалки ДЗ.
    """
    log.info("=" * 60)
    log.info("ЗАПУСК Микросервиса Авторешалки ДЗ (para-hw-solver)")
    log.info(f"  Входящий топик: {config.HW_INPUT_TOPIC_THREAD_ID}")
    log.info(f"  Исходящий топик: {config.HW_OUTPUT_TOPIC_THREAD_ID}")
    log.info("=" * 60)

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(hw_solver_router)

    await init_redis()

    try:
        await dp.start_polling(bot)
    except Exception as e:
        log.error(f"❌ Ошибка микросервиса авторешалки: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
