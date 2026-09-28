"""
Unit-тесты для сервиса дней рождения (services/birthday_manager.py).

Проверяет:
  1. Математику расчета оставшихся дней и возраста именинника (calculate_days_and_age)
  2. Склонения дней (день/дня/дней) и возраста (год/года/лет)
  3. Форматирование упоминаний пользователей (format_person_tag, get_person_mention)
  4. Логику персональных поздравлений и цитаты старосты (format_congrats_message)
  5. Ротацию неповторяющихся поздравлений (pick_unique_wish)
"""

from datetime import date
from typing import Any, Dict
from unittest.mock import patch
import pytest

from services.birthday_manager import (
    calculate_days_and_age,
    format_age_badge,
    format_congrats_message,
    format_days_left_badge,
    format_person_tag,
    format_starosta_block,
    pick_unique_wish,
    season_sort_key,
)


def test_calculate_days_and_age_today() -> None:
    """Проверяет расчет для дня рождения, который наступил сегодня."""
    today = date(2026, 9, 28)
    item = {"day": 28, "month": 9, "year": 2008, "full_name": "Иван"}
    res = calculate_days_and_age(item, today)
    assert res["days_until"] == 0
    assert res["turning_age"] == 18
    assert res["is_today"] is True


def test_calculate_days_and_age_later_this_year() -> None:
    """Проверяет расчет для дня рождения позже в текущем году."""
    today = date(2026, 9, 28)
    item = {"day": 10, "month": 10, "year": 2007, "full_name": "Петр"}
    res = calculate_days_and_age(item, today)
    assert res["days_until"] == 12
    assert res["turning_age"] == 19
    assert res["is_today"] is False


def test_calculate_days_and_age_passed_this_year() -> None:
    """Проверяет расчет для дня рождения, который уже прошел в текущем году."""
    today = date(2026, 9, 28)
    item = {"day": 15, "month": 1, "year": 2008, "full_name": "Сергей"}
    res = calculate_days_and_age(item, today)
    assert res["days_until"] > 100
    assert res["turning_age"] == 19
    assert res["is_today"] is False


def test_calculate_days_and_age_leap_year_handling() -> None:
    """Проверяет обработку 29 февраля в невисокосный год."""
    today = date(2026, 1, 1)
    item = {"day": 29, "month": 2, "year": 2004, "full_name": "Leap Person"}
    res = calculate_days_and_age(item, today)
    assert res["turning_age"] == 22
    assert res["days_until"] > 0


@pytest.mark.parametrize(
    "days,expected_badge",
    [
        (0, "сегодня"),
        (1, "завтра"),
        (2, "через 2 дня"),
        (3, "через 3 дня"),
        (4, "через 4 дня"),
        (5, "через 5 дней"),
        (11, "через 11 дней"),
        (12, "через 12 дней"),
        (14, "через 14 дней"),
        (20, "через 20 дней"),
        (21, "через 21 день"),
        (22, "через 22 дня"),
        (25, "через 25 дней"),
        (101, "через 101 день"),
        (112, "через 112 дней"),
    ],
)
def test_format_days_left_badge(days: int, expected_badge: str) -> None:
    """Проверяет склонение оставшихся дней до события."""
    assert format_days_left_badge(days) == expected_badge


@pytest.mark.parametrize(
    "age,expected_str",
    [
        (1, "1 год"),
        (2, "2 года"),
        (4, "4 года"),
        (5, "5 лет"),
        (11, "11 лет"),
        (14, "14 лет"),
        (18, "18 лет"),
        (19, "19 лет"),
        (20, "20 лет"),
        (21, "21 год"),
        (22, "22 года"),
        (25, "25 лет"),
    ],
)
def test_format_age_badge(age: int, expected_str: str) -> None:
    """Проверяет склонение возраста именинника (год/года/лет)."""
    assert format_age_badge(age) == expected_str


@pytest.mark.parametrize(
    "item,expected_tag",
    [
        ({"full_name": "Иван", "username": "ivan_tg"}, "Иван (@ivan_tg)"),
        ({"full_name": "Ольга", "tg_id": 12345}, '<a href="tg://user?id=12345">Ольга</a>'),
        ({"full_name": "Дмитрий"}, "Дмитрий"),
    ],
)
def test_format_person_tag(item: Dict[str, Any], expected_tag: str) -> None:
    """Проверяет формирование ссылки или юзернейма для карточки."""
    assert format_person_tag(item) == expected_tag


def test_season_sort_key_order() -> None:
    """Проверяет сортировочный ключ внутри сезона (Осень: 9, 10, 11)."""
    months = [9, 10, 11]
    item_sep = {"day": 5, "month": 9}
    item_oct = {"day": 1, "month": 10}
    assert season_sort_key(item_sep, months) < season_sort_key(item_oct, months)


def test_format_starosta_block() -> None:
    """Проверяет формирование цитаты старосты."""
    assert format_starosta_block(None) == ""
    assert format_starosta_block("") == ""
    block = format_starosta_block("Учитесь усердно!")
    assert "Слово старосты:" in block
    assert "Учитесь усердно!" in block


def test_format_congrats_message_starosta_vs_student() -> None:
    """Проверяет поздравление старосты (без дублирования слова старосты) и студента."""
    starosta_item = {"full_name": "Стрыгин Дмитрий", "turning_age": 19}
    msg_starosta = format_congrats_message(starosta_item, "Успехов!", "Слово...")
    assert "нашего старосту" in msg_starosta
    assert "Слово старосты" not in msg_starosta

    student_item = {"full_name": "Иванов Иван", "turning_age": 18}
    msg_student = format_congrats_message(student_item, "Успехов!", "Слово старосты текст")
    assert "виновника торжества" in msg_student
    assert "Слово старосты:" in msg_student


def test_pick_unique_wish_rotation(tmp_path) -> None:
    """Проверяет ротацию пожеланий без повторов до исчерпания пула."""
    history_file = str(tmp_path / "hist.json")
    wishes = ["Wish 1", "Wish 2", "Wish 3"]
    chosen = {pick_unique_wish("User1", wishes, history_file) for _ in range(3)}
    assert len(chosen) == 3
    # Четвертый вызов перезапустит ротацию
    w4 = pick_unique_wish("User1", wishes, history_file)
    assert w4 in wishes
