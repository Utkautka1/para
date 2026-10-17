"""
Главный модуль запуска Telegram-бота расписания КТМУ.

Инициализирует роутеры хэндлеров, подключение к Redis и запускает
процесс получения обновлений (polling) от Telegram.
Все фоновые задачи синхронизации вынесены в para-worker,
а решение домашних заданий — в para-solver.
"""

import asyncio

from core.api_client import close_api_client
from core.bot import bot, dp
from core.logger import get_logger
from core.redis import close_redis, init_redis

log = get_logger("bot_main")


def _register_admin_routers() -> None:
    """Регистрирует административные роутеры в диспетчере."""
    from bot.handlers.admin.attendance import router as attendance_router
    from bot.handlers.admin.mute import router as mute_router
    from bot.handlers.admin.panel import router as admin_router
    from bot.handlers.admin.ping_all import router as ping_all_router
    from bot.handlers.admin.testers import router as testers_router
    dp.include_router(attendance_router)
    dp.include_router(mute_router)
    dp.include_router(ping_all_router)
    dp.include_router(testers_router)
    dp.include_router(admin_router)


def _register_user_routers() -> None:
    """Регистрирует пользовательские роутеры в диспетчере."""
    from bot.handlers.user.attendance import router as user_att_router
    from bot.handlers.user.auth_fallback import router as fallback_router
    from bot.handlers.user.hw_solver import router as hw_solver_router
    from bot.handlers.user.public_copy import public_router
    from bot.handlers.user.schedule import router as user_router
    from bot.handlers.user.voice_transcribe import router as voice_router
    dp.include_router(voice_router)
    dp.include_router(hw_solver_router)
    dp.include_router(public_router)
    dp.include_router(user_att_router)
    dp.include_router(user_router)
    dp.include_router(fallback_router)


def register_all_routers() -> None:
    """Регистрирует все группы роутеров в диспетчере aiogram."""
    from bot.handlers.errors import router as error_router
    _register_admin_routers()
    _register_user_routers()
    dp.include_router(error_router)



async def shutdown_bot() -> None:
    """Корректно закрывает сессию бота, HTTP-клиент API и подключение к Redis."""
    log.info("Остановка бота: закрытие сессий...")
    await close_api_client()
    if dp.storage:
        await dp.storage.close()
    await close_redis()
    await bot.session.close()
    log.info("Сессии Telegram, API, Storage и Redis закрыты. Бот остановлен.")



def setup_all_middlewares() -> None:
    """Регистрирует глобальные middleware для отказоустойчивости бота."""
    from bot.middlewares.retry import RetryAfterMiddleware
    from bot.middlewares.throttling import CallbackThrottleMiddleware
    dp.message.middleware(RetryAfterMiddleware())
    dp.callback_query.middleware(RetryAfterMiddleware())
    dp.callback_query.middleware(CallbackThrottleMiddleware())


async def _warmup_stt() -> None:
    """Асинхронно прогревает STT-модель в фоне при старте бота."""
    from services.transcriber import transcriber_service
    try:
        await transcriber_service.warmup()
        log.info("✅ STT модель (faster-whisper) прогрета и готова к работе")
    except Exception as e:
        log.warning(f"⚠️ Ошибка фонового прогрева STT модели: {e}")


async def main() -> None:
    """Основная асинхронная функция инициализации и запуска бота."""
    from bot.commands import register_bot_commands
    log.info("=" * 60)
    log.info("ЗАПУСК Персонального Telegram Бота КТМУ (para-bot)")
    log.info("=" * 60)
    register_all_routers()
    setup_all_middlewares()
    await init_redis()
    await register_bot_commands(bot)
    asyncio.create_task(_warmup_stt())
    try:
        await dp.start_polling(bot, drop_pending_updates=True)
    except Exception as e:
        log.error(f"❌ Критическая ошибка при работе бота: {e}")
    finally:
        await shutdown_bot()


if __name__ == "__main__":
    asyncio.run(main())
