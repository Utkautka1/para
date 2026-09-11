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

from config import TIMEZONE
from bot.filters.auth import AuthFilter
from services.docx_parser import get_teacher_links
from services.schedule_parser import Lesson, get_schedule_for_date, get_week_schedule
from bot.templates.user.keyboards import get_schedule_inline_kb
from bot.templates.user.messages import format_day_schedule, format_week_schedule

from core.logger import get_logger

log = get_logger("user_schedule")

router = Router()
router.message.filter(AuthFilter())
router.callback_query.filter(AuthFilter())


async def edit_or_answer(
    callback: CallbackQuery, text: str, lessons: List[Lesson] = None, week_offset: int = 0
) -> None:
    """
    Безопасно обновляет содержимое текущего сообщения.

    :param callback: Объект CallbackQuery
    :param text: Новый HTML текст
    :param lessons: Список пар для кнопок подключений
    :param week_offset: Смещение недели
    """
    kb = get_schedule_inline_kb(lessons, week_offset=week_offset)
    try:
        if callback.message:
            await callback.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.message(CommandStart())
@router.message(Command("today"))
async def cmd_start(message: Message) -> None:
    """
    Отправляет расписание с инлайн-меню и гарантированно скрывает Reply-кнопки.

    :param message: Telegram сообщение
    """
    user_id = message.from_user.id if message.from_user else "unknown"
    log.info(f"Получена команда /start или /today от user_id={user_id}")
    now = datetime.now(TIMEZONE).date()
    lessons = await get_schedule_for_date(now)
    text = format_day_schedule(now, lessons)
    await message.answer(text, reply_markup=get_schedule_inline_kb(lessons))



@router.callback_query(F.data == "sched:today")
async def cb_today(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на сегодня.

    :param callback: CallbackQuery
    """
    now = datetime.now(TIMEZONE).date()
    lessons = await get_schedule_for_date(now)
    text = format_day_schedule(now, lessons)
    await edit_or_answer(callback, text, lessons)


@router.callback_query(F.data == "sched:tomorrow")
async def cb_tomorrow(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на завтра.

    :param callback: CallbackQuery
    """
    tomorrow = datetime.now(TIMEZONE).date() + timedelta(days=1)
    lessons = await get_schedule_for_date(tomorrow)
    text = format_day_schedule(tomorrow, lessons)
    await edit_or_answer(callback, text, lessons)


@router.callback_query(F.data == "sched:week")
async def cb_week(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на текущую неделю.

    :param callback: CallbackQuery
    """
    today = datetime.now(TIMEZONE).date()
    monday = today - timedelta(days=today.weekday())
    days_data = await get_week_schedule(monday)
    text = format_week_schedule(days_data)
    await edit_or_answer(callback, text, week_offset=0)


@router.callback_query(F.data == "sched:week_next")
async def cb_week_next(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на следующую неделю.

    :param callback: CallbackQuery
    """
    today = datetime.now(TIMEZONE).date()
    next_monday = today - timedelta(days=today.weekday()) + timedelta(weeks=1)
    days_data = await get_week_schedule(next_monday)
    text = format_week_schedule(days_data)
    await edit_or_answer(callback, text, week_offset=1)


@router.callback_query(F.data.startswith("copy:"))
async def cb_copy_value(callback: CallbackQuery) -> None:
    """
    Всплывающее уведомление для копирования значение в буфер обмена.

    :param callback: CallbackQuery
    """
    val = callback.data.split("copy:", 1)[1]
    await callback.answer(f"Скопировано: {val}", show_alert=True)


@router.callback_query(F.data == "sched:refresh")
async def cb_refresh(callback: CallbackQuery) -> None:
    """
    Принудительно скачивает свежее расписание с сайта и ссылки с Яндекс Диска.

    :param callback: CallbackQuery
    """
    links = await get_teacher_links(force_refresh=True)
    now = datetime.now(TIMEZONE).date()
    lessons = await get_schedule_for_date(now, force_refresh=True)
    text = format_day_schedule(now, lessons)
    text += f"\n\n<i>✅ Расписание КТМУ и контакты преподавателей ({len(links)}) сверены и обновлены!</i>"
    await edit_or_answer(callback, text, lessons)
