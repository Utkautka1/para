"""
Unit-тесты точечной отметки одного студента в посещаемости.

Проверяет:
  1. Генерацию клавиатур выбора режима, списка студентов и отметок
  2. Текстовые шаблоны карточек и подтверждений
  3. Хэндлеры выбора режима, меню студентов, карточки и установки отметки
  4. Оптимистичное обновление статистики при сбросе/изменении отметки
"""

from unittest.mock import AsyncMock, patch

import pytest
from aiogram.types import User

from bot.handlers.admin.attendance import (
    _build_single_session,
    cb_lesson_mode,
    cb_pick_student,
    cb_set_single_mark,
    cb_single_student_menu,
    notify_partner_about_single_update,
)
from bot.templates.admin.attendance import (
    format_partner_single_report,
    format_single_student_card,
    format_single_update_confirm,
    get_lesson_mode_kb,
    get_single_mark_confirmed_kb,
    get_single_student_select_kb,
    get_student_mark_choice_kb,
)
from services.attendance_stats import _update_session_marks_in_stats


def test_get_lesson_mode_kb_structure() -> None:
    """Проверяет структуру клавиатуры выбора режима пары."""
    kb = get_lesson_mode_kb("2026-11-21", 2)
    assert len(kb.inline_keyboard) == 3
    assert kb.inline_keyboard[0][0].callback_data == "att:start:2026-11-21:2"
    assert kb.inline_keyboard[1][0].callback_data == "att:sngl:2026-11-21:2"
    assert kb.inline_keyboard[2][0].callback_data == "att:day:2026-11-21"


def test_get_single_student_select_kb_layout() -> None:
    """Проверяет группировку студентов по 2 в ряд и метки с текущим статусом."""
    students = [(5, "Базаров Аюр Этигэлович"), (6, "Барчугова Ева Алексеевна"), (7, "Васильев Василий")]
    saved_marks = {"5": "П"}
    kb = get_single_student_select_kb(students, saved_marks, "2026-11-21", 1)
    # 2 кнопки в 1 ряду, 1 кнопка во 2 ряду, 1 кнопка 'Назад' в 3 ряду
    assert len(kb.inline_keyboard) == 3
    assert len(kb.inline_keyboard[0]) == 2
    assert "Базаров Аюр [П]" in kb.inline_keyboard[0][0].text
    assert kb.inline_keyboard[0][0].callback_data == "att:p:2026-11-21:1:5"
    assert "Барчугова Ева" in kb.inline_keyboard[0][1].text
    assert "[" not in kb.inline_keyboard[0][1].text
    assert kb.inline_keyboard[2][0].callback_data == "att:mode:2026-11-21:1"


def test_get_student_mark_choice_kb_options() -> None:
    """Проверяет наличие всех статусов (П, О, У, Н) и кнопки сброса."""
    kb = get_student_mark_choice_kb("2026-11-21", 1, 5)
    assert len(kb.inline_keyboard) == 4
    assert kb.inline_keyboard[0][0].callback_data == "att:set:2026-11-21:1:5:П"
    assert kb.inline_keyboard[0][1].callback_data == "att:set:2026-11-21:1:5:О"
    assert kb.inline_keyboard[1][0].callback_data == "att:set:2026-11-21:1:5:У"
    assert kb.inline_keyboard[1][1].callback_data == "att:set:2026-11-21:1:5:Н"
    assert kb.inline_keyboard[2][0].callback_data == "att:set:2026-11-21:1:5:_"


def test_get_single_mark_confirmed_kb_options() -> None:
    """Проверяет кнопки подтверждения после обновления отметки."""
    kb = get_single_mark_confirmed_kb("2026-11-21", 1)
    assert len(kb.inline_keyboard) == 3
    assert kb.inline_keyboard[0][0].callback_data == "att:sngl:2026-11-21:1"
    assert kb.inline_keyboard[1][0].callback_data == "att:day:2026-11-21"
    assert kb.inline_keyboard[2][0].callback_data == "att:close"


def test_format_single_templates() -> None:
    """Проверяет форматирование карточки, подтверждения и отчета напарнику."""
    card = format_single_student_card("Базаров Аюр", "2026-11-21", 1, "БЖД", "Н")
    assert "Базаров Аюр" in card
    assert "[Н]" in card

    confirm = format_single_update_confirm("Базаров Аюр", "2026-11-21", 1, "БЖД", "П")
    assert "Базаров Аюр" in confirm
    assert "[П]" in confirm

    report = format_partner_single_report("Базаров Аюр", "2026-11-21", 1, "БЖД", "У", "Староста")
    assert "Староста" in report
    assert "[У]" in report


