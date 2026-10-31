"""
Фоновая выдача ачивок по журналу посещаемости и рейтингу (крутится в worker).

Цикл раз в ACHIEVEMENT_SYNC_INTERVAL секунд:
  1. Берёт сквозную статистику журнала (из кэша Redis/SQLite — Яндекс не дёргаем)
  2. Строит рейтинг с уже открытыми ачивками, чтобы знать место и пульс группы
  3. Для каждого студента считает журнальные и мета-правила
  4. Сохраняет новые ачивки и шлёт одно сводное уведомление в ЛС

Ачивки «остаются навсегда»: если условие потом нарушено (например, появилась «Н»),
ранее выданная ачивка не отзывается — проверяем только то, чего ещё нет.

Журнал считается от точки отсчёта (achievement_baselines, ставится командой
services.achievement_reset): пульс группы для ачивок — по отметкам после сброса,
места в «Топ-3» — по лидерборду, который тоже считает только новые отметки.

Выдаёт именно worker, а не API: API строит лидерборд на каждый запрос Mini App,
и если бы он сохранял ачивки сам, уведомления в бот терялись бы.
"""

import asyncio
from datetime import datetime
from typing import Any

from config import TIMEZONE
from core.logger import get_logger
from db.sqlite.repositories import AchievementResetRepository
from services.achievement_rules import (
    MetaContext,
    StudentStat,
    build_student_stat,
    evaluate_meta_rules,
    evaluate_stat_rules,
)
from services.achievement_service import (
    format_achievements_digest,
    invalidate_leaderboard_cache,
    send_achievement_message,
    unlock_for_fio,
)
from services.attendance_stats import fetch_all_time_attendance
from services.classmates_auth import find_classmate_by_fio
from services.gamification import get_group_leaderboard, is_starosta
from services.gamification_models import AchievementDefinition, StudentProfile

log = get_logger("achievement_sync")

# Интервал пересчёта (секунды): журнал обновляется не чаще раза в несколько минут
ACHIEVEMENT_SYNC_INTERVAL = 600

# Пауза перед первым проходом (секунды) — даём worker поднять Redis и кэш журнала
ACHIEVEMENT_SYNC_START_DELAY = 90


def _is_birthday_today(classmate: dict[str, Any] | None) -> bool:
    """Проверяет по календарю группы, что у студента сегодня (МСК) день рождения."""
    today = datetime.now(TIMEZONE).date()
    return bool(classmate) and (classmate.get("day"), classmate.get("month")) == (today.day, today.month)


def _delta_stats(stats: dict[str, dict[str, Any]], baselines: dict[str, dict[str, Any]]) -> dict[str, StudentStat]:
    """Строит срезы журнала после точки отсчёта для всех студентов."""
    result: dict[str, StudentStat] = {}
    for fio, raw in stats.items():
        result[fio] = build_student_stat(raw, _is_birthday_today(find_classmate_by_fio(fio)), baselines.get(fio))
    return result


def _group_context(board: list[StudentProfile], deltas: dict[str, StudentStat]) -> tuple[dict[str, int], float]:
    """
    Считает места в рейтинге (без старосты) и пульс группы после точки отсчёта.

    Места берём из лидерборда (очки гильдии), чтобы «Топ-3» совпадал с тем,
    что студенты видят в Mini App. Пульс — средний процент по отметкам после сброса.

    Возвращает ({ФИО: место}, пульс группы в процентах).
    """
    competing = [p.fio for p in board if not is_starosta(p.fio)]
    marked = [s.overall.pct for s in deltas.values() if s.overall.total > 0]
    pulse = sum(marked) / len(marked) if marked else 0.0
    return {fio: idx for idx, fio in enumerate(competing, start=1)}, pulse


def compute_new_achievements(
    profile: StudentProfile, stat: StudentStat, places: dict[str, int], pulse: float
) -> set[str]:
    """
    Определяет ачивки, которые студент заработал, но ещё не получил.

    Возвращает множество новых id.
    """
    owned = set(profile.unlocked_achievements)
    earned = owned | evaluate_stat_rules(stat)
    ctx = MetaContext(places.get(profile.fio), stat.overall.pct, stat.overall.total, pulse)
    earned |= evaluate_meta_rules(earned, ctx)
    return earned - owned


async def _grant_to_student(bot: Any, fio: str, new_ids: set[str]) -> int:
    """
    Сохраняет новые ачивки студента и отправляет сводку в ЛС, если известен tg_id.

    Ачивки пишем под ФИО из реестра одногруппников (если найдено) — под ним же
    их сохраняют хэндлеры бота, и профиль не расслаивается на два ФИО.

    Возвращает количество реально открытых ачивок.
    """
    classmate = find_classmate_by_fio(fio)
    owner = str(classmate["full_name"]) if classmate and classmate.get("full_name") else fio
    granted: list[AchievementDefinition] = []
    for aid in sorted(new_ids):
        ach = await unlock_for_fio(owner, aid)
        if ach:
            granted.append(ach)
    tg_id = classmate.get("tg_id") if classmate else None
    if granted and tg_id and bot:
        await send_achievement_message(bot, int(tg_id), format_achievements_digest(granted))
    return len(granted)


async def sync_stat_achievements(bot: Any) -> int:
    """
    Один проход выдачи журнальных и мета-ачивок всей группе.

    Возвращает общее количество выданных ачивок.
    """
    stats = await fetch_all_time_attendance()
    if not stats:
        log.debug("Журнал посещаемости пуст — пропускаем выдачу ачивок")
        return 0
    board = await get_group_leaderboard(provided_stats=stats)
    deltas = _delta_stats(stats, await AchievementResetRepository.get_baselines())
    places, pulse = _group_context(board, deltas)
    granted = 0
    for profile in board:
        new_ids = compute_new_achievements(profile, deltas[profile.fio], places, pulse)
        if new_ids:
            granted += await _grant_to_student(bot, profile.fio, new_ids)
    if granted:
        await invalidate_leaderboard_cache()
        log.info("✅ Выдано журнальных ачивок: %s", granted)
    return granted


async def achievement_sync_loop(bot: Any) -> None:
    """
    Бесконечный цикл фоновой выдачи ачивок в worker.

    Никогда не завершается штатно: ошибка одного прохода логируется,
    следующий проход будет через ACHIEVEMENT_SYNC_INTERVAL.
    """
    log.info("Запущен цикл выдачи журнальных ачивок (интервал %s сек)", ACHIEVEMENT_SYNC_INTERVAL)
    await asyncio.sleep(ACHIEVEMENT_SYNC_START_DELAY)
    while True:
        try:
            await sync_stat_achievements(bot)
        except Exception as exc:
            log.error("❌ Ошибка в цикле выдачи ачивок: %s", exc)
        await asyncio.sleep(ACHIEVEMENT_SYNC_INTERVAL)
