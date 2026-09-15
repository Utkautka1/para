"""
Главный модуль запуска Telegram-бота расписания КТМУ.

Инициализирует роутеры хэндлеров, планировщик задач рассылки
и запускает процесс получения обновлений (polling) от Telegram.
"""

import asyncio
from datetime import datetime
from config import TIMEZONE
from core.bot import bot, dp
from core.logger import get_logger
from bot.handlers.user.schedule import router as user_router
from bot.handlers.user.auth_fallback import router as fallback_router
from services.notifier import schedule_lesson_reminder, setup_scheduler
from services.schedule_parser import get_schedule_for_date

log = get_logger("bot_main")


async def schedule_today_reminders_on_startup() -> None:
    """
    Планирует напоминания на остаток сегодняшнего дня при старте бота.
    """
    now_dt = datetime.now(TIMEZONE)
    today = now_dt.date()
    log.info(f"Проверка сегодняшних пар на момент запуска: {now_dt.strftime('%H:%M:%S')}")
    lessons = await get_schedule_for_date(today)
    for lesson in lessons:
        schedule_lesson_reminder(today, lesson, now_dt)


async def main() -> None:
    """
    Основная асинхронная функция инициализации и запуска бота.
    """
    log.info("=" * 60)
    log.info("ЗАПУСК Персонального Telegram Бота КТМУ (Группа 1-КПД-3)")
    log.info("=" * 60)

    from bot.handlers.user.public_copy import public_router
    from bot.handlers.admin.panel import router as admin_router
    from bot.handlers.admin.mute import router as mute_router
    # Порядок подключения: модерация/админка, публичные команды, авторизованные, затем fallback
    dp.include_router(mute_router)
    dp.include_router(public_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(fallback_router)

    from services.topic_updater import topic_sync_loop
    from services.exam_topic_updater import exam_topic_sync_loop
    from core.redis import init_redis
    await init_redis()
    setup_scheduler()
    await schedule_today_reminders_on_startup()
    asyncio.create_task(topic_sync_loop())
    asyncio.create_task(exam_topic_sync_loop())


    try:
        await dp.start_polling(bot)
    except Exception as e:
        log.error(f"❌ Критическая ошибка при работе бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
