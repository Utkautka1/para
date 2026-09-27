"""
Главный модуль запуска Telegram-бота расписания КТМУ.

Инициализирует роутеры хэндлеров, подключение к Redis и MongoDB
и запускает процесс получения обновлений (polling) от Telegram.
"""

import asyncio
from core.bot import bot, dp
from core.logger import get_logger
from core.mongo import close_mongo, init_mongo
from core.redis import init_redis, redis_client

log = get_logger("bot_main")


def register_all_routers() -> None:
    """Регистрирует все хэндлеры и роутеры в диспетчере aiogram."""
    from bot.handlers.admin.mute import router as mute_router
    from bot.handlers.admin.panel import router as admin_router
    from bot.handlers.user.auth_fallback import router as fallback_router
    from bot.handlers.user.hw_solver import router as hw_solver_router
    from bot.handlers.user.public_copy import public_router
    from bot.handlers.user.schedule import router as user_router
    dp.include_router(mute_router)
    dp.include_router(hw_solver_router)
    dp.include_router(public_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(fallback_router)


async def shutdown_bot() -> None:
    """Корректно закрывает сессию бота, соединения с Redis и MongoDB."""
    log.info("Остановка бота: закрытие сессий...")
    if redis_client:
        await redis_client.aclose()
    await close_mongo()
    await bot.session.close()
    log.info("Сессии Telegram, Redis и MongoDB закрыты. Бот остановлен.")


async def main() -> None:
    """Основная асинхронная функция инициализации и запуска бота."""
    log.info("=" * 60)
    log.info("ЗАПУСК Персонального Telegram Бота КТМУ (para-bot)")
    log.info("=" * 60)
    register_all_routers()
    await init_redis()
    await init_mongo()
    try:
        await dp.start_polling(bot)
    except Exception as e:
        log.error(f"❌ Критическая ошибка при работе бота: {e}")
    finally:
        await shutdown_bot()


if __name__ == "__main__":
    asyncio.run(main())
