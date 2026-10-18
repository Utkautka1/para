"""
Unit-тесты для парсеров расписания и аттестаций (services/schedule_parser.py, services/exam_parser.py).

Проверяет:
  1. Разрешение адресов корпусов КТМУ по номеру аудитории (resolve_room_address)
  2. Извлечение реквизитов видеоконференций Zoom/Телемост (extract_zoom_creds)
  3. Очистку дублирующихся названий предметов (clean_subject_title)
  4. Расчет номера учебной недели (calculate_week_number)
  5. Проверку активности пары по четности и шаблонам недель (is_instance_active_for_week)
  6. Определение потоковых пар и принадлежности целевой группе (is_item_for_group, is_stream_lesson)
  7. Классификацию видов аттестаций и резолвинг преподавателей (is_assessment_type, resolve_teacher_name)
"""

from datetime import date
from typing import Any

import pytest

from config import (
    CAMPUS_ADDRESS_REMOTE,
    CAMPUS_ADDRESS_TSVETOCHNAYA,
    CAMPUS_ADDRESS_VOZNESENSKY,
)
from services.exam_parser import (
    extract_load_weeks,
    is_assessment_type,
    resolve_teacher_name,
)
from services.schedule_parser import (
    calculate_week_number,
    clean_subject_title,
    extract_zoom_creds,
    is_instance_active_for_week,
    is_item_for_group,
    is_stream_lesson,
    resolve_room_address,
)


@pytest.mark.parametrize(
    "room,is_remote,expected_addr",
    [
        ("", True, CAMPUS_ADDRESS_REMOTE),
        ("101", True, CAMPUS_ADDRESS_REMOTE),
        ("В-204", False, CAMPUS_ADDRESS_VOZNESENSKY),
        ("в-101", False, CAMPUS_ADDRESS_VOZNESENSKY),
        ("В-Актовый", False, CAMPUS_ADDRESS_VOZNESENSKY),
        ("101", False, CAMPUS_ADDRESS_TSVETOCHNAYA),
        ("Ц-204", False, CAMPUS_ADDRESS_TSVETOCHNAYA),
        ("Актовый зал", False, CAMPUS_ADDRESS_TSVETOCHNAYA),
    ],
)
def test_resolve_room_address(room: str, is_remote: bool, expected_addr: str) -> None:
    """Проверяет маршрутизацию адреса корпуса по префиксу аудитории."""
    assert resolve_room_address(room, is_remote) == expected_addr


def test_extract_zoom_creds_complete() -> None:
    """Проверяет извлечение полного набора данных Zoom (URL, ID, пароль)."""
    text = (
        "Ссылка: https://zoom.us/j/1234567890 \n"
        "Идентификатор конференции: 123 456 7890 \n"
        "Код доступа: SecretPass123"
    )
    url, mid, code = extract_zoom_creds(text)
    assert url == "https://zoom.us/j/1234567890"
    assert mid == "123 456 7890"
    assert code == "SecretPass123"


def test_extract_zoom_creds_empty() -> None:
    """Проверяет корректный возврат None для пустого текста."""
    assert extract_zoom_creds("") == (None, None, None)
    assert extract_zoom_creds(None) == (None, None, None)


@pytest.mark.parametrize(
    "input_subj,expected_clean",
    [
        ("Математика / Математика", "Математика"),
        ("Базы данных / Базы данных (SQL)", "Базы данных (SQL)"),
        ("Физика", "Физика"),
        ("История / История (практика)", "История (практика)"),
        ("Экономика / Финансы", "Экономика / Финансы"),
    ],
)
def test_clean_subject_title(input_subj: str, expected_clean: str) -> None:
    """Проверяет дедупликацию и очистку названий предметов."""
    assert clean_subject_title(input_subj) == expected_clean


