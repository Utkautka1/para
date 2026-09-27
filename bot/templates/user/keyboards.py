"""
Модуль аккуратных Inline-клавиатур навигации.

Создает компактные кнопки управления и ссылки для подключения к парам.
Ссылки группируются максимум по 2 в ряд для аккуратного отображения в топике.
"""

from typing import List, Optional
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.schedule_parser import Lesson


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
                btns.append(InlineKeyboardButton(
                    text=format_lesson_button_text(l),
                    url=url,
                    style="success"
                ))
    return [btns[i:i + 2] for i in range(0, len(btns), 2)]


def _build_nav_rows(week_offset: int) -> List[List[InlineKeyboardButton]]:
    """Формирует основные кнопки навигации по календарю и неделям со стилями."""
    week_btn = (
        InlineKeyboardButton(text="⏭ Неделя (След.)", callback_data="sched:week_next", style="primary")
        if week_offset == 0
        else InlineKeyboardButton(text="⏮ Неделя (Тек.)", callback_data="sched:week", style="primary")
    )
    return [
        [
            InlineKeyboardButton(text="📅 Сегодня", callback_data="sched:today", style="success"),
            InlineKeyboardButton(text="📆 Завтра", callback_data="sched:tomorrow", style="success")
        ],
        [
            week_btn,
            InlineKeyboardButton(text="🔄 Обновить", callback_data="sched:refresh", style="primary")
        ],
        [InlineKeyboardButton(text="⚙️ Панель управления (Админ)", callback_data="admin:menu", style="danger")]
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


def get_topic_inline_kb(lessons: Optional[List[Lesson]] = None) -> Optional[InlineKeyboardMarkup]:
    """
    Генерирует чистую инлайн-клавиатуру исключительно для топика группы.

    Содержит только ссылки на дистанционные пары без громоздких кнопок копирования.

    :param lessons: Список пар на день
    :return: InlineKeyboardMarkup или None
    """
    if not lessons:
        return None
    rows = chunk_link_buttons(lessons)
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None
