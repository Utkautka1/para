"""
Модуль синхронизации и авто-обновления сообщения в топике 'Экзамены'.

Сохраняет состояние EXAM_MAIN_MSG_ID в data/exam_topic_state.json.
Автоматически формирует реестр экзаменов с точным расчётом дат проведения.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional
from aiogram.exceptions import TelegramBadRequest

from config import EXAM_TOPIC_THREAD_ID, TOPIC_CHAT_ID
from core.bot import bot
from core.logger import get_logger
from services.exam_parser import ExamItem, get_group_exams

log = get_logger("exam_topic_updater")
STATE_FILE = "data/exam_topic_state.json"
SEMESTER_START = datetime.strptime("2026-09-01", "%Y-%m-%d").date()

_EXAM_MAIN_MSG_ID: Optional[int] = None


def load_exam_topic_state() -> Optional[int]:
    """
    Загружает ID главного сообщения топика экзаменов.
    """
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("main_msg_id")
        except Exception as e:
            log.error(f"Ошибка чтения exam_topic_state.json: {e}")
    return None


def save_exam_topic_state(msg_id: Optional[int]) -> None:
    """
    Сохраняет ID главного сообщения топика экзаменов.
    """
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"main_msg_id": msg_id}, f)
    except Exception as e:
        log.error(f"Ошибка записи exam_topic_state.json: {e}")


def get_week_date_range_str(week_num: int) -> str:
    """
    Вычисляет диапазон дат для порядкового номера учебной недели.
    """
    start_sunday = SEMESTER_START + timedelta(days=(6 - SEMESTER_START.weekday()))
    if week_num == 1:
        return f"{SEMESTER_START.strftime('%d.%m')}–{start_sunday.strftime('%d.%m')}"

    mon = start_sunday + timedelta(days=1) + timedelta(weeks=week_num - 2)
    sun = mon + timedelta(days=6)
    return f"{mon.strftime('%d.%m')}–{sun.strftime('%d.%m.%Y')}"


def format_exam_card(ex: ExamItem) -> str:
    """
    Формирует единичную карточку аттестации/экзамена.
    """
    if ex.weeks:
        date_ranges = [get_week_date_range_str(w) for w in ex.weeks]
        weeks_str = f"{', '.join(map(str, ex.weeks))} нед. (🗓 <b>{', '.join(date_ranges)}</b>)"
    else:
        weeks_str = "Дата уточняется"

    sg_str = f" • 👥 Подгруппа {ex.subgroup}" if ex.subgroup > 0 else ""
    return (
        f"📌 <b>{ex.subject}</b> ({ex.exam_type}){sg_str}\n"
        f"⏳ <b>Период сдачи:</b> {weeks_str}\n"
        f"👨‍🏫 <i>{ex.teacher}</i>\n"
        f"{ex.format_str} • 🏢 {ex.address} ({ex.room})"
    )


def format_exams_schedule_message(exams: List[ExamItem]) -> str:
    """
    Форматирует расписание экзаменов и аттестаций в чистый HTML.
    """
    header = (
        "📑 <b>АТТЕСТАЦИИ И ЭКЗАМЕНЫ ГРУППЫ 1-КПД-3</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    if not exams:
        return header + "<i>Информация о зачётах и экзаменах формируется...</i> ☕️"

    blocks = [format_exam_card(ex) for ex in exams]
    return header + "\n\n".join(blocks)


async def send_or_edit_exam_msg(text: str) -> None:
    """
    Отправляет или редактирует главное сообщение в топике экзаменов.
    """
    global _EXAM_MAIN_MSG_ID
    try:
        if _EXAM_MAIN_MSG_ID is None:
            msg = await bot.send_message(
                chat_id=TOPIC_CHAT_ID, message_thread_id=EXAM_TOPIC_THREAD_ID, text=text
            )
            _EXAM_MAIN_MSG_ID = msg.message_id
            save_exam_topic_state(_EXAM_MAIN_MSG_ID)
            log.info(f"Главное сообщение создано в топике Экзамены: MSG_ID={_EXAM_MAIN_MSG_ID}")
        else:
            await bot.edit_message_text(
                chat_id=TOPIC_CHAT_ID, message_id=_EXAM_MAIN_MSG_ID, text=text
            )
            log.debug(f"Сообщение в топике Экзамены обновлено: MSG_ID={_EXAM_MAIN_MSG_ID}")
    except TelegramBadRequest as e:
        if "message to edit not found" in str(e).lower():
            _EXAM_MAIN_MSG_ID = None
            save_exam_topic_state(None)


async def sync_exam_topic_message() -> None:
    """
    Атомарно публикует или обновляет расписание экзаменов в топике.
    """
    global _EXAM_MAIN_MSG_ID
    if _EXAM_MAIN_MSG_ID is None:
        _EXAM_MAIN_MSG_ID = load_exam_topic_state()

    exams = await get_group_exams()
    text = format_exams_schedule_message(exams)
    try:
        await send_or_edit_exam_msg(text)
    except Exception as e:
        log.error(f"Ошибка обновления топика экзаменов: {e}")


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
