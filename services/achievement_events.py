"""
Выдача событийных ачивок: связывает действия в боте, чате и Mini App со счётчиками.

Хэндлеры вызывают on_* в фоне (asyncio.create_task) — ачивка никогда
не должна задерживать ответ пользователю. Условия берутся из achievement_triggers,
накопительные счётчики живут в SQLite (CounterRepository), короткие окна
(«3 раза за минуту», «15 минут после /all») — в Redis с TTL.

Счётчики ведутся только для одногруппников: тестеры и случайные люди,
открывшие бота, не должны засорять таблицу.
"""

from datetime import date, datetime
from typing import Any

from aiogram.types import Message, User

from config import ALLOWED_USER_ID, TIMEZONE
from core.logger import get_logger
from core.redis_cache import cache_get, cache_set, incr_with_ttl
from db.sqlite.repositories import CounterRepository
from services.achievement_service import award_achievement, resolve_student_fio
from services.achievement_triggers import (
    BIRTHDAY_GREETING_RE,
    HomeworkTask,
    ScheduleView,
    homework_achievements,
    schedule_view_achievements,
)
from services.classmates_auth import find_classmate_by_tg_id, load_classmates_registry
from services.models import Lesson

log = get_logger("achievement_events")

# Пороги накопительных ачивок: {ключ счётчика: [(порог, id ачивки), ...]}
COUNTER_THRESHOLDS: dict[str, list[tuple[int, str]]] = {
    "actions": [(100, "egg_tapper"), (300, "egg_jubilee_300")],
    "active_days": [(7, "bot_subscriber")],
    "hw_tasks": [(3, "ai_gost_docx"), (10, "ai_deepseek_fan")],
    "hw_days": [(5, "ai_marathon")],
    "attendance_days": [(5, "egg_tracer")],
    "chat_messages": [(100, "soc_chatter")],
    "chat_stickers": [(10, "soc_meme_lord")],
    "chat_replies": [(20, "soc_colloquium")],
}

# Счётчики «раз в день» — растут не чаще одного раза за сутки
DAILY_COUNTERS = frozenset({"active_days", "hw_days", "attendance_days"})

# Окно «Нетерпеливого»: 3 нажатия «Обновить» за 60 секунд
IMPATIENT_CLICKS = 3
IMPATIENT_WINDOW_SECONDS = 60

# Ключ и окно «Общего сбора» после /all (секунды)
PING_ALL_KEY = "ach:ping_all"
PING_ALL_WINDOW_SECONDS = 900

# Сколько разных одногруппников нужно открыть в Mini App для «Солидарности»
SOLIDARITY_PROFILES = 5


def _now() -> datetime:
    """Текущее московское время — во всех описаниях ачивок время московское."""
    return datetime.now(TIMEZONE)


def is_group_member(user_id: int) -> bool:
    """Проверяет, что пользователь — одногруппник (или староста)."""
    return user_id == ALLOWED_USER_ID or find_classmate_by_tg_id(user_id) is not None


async def _award_all(uid: int, ids: set[str], bot: Any, name: str | None) -> None:
    """Выдаёт набор ачивок по одной (каждая сама проверяет, не открыта ли уже)."""
    for aid in sorted(ids):
        await award_achievement(uid, aid, bot, name)


async def bump_counter(uid: int, key: str, bot: Any, name: str | None) -> int:
    """
    Увеличивает счётчик студента и выдаёт ачивки за пройденные пороги.

    Проверяем «>=», а не «==»: если выдача когда-то сорвалась (бот лежал),
    ачивка догонит студента на следующем действии.

    Возвращает новое значение счётчика.
    """
    today: date | None = _now().date() if key in DAILY_COUNTERS else None
    value = await CounterRepository.increment(resolve_student_fio(uid, name), key, today)
    reached = {aid for threshold, aid in COUNTER_THRESHOLDS.get(key, []) if value >= threshold}
    await _award_all(uid, reached, bot, name)
    return value


async def on_interaction(user: User, bot: Any) -> None:
    """Любое действие одногруппника в ЛС бота: «Тапер», «Юбиляр», «На связи»."""
    if not is_group_member(user.id):
        return
    await bump_counter(user.id, "actions", bot, user.full_name)
    await bump_counter(user.id, "active_days", bot, user.full_name)


async def on_schedule_view(user: User | None, bot: Any, view: ScheduleView, lessons: list[Lesson]) -> None:
    """Просмотр расписания: время суток, кнопка и пары показанного дня."""
    if not user or not is_group_member(user.id):
        return
    await _award_all(user.id, schedule_view_achievements(view, _now(), lessons), bot, user.full_name)


