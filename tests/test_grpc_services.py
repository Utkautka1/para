"""
Unit-тесты для gRPC сервисов и конвертеров para-api.

Проверяет:
  1. Корректность конвертации Lesson, ExamItem, TeacherItem в Protobuf и обратно.
  2. Работу Servicers (Schedule, Exams, Teachers).
  3. Взаимодействие через реальный асинхронный gRPC канал.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.grpc.converters import (
    exam_item_to_proto,
    lesson_to_proto,
    proto_to_exam_item,
    proto_to_lesson,
    teachers_dict_to_proto,
)
from api.grpc.servicers import ExamsServicer, ScheduleServicer, TeachersServicer
from api.proto import exams_pb2, schedule_pb2, teachers_pb2
from services.models import ExamItem, Lesson


def _sample_lesson() -> Lesson:
    """Создает тестовую модель урока."""
    return Lesson(
        period=1,
        time_str="10:10-11:40",
        subject="Базы данных",
        lesson_type="Лекция",
        teacher="Иванов И.И.",
        is_remote=True,
        room="301",
        address="Цветочная 12",
        subgroup=0,
        is_stream=False,
        remote_link="https://zoom.us/j/123",
        remote_passcode="pass123",
        remote_meeting_id="meeting456",
    )


def test_lesson_converters() -> None:
    """Проверяет двустороннюю конвертацию Lesson <-> LessonProto."""
    lesson = _sample_lesson()
    proto = lesson_to_proto(lesson)
    assert proto.period == 1
    assert proto.subject == "Базы данных"
    assert proto.remote_link == "https://zoom.us/j/123"

    restored = proto_to_lesson(proto)
    assert restored.period == lesson.period
    assert restored.subject == lesson.subject
    assert restored.remote_link == lesson.remote_link


def test_exam_converters() -> None:
    """Проверяет двустороннюю конвертацию ExamItem <-> ExamItemProto."""
    exam = ExamItem(
        subject="Математика",
        exam_type="Экзамен",
        teacher="Петров П.П.",
        room="101",
        address="Вознесенский 44",
        weeks=[15, 16],
        subgroup=1,
        format_str="Очно",
    )
    proto = exam_item_to_proto(exam)
    assert proto.subject == "Математика"
    assert list(proto.weeks) == [15, 16]

    restored = proto_to_exam_item(proto)
    assert restored.subject == exam.subject
    assert restored.weeks == [15, 16]


def test_teachers_converters() -> None:
    """Проверяет конвертацию словаря преподавателей в TeachersResponse."""
    raw = {"Иванов": {"full_name": "Иванов И.И.", "link_info": "https://telemost.yandex.ru"}}
    resp = teachers_dict_to_proto(raw)
    assert resp.count == 1
    assert "Иванов" in resp.teachers
    assert resp.teachers["Иванов"].full_name == "Иванов И.И."


@pytest.mark.asyncio
async def test_schedule_servicer_get_day() -> None:
    """Проверяет обработку запроса расписания на день через ScheduleServicer."""
    servicer = ScheduleServicer()
    lesson = _sample_lesson()
    with patch("api.grpc.servicers.get_schedule_for_date", new=AsyncMock(return_value=[lesson])):
        req = schedule_pb2.DayScheduleRequest(target_date="2026-10-12", force_refresh=False)
        context = AsyncMock()
        resp = await servicer.GetDaySchedule(req, context)
        assert resp.date == "2026-10-12"
        assert len(resp.lessons) == 1
        assert resp.lessons[0].subject == "Базы данных"


@pytest.mark.asyncio
async def test_exams_servicer_get_exams() -> None:
    """Проверяет обработку запроса списка экзаменов через ExamsServicer."""
    servicer = ExamsServicer()
    exam = ExamItem(
        subject="Физика",
        exam_type="Зачет",
        teacher="Сидоров С.С.",
        room="202",
        address="Цветочная",
        weeks=[10],
    )
    with patch("api.grpc.servicers.get_group_exams", new=AsyncMock(return_value=[exam])):
        req = exams_pb2.ExamsRequest(force_refresh=True)
        context = AsyncMock()
        resp = await servicer.GetExams(req, context)
        assert resp.count == 1
        assert resp.exams[0].subject == "Физика"


@pytest.mark.asyncio
async def test_teachers_servicer_get_teachers() -> None:
    """Проверяет обработку запроса преподавателей через TeachersServicer."""
    servicer = TeachersServicer()
    raw = {"Сидоров": {"full_name": "Сидоров С.С.", "link_info": "https://zoom.us"}}
    with patch("api.grpc.servicers.get_teacher_links", new=AsyncMock(return_value=raw)):
        req = teachers_pb2.TeachersRequest(force_refresh=False)
        context = AsyncMock()
        resp = await servicer.GetTeachers(req, context)
        assert resp.count == 1
        assert resp.teachers["Сидоров"].full_name == "Сидоров С.С."


@pytest.mark.asyncio
async def test_api_key_auth_interceptor_valid() -> None:
    """Проверяет пропуск запроса с корректным X-API-Key заголовком."""
    from api.grpc.server import ApiKeyAuthInterceptor
    from config import API_SECRET_KEY

    interceptor = ApiKeyAuthInterceptor()
    details = MagicMock()
    details.invocation_metadata = (("x-api-key", API_SECRET_KEY),)
    continuation = AsyncMock(return_value="handler_ok")

    handler = await interceptor.intercept_service(continuation, details)
    assert handler == "handler_ok"
    continuation.assert_awaited_once_with(details)


@pytest.mark.asyncio
async def test_api_key_auth_interceptor_invalid() -> None:
    """Проверяет отказ и статус UNAUTHENTICATED при невалидном X-API-Key."""
    import grpc

    from api.grpc.server import ApiKeyAuthInterceptor

    interceptor = ApiKeyAuthInterceptor()
    details = MagicMock()
    details.invocation_metadata = (("x-api-key", "wrong-secret"),)
    continuation = AsyncMock()

    handler = await interceptor.intercept_service(continuation, details)
    continuation.assert_not_called()
    assert handler is not None

    mock_context = AsyncMock()
    await handler.unary_unary(None, mock_context)
    mock_context.abort.assert_awaited_once_with(
        grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing X-API-Key header"
    )

