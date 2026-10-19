"""
Unit-тесты для комплексной проверки и исправления бизнес-логики бота.

Проверяет:
  1. Ограничение отправки поздравлений с ДР строго с 07:00 МСК
  2. Изоляцию сессии посещаемости и запрет гонки между старостами
  3. Ручную привязку Telegram ID для студентов без username
  4. Динамический расчет дат экзаменов с учетом старта семестра
  5. Справку /help и дружелюбный UX для авторизованных студентов в ЛС
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, User

from bot.handlers.admin.attendance import check_session_ownership, get_initiator_title
from bot.handlers.user.schedule import format_help_text
from config import ALLOWED_USER_ID, DEPUTY_USER_ID, TIMEZONE
from services.attendance_manager import AttendanceSession, create_attendance_session
from services.birthday_manager import (
    check_and_send_birthday_congratulations,
    is_morning_congrats_time,
)
from services.classmates_auth import bind_student_tg_id
from services.exam_topic_updater import get_week_date_range_str


def test_is_morning_congrats_time() -> None:
    """Проверяет блокировку ночных поздравлений до 07:00 МСК."""
    night_time = datetime(2026, 10, 5, 3, 30, tzinfo=TIMEZONE)
    morning_time = datetime(2026, 10, 5, 7, 0, tzinfo=TIMEZONE)
    day_time = datetime(2026, 10, 5, 12, 15, tzinfo=TIMEZONE)

    assert is_morning_congrats_time(night_time) is False
    assert is_morning_congrats_time(morning_time) is True
    assert is_morning_congrats_time(day_time) is True


@pytest.mark.asyncio
async def test_congrats_blocked_before_seven_am() -> None:
    """Проверяет, что ночью поздравления не уходят в топик."""
    items = [{"full_name": "Иванов Иван", "is_today": True}]
    fake_night = datetime(2026, 10, 5, 2, 0, tzinfo=TIMEZONE)

    with (
        patch("services.birthday_manager.datetime") as mock_dt,
        patch("services.birthday_manager.send_congrats_for_item", new_callable=AsyncMock) as mock_send,
    ):
        mock_dt.now.return_value = fake_night
        await check_and_send_birthday_congratulations(items, date(2026, 10, 5))
        mock_send.assert_not_called()


def test_get_initiator_title() -> None:
    """Проверяет корректное определение роли старосты и замстаросты."""
    assert get_initiator_title(ALLOWED_USER_ID) == "Староста"
    assert get_initiator_title(DEPUTY_USER_ID) == "Замстаросты"


@pytest.mark.asyncio
async def test_check_session_ownership_success() -> None:
    """Проверяет разрешение действий для автора активной сессии."""
    session = AttendanceSession(
        target_date="2026-10-05",
        lesson_num=1,
        lesson_title="Тест",
        students=[(5, "Студент")],
        initiator_id=ALLOWED_USER_ID,
    )
    cb = MagicMock(spec=CallbackQuery)
    cb.from_user = User(id=ALLOWED_USER_ID, is_bot=False, first_name="Староста")
    cb.answer = AsyncMock()

    allowed = await check_session_ownership(cb, session)
    assert allowed is True
    cb.answer.assert_not_called()


@pytest.mark.asyncio
async def test_check_session_ownership_forbidden() -> None:
    """Проверяет блокировку действий, если опрос начал другой староста."""
    session = AttendanceSession(
        target_date="2026-10-05",
        lesson_num=1,
        lesson_title="Тест",
        students=[(5, "Студент")],
        initiator_id=ALLOWED_USER_ID,
    )
    cb = MagicMock(spec=CallbackQuery)
    cb.from_user = User(id=DEPUTY_USER_ID, is_bot=False, first_name="Зам")
    cb.answer = AsyncMock()

    allowed = await check_session_ownership(cb, session)
    assert allowed is False
    cb.answer.assert_called_once()
    assert "заполняет Староста" in cb.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_create_session_collision_protection() -> None:
    """Проверяет выброс ошибки при попытке перетереть чужую сессию."""
    existing_session = AttendanceSession(
        target_date="2026-10-05",
        lesson_num=1,
        lesson_title="Тест",
        students=[(5, "Студент")],
        initiator_id=ALLOWED_USER_ID,
    )
    with (
        patch("services.attendance_manager.get_active_session", return_value=existing_session),
        pytest.raises(PermissionError),
    ):
        await create_attendance_session(date(2026, 10, 5), 1, "Новая пара", initiator_id=DEPUTY_USER_ID)


def test_bind_student_tg_id() -> None:
    """Проверяет ручную привязку Telegram ID для студента без юзернейма."""
    registry = [
        {"full_name": "Куулар Алдын-Сай", "username": None, "tg_id": None},
        {"full_name": "Мазур Арсений", "username": "mazur", "tg_id": 12345},
    ]
    with (
        patch("services.classmates_auth.load_classmates_registry", return_value=registry),
        patch("services.classmates_auth.sync_atomic_save_json") as mock_save,
        patch("services.classmates_auth.clear_registry_cache"),
    ):
        updated = bind_student_tg_id("Куулар Алдын-Сай", 777888999)
        assert updated is not None
        assert updated["tg_id"] == 777888999
        mock_save.assert_called_once()


def test_exam_date_range_dynamic_semester() -> None:
    """Проверяет расчет дат недель экзаменов с динамическим стартом семестра."""
    spring_start = date(2027, 2, 8)
    range_str = get_week_date_range_str(1, spring_start)
    assert "08.02" in range_str
    assert "14.02" in range_str


def test_format_help_text() -> None:
    """Проверяет форматирование справки для обычных студентов и старосты."""
    user_help = format_help_text(is_admin=False)
    assert "/today" in user_help
    assert "/notice" in user_help
    assert "/admin" not in user_help

    admin_help = format_help_text(is_admin=True)
    assert "/admin" in admin_help
    assert "/attendance" in admin_help
