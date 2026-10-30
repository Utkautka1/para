"""
Unit-тесты привязки аттестаций к сетке расписания (services/exam_parser.py).

Проверяет на мини-снапшоте (семестр с 01.09.2026, опубликованы недели 7–9):
  1. Кабинет и адрес берутся из назначения в сетке, а не из preferredRoomIds
  2. Назначенная аттестация получает дату, номер пары и звонки
  3. Без назначения остаётся период недели и «Кабинет уточняется» без адреса
  4. Пометку «предварительно» для недель позже последней опубликованной
"""

from datetime import date
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from config import CAMPUS_ADDRESS_VOZNESENSKY, GROUP_ID
from services import exam_parser as ep
from services.models import EXAM_ROOM_TBD, ExamItem
from services.schedule_parser import week_day_to_date

KR_TYPE = "yvorytrz"


def _load(subject: str, week: int) -> dict[str, Any]:
    """Плановая нагрузка-аттестация группы на неделю week."""
    return {
        "groupId": GROUP_ID,
        "subjectId": subject,
        "typeId": KR_TYPE,
        "teacherId": "t1",
        "weeklyPairs": {str(week): 1},
    }


def _inst(subject: str, week: int) -> dict[str, Any]:
    """Инстанс аттестации в сетке с пожеланием кабинета r_pref."""
    return {
        "instId": f"{subject}__PUBW{week}",
        "groupId": GROUP_ID,
        "subjectId": subject,
        "typeId": KR_TYPE,
        "customWeeks": [week],
        "preferredRoomIds": ["r_pref"],
    }


def _snapshot(published_weeks: list[int]) -> dict[str, Any]:
    """Мат. аппарат поставлен в сетку (ср, 5 пара, В-452), БЖД — только в плане."""
    return {
        "config": {"semesterStart": "2026-09-01", "periodTimes": ["8:30–10:00"] * 4 + ["15:20–16:45"]},
        "subjects": [{"id": "math", "name": "Мат. аппарат"}, {"id": "bzh", "name": "БЖД"}],
        "teachers": [{"id": "t1", "name": "Третьякова Ю.М."}],
        "rooms": [{"id": "r_pref", "name": "40"}, {"id": "r_v452", "name": "В-452"}],
        "groups": [{"id": GROUP_ID}],
        "lessonTypes": [],
        "loads": [_load("math", 16), _load("bzh", 14)],
        "schedule": {
            "instances": [_inst("math", 16), _inst("bzh", 14)],
            "assignment": {"math__PUBW16": {"day": 2, "period": 4, "roomId": "r_v452"}},
        },
        "publishedWeeks": published_weeks,
    }


async def _exams(published_weeks: list[int]) -> dict[str, ExamItem]:
    """Реестр аттестаций мини-снапшота по названию предмета."""
    data = _snapshot(published_weeks)
    with (
        patch.object(ep, "fetch_schedule_data", AsyncMock(return_value=data)),
        patch.object(ep, "get_teacher_links", AsyncMock(return_value={})),
    ):
        return {ex.subject: ex for ex in await ep.get_group_exams()}


@pytest.mark.asyncio
async def test_assigned_exam_uses_grid_room_and_slot() -> None:
    math = (await _exams([7, 8, 9]))["Мат. аппарат"]

    assert (math.room, math.address) == ("В-452", CAMPUS_ADDRESS_VOZNESENSKY)
    assert (math.exam_date, math.pair_number, math.time_str) == (date(2026, 12, 16), 5, "15:20–16:45")


@pytest.mark.asyncio
async def test_unassigned_exam_keeps_week_and_unknown_room() -> None:
    bzh = (await _exams([7, 8, 9]))["БЖД"]

    assert (bzh.room, bzh.address, bzh.weeks) == (EXAM_ROOM_TBD, "", [14])
    assert (bzh.exam_date, bzh.pair_number, bzh.time_str) == (None, None, None)


@pytest.mark.asyncio
@pytest.mark.parametrize(("published", "expected"), [([7, 8, 9], True), ([14, 15, 16], False), ([], False)])
async def test_preliminary_mark_by_published_weeks(published: list[int], expected: bool) -> None:
    exams = await _exams(published)
    assert all(ex.is_preliminary is expected for ex in exams.values())


@pytest.mark.parametrize(
    ("week", "day", "expected"),
    [(1, 1, date(2026, 9, 1)), (9, 5, date(2026, 10, 31)), (14, 3, date(2026, 12, 3))],
)
def test_week_day_to_date(week: int, day: int, expected: date) -> None:
    assert week_day_to_date(week, day, "2026-09-01") == expected