async def on_refresh_click(user: User | None, bot: Any) -> None:
    """Кнопка «Обновить»: «F5 Мастер» и «Нетерпеливый» (3 нажатия за минуту)."""
    if not user or not is_group_member(user.id):
        return
    await award_achievement(user.id, "bot_f5_master", bot, user.full_name)
    clicks = await incr_with_ttl(f"ach:refresh:{user.id}", IMPATIENT_WINDOW_SECONDS)
    if clicks >= IMPATIENT_CLICKS:
        await award_achievement(user.id, "egg_impatient", bot, user.full_name)


async def on_attendance_view(user: User | None, bot: Any) -> None:
    """Личная посещаемость: «Самоконтроль» и «Аналитик» (5 разных дней)."""
    if not user or not is_group_member(user.id):
        return
    await award_achievement(user.id, "bot_self_audit", bot, user.full_name)
    await bump_counter(user.id, "attendance_days", bot, user.full_name)


async def on_homework_task(uid: int, name: str | None, bot: Any, task: HomeworkTask) -> None:
    """
    Задание в топике ДЗ: разовые ачивки, счётчики заданий, дней и форматов.

    Уточнение к своему заданию — не новое задание: даёт только «Работу над ошибками».
    """
    if not is_group_member(uid):
        return
    if task.is_followup:
        await award_achievement(uid, "ai_followup", bot, name)
        return
    await _award_all(uid, homework_achievements(task, _now()), bot, name)
    await bump_counter(uid, "hw_tasks", bot, name)
    await bump_counter(uid, "hw_days", bot, name)
    fio = resolve_student_fio(uid, name)
    await CounterRepository.increment(fio, f"hw_kind:{task.kind}")
    if await CounterRepository.count_keys(fio, "hw_kind:") >= 3:
        await award_achievement(uid, "ai_formats", bot, name)


async def mark_ping_all() -> None:
    """Открывает 15-минутное окно «Общего сбора» после /all старосты."""
    await cache_set(PING_ALL_KEY, "1", ttl=PING_ALL_WINDOW_SECONDS)


def _has_birthday_today(exclude_uid: int, today: date) -> bool:
    """Проверяет, есть ли сегодня именинник среди одногруппников, кроме автора."""
    return any(
        s.get("day") == today.day and s.get("month") == today.month and s.get("tg_id") != exclude_uid
        for s in load_classmates_registry()
    )


def _chat_reply_achievement(message: Message, uid: int) -> str | None:
    """
    Классифицирует реплай в чате: старосте → «Связь со старостой», одногруппнику → «Коллоквиум».

    Реплаи боту и самому себе не считаются.
    """
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target or target.is_bot or target.id == uid:
        return None
    if target.id == ALLOWED_USER_ID:
        return "soc_headman_ally"
    return "chat_replies" if is_group_member(target.id) else None


async def _award_chat_specials(message: Message, uid: int, bot: Any, name: str | None) -> None:
    """Разовые ачивки чата: поздравление именинника и реакция на /all."""
    text = message.text or message.caption or ""
    if BIRTHDAY_GREETING_RE.search(text) and _has_birthday_today(uid, _now().date()):
        await award_achievement(uid, "soc_heart", bot, name)
    if await cache_get(PING_ALL_KEY):
        await award_achievement(uid, "soc_ping_muster", bot, name)


async def on_group_message(message: Message, bot: Any) -> None:
    """
    Сообщение в чате группы: счётчики сообщений, стикеров и реплаев.

    Текст сообщений не сохраняется — только счётчики и разовые проверки.
    """
    user = message.from_user
    if not user or user.is_bot or not is_group_member(user.id):
        return
    name = user.full_name
    await bump_counter(user.id, "chat_messages", bot, name)
    if message.sticker:
        await bump_counter(user.id, "chat_stickers", bot, name)
    reply_kind = _chat_reply_achievement(message, user.id)
    if reply_kind == "chat_replies":
        await bump_counter(user.id, reply_kind, bot, name)
    elif reply_kind:
        await award_achievement(user.id, reply_kind, bot, name)
    await _award_chat_specials(message, user.id, bot, name)


async def on_profile_view(uid: int, viewed_fio: str) -> bool:
    """
    Просмотр чужого профиля в Mini App: «Солидарность» за 5 разных одногруппников.

    Множество просмотренных хранится ключами 'viewed:<ФИО>' — повторный
    просмотр того же профиля счётчик не увеличивает.

    Возвращает True, если ачивка открыта этим просмотром.
    """
    fio = resolve_student_fio(uid)
    target = viewed_fio.strip().lower()
    if not target or target in fio.lower() or fio.lower() in target:
        return False
    await CounterRepository.increment(fio, f"viewed:{target[:50]}")
    if await CounterRepository.count_keys(fio, "viewed:") < SOLIDARITY_PROFILES:
        return False
    return await award_achievement(uid, "soc_solidarity")
