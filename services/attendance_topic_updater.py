"""
Модуль синхронизации и авто-обновления сообщения в топике 'Посещаемость'.

Отвечает за:
  1. Публикацию и закрепление сводного реестра группы с подсчетом П/О/У/Н
  2. Поддержание актуального счётчика за все месяцы (сентябрь - декабрь)
  3. Сохранение идентификатора сообщения в data/attendance_topic_state.json
  4. Фоновый цикл авто-обновления и ручной сброс/пересоздание из админки
"""

import asyncio
from datetime import datetime
import html
from typing import Any, Dict, Optional
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import ATTENDANCE_TOPIC_THREAD_ID, TIMEZONE, TOPIC_CHAT_ID
from core.bot import bot
from core.logger import get_logger
from services.attendance_stats import fetch_all_time_attendance
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("att_topic_updater")
STATE_FILE = "data/attendance_topic_state.json"
_ATT_MAIN_MSG_ID: Optional[int] = None


def load_attendance_topic_state() -> Optional[int]:
    """Загружает сохраненный ID главного сообщения топика посещаемости."""
    data = sync_load_json(STATE_FILE, default={})
    return data.get("main_msg_id") if isinstance(data, dict) else None


def save_attendance_topic_state(msg_id: Optional[int]) -> None:
    """Атомарно сохраняет ID главного сообщения топика посещаемости."""
    sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})


