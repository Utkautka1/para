"""
Сервис рассылки уведомлений и динамических напоминаний.

Использует AsyncIOScheduler для отправки ежедневного расписания в 06:00 МСК
и планирования индивидуальных напоминаний за 10 минут до каждой пары.
"""

import asyncio
import re
from datetime import date, datetime, timedelta
from datetime import time as dtime
from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.templates.admin.attendance import format_confirm_text, get_lesson_confirm_kb
from bot.templates.user.keyboards import get_schedule_inline_kb
from bot.templates.user.messages import format_reminder_text
from config import (
    ALLOWED_ATTENDANCE_USER_IDS,
    ALLOWED_USER_ID,
    DAILY_NOTIFY_HOUR,
    DAILY_NOTIFY_MINUTE,
    REMINDER_OFFSET_MINUTES,
    TIMEZONE,
)
from core.api_client import get_api_schedule_for_date
from core.bot import bot
from core.logger import get_logger
from services.attendance_manager import clear_session, get_active_session
from services.models import Lesson

log = get_logger("notifier")
scheduler = AsyncIOScheduler(timezone=TIMEZONE)

_NOTIFIED_MISSING_TEACHERS: set[str] = set()


def build_missing_teacher_alert(raw_teacher: str, subj_name: str) -> tuple[str, InlineKeyboardMarkup]:
    """
    Формирует текст и клавиатуру предупреждения об отсутствии преподавателя.

    Генерирует инлайн-кнопку быстрого перехода старосты к заполнению контактов.

    Возвращает кортеж (текст_оповещения, клавиатура).
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

    Использует in-memory сет для предотвращения спама повторными уведомлениями.

    Ничего не возвращает.
    """
    if not raw_teacher or raw_teacher in _NOTIFIED_MISSING_TEACHERS:
        return

    _NOTIFIED_MISSING_TEACHERS.add(raw_teacher)
    text, kb = build_missing_teacher_alert(raw_teacher, subj_name)

    log.warning(f"Уведомление админа об отсутствующем преподавателе: {raw_teacher}")
    await send_to_user(text, reply_markup=kb)


async def send_to_user(text: str, reply_markup: Any = None) -> None:
    """
    Отправляет сервисное HTML-сообщение администратору в ЛС.

    Перехватывает исключения блокировки бота администратором.

    Ничего не возвращает.
    """
    try:
        await bot.send_message(ALLOWED_USER_ID, text, reply_markup=reply_markup)
        log.info(f"Сообщение успешно отправлено пользователю {ALLOWED_USER_ID}")
    except Exception as e:
        log.error(f"Ошибка отправки сообщения пользователю {ALLOWED_USER_ID}: {e}")


def parse_lesson_start_time(time_str: str) -> dtime | None:
    """
    Парсит время начала пары из строки любого формата ('08:30–09:55', '8:30-09:55').

    Использует регулярные выражения для точного выделения часов и минут.

    Возвращает объект datetime.time или None при невозможности распознавания.
    """
    try:
        match = re.search(r"(\d{1,2})[:\.](\d{2})", time_str)
        if match:
            h, m = int(match.group(1)), int(match.group(2))
            return dtime(hour=h, minute=m)
    except Exception as e:
        log.error(f"Не удалось распарсить время пары {time_str}: {e}")

    return None


def parse_lesson_end_time(time_str: str) -> dtime | None:
    """
    Парсит время окончания пары из строки диапазона ('08:30–09:55').

    Выделяет второй временной маркер из диапазона звонков пары.

    Возвращает объект datetime.time окончания занятия или None.
    """
    try:
        matches = re.findall(r"(\d{1,2})[:\.](\d{2})", time_str)
        if len(matches) >= 2:
            h, m = int(matches[1][0]), int(matches[1][1])
            return dtime(hour=h, minute=m)
    except Exception as e:
        log.error(f"Не удалось распарсить время окончания пары {time_str}: {e}")

    return None


async def _send_reminder_to_chat(
    chat_id: int,
    text: str,
    lesson: Lesson,
    sem: asyncio.Semaphore,
) -> None:
    """
    Отправляет персональное напоминание одному подписчику под контролем семафора.

    Защищает от превышения rate-limit Telegram API (30 сообщений в секунду).

    Ничего не возвращает.
    """
    kb = get_schedule_inline_kb([lesson], is_admin=(chat_id == ALLOWED_USER_ID), is_subscribed=True)

    async with sem:
        try:
            await bot.send_message(chat_id, text, reply_markup=kb)
        except Exception as e:
            log.warning(f"Не удалось доставить напоминание {chat_id}: {e}")


async def send_single_reminder(lesson: Lesson) -> None:
    """
    Отправляет 10-минутное напоминание о паре всем активным подписчикам конкурентно.

    Загружает список получателей из базы и рассылает сообщения параллельно.

    Ничего не возвращает.
    """
    log.info(f"Отправка напоминания для пары {lesson.period + 1}: {lesson.subject}")
    text = format_reminder_text(lesson)

    from db.subscribers import load_subscribers

    targets = load_subscribers()
    if not targets:
        return

    sem = asyncio.Semaphore(10)
    tasks = [_send_reminder_to_chat(cid, text, lesson, sem) for cid in targets]
    await asyncio.gather(*tasks, return_exceptions=True)


def _add_lesson_reminder_job(today: date, lesson: Lesson, remind_dt: datetime) -> None:
    """
    Регистрирует отложенную отправку напоминания в планировщике.

    Ничего не возвращает.
    """
    job_id = f"remind_{today.isoformat()}_{lesson.period}"
    scheduler.add_job(
        send_single_reminder,
        "date",
        run_date=remind_dt,
        args=[lesson],
        id=job_id,
        replace_existing=True,
    )
    log.info(f"Запланировано напоминание для пары {lesson.period + 1} на {remind_dt.strftime('%H:%M:%S')}")


