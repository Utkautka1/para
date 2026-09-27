"""
Unit-тесты модуля форматирования сообщений и экранирования HTML.

Проверяет:
  1. Защиту от HTML-инъекций в названиях предметов, ФИО и кабинетах
  2. Корректность сборки карточки пары (дистант vs очно)
  3. Форматирование временных интервалов и расписания
"""

from datetime import date
import pytest
from bot.templates.user.messages import (
    format_day_schedule,
    format_lesson_card,
    format_minutes,
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


def test_format_lesson_card_escapes_html():
    """Проверяет экранирование спецсимволов HTML в полях предмета и преподавателя."""
    lesson = make_dummy_lesson(
        subject="Базы данных <SQL & NoSQL>",
        teacher="Петров & Сидоров <доценты>",
        room="А<12>",
        address="Корпус 'Север & Юг'"
    )
    card = format_lesson_card(lesson)
    assert "<SQL & NoSQL>" not in card
    assert "&lt;SQL &amp; NoSQL&gt;" in card
    assert "&amp; Сидоров" in card
    assert "&lt;доценты&gt;" in card


def test_format_lesson_card_remote_credentials():
    """Проверяет вывод Zoom реквизитов для дистанционных занятий."""
    lesson = make_dummy_lesson(
        is_remote=True,
        remote_meeting_id="123 456 7890",
        remote_passcode="Pass<123>"
    )
    card = format_lesson_card(lesson)
    assert "🌐 Дистанционно" in card
    assert "123 456 7890" in card
    assert "Pass&lt;123&gt;" in card


def test_format_minutes():
    """Проверяет преобразование минут в строку формата 'X ч Y мин'."""
    assert format_minutes(15) == "15 мин"
    assert format_minutes(60) == "1 ч"
    assert format_minutes(95) == "1 ч 35 мин"


def test_format_day_schedule_empty():
    """Проверяет форматирование свободного дня без занятий."""
    day = date(2026, 9, 28)
    text = format_day_schedule(day, [])
    assert "свободный день" in text
