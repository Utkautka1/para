"""
Модуль синхронизации и авто-обновления расписания в Telegram-топике группы.

Сохраняет состояние _TOPIC_MAIN_MSG_ID в data/topic_state.json для устойчивости к перезапускам.
Синхронизирует расписание каждые 60 секунд и отправляет временные 10-минутные уведомления.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Optional
from aiogram.exceptions import TelegramBadRequest

from config import TIMEZONE, TOPIC_CHAT_ID, TOPIC_THREAD_ID
from core.bot import bot
from core.logger import get_logger
from services.schedule_parser import Lesson, get_schedule_for_date
from bot.templates.user.keyboards import get_topic_inline_kb
from bot.templates.user.messages import format_day_schedule, format_reminder_text
from services.notifier import parse_lesson_start_time

log = get_logger("topic_updater")
STATE_FILE = "data/topic_state.json"

_TOPIC_MAIN_MSG_ID: Optional[int] = None
_SENT_REMINDERS: set = set()


def load_topic_state() -> Optional[int]:
    """
    Загружает сохраненный ID главного сообщения из JSON файла.

    :return: ID сообщения или None
    """
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("main_msg_id")
        except Exception as e:
            log.error(f"Ошибка чтения topic_state.json: {e}")
    return None


def save_topic_state(msg_id: Optional[int]) -> None:
    """
    Сохраняет ID главного сообщения в JSON файл.

    :param msg_id: ID сообщения
    """
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"main_msg_id": msg_id}, f)
    except Exception as e:
        log.error(f"Ошибка записи topic_state.json: {e}")


async def send_temp_topic_reminder(lesson: Lesson) -> None:
    """
    Отправляет удаляемое через 15 минут уведомление за 10 минут до пары.

    :param lesson: Объект пары
    """
    try:
        text = format_reminder_text(lesson)
        kb = get_topic_inline_kb([lesson])
        msg = await bot.send_message(
            chat_id=TOPIC_CHAT_ID,
            message_thread_id=TOPIC_THREAD_ID,
            text=text,
            reply_markup=kb
        )
        log.info(f"Временное уведомление о паре {lesson.period + 1} отправлено в топик. MSG_ID={msg.message_id}")
        await asyncio.sleep(900)
        await bot.delete_message(chat_id=TOPIC_CHAT_ID, message_id=msg.message_id)
        log.info(f"Временное уведомление MSG_ID={msg.message_id} успешно удалено.")
    except TelegramBadRequest:
        pass
    except Exception as e:
        log.error(f"Ошибка отправки/удаления временного уведомления: {e}")


def check_and_trigger_reminder(lesson: Lesson, now_dt: datetime, today: datetime.date) -> None:
    """
    Проверяет время до пары и спавнит таску временного уведомления.

    :param lesson: Объект пары
    :param now_dt: Время МСК
    :param today: Дата
    """
    rem_key = f"{today.isoformat()}_{lesson.period}_{lesson.subgroup}"
    if rem_key in _SENT_REMINDERS:
        return
    start_t = parse_lesson_start_time(lesson.time_str)
    if not start_t:
        return
    pair_dt = datetime.combine(today, start_t).replace(tzinfo=TIMEZONE)
    diff_sec = (pair_dt - now_dt).total_seconds()
    if 480 <= diff_sec <= 660:
        _SENT_REMINDERS.add(rem_key)
        asyncio.create_task(send_temp_topic_reminder(lesson))


async def sync_topic_main_message(ignore_time_restriction: bool = False) -> None:
    """
    Атомарно обновляет главное сообщение расписания в топике без создания дублей.

    :param ignore_time_restriction: Флаг принудительной отправки (из админки)
    """
    global _TOPIC_MAIN_MSG_ID
    if _TOPIC_MAIN_MSG_ID is None:
        _TOPIC_MAIN_MSG_ID = load_topic_state()

    now_dt = datetime.now(TIMEZONE)
    today = now_dt.date()
    if today.weekday() == 6 and not ignore_time_restriction:
        log.debug("Воскресенье — авто-обновление топика пропущено.")
        return

    lessons = await get_schedule_for_date(today)
    text = format_day_schedule(today, lessons)
    kb = get_topic_inline_kb(lessons)

    if not lessons:
        return

    # Находим первую пару дня
    first_lesson = min(lessons, key=lambda x: x.period)
    start_t = parse_lesson_start_time(first_lesson.time_str)
    if start_t and not ignore_time_restriction:
        first_pair_dt = datetime.combine(today, start_t).replace(tzinfo=TIMEZONE)
        publish_dt = first_pair_dt - timedelta(minutes=60)
        if now_dt < publish_dt and _TOPIC_MAIN_MSG_ID is None:
            log.debug(f"Публикация в топик отложена до {publish_dt.strftime('%H:%M:%S')} (за 1 час до 1 пары)")
            return

    for l in lessons:
        check_and_trigger_reminder(l, now_dt, today)

    try:
        if _TOPIC_MAIN_MSG_ID is None:
            msg = await bot.send_message(
                chat_id=TOPIC_CHAT_ID,
                message_thread_id=TOPIC_THREAD_ID,
                text=text,
                reply_markup=kb
            )
            _TOPIC_MAIN_MSG_ID = msg.message_id
            save_topic_state(_TOPIC_MAIN_MSG_ID)
            log.info(f"Главное сообщение расписания создано в топике: MSG_ID={_TOPIC_MAIN_MSG_ID}")
        else:
            await bot.edit_message_text(
                chat_id=TOPIC_CHAT_ID,
                message_id=_TOPIC_MAIN_MSG_ID,
                text=text,
                reply_markup=kb
            )
            log.debug(f"Сообщение расписания в топике обновлено: MSG_ID={_TOPIC_MAIN_MSG_ID}")
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            pass
        elif "message to edit not found" in str(e).lower():
            _TOPIC_MAIN_MSG_ID = None
            save_topic_state(None)
    except Exception as e:
        log.error(f"Ошибка обновления топика: {e}")


async def topic_sync_loop() -> None:
    """
    Фоновый цикл синхронизации топика каждые 60 секунд.
    """
    log.info("Запущен фоновый сервис авто-обновления расписания в топике Telegram (60 сек)")
    while True:
        try:
            await sync_topic_main_message()
        except Exception as e:
            log.error(f"Ошибка в цикле topic_sync_loop: {e}")
        await asyncio.sleep(60)
