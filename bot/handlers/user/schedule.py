"""
Хэндлеры команд и Inline-кнопок пользователя.

Обрабатывает команды и инлайн-переходы sched:today, sched:tomorrow,
sched:week, sched:refresh с редактированием существующего сообщения.
"""

from datetime import datetime, timedelta
from typing import List
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from config import ALLOWED_USER_ID, TIMEZONE
from bot.filters.auth import ClassmateAuthFilter
from bot.templates.user.keyboards import get_schedule_inline_kb
from bot.templates.user.messages import format_day_schedule, format_week_schedule
from core.api_client import (
    fetch_teachers,
    get_api_schedule_for_date,
    get_api_week_schedule,
)
from core.logger import get_logger
from services.classmates_auth import process_user_auth
from services.models import Lesson
from services.redis_cache import cache_flush, cache_get, cache_set

log = get_logger("user_schedule")

router = Router()
router.callback_query.filter(ClassmateAuthFilter())


async def edit_or_answer(
    callback: CallbackQuery, text: str, lessons: List[Lesson] = None, week_offset: int = 0
) -> None:
    """
    Безопасно обновляет содержимое текущего сообщения.

    Кнопка админ-панели отображается исключительно Главному Администратору.
    """
    is_admin = bool(callback.from_user and callback.from_user.id == ALLOWED_USER_ID)
    kb = get_schedule_inline_kb(lessons, week_offset=week_offset, is_admin=is_admin)
    try:
        if callback.message:
            await callback.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        pass
    try:
        await callback.answer("Расписание обновлено!")
    except TelegramBadRequest:
        pass


async def _greet_new_student(message: Message, student: dict) -> None:
    """Отправляет персональное приветствие новому зарегистрированному студенту."""
    name = student.get("full_name", "Студент")
    await message.answer(
        f"🎉 <b>Добро пожаловать, {name}!</b>\n"
        "Ты успешно авторизован(а) в боте группы 1-КПД-3."
    )


@router.message(CommandStart())
@router.message(Command("today"))
async def cmd_start(message: Message) -> None:
    """
    Авторизует пользователя и отправляет расписание на сегодня.

    При первом входе одногруппника разово привязывает его Telegram ID.
    Посторонним пользователям доступ к расписанию блокируется.
    """
    is_auth, is_just_registered, student = process_user_auth(message.from_user)
    if not is_auth:
        await message.answer(
            "⛔ <b>Доступ ограничен.</b>\n"
            "Этот бот работает исключительно для студентов группы 1-КПД-3."
        )
        return
    if is_just_registered and student:
        await _greet_new_student(message, student)
    is_admin = bool(message.from_user and message.from_user.id == ALLOWED_USER_ID)
    now = datetime.now(TIMEZONE).date()
    lessons = await get_api_schedule_for_date(now)
    text = format_day_schedule(now, lessons)
    await message.answer(text, reply_markup=get_schedule_inline_kb(lessons, is_admin=is_admin))


@router.callback_query(F.data == "sched:today")
async def cb_today(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на сегодня.

    :param callback: CallbackQuery
    """
    log.info("Нажата инлайн-кнопка: Сегодня")
    now = datetime.now(TIMEZONE).date()
    lessons = await get_api_schedule_for_date(now)
    text = format_day_schedule(now, lessons)
    await edit_or_answer(callback, text, lessons)


@router.callback_query(F.data == "sched:tomorrow")
async def cb_tomorrow(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на завтра.

    :param callback: CallbackQuery
    """
    log.info("Нажата инлайн-кнопка: Завтра")
    tomorrow = datetime.now(TIMEZONE).date() + timedelta(days=1)
    lessons = await get_api_schedule_for_date(tomorrow)
    text = format_day_schedule(tomorrow, lessons)
    await edit_or_answer(callback, text, lessons)


@router.callback_query(F.data == "sched:week")
async def cb_week(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на текущую неделю с Redis-кэшированием.

    :param callback: CallbackQuery
    """
    log.info("Нажата инлайн-кнопка: Эта неделя")
    today = datetime.now(TIMEZONE).date()
    monday = today - timedelta(days=today.weekday())
    cache_key = f"sched:week:{monday.isoformat()}"
    cached_text = await cache_get(cache_key)

    if cached_text:
        await edit_or_answer(callback, cached_text, week_offset=0)
        return

    days_data = await get_api_week_schedule(monday)
    text = format_week_schedule(days_data)
    await cache_set(cache_key, text)
    await edit_or_answer(callback, text, week_offset=0)


@router.callback_query(F.data == "sched:week_next")
async def cb_week_next(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на следующую неделю с Redis-кэшированием.

    :param callback: CallbackQuery
    """
    log.info("Нажата инлайн-кнопка: Следующая неделя")
    today = datetime.now(TIMEZONE).date()
    next_monday = today - timedelta(days=today.weekday()) + timedelta(weeks=1)
    cache_key = f"sched:week_next:{next_monday.isoformat()}"
    cached_text = await cache_get(cache_key)

    if cached_text:
        await edit_or_answer(callback, cached_text, week_offset=1)
        return

    days_data = await get_api_week_schedule(next_monday)
    text = format_week_schedule(days_data)
    await cache_set(cache_key, text)
    await edit_or_answer(callback, text, week_offset=1)


@router.callback_query(F.data.startswith("copy:"))
async def cb_copy_value(callback: CallbackQuery) -> None:
    """
    Всплывающее уведомление для копирования значение в буфер обмена.

    :param callback: CallbackQuery
    """
    val = callback.data.split("copy:", 1)[1]
    log.debug(f"Нажато копирование реквизитов: {val}")
    await callback.answer(f"Скопировано: {val}", show_alert=True)


@router.callback_query(F.data == "sched:refresh")
async def cb_refresh(callback: CallbackQuery) -> None:
    """
    Принудительно скачивает расписание, очищает Redis-кэш и обновляет экран.

    :param callback: CallbackQuery
    """
    log.info("Нажата инлайн-кнопка: Обновить расписание (Сброс Redis)")
    try:
        await callback.answer("Синхронизация с API КТМУ...")
    except TelegramBadRequest:
        pass
    await cache_flush()
    teachers_res = await fetch_teachers(force_refresh=True)
    count = teachers_res.get("count", 0)
    now = datetime.now(TIMEZONE).date()
    lessons = await get_api_schedule_for_date(now, force_refresh=True)
    text = format_day_schedule(now, lessons)
    text += f"\n\n<i>✅ Расписание КТМУ и контакты ({count}) сверены, Redis очищен!</i>"
    await edit_or_answer(callback, text, lessons)



