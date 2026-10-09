"""
Unit-тесты для парсеров времени и вспомогательных функций оповещений (services/notifier.py).

Проверяет:
  1. Извлечение времени начала пары (parse_lesson_start_time)
  2. Извлечение времени окончания пары (parse_lesson_end_time)
  3. Формирование предупреждения об отсутствующем преподавателе (build_missing_teacher_alert)
"""

from datetime import time as dtime

import pytest

from services.notifier import (
    build_missing_teacher_alert,
    parse_lesson_end_time,
    parse_lesson_start_time,
)


@pytest.mark.parametrize(
    "time_str,expected_hour,expected_minute",
    [
        ("08:30-10:00", 8, 30),
        ("8:30-10:00", 8, 30),
        ("10:05–11:30", 10, 5),
        ("11.45 - 13.10", 11, 45),
        ("13:20-14:50", 13, 20),
        ("15:00-16:30", 15, 0),
        ("16:40-18:10", 16, 40),
        ("18:20-19:50", 18, 20),
        ("9:00", 9, 0),
    ],
)
def test_parse_lesson_start_time_valid(time_str: str, expected_hour: int, expected_minute: int) -> None:
    """Проверяет корректность разбора времени старта занятия для разных форматов."""
    res = parse_lesson_start_time(time_str)
    assert res is not None
    assert res == dtime(hour=expected_hour, minute=expected_minute)


@pytest.mark.parametrize(
    "invalid_str",
    [
        "",
        "не указано",
        "без времени",
        "пара 1",
        "abc:def",
    ],
)
def test_parse_lesson_start_time_invalid(invalid_str: str) -> None:
    """Проверяет возврат None для некорректных строк времени старта."""
    assert parse_lesson_start_time(invalid_str) is None


@pytest.mark.parametrize(
    "time_str,expected_hour,expected_minute",
    [
        ("08:30-10:00", 10, 0),
        ("8:30-10:00", 10, 0),
        ("10:05–11:30", 11, 30),
        ("11.45 - 13.10", 13, 10),
        ("13:20-14:50", 14, 50),
        ("15:00-16:30", 16, 30),
        ("16:40-18:10", 18, 10),
        ("18:20-19:50", 19, 50),
    ],
)
def test_parse_lesson_end_time_valid(time_str: str, expected_hour: int, expected_minute: int) -> None:
    """Проверяет корректность разбора времени окончания занятия."""
    res = parse_lesson_end_time(time_str)
    assert res is not None
    assert res == dtime(hour=expected_hour, minute=expected_minute)


@pytest.mark.parametrize(
    "invalid_str",
    [
        "",
        "08:30",  # Только время начала
        "10:00",
        "не указано",
        "123-456",
    ],
)
def test_parse_lesson_end_time_invalid(invalid_str: str) -> None:
    """Проверяет возврат None при отсутствии второго токена времени окончания."""
    assert parse_lesson_end_time(invalid_str) is None


@pytest.mark.parametrize(
    "raw_teacher,expected_callback",
    [
        ("Иванов И.И.", "admin:add_t:иванов"),
        ("Петрова Анна", "admin:add_t:петрова"),
        ("Smith John", "admin:add_t:smith"),
        ("Сидоров", "admin:add_t:сидоров"),
    ],
)
def test_build_missing_teacher_alert_callback(raw_teacher: str, expected_callback: str) -> None:
    """Проверяет генерацию callback_data с фамилией в нижнем регистре."""
    text, kb = build_missing_teacher_alert(raw_teacher, "Математика")
    assert raw_teacher in text
    assert "Математика" in text
    assert len(kb.inline_keyboard) == 1
    assert kb.inline_keyboard[0][0].callback_data == expected_callback
