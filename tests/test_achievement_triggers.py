"""
Тесты событийных правил ачивок (services/achievement_triggers.py).

Время фиксированное и московское. Проверяет:
  1. «Полуночник» — только на кнопке «Завтра» и только с 21:00 до 05:00
     (баг: раньше проверялся на /start и не срабатывал на «Завтра»)
  2. Пара / перемена / «форточка» по сетке сегодняшнего дня
  3. Дни недели: понедельник, пятница, выходные
  4. Ачивки за одно задание ДЗ
"""

from datetime import datetime, time

import pytest

from config import TIMEZONE
from services.achievement_triggers import (
    BIRTHDAY_GREETING_RE,
    HomeworkTask,
    ScheduleView,
    homework_achievements,
    homework_kind,
    lesson_moment_achievements,
    parse_lesson_slot,
    schedule_view_achievements,
)
from services.models import Lesson

# 2026-11-02 — понедельник
MONDAY = datetime(2026, 11, 2, tzinfo=TIMEZONE)


def _at(day_offset: int, hh: int, mm: int = 0) -> datetime:
    """Момент на неделе 02.11–08.11 (0 — понедельник)."""
    return MONDAY.replace(day=2 + day_offset, hour=hh, minute=mm)


def _lesson(time_str: str, remote: bool = False) -> Lesson:
    return Lesson(
        period=0,
        time_str=time_str,
        subject="ИТ",
        lesson_type="Пр",
        teacher="Шустов Д.А.",
        is_remote=remote,
        room="В-452",
        address="",
    )


# Пары 1, 2 и 4: между 2-й и 4-й — «форточка»
DAY = [_lesson("8:30–9:55"), _lesson("10:20–11:45"), _lesson("13:40–15:05")]


@pytest.mark.parametrize(
    ("moment", "view", "expected"),
    [
        (_at(1, 21, 30), ScheduleView.TOMORROW, True),
        (_at(2, 0, 30), ScheduleView.TOMORROW, True),
        (_at(1, 20, 59), ScheduleView.TOMORROW, False),
        (_at(2, 5, 0), ScheduleView.TOMORROW, False),
        (_at(1, 21, 30), ScheduleView.TODAY, False),
    ],
)
def test_night_owl_only_on_tomorrow_at_night(moment: datetime, view: ScheduleView, expected: bool) -> None:
    assert ("time_night_owl" in schedule_view_achievements(view, moment, [])) is expected


@pytest.mark.parametrize(
    ("hh", "mm", "expected"),
    [
        (9, 0, {"time_second_shift"}),
        (10, 0, {"egg_tea_break"}),
        (12, 30, {"life_window_chill"}),
        (16, 0, set()),
        (7, 0, set()),
    ],
)
def test_lesson_moment(hh: int, mm: int, expected: set[str]) -> None:
    assert lesson_moment_achievements(time(hh, mm), DAY) == expected


def test_lesson_moment_only_for_today_view() -> None:
    moment = _at(1, 9, 0)
    assert "time_second_shift" in schedule_view_achievements(ScheduleView.TODAY, moment, DAY)
    assert "time_second_shift" not in schedule_view_achievements(ScheduleView.TOMORROW, moment, DAY)


def test_time_of_day_and_weekdays() -> None:
    assert {"time_early_bird", "life_monday"} <= schedule_view_achievements(ScheduleView.WEEK, _at(0, 7, 50), [])
    assert "life_monday" not in schedule_view_achievements(ScheduleView.WEEK, _at(0, 8, 40), [])
    assert "egg_insomnia" in schedule_view_achievements(ScheduleView.WEEK, _at(3, 3, 15), [])
    assert "life_friday" in schedule_view_achievements(ScheduleView.WEEK_NEXT, _at(4, 15, 1), [])
    assert "life_friday" not in schedule_view_achievements(ScheduleView.WEEK, _at(4, 16), [])


@pytest.mark.parametrize(
    ("moment", "view", "expected"),
    [
        (_at(6, 12), ScheduleView.TOMORROW, True),
        (_at(5, 12), ScheduleView.TOMORROW, False),
        (_at(5, 12), ScheduleView.WEEK_NEXT, True),
        (_at(3, 12), ScheduleView.WEEK_NEXT, False),
    ],
)
def test_sunday_scout(moment: datetime, view: ScheduleView, expected: bool) -> None:
    assert ("time_sunday_scout" in schedule_view_achievements(view, moment, [])) is expected


def test_remote_lesson_day() -> None:
    lessons = [_lesson("8:30–9:55", remote=True)]
    assert "life_remote" in schedule_view_achievements(ScheduleView.TOMORROW, _at(1, 12), lessons)
    assert "life_remote" not in schedule_view_achievements(ScheduleView.TOMORROW, _at(1, 12), DAY)


@pytest.mark.parametrize(
    ("raw", "ok"), [("8:30–9:55", True), ("09:00 - 10:30", True), ("—", False), ("25:00-26:00", False)]
)
def test_parse_lesson_slot(raw: str, ok: bool) -> None:
    assert (parse_lesson_slot(raw) is not None) is ok


def test_homework_single_task_achievements() -> None:
    task = HomeworkTask(prompt="x" * 210, kind="document", file_name="lab3.PY", is_followup=True)
    got = homework_achievements(task, _at(1, 23))
    assert got == {"ai_first_task", "ai_prompt_pro", "ai_followup", "ai_night_grind", "ai_clean_code"}
    plain = HomeworkTask(prompt="реши задачу", kind="photo", file_name="image.jpg", is_followup=False)
    assert homework_achievements(plain, _at(1, 12)) == {"ai_first_task", "ai_photo"}


def test_homework_kind() -> None:
    assert homework_kind(None, False) == "text"
    assert homework_kind("image/jpeg", True) == "photo"
    assert homework_kind("application/pdf", True) == "document"


@pytest.mark.parametrize(
    ("text", "ok"),
    [
        ("С днём рождения, Саня!", True),
        ("с др!!", True),
        ("с днюхой", True),
        ("сдружились", False),
        ("мой др завтра", False),
    ],
)
def test_birthday_greeting(text: str, ok: bool) -> None:
    assert bool(BIRTHDAY_GREETING_RE.search(text)) is ok
