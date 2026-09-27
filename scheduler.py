"""
Фоновый сервис планировщика и рассылок оповещений.

Отвечает за:
  1. APScheduler: ежедневная утренняя рассылка в 06:00 МСК
  2. Напоминания за 10 минут до начала каждой пары
  3. Синхронизацию расписания экзаменов и сессии (раз в 10 минут)
  4. Мониторинг и публикацию поздравлений с ДР (в 07:00 МСК)
"""

import asyncio
from datetime import datetime
from config import TIMEZONE
from core.bot import bot
from core.logger import get_logger
from core.mongo import close_mongo, init_mongo
from core.redis import init_redis, redis_client
from services.birthday_manager import birthday_sync_loop
from services.exam_topic_updater import exam_topic_sync_loop
from services.notifier import schedule_lesson_reminder, setup_scheduler, scheduler
from services.schedule_parser import get_schedule_for_date

log = get_logger("scheduler_main")


async def schedule_today_reminders() -> None:
    """Планирует напоминания на остаток сегодняшнего дня при старте сервиса."""
    now_dt = datetime.now(TIMEZONE)
    today = now_dt.date()
    log.info(f"Проверка сегодняшних пар на момент запуска: {now_dt.strftime('%H:%M:%S')}")
    lessons = await get_schedule_for_date(today)
    for lesson in lessons:
        schedule_lesson_reminder(today, lesson, now_dt)


async def shutdown_scheduler() -> None:
    """Освобождает сетевые ресурсы и останавливает таймеры шедулера."""
    log.info("Остановка para-scheduler: закрытие сессий...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    if redis_client:
        await redis_client.aclose()
    await close_mongo()
    await bot.session.close()
    log.info("Сервис para-scheduler успешно остановлен.")


async def main() -> None:
    """Точка входа фонового сервиса-шедулера."""
    log.info("=" * 60)
    log.info("ЗАПУСК Планировщика и Оповещений (para-scheduler)")
    log.info("=" * 60)
    await init_redis()
    await init_mongo()
    setup_scheduler()
    await schedule_today_reminders()
    try:
        await asyncio.gather(
            exam_topic_sync_loop(),
            birthday_sync_loop()
        )
    except asyncio.CancelledError:
        log.info("Получен сигнал завершения работы para-scheduler.")
    except Exception as e:
        log.error(f"❌ Критическая ошибка в работе para-scheduler: {e}")
    finally:
        await shutdown_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
