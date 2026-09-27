"""
Модуль синхронизации и авто-обновления расписания в Telegram-топике группы.

Сохраняет состояние _TOPIC_MAIN_MSG_ID в data/topic_state.json для устойчивости к перезапускам.
Синхронизирует расписание каждые 60 секунд и отправляет временные 10-минутные уведомления.
"""

import asyncio
import json
import os
from datetime import date, datetime, timedelta
from typing import Any, List, Optional
from aiogram.exceptions import TelegramBadRequest

from config import TIMEZONE, TOPIC_CHAT_ID, TOPIC_THREAD_ID
from core.api_client import get_api_schedule_for_date
from core.bot import bot
from core.logger import get_logger
from services.models import Lesson
from bot.templates.user.keyboards import get_topic_inline_kb
from bot.templates.user.messages import format_day_schedule, format_reminder_text
from services.notifier import parse_lesson_end_time, parse_lesson_start_time

log = get_logger("topic_updater")
STATE_FILE = "data/topic_state.json"

_TOPIC_MAIN_MSG_ID: Optional[int] = None
_SENT_REMINDERS: set = set()


from utils.storage import sync_atomic_save_json, sync_load_json


def load_topic_state() -> Optional[int]:
    """
    Загружает сохраненный ID главного сообщения из JSON файла.

    :return: ID сообщения или None
    """
    data = sync_load_json(STATE_FILE, default={})
    return data.get("main_msg_id") if isinstance(data, dict) else None


def save_topic_state(msg_id: Optional[int]) -> None:
    """
    Атомарно сохраняет ID главного сообщения в JSON файл.

    :param msg_id: ID сообщения
    """
    sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})


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
    rem_key = f"{today.isoformat()}_{lesson.period}_{lesson.subgroup}_{lesson.subject}"
    if rem_key in _SENT_REMINDERS:
        return
    start_t = parse_lesson_start_time(lesson.time_str)
    if not start_t:
        return
    pair_dt = datetime.combine(today, start_t, tzinfo=TIMEZONE)
    diff_sec = (pair_dt - now_dt).total_seconds()
    if 0 < diff_sec <= 600:
        _SENT_REMINDERS.add(rem_key)
        asyncio.create_task(send_temp_topic_reminder(lesson))


def get_next_working_day(target_date: datetime.date) -> datetime.date:
    """
    Возвращает следующий рабочий день (пропускает воскресенье, сдвигая на понедельник).

    :param target_date: Текущая дата
    :return: Следующая дата без воскресенья
    """
    next_d = target_date + timedelta(days=1)
    if next_d.weekday() == 6:
        return next_d + timedelta(days=1)
    return next_d


async def resolve_target_date(now_dt: datetime, ignore_restriction: bool) -> Optional[datetime.date]:
    """
    Вычисляет целевую дату: при завершении всех пар на сегодня переключает на следующий день.

    :param now_dt: Текущее время МСК
    :param ignore_restriction: Игнорировать ли временные фильтры
    :return: Дата или None
    """
    today = now_dt.date()
    if today.weekday() == 6:
        if now_dt.hour < 18 and not ignore_restriction:
            return None
        return today + timedelta(days=1)
    today_lessons = await get_api_schedule_for_date(today)
    if not today_lessons:
        return today
    last_lesson = max(today_lessons, key=lambda x: x.period)
    end_t = parse_lesson_end_time(last_lesson.time_str)
    if end_t:
        last_end_dt = datetime.combine(today, end_t, tzinfo=TIMEZONE)
        if now_dt >= last_end_dt:
            return get_next_working_day(today)
    return today


def is_too_early_to_publish(lessons: List[Lesson], now_dt: datetime, today: datetime.date, ignore_restriction: bool) -> bool:
    """
    Проверяет, не рано ли публиковать расписание (за 1 час до 1-й пары).

    :return: True если еще рано отправлять новое сообщение
    """
    if today.weekday() == 6 or ignore_restriction or _TOPIC_MAIN_MSG_ID is not None:
        return False
    first_lesson = min(lessons, key=lambda x: x.period)
    start_t = parse_lesson_start_time(first_lesson.time_str)
    if start_t:
        first_pair_dt = datetime.combine(today, start_t, tzinfo=TIMEZONE)
        if now_dt < first_pair_dt - timedelta(minutes=60):
            return True
    return False


