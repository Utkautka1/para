"""
Модуль аккуратных Inline-клавиатур навигации.

Создает компактные кнопки управления и ссылки для подключения к парам в один ряд.
"""

from typing import List, Optional
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.schedule_parser import Lesson


def build_zoom_copy_row(lessons: List[Lesson]) -> List[InlineKeyboardButton]:
    """
    Создает зелёные кнопки быстрой подстановки ID/пароля в кликборд Telegram.

    :param lessons: Список пар
    :return: Ряд кнопок
    """
    row = []
    for l in lessons:
        if l.is_remote:
            if l.remote_meeting_id:
                row.append(InlineKeyboardButton(text=f"📋 ID: {l.remote_meeting_id}", callback_data=f"copy:{l.remote_meeting_id}", style="success"))
            if l.remote_passcode:
                row.append(InlineKeyboardButton(text=f"🔑 Код: {l.remote_passcode}", callback_data=f"copy:{l.remote_passcode}", style="success"))
    return row


def get_schedule_inline_kb(
    lessons: Optional[List[Lesson]] = None,
    week_offset: int = 0
) -> InlineKeyboardMarkup:
    """
    Генерирует продвинутую инлайн-клавиатуру навигации с зелеными акцентами.

    :param lessons: Список пар на день
    :param week_offset: Смещение недели (0 = текущая, 1 = следующая)
    :return: InlineKeyboardMarkup
    """
    rows = []

    if lessons:
        link_btns = []
        for l in lessons:
            if l.is_remote and l.remote_link:
                url = next((w for w in l.remote_link.split() if w.startswith("http")), None)
                if url:
                    link_btns.append(InlineKeyboardButton(text=f"🔗 {l.period + 1}-я пара", url=url, style="success"))
        if link_btns:
            rows.append(link_btns)

        copy_row = build_zoom_copy_row(lessons)
        if copy_row:
            rows.append(copy_row)

    rows.append([
        InlineKeyboardButton(text="📅 Сегодня", callback_data="sched:today", style="success"),
        InlineKeyboardButton(text="📆 Завтра", callback_data="sched:tomorrow")
    ])

    if week_offset == 0:
        week_btn = InlineKeyboardButton(text="⏭ Неделя (След.)", callback_data="sched:week_next")
    else:
        week_btn = InlineKeyboardButton(text="⏮ Неделя (Тек.)", callback_data="sched:week")

    rows.append([
        week_btn,
        InlineKeyboardButton(text="🔄 Обновить", callback_data="sched:refresh")
    ])
    rows.append([
        InlineKeyboardButton(text="⚙️ Панель управления (Админ)", callback_data="admin:menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_topic_inline_kb(lessons: Optional[List[Lesson]] = None) -> InlineKeyboardMarkup:
    """
    Генерирует чистую зелёную инлайн-клавиатуру исключительно для топика группы.

    :param lessons: Список пар на день
    :return: InlineKeyboardMarkup
    """
    rows = []

    if lessons:
        link_btns = []
        for l in lessons:
            if l.is_remote and l.remote_link:
                url = next((w for w in l.remote_link.split() if w.startswith("http")), None)
                if url:
                    sg = f" (Подгруппа {l.subgroup})" if l.subgroup > 0 else ""
                    link_btns.append(InlineKeyboardButton(text=f"🔗 {l.period + 1}-я пара{sg}", url=url, style="success"))
        if link_btns:
            rows.append(link_btns)

        copy_row = build_zoom_copy_row(lessons)
        if copy_row:
            rows.append(copy_row)

    return InlineKeyboardMarkup(inline_keyboard=rows)
