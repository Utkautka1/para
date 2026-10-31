"""
Ручное управление геймификацией из админ-панели старосты.

Староста может:
  1. Прибавлять и отнимать бонусные XP и очки гильдии (счётчики xp_bonus / guild_bonus)
  2. Выдавать и снимать любые ачивки, включая секретные

Студент получает уведомление о каждом изменении. Студенты адресуются индексом
в алфавитном списке журнала: ФИО не влезает в 64 байта callback_data, а алфавитный
порядок, в отличие от рейтинга, не меняется от каждого нажатия «+10».

Ачивки и бонусы пишутся под ФИО из реестра одногруппников (если студент там есть) —
под ним же их сохраняют хэндлеры бота и worker.
"""

from dataclasses import dataclass
from typing import Any

from core.logger import get_logger
from db.sqlite.repositories import CounterRepository, GamificationRepository
from services.achievement_service import (
    format_achievement_notification,
    invalidate_leaderboard_cache,
    send_achievement_message,
    unlock_for_fio,
)
from services.classmates_auth import find_classmate_by_fio
from services.gamification import GUILD_BONUS_KEY, XP_BONUS_KEY, bonus_for, get_group_leaderboard
from services.gamification_models import StudentProfile
from services.gamification_registry import ACHIEVEMENTS_MAP

log = get_logger("gamification_admin")

# Какой бонус меняет кнопка: ключ счётчика и подпись для уведомления студенту
BONUS_KINDS: dict[str, tuple[str, str]] = {
    "xp": (XP_BONUS_KEY, "XP"),
    "guild": (GUILD_BONUS_KEY, "очков гильдии"),
}


@dataclass(frozen=True)
class StudentTarget:
    """Студент, которым управляет староста."""

    profile: StudentProfile
    # owner — ФИО, под которым сохраняются ачивки и бонусы
    owner: str
    tg_id: int | None


async def list_students() -> list[StudentProfile]:
    """Возвращает профили всех студентов журнала в алфавитном порядке."""
    board = await get_group_leaderboard(force_refresh=True)
    return sorted(board, key=lambda p: p.fio)


def _target_of(profile: StudentProfile) -> StudentTarget:
    """Определяет ФИО-владельца и Telegram ID студента по реестру одногруппников."""
    classmate = find_classmate_by_fio(profile.fio) or {}
    owner = str(classmate.get("full_name") or profile.fio)
    tg_id = classmate.get("tg_id")
    return StudentTarget(profile, owner, int(tg_id) if tg_id else None)


async def get_student(index: int) -> StudentTarget | None:
    """
    Находит студента по индексу в алфавитном списке.

    Возвращает StudentTarget или None, если индекс вне списка.
    """
    students = await list_students()
    return _target_of(students[index]) if 0 <= index < len(students) else None


async def get_bonuses(target: StudentTarget) -> tuple[int, int]:
    """Возвращает (бонус XP, бонус очков гильдии) студента."""
    xp = bonus_for(target.profile.fio, await CounterRepository.get_key_values(XP_BONUS_KEY))
    guild = bonus_for(target.profile.fio, await CounterRepository.get_key_values(GUILD_BONUS_KEY))
    return xp, guild


async def _notify(bot: Any, target: StudentTarget, text: str) -> None:
    """Сообщает студенту об изменении, если у него привязан Telegram."""
    if bot and target.tg_id:
        await send_achievement_message(bot, target.tg_id, text)


def format_bonus_notification(label: str, delta: int) -> str:
    """Текст уведомления студенту о ручном начислении или списании."""
    verb = "начислил" if delta > 0 else "списал"
    return f"👑 <b>Староста {verb} {abs(delta)} {label}</b>\n\n⚔️ Проверь свой прогресс в <b>Mini App</b>!"


async def adjust_bonus(bot: Any, target: StudentTarget, kind: str, delta: int) -> int:
    """
    Прибавляет к бонусу студента delta (отрицательная — списание) и уведомляет его.

    Возвращает новое значение бонуса.
    """
    key, label = BONUS_KINDS[kind]
    value = await CounterRepository.add_value(target.owner, key, delta)
    await invalidate_leaderboard_cache()
    log.info("Бонус %s студента %s: %+d (итого %s)", key, target.owner, delta, value)
    await _notify(bot, target, format_bonus_notification(label, delta))
    return value


async def set_bonus(bot: Any, target: StudentTarget, kind: str, value: int) -> int:
    """
    Выставляет бонус студента ровно в value и уведомляет его.

    Возвращает установленное значение.
    """
    key, label = BONUS_KINDS[kind]
    await CounterRepository.set_value(target.owner, key, value)
    await invalidate_leaderboard_cache()
    log.info("Бонус %s студента %s выставлен: %s", key, target.owner, value)
    await _notify(bot, target, f"👑 <b>Староста выставил бонус {label}: {value:+d}</b>")
    return value


async def reset_bonuses(bot: Any, target: StudentTarget) -> None:
    """Обнуляет оба бонуса студента и уведомляет его."""
    for key, _ in BONUS_KINDS.values():
        await CounterRepository.set_value(target.owner, key, 0)
    await invalidate_leaderboard_cache()
    log.info("Бонусы студента %s обнулены", target.owner)
    await _notify(bot, target, "👑 <b>Староста обнулил твои бонусные XP и очки гильдии</b>")


async def toggle_achievement(bot: Any, target: StudentTarget, achievement_id: str) -> bool:
    """
    Выдаёт ачивку, если её нет, или снимает, если есть, и уведомляет студента.

    Возвращает True, если ачивка теперь выдана.
    """
    ach = ACHIEVEMENTS_MAP[achievement_id]
    if achievement_id in target.profile.unlocked_achievements:
        await GamificationRepository.revoke_achievement({target.owner, target.profile.fio}, achievement_id)
        await invalidate_leaderboard_cache()
        log.info("Ачивка %s снята со студента %s", achievement_id, target.owner)
        await _notify(
            bot, target, f"👑 <b>Староста снял достижение</b>\n\n{ach.icon} {ach.title} (−{ach.xp_reward} XP)"
        )
        return False
    await unlock_for_fio(target.owner, achievement_id)
    await invalidate_leaderboard_cache()
    await _notify(bot, target, format_achievement_notification(ach))
    return True