async def update_topic_message_payload(text: str, kb: Any, _retry: bool = False) -> bool:
    """
    Атомарно отправляет новое или редактирует существующее сообщение топика.

    При ошибке редактирования (сообщение удалено/недоступно) — пересоздаёт.
    _retry=True предотвращает бесконечную рекурсию.

    :return: True если сообщение обновлено/создано, False при ошибке
    """
    global _TOPIC_MAIN_MSG_ID
    try:
        if _TOPIC_MAIN_MSG_ID is None:
            return await _send_new_topic_message(text, kb)
        await bot.edit_message_text(
            chat_id=TOPIC_CHAT_ID, message_id=_TOPIC_MAIN_MSG_ID,
            text=text, reply_markup=kb
        )
        log.info(f"✅ Сообщение топика ОТРЕДАКТИРОВАНО: MSG_ID={_TOPIC_MAIN_MSG_ID}, chat={TOPIC_CHAT_ID}")
        return True
    except TelegramBadRequest as e:
        return await _handle_edit_failure(e, text, kb, _retry)
    except Exception as e:
        log.error(f"❌ Ошибка обновления топика: {type(e).__name__}: {e}")
        return False


async def _send_new_topic_message(text: str, kb: Any) -> bool:
    """Создаёт новое сообщение расписания в топике и закрепляет его."""
    global _TOPIC_MAIN_MSG_ID
    msg = await bot.send_message(
        chat_id=TOPIC_CHAT_ID, message_thread_id=TOPIC_THREAD_ID,
        text=text, reply_markup=kb
    )
    _TOPIC_MAIN_MSG_ID = msg.message_id
    save_topic_state(_TOPIC_MAIN_MSG_ID)
    await _pin_silently(TOPIC_CHAT_ID, _TOPIC_MAIN_MSG_ID)
    log.info(f"Главное сообщение создано и закреплено: MSG_ID={_TOPIC_MAIN_MSG_ID}")
    return True


async def _pin_silently(chat_id: int, message_id: int) -> None:
    """Закрепляет сообщение без уведомления участникам."""
    try:
        await bot.pin_chat_message(
            chat_id=chat_id, message_id=message_id,
            disable_notification=True
        )
    except Exception as e:
        log.warning(f"Не удалось закрепить MSG_ID={message_id}: {e}")


async def recreate_topic_message() -> bool:
    """
    Удаляет текущее сообщение и создаёт новое (одноразовый сброс MSG_ID).

    Используется когда MSG_ID в state указывает на призрачное/невидимое сообщение.
    После вызова — дальнейшие sync будут редактировать уже правильное сообщение.

    :return: True если пересоздание прошло
    """
    global _TOPIC_MAIN_MSG_ID
    old_id = _TOPIC_MAIN_MSG_ID or load_topic_state()

    # Пытаемся удалить старое призрачное сообщение
    if old_id:
        try:
            await bot.delete_message(chat_id=TOPIC_CHAT_ID, message_id=old_id)
            log.info(f"Старое сообщение MSG_ID={old_id} удалено")
        except Exception as e:
            log.warning(f"Не удалось удалить MSG_ID={old_id}: {e}")

    # Сбрасываем state — sync создаст новое сообщение
    _TOPIC_MAIN_MSG_ID = None
    save_topic_state(None)
    log.info("State сброшен — следующий sync создаст новое сообщение")
    return await sync_topic_main_message(ignore_time_restriction=True)


