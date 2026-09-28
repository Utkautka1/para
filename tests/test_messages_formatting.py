"""
Unit-тесты модуля форматирования сообщений и экранирования HTML (bot/templates/user/messages.py).

Проверяет:
  1. Защиту от HTML-инъекций в названиях предметов, ФИО, аудиториях и Zoom-реквизитах
  2. Разбор временных интервалов и расчет оставшихся минут
  3. Форматирование карточек пар (очно/дистант/поток/подгруппы)
  4. Сборку расписания на день и неделю с цитатами blockquote
"""

from datetime import date
from typing import Optional, Tuple
import pytest

from bot.templates.user.messages import (
    _parse_time_interval_minutes,
    format_day_schedule,
    format_lesson_card,
    format_minutes,
    format_reminder_text,
    format_week_day_block,
    format_week_lesson_card,
    format_week_lesson_loc,
    format_week_schedule,
)
from services.models import Lesson


def make_dummy_lesson(**kwargs) -> Lesson:
    """Создает валидный тестовый объект Lesson с дефолтными полями."""
    base = {
        "period": 0,
        "time_str": "08:30-10:00",
        "subject": "Высшая математика",
        "lesson_type": "Лекция",
        "teacher": "Иванов И.И.",
        "is_remote": False,
        "room": "101",
        "address": "Цветочная ул., 8",
        "subgroup": 0,
        "is_stream": False,
    }
    base.update(kwargs)
    return Lesson(**base)


@pytest.mark.parametrize(
    "minutes,expected",
    [
        (0, "0 мин"),
        (1, "1 мин"),
        (45, "45 мин"),
        (59, "59 мин"),
        (60, "1 ч"),
        (61, "1 ч 1 мин"),
        (90, "1 ч 30 мин"),
        (120, "2 ч"),
        (125, "2 ч 5 мин"),
        (300, "5 ч"),
        (1439, "23 ч 59 мин"),
    ],
)
def test_format_minutes_parametrized(minutes: int, expected: str) -> None:
    """Проверяет преобразование минут в читаемую строку часов и минут."""
    assert format_minutes(minutes) == expected


@pytest.mark.parametrize(
    "time_str,expected",
    [
        ("08:30-10:00", (510, 600)),
        ("8:30-10:00", (510, 600)),
        ("10:05–11:30", (605, 690)),
        ("11.45 - 13.10", (705, 790)),
        ("13:20-14:50", (800, 890)),
        ("15:00-16:30", (900, 990)),
        ("16:40-18:10", (1000, 1090)),
    ],
)
def test_parse_time_interval_valid(time_str: str, expected: Tuple[int, int]) -> None:
    """Проверяет корректное извлечение минут начала и конца для валидных строк."""
    assert _parse_time_interval_minutes(time_str) == expected


@pytest.mark.parametrize(
    "invalid_time",
    [
        "",
        "не указано",
        "08:30",
        "10:00",
        "random text without time",
        "123-456",
    ],
)
def test_parse_time_interval_invalid(invalid_time: str) -> None:
    """Проверяет возврат None для некорректных временных форматов."""
    assert _parse_time_interval_minutes(invalid_time) is None


def test_format_lesson_card_escapes_html() -> None:
    """Проверяет экранирование спецсимволов HTML в полях предмета и преподавателя."""
    lesson = make_dummy_lesson(
        subject="Базы данных <SQL & NoSQL>",
        teacher="Петров & Сидоров <доценты>",
        room="А<12>",
        address="Корпус 'Север & Юг'",
    )
    card = format_lesson_card(lesson)
    assert "<SQL & NoSQL>" not in card
    assert "&lt;SQL &amp; NoSQL&gt;" in card
    assert "&amp; Сидоров" in card
    assert "&lt;доценты&gt;" in card


def test_format_lesson_card_remote_credentials() -> None:
    """Проверяет вывод Zoom реквизитов для дистанционных занятий."""
    lesson = make_dummy_lesson(
        is_remote=True,
        remote_meeting_id="123 456 7890",
        remote_passcode="Pass<123>",
    )
    card = format_lesson_card(lesson)
    assert "🌐 Дистанционно" in card
    assert "123 456 7890" in card
    assert "Pass&lt;123&gt;" in card


