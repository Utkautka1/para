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
from bot.templates.user.keyboards import get_notice_settings_kb, get_schedule_inline_kb
from bot.templates.user.messages import (
    format_day_schedule,
    format_notice_settings_text,
    format_week_schedule,
)
from core.api_client import (
    fetch_teachers,
    get_api_schedule_for_date,
    get_api_week_schedule,
)
from core.logger import get_logger
from db.subscribers import add_subscriber, is_subscribed, toggle_subscriber
from services.classmates_auth import is_authorized_user, process_user_auth
from services.models import Lesson
from services.redis_cache import cache_flush, cache_get, cache_set

log = get_logger("user_schedule")

router = Router()
router.callback_query.filter(ClassmateAuthFilter())


async def edit_or_answer(
    callback: CallbackQuery, text: str, lessons: List[Lesson] = None, week_offset: int = 0
) -> None:
    """Безопасно обновляет содержимое текущего сообщения с учетом прав и подписки."""
    uid = callback.from_user.id if callback.from_user else 0
    is_admin = bool(uid == ALLOWED_USER_ID)
    kb = get_schedule_inline_kb(
        lessons, week_offset=week_offset, is_admin=is_admin, is_subscribed=is_subscribed(uid)
    )
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
    """Авторизует пользователя и отправляет расписание на сегодня."""
    is_auth, is_just_reg, student = process_user_auth(message.from_user)
    if not is_auth:
        await message.answer(
            "⛔ <b>Доступ ограничен.</b>\n"
            "Этот бот работает исключительно для студентов группы 1-КПД-3."
        )
        return
    if is_just_reg and student and message.from_user:
        add_subscriber(message.from_user.id)
        await _greet_new_student(message, student)
    uid = message.from_user.id if message.from_user else 0
    now = datetime.now(TIMEZONE).date()
    lessons = await get_api_schedule_for_date(now)
    text = format_day_schedule(now, lessons)
    kb = get_schedule_inline_kb(
        lessons, is_admin=(uid == ALLOWED_USER_ID), is_subscribed=is_subscribed(uid)
    )
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "sched:toggle_notify")
async def cb_toggle_notify(callback: CallbackQuery) -> None:
    """Переключает статус подписки на 10-минутные напоминания о парах в ЛС."""
    uid = callback.from_user.id if callback.from_user else 0
    new_sub = toggle_subscriber(uid)
    ans_text = "🔔 Напоминания за 10 мин включены!" if new_sub else "🔕 Напоминания отключены."
    try:
        await callback.answer(ans_text)
    except TelegramBadRequest:
        pass
    now = datetime.now(TIMEZONE).date()
    lessons = await get_api_schedule_for_date(now)
    kb = get_schedule_inline_kb(lessons, is_admin=(uid == ALLOWED_USER_ID), is_subscribed=new_sub)
    try:
        if callback.message:
            await callback.message.edit_reply_markup(reply_markup=kb)
    except TelegramBadRequest:
        pass


@router.message(Command("notice"))
async def cmd_notice(message: Message) -> None:
    """Отображает экран настроек уведомлений /notice."""
    if not is_authorized_user(message.from_user):
        await message.answer(
            "⛔ <b>Доступ ограничен.</b>\n"
            "Этот бот работает исключительно для студентов группы 1-КПД-3."
        )
        return
    uid = message.from_user.id if message.from_user else 0
    is_sub = is_subscribed(uid)
    text = format_notice_settings_text(is_sub)
    await message.answer(text, reply_markup=get_notice_settings_kb(is_sub))


@router.callback_query(F.data == "notice:toggle")
async def cb_notice_toggle(callback: CallbackQuery) -> None:
    """Переключает статус подписки в меню /notice с обновлением экрана."""
    uid = callback.from_user.id if callback.from_user else 0
    new_sub = toggle_subscriber(uid)
    ans = "🔔 Уведомления включены!" if new_sub else "🔕 Уведомления отключены."
    try:
        await callback.answer(ans)
    except TelegramBadRequest:
        pass
    text = format_notice_settings_text(new_sub)
    try:
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_notice_settings_kb(new_sub))
    except TelegramBadRequest:
        pass


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



