"""
Unit-тесты для парсера длительности мута (utils/mute_parser.py).

Проверяет корректность разбора интервалов времени (секунды, минуты, часы, дни),
поддержку русских и английских суффиксов, нечувствительность к регистру,
обработку пробелов, граничных условий и некорректных форматов.
"""

import pytest

from utils.mute_parser import parse_duration_to_seconds


@pytest.mark.parametrize(
    "raw_input,expected_seconds",
    [
        ("10с", 10),
        ("45s", 45),
        ("1с", 1),
        ("59s", 59),
        ("0с", 0),
        ("120s", 120),
    ],
)
def test_parse_duration_seconds(raw_input: str, expected_seconds: int) -> None:
    """Проверяет парсинг интервалов в секундах с русскими и английскими суффиксами."""
    assert parse_duration_to_seconds(raw_input) == expected_seconds


@pytest.mark.parametrize(
    "raw_input,expected_seconds",
    [
        ("1м", 60),
        ("5m", 300),
        ("10м", 600),
        ("30m", 1800),
        ("60м", 3600),
        ("15", 900),  # Без суффикса — по умолчанию минуты
        ("1", 60),
    ],
)
def test_parse_duration_minutes_and_default(raw_input: str, expected_seconds: int) -> None:
    """Проверяет парсинг минут и поведение по умолчанию (минуты при отсутствии суффикса)."""
    assert parse_duration_to_seconds(raw_input) == expected_seconds


@pytest.mark.parametrize(
    "raw_input,expected_seconds",
    [
        ("1ч", 3600),
        ("2h", 7200),
        ("12ч", 43200),
        ("24h", 86400),
        ("48ч", 172800),
    ],
)
def test_parse_duration_hours(raw_input: str, expected_seconds: int) -> None:
    """Проверяет парсинг часов (ч/h) с расчетом секунд."""
    assert parse_duration_to_seconds(raw_input) == expected_seconds


@pytest.mark.parametrize(
    "raw_input,expected_seconds",
    [
        ("1д", 86400),
        ("2d", 172800),
        ("7д", 604800),
        ("30d", 2592000),
        ("365д", 31536000),
    ],
)
def test_parse_duration_days(raw_input: str, expected_seconds: int) -> None:
    """Проверяет парсинг дней (д/d) для долгосрочных ограничений."""
    assert parse_duration_to_seconds(raw_input) == expected_seconds


@pytest.mark.parametrize(
    "raw_input,expected_seconds",
    [
        ("  10м  ", 600),
        ("5  с", 5),
        (" 2  h ", 7200),
        ("1   д", 86400),
        ("10М", 600),
        ("2Ч", 7200),
        ("1D", 86400),
        ("30S", 30),
    ],
)
def test_parse_duration_whitespace_and_case(raw_input: str, expected_seconds: int) -> None:
    """Проверяет устойчивость к пробелам и верхнему регистру символов."""
    assert parse_duration_to_seconds(raw_input) == expected_seconds


@pytest.mark.parametrize(
    "invalid_input",
    [
        "",
        "   ",
        "abc",
        "10x",
        "5w",
        "-5м",
        "+10с",
        "10.5м",
        "10,5ч",
        "минута",
        "10 мм",
        "час",
        "10d5m",
    ],
)
def test_parse_duration_invalid_formats(invalid_input: str) -> None:
    """Проверяет, что некорректные форматы возвращают None без исключений."""
    assert parse_duration_to_seconds(invalid_input) is None