@pytest.mark.asyncio
async def test_cb_lesson_mode_handler() -> None:
    """Проверяет отображение меню выбора режима пары."""
    cb = AsyncMock()
    cb.data = "att:mode:2026-11-21:2"
    cb.message = AsyncMock()
    with patch("bot.handlers.admin.attendance._resolve_lesson_title_for_start", return_value="Философия"):
        await cb_lesson_mode(cb)
    cb.message.edit_text.assert_awaited_once()
    assert "Философия" in cb.message.edit_text.call_args[0][0]


@pytest.mark.asyncio
async def test_cb_single_student_menu_handler() -> None:
    """Проверяет отображение меню со списком студентов."""
    cb = AsyncMock()
    cb.data = "att:sngl:2026-11-21:2"
    cb.message = AsyncMock()
    students = [(5, "Базаров Аюр"), (6, "Барчугова Ева")]
    with (
        patch("bot.handlers.admin.attendance.fetch_target_students", return_value=students),
        patch("bot.handlers.admin.attendance.get_saved_lesson_marks", return_value={"5": "Н"}),
    ):
        await cb_single_student_menu(cb)
    cb.message.edit_text.assert_awaited_once()
    assert "Выберите студента" in cb.message.edit_text.call_args[0][0]


@pytest.mark.asyncio
async def test_cb_pick_student_handler() -> None:
    """Проверяет открытие карточки конкретного студента для выбора отметки."""
    cb = AsyncMock()
    cb.data = "att:p:2026-11-21:2:5"
    cb.message = AsyncMock()
    students = [(5, "Базаров Аюр")]
    with (
        patch("bot.handlers.admin.attendance.fetch_target_students", return_value=students),
        patch("bot.handlers.admin.attendance._resolve_lesson_title_for_start", return_value="БЖД"),
        patch("bot.handlers.admin.attendance.get_saved_lesson_marks", return_value={"5": "О"}),
    ):
        await cb_pick_student(cb)
    cb.message.edit_text.assert_awaited_once()
    assert "Базаров Аюр" in cb.message.edit_text.call_args[0][0]
    assert "[О]" in cb.message.edit_text.call_args[0][0]


@pytest.mark.asyncio
async def test_cb_set_single_mark_handler() -> None:
    """Проверяет установку отметки, вызов оптимистичного обновления и подтверждение."""
    cb = AsyncMock()
    cb.data = "att:set:2026-11-21:2:5:П"
    cb.from_user = User(id=123, is_bot=False, first_name="Admin", full_name="Admin Admin")
    cb.message = AsyncMock()
    students = [(5, "Базаров Аюр")]
    with (
        patch("bot.handlers.admin.attendance.fetch_target_students", return_value=students),
        patch("bot.handlers.admin.attendance._resolve_lesson_title_for_start", return_value="БЖД"),
        patch("bot.handlers.admin.attendance.apply_session_optimistic_update", new=AsyncMock()) as mock_opt,
        patch("bot.handlers.admin.attendance.spawn") as mock_spawn,
    ):
        await cb_set_single_mark(cb)
    mock_opt.assert_awaited_once()
    assert mock_spawn.call_count == 3
    cb.message.edit_text.assert_awaited_once()
    assert "Отметка обновлена" in cb.message.edit_text.call_args[0][0]


@pytest.mark.asyncio
async def test_notify_partner_about_single_update() -> None:
    """Проверяет отправку сообщения напарнику об изменении отметки."""
    session = _build_single_session("2026-11-21", 1, "БЖД", [(5, "Базаров Аюр")], 5, "П", 123)
    with (
        patch("bot.handlers.admin.attendance.get_partner_admin_id", return_value=456),
        patch("bot.handlers.admin.attendance.bot.send_message", new=AsyncMock()) as mock_send,
    ):
        await notify_partner_about_single_update(session, "Базаров Аюр", "П", 123, "Starosta")
        mock_send.assert_awaited_once()
        assert "Базаров Аюр" in mock_send.call_args[0][1]


def test_update_session_marks_in_stats_with_cleared_mark() -> None:
    """Проверяет корректное уменьшение счетчика при сбросе отметки."""
    session = _build_single_session("2026-11-21", 1, "БЖД", [(5, "Базаров Аюр")], 5, "", 123)
    saved_marks = {"5": "Н"}
    stats = {"Базаров Аюр": {"total": {"П": 1, "О": 0, "У": 0, "Н": 1}}}
    new_saved = _update_session_marks_in_stats(session, saved_marks, stats)
    assert "5" not in new_saved
    assert stats["Базаров Аюр"]["total"]["Н"] == 0