@pytest.mark.parametrize(
    "target_date,expected_week",
    [
        (date(2026, 8, 25), 1),  # До начала семестра
        (date(2026, 9, 1), 1),
        (date(2026, 9, 6), 1),
        (date(2026, 9, 7), 2),
        (date(2026, 9, 14), 3),
        (date(2026, 9, 28), 5),
        (date(2026, 12, 14), 16),
    ],
)
def test_calculate_week_number(target_date: date, expected_week: int) -> None:
    """Проверяет расчет учебной недели от 01.09.2026."""
    assert calculate_week_number(target_date, "2026-09-01") == expected_week


@pytest.mark.parametrize(
    "pattern,custom_weeks,week_num,expected_active",
    [
        ("all", [], 1, True),
        ("all", [], 2, True),
        ("even", [], 2, True),
        ("even", [], 3, False),
        ("odd", [], 1, True),
        ("odd", [], 2, False),
        ("custom", [1, 3, 5], 3, True),
        ("custom", [1, 3, 5], 4, False),
    ],
)
def test_is_instance_active_for_week(
    pattern: str, custom_weeks: list[int], week_num: int, expected_active: bool
) -> None:
    """Проверяет активность занятия по четным, нечетным и кастомным неделям."""
    inst = {"weekPattern": pattern, "customWeeks": custom_weeks}
    assert is_instance_active_for_week(inst, week_num) == expected_active


@pytest.mark.parametrize(
    "item,group_id,expected",
    [
        ({"groupId": "g1"}, "g1", True),
        ({"groupId": "g2"}, "g1", False),
        ({"groupIds": ["g1", "g2"]}, "g1", True),
        ({"streamGroupIds": ["g1"]}, "g1", True),
        ({"streamParticipants": [{"groupId": "g1"}]}, "g1", True),
        ({}, "g1", False),
    ],
)
def test_is_item_for_group(item: dict[str, Any], group_id: str, expected: bool) -> None:
    """Проверяет принадлежность элемента целевой группе (включая потоки)."""
    assert is_item_for_group(item, group_id) == expected


@pytest.mark.parametrize(
    "inst,expected_is_stream",
    [
        ({"streamGroupIds": ["g1"]}, True),
        ({"streamParticipants": [{"groupId": "g1"}]}, True),
        ({"streamId": "stream_123"}, True),
        ({}, False),
    ],
)
def test_is_stream_lesson(inst: dict[str, Any], expected_is_stream: bool) -> None:
    """Проверяет детекцию потокового занятия по наличию потоковых идентификаторов."""
    assert is_stream_lesson(inst) == expected_is_stream


@pytest.mark.parametrize(
    "type_id,expected_valid,expected_name",
    [
        ("yvorytrz", True, "Контрольная работа"),
        ("aeybq2f1", True, "Зачёт"),
        ("dacst0q5", True, "Диф. зачёт"),
        ("dop7h4j9", True, "Курсовая работа"),
        ("unknown_lecture", False, ""),
    ],
)
def test_is_assessment_type(type_id: str, expected_valid: bool, expected_name: str) -> None:
    """Проверяет фильтрацию аттестационных пар по их типам."""
    is_valid, name = is_assessment_type(type_id, {})
    assert is_valid == expected_valid
    assert name == expected_name


def test_resolve_teacher_name() -> None:
    """Проверяет сопоставление полного ФИО преподавателя по справочнику."""
    links = {"иванов": {"full_name": "Иванов Иван Иванович"}}
    assert resolve_teacher_name("Иванов И.И.", links) == "Иванов Иван Иванович"
    assert resolve_teacher_name("Сидоров С.С.", links) == "Сидоров С.С."
    assert resolve_teacher_name("", links) == ""


def test_extract_load_weeks() -> None:
    """Проверяет извлечение и сортировку недель нагрузки."""
    load_pairs = {"weeklyPairs": {"5": 1, "2": 1, "10": 1}}
    assert extract_load_weeks(load_pairs) == [2, 5, 10]

    load_custom = {"customWeeks": [7, 3, 9]}
    assert extract_load_weeks(load_custom) == [3, 7, 9]
