"""
Сервис разблокировки академических достижений и мгновенных уведомлений в Telegram.

Обеспечивает:
  1. Атомарную выдачу ачивок студентам с сохранением в SQLite
  2. Мгновенную инвалидацию кэша лидерборда в Redis
  3. Отправку поздравительных уведомлений в Telegram — по одной ачивке
     (события в боте) или сводкой (фоновая выдача журнальных ачивок в worker)

Ачивки привязаны к ФИО, а не к Telegram ID: журнальные ачивки выдаются
и тем, кто ещё ни разу не открывал бота.
"""

from typing import Any

from core.logger import get_logger
from core.redis_cache import cache_delete
from db.sqlite.repositories import GamificationRepository
from services.classmates_auth import find_classmate_by_tg_id
from services.gamification import LEADERBOARD_CACHE_KEY
from services.gamification_models import AchievementDefinition
from services.gamification_registry import ACHIEVEMENTS_MAP, SECRET_IDS

log = get_logger("achievement_service")


def resolve_student_fio(user_id: int, fallback_name: str | None = None) -> str:
    """Определяет ФИО студента по Telegram ID из реестра или возвращает имя профиля."""
    classmate = find_classmate_by_tg_id(user_id)
    if classmate and classmate.get("full_name"):
        return str(classmate["full_name"])
    return fallback_name or f"Студент {user_id}"


def format_achievement_notification(ach: AchievementDefinition) -> str:
    """Форматирует поздравительное сообщение о новом достижении."""
    header = "🤫 <b>СЕКРЕТНОЕ ДОСТИЖЕНИЕ!</b>" if ach.id in SECRET_IDS else "🏆 <b>НОВОЕ ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!</b>"
    return (
        f"{header}\n\n"
        f"{ach.icon} <b>{ach.title}</b> (+{ach.xp_reward} XP)\n"
        f"<i>{ach.description}</i>\n"
        f"Редкость: <b>{ach.rarity.value}</b>\n\n"
        f"⚔️ Проверь свой прогресс в <b>Mini App</b>!"
    )


def format_achievements_digest(achs: list[AchievementDefinition]) -> str:
    """
    Форматирует одно сообщение сразу о нескольких новых ачивках.

    Worker открывает журнальные ачивки пачками — при первом запуске у студента
    их может быть 5–10, и отдельное сообщение на каждую было бы спамом.
    """
    if len(achs) == 1:
        return format_achievement_notification(achs[0])
    lines = [f"{a.icon} <b>{a.title}</b> (+{a.xp_reward} XP)\n<i>{a.description}</i>" for a in achs]
    total_xp = sum(a.xp_reward for a in achs)
    return (
        f"🏆 <b>НОВЫЕ ДОСТИЖЕНИЯ: {len(achs)}</b> (+{total_xp} XP)\n\n"
        + "\n\n".join(lines)
        + "\n\n⚔️ Проверь свой прогресс в <b>Mini App</b>!"
    )


async def send_achievement_message(bot: Any, user_id: int, text: str) -> None:
    """Безопасно отправляет студенту уведомление — ошибка доставки не ломает выдачу."""
    try:
        await bot.send_message(user_id, text, parse_mode="HTML")
    except Exception as exc:
        log.warning("Не удалось отправить уведомление студенту %s: %s", user_id, exc)


async def invalidate_leaderboard_cache() -> None:
    """Инвалидирует кэш лидерборда в Redis для мгновенного обновления MiniApp."""
    try:
        await cache_delete(LEADERBOARD_CACHE_KEY)
    except Exception as exc:
        log.debug("Ошибка инвалидации кэша лидерборда: %s", exc)


async def unlock_for_fio(fio: str, achievement_id: str) -> AchievementDefinition | None:
    """
    Сохраняет ачивку за студентом без уведомления.

    Возвращает паспорт ачивки, если она открыта впервые, иначе None.
    """
    ach = ACHIEVEMENTS_MAP.get(achievement_id)
    if not ach or not await GamificationRepository.unlock_achievement(fio, achievement_id):
        return None
    log.info("🏆 Студент %s разблокировал: %s (+%s XP)", fio, ach.title, ach.xp_reward)
    return ach


async def award_achievement(
    user_id: int,
    achievement_id: str,
    bot: Any | None = None,
    user_full_name: str | None = None,
) -> bool:
    """
    Разблокирует ачивку за действие в боте, сбрасывает кэш и шлёт уведомление.

    Возвращает True, если ачивка открыта впервые.
    """
    fio = resolve_student_fio(user_id, user_full_name)
    ach = await unlock_for_fio(fio, achievement_id)
    if not ach:
        return False
    await invalidate_leaderboard_cache()
    if bot:
        await send_achievement_message(bot, user_id, format_achievement_notification(ach))
    return True
