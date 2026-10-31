"""
Разовый сброс ачивок группы с новой точкой отсчёта журнала.

Запуск на сервере (внутри worker — там есть журнал, Redis и SQLite на запись):
    docker exec para-worker python -m services.achievement_reset --confirm

Что делает:
  1. Делает онлайн-бэкап SQLite в BACKUP_DIR_PATH (откат — вернуть файл)
  2. Скачивает свежий журнал посещаемости
  3. В одной транзакции удаляет все ачивки и счётчики и записывает снимок журнала
  4. Сбрасывает кэш рейтинга, чтобы Mini App сразу показал обнулённые ачивки

После сброса журнальные ачивки считаются только по отметкам, поставленным позже:
прошлые пропуски остаются в журнале и рейтинге, но шансы на ачивки у всех равные.
"""

import asyncio
import os
import sys
from datetime import datetime

from config import BACKUP_DIR_PATH, TIMEZONE
from core.logger import get_logger

log = get_logger("achievement_reset")


async def _backup_database() -> str | None:
    """
    Сохраняет копию SQLite перед удалением ачивок.

    Возвращает путь к копии или None, если бэкап не удался.
    """
    from services.backup_manager import backup_sqlite_online

    os.makedirs(BACKUP_DIR_PATH, exist_ok=True)
    stamp = datetime.now(TIMEZONE).strftime("%Y%m%d-%H%M%S")
    path = os.path.join(BACKUP_DIR_PATH, f"para-before-achievement-reset-{stamp}.db")
    return path if await asyncio.to_thread(backup_sqlite_online, path) else None


async def reset_achievements() -> bool:
    """
    Обнуляет ачивки и счётчики группы и ставит точку отсчёта по текущему журналу.

    Без бэкапа или без журнала ничего не удаляет.

    Возвращает True при успешном сбросе.
    """
    from core.database import init_db
    from db.sqlite.repositories import AchievementResetRepository
    from services.achievement_service import invalidate_leaderboard_cache
    from services.attendance_stats import fetch_all_time_attendance

    await init_db()
    backup = await _backup_database()
    if not backup:
        log.error("❌ Бэкап SQLite не создан — сброс ачивок отменён")
        return False
    stats = await fetch_all_time_attendance(force_refresh=True)
    if not stats:
        log.error("❌ Журнал посещаемости пуст — точку отсчёта ставить не от чего, сброс отменён")
        return False
    achievements, counters = await AchievementResetRepository.reset_with_baseline(stats)
    await invalidate_leaderboard_cache()
    log.info("✅ Ачивки сброшены: удалено %s ачивок и %s счётчиков", achievements, counters)
    log.info("  Точка отсчёта: %s студентов, бэкап: %s", len(stats), backup)
    return True


async def _run() -> bool:
    """Поднимает Redis, выполняет сброс и закрывает соединения короткого процесса."""
    from core.redis import close_redis, init_redis

    await init_redis()
    try:
        return await reset_achievements()
    finally:
        await close_redis()


def main(argv: list[str]) -> int:
    """
    Требует явный --confirm: команда необратимо удаляет ачивки всей группы.

    Возвращает код выхода: 0 — сброшено, 1 — ошибка, 2 — нет подтверждения.
    """
    if argv != ["--confirm"]:
        log.error("Использование: python -m services.achievement_reset --confirm")
        return 2
    return 0 if asyncio.run(_run()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
