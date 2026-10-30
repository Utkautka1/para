"""
Unit-тесты для Pydantic-моделей сервисов и схем FastAPI (services/models.py, api/schemas/).

Проверяет:
  1. Валидацию обязательных полей и дефолтных значений в Lesson и ExamItem
  2. Сериализацию и десериализацию моделей расписания и экзаменов
  3. Структуру схем ответов API (DayScheduleResponse, WeekScheduleResponse, TeachersResponse)
  4. Корректность типов и валидацию некорректных данных
"""

from datetime import date

import pytest
from pydantic import ValidationError

from api.schemas.exams import ExamsResponse
from api.schemas.schedule import DayScheduleResponse, WeekDayItem, WeekScheduleResponse
from api.schemas.teachers import TeacherItem, TeachersResponse
from services.models import ExamItem, Lesson


def test_lesson_model_defaults() -> None:
    """Проверяет значения по умолчанию для модели Lesson."""
    lesson = Lesson(
        period=1,
        time_str="10:05-11:30",
        subject="Информатика",
        lesson_type="Практика",
        teacher="Петров П.П.",
        is_remote=False,
        room="201",
        address="Цветочная ул., 8",
    )
    assert lesson.subgroup == 0
    assert lesson.is_stream is False
    assert lesson.remote_link is None
    assert lesson.remote_passcode is None
    assert lesson.remote_meeting_id is None


def test_lesson_model_required_fields_validation() -> None:
    """Проверяет выброс ValidationError при отсутствии обязательных полей."""
    with pytest.raises(ValidationError):
        Lesson(period=0, time_str="08:30-10:00")  # Отсутствуют subject, teacher и др.


@pytest.mark.parametrize(
    "subgroup,is_stream,is_remote",
    [
        (0, False, False),
        (1, False, True),
        (2, True, False),
        (1, True, True),
    ],
)
def test_lesson_model_matrix(subgroup: int, is_stream: bool, is_remote: bool) -> None:
    """Проверяет создание моделей Lesson с различными комбинациями флагов."""
    lesson = Lesson(
        period=0,
        time_str="08:30-10:00",
        subject="Математика",
        lesson_type="Лекция",
        teacher="Иванов И.И.",
        is_remote=is_remote,
        room="101",
        address="Цветочная ул., 8",
        subgroup=subgroup,
        is_stream=is_stream,
    )
    assert lesson.subgroup == subgroup
    assert lesson.is_stream is is_stream
    assert lesson.is_remote is is_remote


def test_exam_item_defaults() -> None:
    """Проверяет значения по умолчанию для ExamItem."""
    exam = ExamItem(
        subject="Физика",
        exam_type="Экзамен",
        teacher="Сидоров С.С.",
        room="105",
        address="Вознесенский пр., 44",
        weeks=[10, 11],
    )
    assert exam.subgroup == 0
    assert exam.format_str == "Очно"
    assert exam.weeks == [10, 11]


def test_day_schedule_response_serialization() -> None:
    """Проверяет схему ответа DayScheduleResponse."""
    d = date(2026, 9, 28)
    lesson = Lesson(
        period=0,
        time_str="08:30-10:00",
        subject="История",
        lesson_type="Семинар",
        teacher="Васильев В.В.",
        is_remote=False,
        room="303",
        address="Цветочная ул., 8",
    )
    resp = DayScheduleResponse(date=d, lessons=[lesson])
    assert resp.date == d
    assert len(resp.lessons) == 1
    dump = resp.model_dump()
    assert dump["date"] == d
    assert dump["lessons"][0]["subject"] == "История"


def test_week_schedule_response_serialization() -> None:
    """Проверяет схему недельного ответа WeekScheduleResponse."""
    monday = date(2026, 9, 28)
    day_item = WeekDayItem(date=monday, lessons=[])
    resp = WeekScheduleResponse(monday=monday, days=[day_item])
    assert resp.monday == monday
    assert len(resp.days) == 1


def test_exams_response_serialization() -> None:
    """Проверяет схему ответа ExamsResponse."""
    item = ExamItem(
        subject="Информатика",
        exam_type="Зачёт",
        teacher="Козлов К.К.",
        room="202",
        address="Цветочная",
        weeks=[15],
    )
    resp = ExamsResponse(count=1, exams=[item])
    assert resp.count == 1
    assert resp.exams[0].subject == "Информатика"


def test_teachers_response_serialization() -> None:
    """Проверяет схему справочника преподавателей TeachersResponse."""
    t_item = TeacherItem(
        full_name="Иванов Иван Иванович",
        link_info="https://zoom.us/j/123",
    )
    resp = TeachersResponse(count=1, teachers={"иванов": t_item})
    assert resp.count == 1
    assert resp.teachers["иванов"].full_name == "Иванов Иван Иванович"
    assert resp.teachers["иванов"].link_info == "https://zoom.us/j/123"
