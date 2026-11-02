"""
Главный модуль запуска Telegram-бота расписания КТМУ.

Инициализирует роутеры хэндлеров, подключение к Redis и запускает
процесс получения обновлений (polling) от Telegram.
Все фоновые задачи синхронизации вынесены в para-worker,
а решение домашних заданий — в para-solver.
"""

import asyncio

from core.api_client import close_api_client
from core.background import drain_background
from core.bot import bot, dp
from core.logger import get_logger
from core.redis import close_redis, init_redis

log = get_logger("bot_main")


def _register_admin_routers() -> None:
    """
    Регистрирует административные роутеры в диспетчере aiogram.

    Подключает хэндлеры посещаемости, мутов, пингов, тестеров, ачивок и админ-панели.
    Соблюдает строгую последовательность приоритета перехвата событий.

    Ничего не возвращает.
    """

    from bot.handlers.admin.attendance import router as attendance_router
    from bot.handlers.admin.gamification import router as gamification_admin_router
    from bot.handlers.admin.mute import router as mute_router
    from bot.handlers.admin.panel import router as admin_router
    from bot.handlers.admin.ping_all import router as ping_all_router
    from bot.handlers.admin.testers import router as testers_router

    dp.include_router(attendance_router)
    dp.include_router(mute_router)
    dp.include_router(ping_all_router)
    dp.include_router(testers_router)
    dp.include_router(gamification_admin_router)
    dp.include_router(admin_router)


def _register_user_routers() -> None:
    """
    Регистрирует пользовательские роутеры в диспетчере aiogram.

    Подключает распознавание речи, решение ДЗ, публичное копирование и расписание.
    В конце подключает fallback для информирования неавторизованных пользователей.

    Ничего не возвращает.
    """

    from bot.handlers.user.attendance import router as user_att_router
    from bot.handlers.user.auth_fallback import router as fallback_router
    from bot.handlers.user.hw_solver import router as hw_solver_router
    from bot.handlers.user.profile import router as profile_router
    from bot.handlers.user.public_copy import public_router
    from bot.handlers.user.schedule import router as user_router
    from bot.handlers.user.voice_transcribe import router as voice_router

    dp.include_router(voice_router)
    dp.include_router(hw_solver_router)
    dp.include_router(public_router)
    dp.include_router(profile_router)
    dp.include_router(user_att_router)
    dp.include_router(user_router)
    dp.include_router(fallback_router)


def register_all_routers() -> None:
    """
    Регистрирует все группы роутеров и обработчик ошибок в диспетчере.

    Обеспечивает агрегацию административных и пользовательских маршрутов.
    Замыкает цепочку глобальным фильтром необработанных исключений.

    Ничего не возвращает.
    """

    from bot.handlers.errors import router as error_router

    _register_admin_routers()
    _register_user_routers()
    dp.include_router(error_router)


async def shutdown_bot() -> None:
    """
    Корректно закрывает сессию бота, HTTP-клиент API и подключение к Redis.

    Освобождает дескрипторы соединений и хранилище FSM при завершении процесса.
    Предотвращает появление предупреждений о незакрытых сокетах в логах.

    Ничего не возвращает.
    """

    log.info("Остановка бота: закрытие сессий...")
    # Даём доработать фоновым ачивкам и уведомлениям, пока соединения ещё открыты
    await drain_background()
    await close_api_client()
    if dp.storage:
        await dp.storage.close()

    await close_redis()
    await bot.session.close()
    log.info("Сессии Telegram, API, Storage и Redis закрыты. Бот остановлен.")


def setup_all_middlewares() -> None:
    """
    Регистрирует глобальные middleware для отказоустойчивости бота.

    Подключает трейсинг (TracingMiddleware), автоповтор запросов
    (RetryAfterMiddleware), защиту от спама (CallbackThrottleMiddleware)
    и учёт активности для ачивок (AchievementActivityMiddleware, outer —
    чтобы видеть и сообщения чата, которые не обрабатывает ни один хэндлер).

    Ничего не возвращает.
    """

    from bot.middlewares.achievements import AchievementActivityMiddleware
    from bot.middlewares.retry import RetryAfterMiddleware
    from bot.middlewares.throttling import CallbackThrottleMiddleware
    from bot.middlewares.tracing import TracingMiddleware

    dp.message.middleware(TracingMiddleware())
    dp.callback_query.middleware(TracingMiddleware())
    dp.message.middleware(RetryAfterMiddleware())
    dp.callback_query.middleware(RetryAfterMiddleware())
    dp.callback_query.middleware(CallbackThrottleMiddleware())
    dp.message.outer_middleware(AchievementActivityMiddleware())
    dp.callback_query.outer_middleware(AchievementActivityMiddleware())


async def _init_bot_subsystems() -> None:
    """
    Инициализирует роутеры, middleware и соединения (модель STT живёт в сервисе stt).

    Выделяет фазу предварительной конфигурации перед стартом polling.
    Упрощает сопровождение процедуры запуска бота.

    Ничего не возвращает.
    """

    from bot.commands import register_bot_commands
    from core.database import init_db
    from core.telemetry import setup_telemetry

    setup_telemetry("para-bot")
    register_all_routers()
    setup_all_middlewares()
    await init_redis()
    await init_db()
    await register_bot_commands(bot)


async def main() -> None:
    """
    Основная асинхронная функция запуска long polling Telegram-бота.

    Выполняет инициализацию сервисов и переходит к получению обновлений.
    В блоке finally гарантированно закрывает все открытые сетевые сессии.

    Ничего не возвращает.
    """

    log.info("=" * 60)
    log.info("ЗАПУСК Персонального Telegram Бота КТМУ (para-bot)")
    log.info("=" * 60)
    await _init_bot_subsystems()

    try:
        await dp.start_polling(bot, drop_pending_updates=True, polling_timeout=20)
    except Exception as e:
        log.error("❌ Критическая ошибка при работе бота: %s", e)
    finally:
        await shutdown_bot()


if __name__ == "__main__":
    asyncio.run(main())
