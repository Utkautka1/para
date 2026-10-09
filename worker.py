"""
Фоновый сервис синхронизации расписания, экзаменов и оповещений.

Запускает:
  1. Синхронизацию главного расписания КТМУ (topic_sync_loop, раз в 60 сек)
  2. Синхронизацию расписания экзаменов (exam_topic_sync_loop, раз в 10 мин)
  3. Мониторинг и публикацию поздравлений с ДР (birthday_sync_loop, в 07:00)
  4. APScheduler для утренних дайджестов (06:00) и напоминаний за 10 мин до пар
  5. Фоновый Keep-Alive сессии Яндекс Документов (раз в 6 часов)
"""

import asyncio
from datetime import datetime

from config import TIMEZONE
from core.api_client import close_api_client, get_api_schedule_for_date
from core.bot import bot
from core.logger import get_logger
from core.redis import close_redis, init_redis
from integrations.yandex_keepalive import yandex_session_keepalive_loop
from services.attendance_topic_updater import attendance_topic_sync_loop
from services.birthday_manager import birthday_sync_loop
from services.exam_topic_updater import exam_topic_sync_loop
from services.notifier import (
    schedule_attendance_poll,
    schedule_lesson_reminder,
    scheduler,
    setup_scheduler,
)
from services.topic_updater import topic_sync_loop

log = get_logger("worker_main")


async def schedule_today_reminders() -> None:
    """Планирует напоминания на остаток сегодняшнего дня при старте воркера."""
    now_dt = datetime.now(TIMEZONE)
    today = now_dt.date()
    log.info(f"Проверка сегодняшних пар на момент запуска воркера: {now_dt.strftime('%H:%M:%S')}")
    lessons = await get_api_schedule_for_date(today)
    for lesson in lessons:
        schedule_lesson_reminder(today, lesson, now_dt)
        schedule_attendance_poll(today, lesson, now_dt)


async def shutdown_worker() -> None:
    """Освобождает сетевые ресурсы и останавливает шедулер при выключении."""
    log.info("Остановка воркера: освобождение сетевых ресурсов...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    await close_redis()
    await close_api_client()
    await bot.session.close()
    log.info("Воркер para-worker успешно остановлен.")


async def _start_worker_loops() -> None:
    """Запускает все фоновые циклы синхронизации сервиса."""
    await asyncio.gather(
        topic_sync_loop(),
        exam_topic_sync_loop(),
        attendance_topic_sync_loop(),
        birthday_sync_loop(),
        yandex_session_keepalive_loop()
    )


async def main() -> None:
    """Точка входа фонового сервиса-синхронизатора."""
    log.info("=" * 60)
    log.info("ЗАПУСК Фонового Воркера Расписания (para-worker)")
    log.info("=" * 60)
    await init_redis()
    setup_scheduler()
    await schedule_today_reminders()
    try:
        await _start_worker_loops()
    except asyncio.CancelledError:
        log.info("Получен сигнал завершения работы воркера.")
    except Exception as e:
        log.error(f"❌ Критическая ошибка в работе воркера: {e}")
    finally:
        await shutdown_worker()


if __name__ == "__main__":
    asyncio.run(main())