def schedule_lesson_reminder(today: date, lesson: Lesson, now_dt: datetime) -> None:
    """
    Планирует таймер напоминания за 10 минут до пары.

    Регистрирует задачу в APScheduler с уникальным строковым job_id.

    Ничего не возвращает.
    """
    start_t = parse_lesson_start_time(lesson.time_str)
    if not start_t:
        return

    pair_dt = datetime.combine(today, start_t, tzinfo=TIMEZONE)
    remind_dt = pair_dt - timedelta(minutes=REMINDER_OFFSET_MINUTES)

    if remind_dt > now_dt:
        _add_lesson_reminder_job(today, lesson, remind_dt)


async def _send_attendance_to_admin(
    user_id: int,
    text: str,
    kb: Any,
    sem: asyncio.Semaphore,
) -> None:
    """
    Отправляет запрос подтверждения пары старосте или замстаросты под семафором.

    Ничего не возвращает.
    """
    async with sem:
        try:
            await bot.send_message(user_id, text, reply_markup=kb)
            log.info(f"Запрос посещаемости пары отправлен пользователю {user_id}")
        except Exception as e:
            log.warning(f"Не удалось доставить запрос посещаемости пользователю {user_id}: {e}")


async def send_attendance_prompt(lesson: Lesson) -> None:
    """
    Отправляет запрос подтверждения проведения пары старосте и замстаросты параллельно.

    Формирует интерактивные кнопки быстрого запуска сессии опроса посещаемости.

    Ничего не возвращает.
    """
    text = format_confirm_text(lesson.number, lesson.subject, lesson.teacher or "Не указан")
    kb = get_lesson_confirm_kb(lesson.number)
    sem = asyncio.Semaphore(5)

    tasks = [_send_attendance_to_admin(uid, text, kb, sem) for uid in ALLOWED_ATTENDANCE_USER_IDS]
    await asyncio.gather(*tasks, return_exceptions=True)


async def auto_close_attendance_session(lesson_num: int) -> None:
    """
    Автоматически закрывает неактивную сессию отметки по окончании пары.

    Если староста не начал заполнять опрос к концу пары, сбрасывает сессию.

    Ничего не возвращает.
    """
    session = await get_active_session()
    if not session or session.lesson_num != lesson_num:
        return

    if session.current_idx > 0:
        log.debug(f"Сессия пары {lesson_num} не сброшена: идет активное заполнение ({session.current_idx})")
        return

    await clear_session()
    log.info(f"Сессия посещаемости пары {lesson_num} закрыта по окончании пары")


def _schedule_attendance_poll_job(today: date, lesson: Lesson, poll_dt: datetime, now_dt: datetime) -> None:
    """
    Планирует отправку опроса старосте через 30 минут после начала пары.

    Ничего не возвращает.
    """
    if poll_dt > now_dt:
        job_id = f"att_poll_{today.isoformat()}_{lesson.number}"
        scheduler.add_job(
            send_attendance_prompt,
            "date",
            run_date=poll_dt,
            args=[lesson],
            id=job_id,
            replace_existing=True,
        )
        log.info(f"Запланирован опрос посещаемости пары {lesson.number} на {poll_dt.strftime('%H:%M:%S')}")


def _schedule_attendance_close_job(today: date, lesson: Lesson, end_dt: datetime, now_dt: datetime) -> None:
    """
    Планирует автоматическое закрытие нетронутой сессии по окончании пары.

    Ничего не возвращает.
    """
    if end_dt > now_dt:
        close_id = f"att_close_{today.isoformat()}_{lesson.number}"
        scheduler.add_job(
            auto_close_attendance_session,
            "date",
            run_date=end_dt,
            args=[lesson.number],
            id=close_id,
            replace_existing=True,
        )


def schedule_attendance_poll(today: date, lesson: Lesson, now_dt: datetime) -> None:
    """
    Планирует опрос через 30 минут от старта пары и автозавершение в конце.

    Регистрирует две раздельные задачи в планировщике с часовым поясом Europe/Moscow.

    Ничего не возвращает.
    """
    start_t = parse_lesson_start_time(lesson.time_str)
    end_t = parse_lesson_end_time(lesson.time_str)

    if not start_t or not end_t:
        return

    poll_dt = datetime.combine(today, start_t, tzinfo=TIMEZONE) + timedelta(minutes=30)
    end_dt = datetime.combine(today, end_t, tzinfo=TIMEZONE)

    _schedule_attendance_poll_job(today, lesson, poll_dt, now_dt)
    _schedule_attendance_close_job(today, lesson, end_dt, now_dt)


async def daily_schedule_dispatch() -> None:
    """
    Ежедневный воркер расчёта таймеров (пропускает воскресенье).

    Выполняется каждое утро в 06:00, регистрируя все напоминания дня.

    Ничего не возвращает.
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
        schedule_attendance_poll(today, lesson, now_dt)


def setup_scheduler() -> AsyncIOScheduler:
    """
    Инициализирует и запускает планировщик задач APScheduler.

    Регистрирует ежедневную крон-задачу рассылки расписания в 06:00 МСК.

    Возвращает настроенный экземпляр AsyncIOScheduler.
    """
    scheduler.add_job(
        daily_schedule_dispatch,
        "cron",
        hour=DAILY_NOTIFY_HOUR,
        minute=DAILY_NOTIFY_MINUTE,
        id="daily_dispatch",
        replace_existing=True,
    )
    scheduler.start()
    log.info(f"Планировщик запущен. Ежедневная рассылка в {DAILY_NOTIFY_HOUR:02d}:{DAILY_NOTIFY_MINUTE:02d} МСК")

    return scheduler
