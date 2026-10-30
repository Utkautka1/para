"""
Фоновый загрузчик расписания КТМУ — единственный процесс, который качает API.

API КТМУ отдаёт ~57 МБ без gzip и ETag (около 10 сек на загрузку), поэтому
пользователи не должны ждать скачивания. Цикл в worker:
  1. Раз в SCHEDULE_REFRESH_INTERVAL_SECONDS качает расписание и кладёт снапшот в Redis
  2. Каждые SCHEDULE_REFRESH_POLL_SECONDS проверяет флаг «обновить сейчас»
     (его ставят кнопка «Обновить» и админка через force_refresh у читателей)
API и бот читают снапшот из Redis и подхватывают новую версию сами.
"""

import asyncio
import time

from config import SCHEDULE_REFRESH_INTERVAL_SECONDS, SCHEDULE_REFRESH_POLL_SECONDS
from core.logger import get_logger
from core.redis_cache import pop_schedule_refresh_request
from services.schedule_parser import enable_schedule_fetch_ownership, refresh_schedule_in_background

log = get_logger("schedule_refresher")


async def _refresh_if_due(next_due: float) -> float:
    """
    Запускает загрузку, если подошёл срок по таймеру или её запросили вручную.

    Ручной запрос идёт с force=True — обходит кулдаун после сбоя API.

    Возвращает момент следующей плановой загрузки (time.monotonic).
    """
    forced = await pop_schedule_refresh_request()
    now = time.monotonic()
    if not forced and now < next_due:
        return next_due

    log.debug("Загрузка расписания КТМУ: %s", "по запросу" if forced else "по таймеру")
    await refresh_schedule_in_background(force=forced)
    return now + SCHEDULE_REFRESH_INTERVAL_SECONDS


async def schedule_refresh_loop() -> None:
    """
    Бесконечный цикл фонового обновления снапшота расписания в Redis.

    Первая загрузка — сразу при старте, чтобы читатели получили свежий снапшот.

    Никогда не завершается штатно при нормальной работе сервиса.
    """
    enable_schedule_fetch_ownership()
    log.info("=" * 60)
    log.info("ЗАПУСК фонового загрузчика расписания КТМУ")
    log.info("  Интервал загрузки: %s сек", SCHEDULE_REFRESH_INTERVAL_SECONDS)
    log.info("  Проверка запросов «Обновить»: каждые %s сек", SCHEDULE_REFRESH_POLL_SECONDS)
    log.info("=" * 60)

    next_due = 0.0
    while True:
        try:
            next_due = await _refresh_if_due(next_due)
        except Exception as e:
            log.error("❌ Ошибка в цикле schedule_refresh_loop: %s", e)
        await asyncio.sleep(SCHEDULE_REFRESH_POLL_SECONDS)