def get_attendance_topic_kb() -> InlineKeyboardMarkup:
    """Формирует клавиатуру с кнопкой принудительного обновления сводки."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔄 Обновить сводку", callback_data="att_topic:refresh")
    ]])


def format_student_line(idx: int, fio: str, counts: Dict[str, int]) -> str:
    """Формирует строку студента со счётчиками П/О/У/Н за всё время."""
    p_cnt = counts.get("П", 0)
    o_cnt = counts.get("О", 0)
    u_cnt = counts.get("У", 0)
    n_cnt = counts.get("Н", 0)
    clean_fio = html.escape(fio)
    return (
        f"<code>{idx:02d}.</code> <b>{clean_fio}</b> — "
        f"✅ {p_cnt} | ⏰ {o_cnt} | 📋 {u_cnt} | ❌ {n_cnt}"
    )


def _build_attendance_header(total: int, updated_str: str) -> str:
    """Формирует шапку и легенду сводного сообщения посещаемости."""
    return (
        "📊 <b>СВОДНЫЙ РЕЕСТР ПОСЕЩАЕМОСТИ (1-КПД-3)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📅 <b>Период:</b> Сентябрь — Декабрь (Все месяцы)\n"
        f"👥 <b>Студентов в реестре:</b> {total}\n"
        f"🕒 <b>Обновлено:</b> {updated_str} МСК\n\n"
        "<b>Обозначения:</b>\n"
        "• <b>П</b> (✅) — Присутствовал\n"
        "• <b>О</b> (⏰) — Опоздал\n"
        "• <b>У</b> (📋) — Уважительная причина\n"
        "• <b>Н</b> (❌) — Неуважительная причина\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )


def format_attendance_topic_message(stats: Dict[str, Dict[str, Any]]) -> str:
    """Форматирует полный текст сообщения с общим списком группы и счётчиками."""
    now_str = datetime.now(TIMEZONE).strftime("%d.%m.%Y в %H:%M")
    if not stats:
        header = _build_attendance_header(0, now_str)
        return header + "<i>Данные журнала посещаемости загружаются...</i> ⏳"
    header = _build_attendance_header(len(stats), now_str)
    sorted_items = sorted(stats.items(), key=lambda x: x[0])
    lines = [
        format_student_line(i, fio, item.get("total", {}))
        for i, (fio, item) in enumerate(sorted_items, 1)
    ]
    footer = (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Счётчик суммирует все отметки из таблицы с начала учебного года. "
        "Свою статистику можно узнать через /my_attendance в ЛС бота.</i>"
    )
    return header + "\n".join(lines) + footer


async def _pin_attendance_silently(message_id: int) -> None:
    """Закрепляет главное сообщение реестра в топике без звукового уведомления."""
    try:
        await bot.pin_chat_message(
            chat_id=TOPIC_CHAT_ID, message_id=message_id,
            disable_notification=True
        )
    except Exception as e:
        log.warning(f"Не удалось закрепить attendance MSG_ID={message_id}: {e}")


async def create_attendance_message(text: str, kb: InlineKeyboardMarkup) -> int:
    """Создает и закрепляет главное сообщение в топике посещаемости."""
    msg = await bot.send_message(
        chat_id=TOPIC_CHAT_ID,
        message_thread_id=ATTENDANCE_TOPIC_THREAD_ID,
        text=text,
        reply_markup=kb,
    )
    save_attendance_topic_state(msg.message_id)
    await _pin_attendance_silently(msg.message_id)
    log.info(f"Сообщение реестра посещаемости создано: MSG_ID={msg.message_id}")
    return msg.message_id


async def handle_attendance_edit_error(
    text: str, kb: InlineKeyboardMarkup, err_str: str, retry: bool
) -> bool:
    """Обрабатывает ошибки обновления сообщения в топике (not modified / удалено)."""
    global _ATT_MAIN_MSG_ID
    if "not modified" in err_str:
        log.debug(f"sync_att_topic: 'not modified' — реестр уже актуален ({_ATT_MAIN_MSG_ID})")
        return True
    if retry:
        log.error("❌ Повторная ошибка создания attendance-сообщения")
        return False
    log.warning(f"⚠️ Ошибка редактирования attendance MSG_ID={_ATT_MAIN_MSG_ID}, пересоздаём...")
    _ATT_MAIN_MSG_ID = None
    save_attendance_topic_state(None)
    return await send_or_edit_attendance_msg(text, kb, _retry=True)


async def send_or_edit_attendance_msg(
    text: str, kb: InlineKeyboardMarkup, _retry: bool = False
) -> bool:
    """Отправляет или обновляет главное сообщение в топике посещаемости."""
    global _ATT_MAIN_MSG_ID
    try:
        if _ATT_MAIN_MSG_ID is None:
            _ATT_MAIN_MSG_ID = await create_attendance_message(text, kb)
            return True
        await bot.edit_message_text(
            chat_id=TOPIC_CHAT_ID,
            message_id=_ATT_MAIN_MSG_ID,
            text=text,
            reply_markup=kb,
        )
        log.info(f"✅ Реестр посещаемости обновлен: MSG_ID={_ATT_MAIN_MSG_ID}")
        return True
    except TelegramBadRequest as e:
        return await handle_attendance_edit_error(text, kb, str(e).lower(), _retry)
    except Exception as e:
        log.error(f"❌ Ошибка обновления реестра посещаемости: {type(e).__name__}: {e}")
        return False


async def recreate_attendance_topic_message() -> bool:
    """Удаляет старое сообщение топика посещаемости и создаёт новое."""
    global _ATT_MAIN_MSG_ID
    old_id = _ATT_MAIN_MSG_ID or load_attendance_topic_state()
    if old_id:
        try:
            await bot.delete_message(chat_id=TOPIC_CHAT_ID, message_id=old_id)
            log.info(f"Старое attendance-сообщение MSG_ID={old_id} удалено")
        except Exception as e:
            log.warning(f"Не удалось удалить attendance MSG_ID={old_id}: {e}")
    _ATT_MAIN_MSG_ID = None
    save_attendance_topic_state(None)
    return await sync_attendance_topic_message(force_refresh=True)


async def sync_attendance_topic_message(force_refresh: bool = False) -> bool:
    """Синхронизирует данные из таблицы и обновляет сообщение в топике."""
    global _ATT_MAIN_MSG_ID
    if _ATT_MAIN_MSG_ID is None:
        _ATT_MAIN_MSG_ID = load_attendance_topic_state()
    try:
        stats = await fetch_all_time_attendance(force_refresh=force_refresh)
        text = format_attendance_topic_message(stats)
        kb = get_attendance_topic_kb()
        return await send_or_edit_attendance_msg(text, kb)
    except Exception as e:
        log.error(f"Ошибка синхронизации реестра посещаемости: {e}")
        return False


async def attendance_topic_sync_loop() -> None:
    """Фоновый цикл авто-обновления топика посещаемости каждые 15 минут."""
    log.info("Запущен фоновый сервис авто-обновления топика Посещаемость (15 мин)")
    while True:
        try:
            await sync_attendance_topic_message(force_refresh=False)
        except Exception as e:
            log.error(f"Ошибка в цикле attendance_topic_sync_loop: {e}")
        await asyncio.sleep(900)
