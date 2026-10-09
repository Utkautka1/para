"""
Unit-тесты для форматирования топика экзаменов и аттестаций (services/exam_topic_updater.py).

Проверяет:
  1. Корректность вычисления календарных диапазонов учебных недель (get_week_date_range_str)
  2. Защиту от HTML-инъекций в карточке аттестации (format_exam_card)
  3. Форматирование экзаменов с датами, без дат и с подгруппами
  4. Сохранение и загрузку состояния главного сообщения (load_exam_topic_state / save_exam_topic_state)
"""

from unittest.mock import patch

import pytest

from services.exam_topic_updater import (
    format_exam_card,
    format_exams_schedule_message,
    get_week_date_range_str,
    load_exam_topic_state,
    save_exam_topic_state,
)
from services.models import ExamItem


def make_dummy_exam(**kwargs) -> ExamItem:
    """Создает валидный тестовый объект ExamItem."""
    base = {
        "subject": "Информационная безопасность",
        "exam_type": "Диф. зачёт",
        "teacher": "Смирнов А.А.",
        "room": "204",
        "address": "Цветочная ул., 8",
        "weeks": [12, 13],
        "subgroup": 0,
        "format_str": "Очно",
    }
    base.update(kwargs)
    return ExamItem(**base)


@pytest.mark.parametrize(
    "week_num,expected_format",
    [
        (1, "01.09–06.09"),
        (2, "07.09–13.09.2026"),
        (3, "14.09–20.09.2026"),
        (4, "21.09–27.09.2026"),
        (5, "28.09–04.10.2026"),
        (6, "05.10–11.10.2026"),
        (7, "12.10–18.10.2026"),
        (8, "19.10–25.10.2026"),
        (9, "26.10–01.11.2026"),
        (10, "02.11–08.11.2026"),
        (11, "09.11–15.11.2026"),
        (12, "16.11–22.11.2026"),
        (13, "23.11–29.11.2026"),
        (14, "30.11–06.12.2026"),
        (15, "07.12–13.12.2026"),
        (16, "14.12–20.12.2026"),
    ],
)
def test_get_week_date_range_str_weeks(week_num: int, expected_format: str) -> None:
    """Проверяет точный расчет дат недели от старта семестра (01.09.2026)."""
    assert get_week_date_range_str(week_num) == expected_format


def test_format_exam_card_escapes_html() -> None:
    """Проверяет экранирование спецсимволов HTML в карточке экзамена."""
    exam = make_dummy_exam(
        subject="Криптография <RSA & ECC>",
        teacher="Кузнецов & Иванов <к.т.н.>",
        room="Каб. <404>",
        address="Корпус 'Восток & Запад'",
    )
    card = format_exam_card(exam)
    assert "<RSA & ECC>" not in card
    assert "&lt;RSA &amp; ECC&gt;" in card
    assert "&amp; Иванов" in card
    assert "&lt;к.т.н.&gt;" in card


@pytest.mark.parametrize(
    "subgroup,expected_sg_str",
    [
        (0, ""),
        (1, "👥 Подгруппа 1"),
        (2, "👥 Подгруппа 2"),
    ],
)
def test_format_exam_card_subgroups(subgroup: int, expected_sg_str: str) -> None:
    """Проверяет отображение подгруппы в карточке экзамена."""
    exam = make_dummy_exam(subgroup=subgroup)
    card = format_exam_card(exam)
    if expected_sg_str:
        assert expected_sg_str in card
    else:
        assert "Подгруппа" not in card


def test_format_exam_card_without_weeks() -> None:
    """Проверяет отображение статуса 'Дата уточняется', если недели не заданы."""
    exam = make_dummy_exam(weeks=[])
    card = format_exam_card(exam)
    assert "Дата уточняется" in card


def test_format_exams_schedule_message_empty() -> None:
    """Проверяет сообщение топика при пустом списке экзаменов."""
    text = format_exams_schedule_message([])
    assert "АТТЕСТАЦИИ И ЭКЗАМЕНЫ ГРУППЫ 1-КПД-3" in text
    assert "Информация о зачётах и экзаменах формируется..." in text


def test_format_exams_schedule_message_multiple() -> None:
    """Проверяет сборку списка из нескольких экзаменов."""
    exams = [
        make_dummy_exam(subject="Математический анализ", exam_type="Экзамен"),
        make_dummy_exam(subject="Физика", exam_type="Зачёт"),
    ]
    text = format_exams_schedule_message(exams)
    assert "Математический анализ" in text
    assert "Экзамен" in text
    assert "Физика" in text
    assert "Зачёт" in text


def test_exam_topic_state_roundtrip(tmp_path) -> None:
    """Проверяет сохранение и загрузку ID главного сообщения экзаменов."""
    test_state_file = str(tmp_path / "exam_state.json")
    with patch("services.exam_topic_updater.STATE_FILE", test_state_file):
        assert load_exam_topic_state() is None
        save_exam_topic_state(12345)
        assert load_exam_topic_state() == 12345
        save_exam_topic_state(None)
        assert load_exam_topic_state() is None
