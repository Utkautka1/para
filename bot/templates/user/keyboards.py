"""
Модуль аккуратных Inline-клавиатур навигации.

Создает компактные кнопки управления и ссылки для подключения к парам.
Использует нативный CopyTextButton для мгновенного копирования ID/паролей в буфер обмена.
"""

from typing import List, Optional
from aiogram.types import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup
from services.schedule_parser import Lesson


def build_zoom_copy_row(lessons: List[Lesson]) -> List[InlineKeyboardButton]:
    """
    Создает кнопки нативного копирования ID и пароля встречи в буфер обмена.

    :param lessons: Список пар
    :return: Ряд кнопок
    """
    row = []
    for l in lessons:
        if not l.is_remote:
            continue
        if l.remote_meeting_id:
            btn = InlineKeyboardButton(
                text=f"📋 ID: {l.remote_meeting_id}",
                copy_text=CopyTextButton(text=str(l.remote_meeting_id))
            )
            row.append(btn)
        if l.remote_passcode:
            btn = InlineKeyboardButton(
                text=f"🔑 Код: {l.remote_passcode}",
                copy_text=CopyTextButton(text=str(l.remote_passcode))
            )
            row.append(btn)
    return row


def format_lesson_button_text(lesson: Lesson) -> str:
    """
    Формирует лаконичный текст кнопки подключения к дистанционной паре.

    :param lesson: Объект занятия
    :return: Текст для Inline-кнопки
    """
    sg = f" (П/Г {lesson.subgroup})" if lesson.subgroup > 0 else ""
    return f"🔗 {lesson.period + 1}-я пара{sg}"


def chunk_link_buttons(lessons: List[Lesson]) -> List[List[InlineKeyboardButton]]:
    """
    Разбивает кнопки ссылок на дистанционные пары по 2 кнопки в ряд.

    :param lessons: Список предметов
    :return: Двумерный список кнопок
    """
    btns = []
    for l in lessons:
        if l.is_remote and l.remote_link:
            url = next((w for w in l.remote_link.split() if w.startswith("http")), None)
            if url:
                btns.append(InlineKeyboardButton(text=format_lesson_button_text(l), url=url))
    return [btns[i:i + 2] for i in range(0, len(btns), 2)]


def _build_nav_rows(week_offset: int) -> List[List[InlineKeyboardButton]]:
    """Формирует основные кнопки навигации по календарю и неделям."""
    week_btn = (
        InlineKeyboardButton(text="⏭ Неделя (След.)", callback_data="sched:week_next")
        if week_offset == 0
        else InlineKeyboardButton(text="⏮ Неделя (Тек.)", callback_data="sched:week")
    )
    return [
        [
            InlineKeyboardButton(text="📅 Сегодня", callback_data="sched:today"),
            InlineKeyboardButton(text="📆 Завтра", callback_data="sched:tomorrow")
        ],
        [week_btn, InlineKeyboardButton(text="🔄 Обновить", callback_data="sched:refresh")],
        [InlineKeyboardButton(text="⚙️ Панель управления (Админ)", callback_data="admin:menu")]
    ]


def get_schedule_inline_kb(
    lessons: Optional[List[Lesson]] = None,
    week_offset: int = 0
) -> InlineKeyboardMarkup:
    """
    Генерирует продвинутую инлайн-клавиатуру навигации.

    :param lessons: Список пар на день
    :param week_offset: Смещение недели (0 = текущая, 1 = следующая)
    :return: InlineKeyboardMarkup
    """
    rows = []
    if lessons:
        rows.extend(chunk_link_buttons(lessons))
    rows.extend(_build_nav_rows(week_offset))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_topic_inline_kb(lessons: Optional[List[Lesson]] = None) -> InlineKeyboardMarkup:
    """
    Генерирует чистую инлайн-клавиатуру исключительно для топика группы.

    :param lessons: Список пар на день
    :return: InlineKeyboardMarkup
    """
    rows = []
    if lessons:
        rows.extend(chunk_link_buttons(lessons))
        copy_row = build_zoom_copy_row(lessons)
        if copy_row:
            rows.append(copy_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)
