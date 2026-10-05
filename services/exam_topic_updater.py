"""
Модуль синхронизации и авто-обновления сообщения в топике 'Экзамены'.

Сохраняет состояние EXAM_MAIN_MSG_ID в data/exam_topic_state.json.
Автоматически формирует реестр экзаменов с точным расчётом дат проведения.
"""

import asyncio
import html
import json
import os
from datetime import date, datetime, timedelta
from typing import List, Optional
from aiogram.exceptions import TelegramBadRequest

from config import EXAM_TOPIC_THREAD_ID, TOPIC_CHAT_ID
from core.api_client import get_api_exams
from core.bot import bot
from core.logger import get_logger
from services.models import ExamItem

log = get_logger("exam_topic_updater")
STATE_FILE = "data/exam_topic_state.json"
DEFAULT_SEMESTER_START = datetime.strptime("2026-09-01", "%Y-%m-%d").date()

_EXAM_MAIN_MSG_ID: Optional[int] = None


async def get_effective_semester_start() -> date:
    """Определяет актуальную дату старта семестра из расписания КТМУ."""
    try:
        from services.schedule_parser import fetch_schedule_data
        data = await fetch_schedule_data(force_refresh=False)
        if data:
            s_str = data.get("config", {}).get("semesterStart")
            if s_str:
                return datetime.strptime(s_str, "%Y-%m-%d").date()
    except Exception as e:
        log.warning(f"Не удалось получить semesterStart для экзаменов: {e}")
    return DEFAULT_SEMESTER_START


from utils.storage import sync_atomic_save_json, sync_load_json


def load_exam_topic_state() -> Optional[int]:
    """
    Загружает ID главного сообщения топика экзаменов.
    """
    data = sync_load_json(STATE_FILE, default={})
    return data.get("main_msg_id") if isinstance(data, dict) else None


def save_exam_topic_state(msg_id: Optional[int]) -> None:
    """
    Атомарно сохраняет ID главного сообщения топика экзаменов.
    """
    sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})


def get_week_date_range_str(week_num: int, semester_start: Optional[date] = None) -> str:
    """Вычисляет диапазон дат для порядкового номера учебной недели."""
    start_d = semester_start or DEFAULT_SEMESTER_START
    start_sunday = start_d + timedelta(days=(6 - start_d.weekday()))
    if week_num == 1:
        return f"{start_d.strftime('%d.%m')}–{start_sunday.strftime('%d.%m')}"

    mon = start_sunday + timedelta(days=1) + timedelta(weeks=week_num - 2)
    sun = mon + timedelta(days=6)
    return f"{mon.strftime('%d.%m')}–{sun.strftime('%d.%m.%Y')}"


def format_exam_card(ex: ExamItem, semester_start: Optional[date] = None) -> str:
    """Формирует карточку аттестации/экзамена с HTML-экранированием."""
    if ex.weeks:
        date_ranges = [get_week_date_range_str(w, semester_start) for w in ex.weeks]
        weeks_str = f"{', '.join(map(str, ex.weeks))} нед. (🗓 <b>{', '.join(date_ranges)}</b>)"
    else:
        weeks_str = "Дата уточняется"

    sg_str = f" • 👥 Подгруппа {ex.subgroup}" if ex.subgroup > 0 else ""
    subj = html.escape(ex.subject)
    e_type = html.escape(ex.exam_type)
    teacher = html.escape(ex.teacher)
    addr = html.escape(ex.address)
    room = html.escape(ex.room)
    return (
        f"📌 <b>{subj}</b> ({e_type}){sg_str}\n"
        f"⏳ <b>Период сдачи:</b> {weeks_str}\n"
        f"👨‍🏫 <i>{teacher}</i>\n"
        f"{ex.format_str} • 🏢 {addr} ({room})"
    )



