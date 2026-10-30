"""
Unit-тесты применения замен КТМУ к расписанию (services/schedule_substitutions.py).

Проверяет на мини-снапшоте субботы 31.10 (неделя 9):
  1. Сдвиг пары заменой 'sub' (кейс 31.10: иностранный со 2-й пары на 1-ю)
  2. Снятие пары отменами и переносом «отсюда»
  3. stream_group_cancel снимает пару только у исключённых групп потока
  4. Перенос «сюда» (moved + targetDate) добавляет пару с новым кабинетом
  5. Фильтрацию замен по занятиям группы и сброс ETag у снапшота старого формата
     (нет substitutions или publishedWeeks)
"""

from datetime import date
from typing import Any

import pytest

from config import GROUP_ID
from services import schedule_parser as sp
from services.schedule_substitutions import base_inst_id, filter_group_substitutions

SATURDAY = date(2026, 10, 31)
SATURDAY_WEEK = 9
LANG_ID = "lang__WEEK_5__PUBW5__EXACT_W9"


@pytest.fixture(autouse=True)
def _no_teacher_alerts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Глушит фоновое оповещение о дистанте без ссылки — в тестах нет event loop."""
    monkeypatch.setattr(sp, "_handle_missing_remote_teacher", lambda *_: None)


def _inst(inst_id: str, subject: str, week: int = SATURDAY_WEEK, **extra: Any) -> dict[str, Any]:
    """Инстанс занятия группы, проводимый только на неделе week."""
    return {
        "instId": f"{inst_id}__PUBW{week}",
        "groupId": GROUP_ID,
        "subjectId": subject,
        "teacherId": "t1",
        "typeId": "pr",
        "format": "inperson",
        "weekPattern": "custom",
        "customWeeks": [week],
        **extra,
    }


def _snapshot(subs: list[dict[str, Any]]) -> dict[str, Any]:
    """Мини-снапшот: иностранный на 2-й паре субботы и ИТ, по сетке стоящие в четверг."""
    insts = [_inst(LANG_ID, "lang"), _inst("it__W9", "it")]
    return {
        "config": {"semesterStart": "2026-09-01"},
        "subjects": [{"id": "lang", "name": "Иностранный язык"}, {"id": "it", "name": "ИТ"}],
        "teachers": [{"id": "t1", "name": "Шустов Д.А."}, {"id": "t2", "name": "Иванов И.И."}],
        "rooms": [{"id": "r1", "name": "В-452"}, {"id": "r2", "name": "В-481"}],
        "groups": [{"id": GROUP_ID, "dayPeriodTimes": {"5": ["8:30–9:55", "10:20–11:45", "12:00–13:25"]}}],
        "lessonTypes": [{"id": "pr", "name": "Пр"}],
        "schedule": {
            "instances": insts,
            "assignment": {
                f"{LANG_ID}__PUBW9": {"day": 5, "period": 1, "roomId": "r1"},
                "it__W9__PUBW9": {"day": 3, "period": 0, "roomId": "r1"},
            },
        },
        "substitutions": subs,
    }


def _day(subs: list[dict[str, Any]], day: date = SATURDAY) -> list[Any]:
    """Расписание дня мини-снапшота с заданными заменами."""
    return sp._extract_lessons_for_day(_snapshot(subs), day, SATURDAY_WEEK, {})


def test_no_substitutions_keeps_grid() -> None:
    lessons = _day([])
    assert [(lesson.subject, lesson.number) for lesson in lessons] == [("Иностранный язык", 2)]


def test_sub_moves_lesson_to_new_period() -> None:
    sub = {"type": "sub", "date": "2026-10-31", "instId": LANG_ID, "newPeriod": 0, "newRoomId": "r2"}
    (lesson,) = _day([sub])
    assert (lesson.number, lesson.time_str, lesson.room) == (1, "8:30–9:55", "В-481")


def test_sub_changes_teacher_and_format() -> None:
    sub = {"type": "sub", "date": "2026-10-31", "instId": LANG_ID, "newTeacherId": "t2", "newFormat": "remote"}
    (lesson,) = _day([sub])
    assert (lesson.number, lesson.teacher, lesson.is_remote) == (2, "Иванов И.И.", True)


def test_sub_for_other_date_is_ignored() -> None:
    sub = {"type": "sub", "date": "2026-10-24", "instId": LANG_ID, "newPeriod": 0}
    assert _day([sub])[0].number == 2


@pytest.mark.parametrize("sub_type", ["cancel", "cancel_assignment", "pending_move", "excursion", "moved"])
def test_cancel_types_remove_lesson(sub_type: str) -> None:
    sub = {"type": sub_type, "date": "2026-10-31", "instId": LANG_ID, "targetDate": "2026-11-02"}
    assert _day([sub]) == []


@pytest.mark.parametrize(("excluded", "expected"), [([GROUP_ID], 0), (["other_group"], 1)])
def test_stream_group_cancel_only_for_excluded(excluded: list[str], expected: int) -> None:
    sub = {"type": "stream_group_cancel", "date": "2026-10-31", "instId": LANG_ID, "excludedGroupIds": excluded}
    assert len(_day([sub])) == expected


def test_moved_in_adds_lesson_on_target_date() -> None:
    sub = {
        "type": "moved",
        "date": "2026-10-29",
        "instId": "it__W9",
        "targetDate": "2026-10-31",
        "targetPeriod": 2,
        "newRoomId": "r2",
    }
    lessons = _day([sub])
    assert [(lesson.subject, lesson.number, lesson.time_str, lesson.room) for lesson in lessons] == [
        ("Иностранный язык", 2, "10:20–11:45", "В-452"),
        ("ИТ", 3, "12:00–13:25", "В-481"),
    ]
    assert _day([sub], day=date(2026, 10, 29)) == []


def test_base_inst_id_strips_only_publish_suffix() -> None:
    assert base_inst_id("x__WEEK_5__PUBW5__EXACT_W9__PUBW9") == "x__WEEK_5__PUBW5__EXACT_W9"
    assert base_inst_id("x__L1") == "x__L1"


def test_filter_group_substitutions_keeps_only_group_lessons() -> None:
    insts = [_inst(LANG_ID, "lang")]
    subs = [{"instId": LANG_ID, "type": "sub"}, {"instId": "alien__L1", "type": "cancel"}]
    assert filter_group_substitutions(subs, insts) == [subs[0]]


def test_filter_snapshot_keeps_substitutions() -> None:
    raw = _snapshot([{"instId": LANG_ID, "type": "sub"}, {"instId": "alien__L1", "type": "cancel"}])
    assert sp.filter_snapshot_for_target_group(raw)["substitutions"] == [{"instId": LANG_ID, "type": "sub"}]


@pytest.mark.parametrize(
    ("snap", "expected"),
    [
        ({"substitutions": [], "publishedWeeks": []}, ("etag-1", "lm-1")),
        ({"substitutions": []}, (None, None)),
        ({"schedule": {}}, (None, None)),
    ],
)
def test_restorable_cache_headers_resets_legacy_snapshot(snap: dict[str, Any], expected: tuple) -> None:
    meta = {"etag": "etag-1", "last_modified": "lm-1"}
    assert sp._restorable_cache_headers(snap, meta) == expected