async def _handle_edit_failure(
    e: TelegramBadRequest, text: str, kb: Any, is_retry: bool
) -> bool:
    """
    Обрабатывает ошибку редактирования: "not modified" — штатно,
    остальные — пересоздаёт сообщение (один раз, без рекурсии).
    """
    global _TOPIC_MAIN_MSG_ID
    err = str(e).lower()
    if "not modified" in err:
        log.info(f"sync_topic: 'not modified' — текст уже актуален (MSG_ID={_TOPIC_MAIN_MSG_ID})")
        return True
    if is_retry:
        log.error(f"❌ Повторная ошибка создания сообщения топика: {e}")
        return False
    log.warning(f"⚠️ Ошибка редактирования MSG_ID={_TOPIC_MAIN_MSG_ID} ({e}), пересоздаём...")
    _TOPIC_MAIN_MSG_ID = None
    save_topic_state(None)
    return await update_topic_message_payload(text, kb, _retry=True)


def should_skip_topic_update(
    lessons: list, now_dt: datetime, target_date: date, ignore_time_restriction: bool
) -> bool:
    """
    Проверяет, нужно ли пропустить публикацию расписания из-за раннего времени.
    """
    if lessons and is_too_early_to_publish(lessons, now_dt, target_date, ignore_time_restriction):
        log.info("sync_topic: too_early_to_publish, пропуск")
        return True
    return False


def process_today_reminders(lessons: list, now_dt: datetime, target_date: date) -> None:
    """
    Запускает проверку напоминаний для пар текущего дня.
    """
    if lessons and now_dt.date() == target_date:
        for l in lessons:
            check_and_trigger_reminder(l, now_dt, now_dt.date())


async def sync_topic_main_message(ignore_time_restriction: bool = False) -> bool:
    """
    Атомарно обновляет главное сообщение расписания в топике.
    """
    global _TOPIC_MAIN_MSG_ID
    if _TOPIC_MAIN_MSG_ID is None:
        _TOPIC_MAIN_MSG_ID = load_topic_state()

    now_dt = datetime.now(TIMEZONE)
    target_date = await resolve_target_date(now_dt, ignore_time_restriction)
    if not target_date:
        log.info("sync_topic: target_date=None, пропуск")
        return False

    lessons = await get_api_schedule_for_date(target_date)
    if should_skip_topic_update(lessons, now_dt, target_date, ignore_time_restriction):
        return False

    process_today_reminders(lessons, now_dt, target_date)
    text = format_day_schedule(target_date, lessons)
    kb = get_topic_inline_kb(lessons) if lessons else None
    return await update_topic_message_payload(text, kb)


_API_FAIL_START_TIME: Optional[datetime] = None
_API_ALERT_SENT: bool = False


async def notify_admin_about_api_down() -> None:
    """
    Отправляет экстренное уведомление администратору в ЛС при сбое внешних сервисов свыше 30 минут.
    """
    global _API_ALERT_SENT
    if _API_ALERT_SENT:
        return
    try:
        from config import ALLOWED_USER_ID
        msg = "⚠️ <b>ВНИМАНИЕ:</b> Внешний сервис расписания КТМУ или Яндекс Диск недоступен более 30 минут!"
        await bot.send_message(chat_id=ALLOWED_USER_ID, text=msg)
        _API_ALERT_SENT = True
        log.warning("Отправлено экстренное уведомление администратору о сбое API > 30 мин")
    except Exception as e:
        log.error(f"Не удалось отправить алерт администратору: {e}")


async def topic_sync_loop() -> None:
    """
    Фоновый цикл синхронизации топика каждые 60 секунд.
    """
    global _API_FAIL_START_TIME, _API_ALERT_SENT
    log.info("Запущен фоновый сервис авто-обновления расписания в топике Telegram (60 сек)")
    while True:
        try:
            await sync_topic_main_message()
            if _API_FAIL_START_TIME is not None:
                _API_FAIL_START_TIME = None
                _API_ALERT_SENT = False
                log.info("Соединение с внешними сервисами восстановлено.")
        except Exception as e:
            log.error(f"Ошибка в цикле topic_sync_loop: {e}")
            now = datetime.now(TIMEZONE)
            if _API_FAIL_START_TIME is None:
                _API_FAIL_START_TIME = now
            elif (now - _API_FAIL_START_TIME).total_seconds() >= 1800:
                await notify_admin_about_api_down()

        await asyncio.sleep(60)