@pytest.mark.parametrize(
    "subgroup,is_stream,expected_in_card",
    [
        (0, False, "▪️ <b>1 пара</b>"),
        (1, False, "👥 <b>Подгруппа 1</b>"),
        (2, False, "👥 <b>Подгруппа 2</b>"),
        (0, True, "🔗 <b>поток</b>"),
        (1, True, "🔗 <b>поток</b>"),
    ],
)
def test_format_lesson_card_badges(subgroup: int, is_stream: bool, expected_in_card: str) -> None:
    """Проверяет отображение бейджей подгруппы и потока в карточке пары."""
    lesson = make_dummy_lesson(subgroup=subgroup, is_stream=is_stream)
    card = format_lesson_card(lesson)
    assert expected_in_card in card


@pytest.mark.parametrize(
    "is_remote,room,address,expected",
    [
        (True, "", "", "🌐 Дистанционно"),
        (False, "В-204", "Вознесенский пр., 44", "📍 Каб. В-204 (Вознесенский)"),
        (False, "101", "Цветочная ул., 8", "📍 Каб. 101 (Цветочная)"),
        (False, "Ц-205", "ул. Цветочная", "📍 Каб. Ц-205 (Цветочная)"),
    ],
)
def test_format_week_lesson_loc(is_remote: bool, room: str, address: str, expected: str) -> None:
    """Проверяет определение компактной локации для недельного расписания."""
    lesson = make_dummy_lesson(is_remote=is_remote, room=room, address=address)
    assert format_week_lesson_loc(lesson) == expected


def test_format_week_lesson_card_html_escape() -> None:
    """Проверяет безопасное экранирование в цитате недели."""
    lesson = make_dummy_lesson(
        subject="<Script>Alert()</script>",
        teacher="Teacher & Specialist",
        subgroup=1,
        is_stream=True,
    )
    card = format_week_lesson_card(lesson)
    assert "<Script>" not in card
    assert "&lt;Script&gt;" in card
    assert "&amp; Specialist" in card
    assert "<blockquote>" in card
    assert "</blockquote>" in card


def test_format_week_day_block_empty() -> None:
    """Проверяет генерацию блока дня без занятий в недельном виде."""
    day = date(2026, 9, 27)  # Воскресенье
    block = format_week_day_block(day, [])
    assert "Воскресенье, 27.09" in block
    assert "свободный день" in block


def test_format_week_day_block_with_lessons() -> None:
    """Проверяет генерацию блока дня со списком занятий."""
    day = date(2026, 9, 28)
    lessons = [make_dummy_lesson(period=0), make_dummy_lesson(period=1)]
    block = format_week_day_block(day, lessons)
    assert "Понедельник, 28.09" in block
    assert "1 пара" in block
    assert "2 пара" in block


def test_format_week_schedule_structure() -> None:
    """Проверяет заголовок и объединение дней в расписании на неделю."""
    d1 = date(2026, 9, 28)
    d2 = date(2026, 9, 29)
    days_data = [(d1, [make_dummy_lesson(period=0)]), (d2, [])]
    text = format_week_schedule(days_data)
    assert "РАСПИСАНИЕ НА НЕДЕЛЮ" in text
    assert "Понедельник, 28.09" in text
    assert "Вторник, 29.09" in text


def test_format_reminder_text() -> None:
    """Проверяет текст напоминания за 10 минут до начала занятия."""
    lesson = make_dummy_lesson(subject="Философия")
    text = format_reminder_text(lesson)
    assert "Через 10 минут начинается пара!" in text
    assert "Философия" in text


def test_format_day_schedule_empty() -> None:
    """Проверяет форматирование свободного дня без занятий."""
    day = date(2026, 9, 28)
    text = format_day_schedule(day, [])
    assert "свободный день" in text
