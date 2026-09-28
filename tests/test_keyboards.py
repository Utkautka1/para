"""
Unit-тесты модуля генерации клавиатур Telegram (bot/templates/user/keyboards.py).

Проверяет:
  1. Форматирование текста кнопок дистанционных занятий (format_lesson_button_text)
  2. Группировку кнопок по 2 в ряд (chunk_link_buttons) и извлечение URL
  3. Построение навигационных кнопок в зависимости от смещения недели (_build_nav_rows)
  4. Генерацию полных клавиатур для ЛС и топиков (get_schedule_inline_kb, get_topic_inline_kb)
"""

from typing import List
import pytest
from aiogram.types import InlineKeyboardButton

from bot.templates.user.keyboards import (
    _build_nav_rows,
    chunk_link_buttons,
    format_lesson_button_text,
    get_schedule_inline_kb,
    get_topic_inline_kb,
)
from services.models import Lesson


def make_test_lesson(period: int = 0, subgroup: int = 0, is_remote: bool = False, link: str = None) -> Lesson:
    """Вспомогательная функция для создания объекта Lesson."""
    return Lesson(
        period=period,
        time_str="08:30-10:00",
        subject="Предмет",
        lesson_type="Лекция",
        teacher="Преподаватель",
        is_remote=is_remote,
        room="101",
        address="Цветочная",
        subgroup=subgroup,
        remote_link=link,
    )


@pytest.mark.parametrize(
    "period,subgroup,expected",
    [
        (0, 0, "🔗 1-я пара"),
        (1, 1, "🔗 2-я пара (П/Г 1)"),
        (2, 2, "🔗 3-я пара (П/Г 2)"),
        (3, 0, "🔗 4-я пара"),
        (4, 1, "🔗 5-я пара (П/Г 1)"),
    ],
)
def test_format_lesson_button_text_matrix(period: int, subgroup: int, expected: str) -> None:
    """Проверяет формирование надписей кнопок с номером пары и подгруппой."""
    lesson = make_test_lesson(period=period, subgroup=subgroup)
    assert format_lesson_button_text(lesson) == expected


def test_chunk_link_buttons_empty_and_offline() -> None:
    """Проверяет отсутствие кнопок для пустых списков и очных пар."""
    assert chunk_link_buttons([]) == []
    offline_lessons = [make_test_lesson(period=0, is_remote=False)]
    assert chunk_link_buttons(offline_lessons) == []


@pytest.mark.parametrize(
    "links_count,expected_rows,expected_row_lengths",
    [
        (1, 1, [1]),
        (2, 1, [2]),
        (3, 2, [2, 1]),
        (4, 2, [2, 2]),
        (5, 3, [2, 2, 1]),
    ],
)
def test_chunk_link_buttons_grouping(links_count: int, expected_rows: int, expected_row_lengths: List[int]) -> None:
    """Проверяет разбивку кнопок максимум по 2 в ряду."""
    lessons = [
        make_test_lesson(period=i, is_remote=True, link=f"https://zoom.us/j/{i}")
        for i in range(links_count)
    ]
    rows = chunk_link_buttons(lessons)
    assert len(rows) == expected_rows
    assert [len(r) for r in rows] == expected_row_lengths


def test_chunk_link_buttons_extracts_http_url() -> None:
    """Проверяет извлечение URL из составной строки с описанием."""
    lesson = make_test_lesson(
        period=0,
        is_remote=True,
        link="Подключение через браузер: https://telemost.yandex.ru/j/999 (код 123)",
    )
    rows = chunk_link_buttons([lesson])
    assert len(rows) == 1
    assert rows[0][0].url == "https://telemost.yandex.ru/j/999"


@pytest.mark.parametrize(
    "week_offset,expected_btn_text,expected_callback",
    [
        (0, "⏭ Неделя (След.)", "sched:week_next"),
        (1, "⏮ Неделя (Тек.)", "sched:week"),
    ],
)
def test_build_nav_rows_week_offset(week_offset: int, expected_btn_text: str, expected_callback: str) -> None:
    """Проверяет переключение кнопки недели при разном смещении."""
    rows = _build_nav_rows(week_offset)
    week_btn = rows[1][0]
    assert week_btn.text == expected_btn_text
    assert week_btn.callback_data == expected_callback


def test_get_topic_inline_kb_behavior() -> None:
    """Проверяет возвращаемое значение для клавиатуры топика (только ссылки или None)."""
    assert get_topic_inline_kb(None) is None
    assert get_topic_inline_kb([]) is None
    assert get_topic_inline_kb([make_test_lesson(is_remote=False)]) is None

    remote_lesson = make_test_lesson(is_remote=True, link="https://zoom.us/j/123")
    kb = get_topic_inline_kb([remote_lesson])
    assert kb is not None
    assert len(kb.inline_keyboard) == 1
    assert kb.inline_keyboard[0][0].url == "https://zoom.us/j/123"


def test_get_schedule_inline_kb_contains_navigation() -> None:
    """Проверяет присутствие навигационных кнопок в главной клавиатуре."""
    kb = get_schedule_inline_kb([], week_offset=0)
    all_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "sched:today" in all_callbacks
    assert "sched:tomorrow" in all_callbacks
    assert "sched:week_next" in all_callbacks
    assert "sched:refresh" in all_callbacks
    assert "admin:menu" in all_callbacks
