"""
Сервис рассылки уведомлений и динамических напоминаний.

Использует AsyncIOScheduler для отправки ежедневного расписания в 06:00 МСК
и планирования индивидуальных напоминаний за 10 минут до каждой пары.
"""

from datetime import datetime, timedelta, time as dtime
from typing import Any, List, Optional, Tuple
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import ALLOWED_USER_ID, DAILY_NOTIFY_HOUR, DAILY_NOTIFY_MINUTE, REMINDER_OFFSET_MINUTES, TIMEZONE
from core.api_client import get_api_schedule_for_date
from core.bot import bot
from core.logger import get_logger
from services.models import Lesson
from bot.templates.user.keyboards import get_schedule_inline_kb
from bot.templates.user.messages import format_day_schedule, format_reminder_text

log = get_logger("notifier")
scheduler = AsyncIOScheduler(timezone=TIMEZONE)


_NOTIFIED_MISSING_TEACHERS: set = set()


def build_missing_teacher_alert(raw_teacher: str, subj_name: str) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Формирует текст и клавиатуру предупреждения об отсутствии преподавателя.
    """
    text = (
        f"⚠️ <b>Преподаватель не найден в таблице!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📚 <b>Предмет:</b> {subj_name}\n"
        f"👨‍🏫 <b>Преподаватель:</b> {raw_teacher}\n\n"
        f"<i>Пара проходит в дистанционном формате, но ссылки нет в документе Яндекс Диска.</i>"
    )
    last_name = raw_teacher.split()[0].lower()
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Добавить контакты", callback_data=f"admin:add_t:{last_name}")
    ]])
    return text, kb


async def notify_missing_teacher(raw_teacher: str, subj_name: str) -> None:
    """
    Уведомляет администратора в ЛС, если преподаватель дистанционной пары не найден.
    """
    if not raw_teacher or raw_teacher in _NOTIFIED_MISSING_TEACHERS:
        return
    _NOTIFIED_MISSING_TEACHERS.add(raw_teacher)

    text, kb = build_missing_teacher_alert(raw_teacher, subj_name)
    log.warning(f"Уведомление админа об отсутствующем преподавателе: {raw_teacher}")
    await send_to_user(text, reply_markup=kb)


async def send_to_user(text: str, reply_markup=None) -> None:
    """
    Отправляет сообщение разрешенному пользователю ALLOWED_USER_ID.

    :param text: Текст HTML сообщения
    :param reply_markup: Опциональная клавиатура
    """
    try:
        await bot.send_message(ALLOWED_USER_ID, text, reply_markup=reply_markup)
        log.info(f"Сообщение успешно отправлено пользователю {ALLOWED_USER_ID}")
    except Exception as e:
        log.error(f"Ошибка отправки сообщения пользователю {ALLOWED_USER_ID}: {e}")


def parse_lesson_start_time(time_str: str) -> Optional[dtime]:
    """
    Парсит время начала пары из строки любого формата ('08:30–09:55', '8:30-09:55').

    :param time_str: Строка времени
    :return: Объект time или None при ошибке
    """
    try:
        import re
        match = re.search(r"(\d{1,2})[:\.](\d{2})", time_str)
        if match:
            h, m = int(match.group(1)), int(match.group(2))
            return dtime(hour=h, minute=m)
    except Exception as e:
        log.error(f"Не удалось распарсить время пары {time_str}: {e}")
    return None


def parse_lesson_end_time(time_str: str) -> Optional[dtime]:
    """
    Парсит время окончания пары из строки любого формата ('08:30–09:55').

    :param time_str: Строка времени
    :return: Объект time или None при ошибке
    """
    try:
        import re
        matches = re.findall(r"(\d{1,2})[:\.](\d{2})", time_str)
        if len(matches) >= 2:
            h, m = int(matches[1][0]), int(matches[1][1])
            return dtime(hour=h, minute=m)
    except Exception as e:
        log.error(f"Не удалось распарсить время окончания пары {time_str}: {e}")
    return None


async def send_single_reminder(lesson: Lesson) -> None:
    """
    Отправляет 10-минутное напоминание о паре всем подписчикам и админу.

    :param lesson: Объект пары
    """
    log.info(f"Отправка напоминания для пары {lesson.period + 1}: {lesson.subject}")
    text = format_reminder_text(lesson)
    kb = get_schedule_inline_kb([lesson])
    from db.subscribers import load_subscribers
    targets = load_subscribers()
    targets.add(ALLOWED_USER_ID)
    for chat_id in targets:
        try:
            await bot.send_message(chat_id, text, reply_markup=kb)
        except Exception as e:
            log.warning(f"Не удалось доставить напоминание {chat_id}: {e}")


def schedule_lesson_reminder(today: datetime.date, lesson: Lesson, now_dt: datetime) -> None:
    """
    Планирует таймер напоминания за 10 минут до пары.

    :param today: Дата сегодняшнего дня
    :param lesson: Объект пары
    :param now_dt: Текущее время с часовым поясом
    """
    start_t = parse_lesson_start_time(lesson.time_str)
    if not start_t:
        return
    pair_dt = datetime.combine(today, start_t, tzinfo=TIMEZONE)
    remind_dt = pair_dt - timedelta(minutes=REMINDER_OFFSET_MINUTES)
    if remind_dt > now_dt:
        job_id = f"remind_{today.isoformat()}_{lesson.period}"
        scheduler.add_job(
            send_single_reminder, "date", run_date=remind_dt,
            args=[lesson], id=job_id, replace_existing=True
        )
        log.info(f"Запланировано напоминание для пары {lesson.period + 1} на {remind_dt.strftime('%H:%M:%S')}")


async def daily_schedule_dispatch() -> None:
    """
    Ежедневный воркер расчёта таймеров (пропускает воскресенье).
    """
    now_dt = datetime.now(TIMEZONE)
    today = now_dt.date()
    if today.weekday() == 6:
        log.info("Сегодня Воскресенье — фоновый расчет рассылок пропущен.")
        return
    log.info(f"=== ЕЖЕДНЕВНЫЙ ФОНОВЫЙ РАСЧЁТ ТАЙМЕРОВ ({today}) ===")
    lessons = await get_api_schedule_for_date(today, force_refresh=True)
    for lesson in lessons:
        schedule_lesson_reminder(today, lesson, now_dt)


def setup_scheduler() -> AsyncIOScheduler:
    """
    Инициализирует и запускает планировщик задач.

    :return: AsyncIOScheduler
    """
    scheduler.add_job(
        daily_schedule_dispatch, "cron",
        hour=DAILY_NOTIFY_HOUR, minute=DAILY_NOTIFY_MINUTE,
        id="daily_dispatch", replace_existing=True
    )
    scheduler.start()
    log.info(f"Планировщик запущен. Ежедневная рассылка в {DAILY_NOTIFY_HOUR:02d}:{DAILY_NOTIFY_MINUTE:02d} МСК")
    return scheduler