def format_exams_schedule_message(exams: List[ExamItem], semester_start: Optional[date] = None) -> str:
    """Форматирует расписание экзаменов и аттестаций в чистый HTML."""
    header = (
        "📑 <b>АТТЕСТАЦИИ И ЭКЗАМЕНЫ ГРУППЫ 1-КПД-3</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    if not exams:
        return header + "<i>Информация о зачётах и экзаменах формируется...</i> ☕️"

    blocks = [format_exam_card(ex, semester_start) for ex in exams]
    return header + "\n\n".join(blocks)


async def _pin_exam_silently(message_id: int) -> None:
    """Закрепляет сообщение экзаменов без уведомления."""
    try:
        await bot.pin_chat_message(
            chat_id=TOPIC_CHAT_ID, message_id=message_id,
            disable_notification=True
        )
    except Exception as e:
        log.warning(f"Не удалось закрепить exam MSG_ID={message_id}: {e}")


async def create_exam_message(text: str) -> int:
    """
    Создает и закрепляет главное сообщение в топике экзаменов.
    """
    msg = await bot.send_message(
        chat_id=TOPIC_CHAT_ID, message_thread_id=EXAM_TOPIC_THREAD_ID, text=text
    )
    save_exam_topic_state(msg.message_id)
    await _pin_exam_silently(msg.message_id)
    log.info(f"Сообщение экзаменов создано и закреплено: MSG_ID={msg.message_id}")
    return msg.message_id


async def handle_exam_edit_error(text: str, err_str: str, retry: bool) -> bool:
    """
    Обрабатывает ошибку редактирования сообщения топика экзаменов.
    """
    global _EXAM_MAIN_MSG_ID
    if "not modified" in err_str:
        log.debug(f"sync_exam_topic: 'not modified' — текст экзаменов уже актуален (MSG_ID={_EXAM_MAIN_MSG_ID})")
        return True
    if retry:
        log.error("❌ Повторная ошибка создания exam-сообщения")
        return False
    log.warning(f"⚠️ Ошибка редактирования exam MSG_ID={_EXAM_MAIN_MSG_ID}, пересоздаём...")
    _EXAM_MAIN_MSG_ID = None
    save_exam_topic_state(None)
    return await send_or_edit_exam_msg(text, _retry=True)


async def send_or_edit_exam_msg(text: str, _retry: bool = False) -> bool:
    """
    Отправляет или редактирует главное сообщение в топике экзаменов.
    """
    global _EXAM_MAIN_MSG_ID
    try:
        if _EXAM_MAIN_MSG_ID is None:
            _EXAM_MAIN_MSG_ID = await create_exam_message(text)
            return True
        await bot.edit_message_text(
            chat_id=TOPIC_CHAT_ID, message_id=_EXAM_MAIN_MSG_ID, text=text
        )
        log.info(f"✅ Сообщение экзаменов обновлено: MSG_ID={_EXAM_MAIN_MSG_ID}")
        return True
    except TelegramBadRequest as e:
        return await handle_exam_edit_error(text, str(e).lower(), _retry)
    except Exception as e:
        log.error(f"❌ Ошибка обновления топика экзаменов: {type(e).__name__}: {e}")
        return False


async def recreate_exam_topic_message() -> bool:
    """
    Удаляет текущее сообщение экзаменов и создаёт новое (сброс MSG_ID).

    :return: True если пересоздание прошло
    """
    global _EXAM_MAIN_MSG_ID
    old_id = _EXAM_MAIN_MSG_ID or load_exam_topic_state()
    if old_id:
        try:
            await bot.delete_message(chat_id=TOPIC_CHAT_ID, message_id=old_id)
            log.info(f"Старое exam-сообщение MSG_ID={old_id} удалено")
        except Exception as e:
            log.warning(f"Не удалось удалить exam MSG_ID={old_id}: {e}")
    _EXAM_MAIN_MSG_ID = None
    save_exam_topic_state(None)
    return await sync_exam_topic_message()


async def sync_exam_topic_message() -> bool:
    """
    Атомарно публикует или обновляет расписание экзаменов в топике.

    :return: True если обновлено
    """
    global _EXAM_MAIN_MSG_ID
    if _EXAM_MAIN_MSG_ID is None:
        _EXAM_MAIN_MSG_ID = load_exam_topic_state()

    exams = await get_api_exams()
    sem_start = await get_effective_semester_start()
    text = format_exams_schedule_message(exams, sem_start)
    try:
        return await send_or_edit_exam_msg(text)
    except Exception as e:
        log.error(f"Ошибка обновления топика экзаменов: {e}")
        return False


async def exam_topic_sync_loop() -> None:
    """
    Фоновый цикл авто-обновления топика Экзамены раз в 10 минут.
    """
    log.info("Запущен фоновый сервис авто-обновления топика Экзамены (10 мин)")
    while True:
        try:
            await sync_exam_topic_message()
        except Exception as e:
            log.error(f"Ошибка в цикле exam_topic_sync_loop: {e}")
        await asyncio.sleep(600)
