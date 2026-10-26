"""
Сервис разблокировки академических достижений и мгновенных уведомлений в Telegram.

Обеспечивает:
  1. Атомарную выдачу ачивок студентам с сохранением в SQLite
  2. Мгновенную инвалидацию кэша лидерборда в Redis
  3. Отправку интерактивных поздравительных уведомлений в Telegram
"""

from typing import Any

from core.logger import get_logger
from core.redis_cache import cache_delete
from db.sqlite.repositories import GamificationRepository
from services.classmates_auth import find_classmate_by_tg_id
from services.gamification_models import AchievementDefinition
from services.gamification_registry import ACHIEVEMENTS_MAP

log = get_logger("achievement_service")
LEADERBOARD_CACHE_KEY = "gamification:leaderboard:v1"


def resolve_student_fio(user_id: int, fallback_name: str | None = None) -> str:
    """Определяет ФИО студента по Telegram ID из реестра или возвращает имя профиля."""
    classmate = find_classmate_by_tg_id(user_id)
    if classmate and classmate.get("full_name"):
        return str(classmate["full_name"])
    return fallback_name or f"Студент {user_id}"


def format_achievement_notification(ach: AchievementDefinition) -> str:
    """Форматирует красивое поздравительное сообщение о новом достижении."""
    return (
        f"🏆 <b>НОВОЕ ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!</b>\n\n"
        f"{ach.icon} <b>{ach.title}</b> (+{ach.xp_reward} XP)\n"
        f"<i>{ach.description}</i>\n"
        f"Редкость: <b>{ach.rarity.value}</b>\n\n"
        f"⚔️ Проверь свой прогресс в <b>Mini App</b>!"
    )


async def _notify_student(bot: Any, user_id: int, ach: AchievementDefinition) -> None:
    """Безопасно отправляет студенту уведомление о получении достижения."""
    try:
        msg = format_achievement_notification(ach)
        await bot.send_message(user_id, msg, parse_mode="HTML")
    except Exception as exc:
        log.warning(f"Не удалось отправить уведомление студенту {user_id}: {exc}")


async def invalidate_leaderboard_cache() -> None:
    """Инвалидирует кэш лидерборда в Redis для мгновенного обновления MiniApp."""
    try:
        await cache_delete(LEADERBOARD_CACHE_KEY)
    except Exception as exc:
        log.debug(f"Ошибка инвалидации кэша лидерборда: {exc}")


async def award_achievement(
    user_id: int,
    achievement_id: str,
    bot: Any | None = None,
    user_full_name: str | None = None,
) -> bool:
    """Атомарно разблокирует достижение, сбрасывает кэш и шлет уведомление."""
    ach = ACHIEVEMENTS_MAP.get(achievement_id)
    if not ach:
        return False
    fio = resolve_student_fio(user_id, user_full_name)
    unlocked = await GamificationRepository.unlock_achievement(fio, achievement_id)
    if not unlocked:
        return False
    await invalidate_leaderboard_cache()
    log.info(f"🏆 Студент {fio} (tg={user_id}) разблокировал: {ach.title} (+{ach.xp_reward} XP)")
    if bot:
        await _notify_student(bot, user_id, ach)
    return True
