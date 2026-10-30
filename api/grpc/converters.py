"""
Конвертеры между доменными Pydantic-моделями и Protobuf-сообщениями.

Обеспечивают строгую валидацию и чистую трансляцию данных без дублирования
логики сериализации между REST и gRPC.
"""

from datetime import date
from typing import Any

from api.proto.exams_pb2 import ExamItemProto
from api.proto.schedule_pb2 import LessonProto, WeekDayProto
from api.proto.teachers_pb2 import TeacherItemProto, TeachersResponse
from services.models import ExamItem, Lesson


def lesson_to_proto(lesson: Lesson) -> LessonProto:
    """
    Конвертирует Pydantic-модель Lesson в Protobuf-сообщение LessonProto.

    Заполняет все поля звонков, аудитории, подгруппы и ссылок на конференции.

    Возвращает объект LessonProto.
    """
    return LessonProto(
        period=lesson.period,
        time_str=lesson.time_str,
        subject=lesson.subject,
        lesson_type=lesson.lesson_type,
        teacher=lesson.teacher,
        is_remote=lesson.is_remote,
        room=lesson.room,
        address=lesson.address,
        subgroup=lesson.subgroup,
        is_stream=lesson.is_stream,
        remote_link=lesson.remote_link or "",
        remote_passcode=lesson.remote_passcode or "",
        remote_meeting_id=lesson.remote_meeting_id or "",
    )


def proto_to_lesson(proto: LessonProto) -> Lesson:
    """
    Конвертирует Protobuf-сообщение LessonProto в модель Lesson.

    Преобразует пустые строки опциональных полей в None.

    Возвращает валидированный экземпляр Pydantic-модели Lesson.
    """
    return Lesson(
        period=proto.period,
        time_str=proto.time_str,
        subject=proto.subject,
        lesson_type=proto.lesson_type,
        teacher=proto.teacher,
        is_remote=proto.is_remote,
        room=proto.room,
        address=proto.address,
        subgroup=proto.subgroup,
        is_stream=proto.is_stream,
        remote_link=proto.remote_link or None,
        remote_passcode=proto.remote_passcode or None,
        remote_meeting_id=proto.remote_meeting_id or None,
    )


def week_days_to_proto(raw_days: list[tuple[date, list[Lesson]]]) -> list[WeekDayProto]:
    """
    Конвертирует список кортежей (дата, пары) в список сообщений WeekDayProto.

    Упаковывает занятия каждого дня учебной недели в типизированный Protobuf-массив.

    Возвращает список объектов WeekDayProto.
    """
    result: list[WeekDayProto] = []

    for day_date, lessons in raw_days:
        proto_lessons = [lesson_to_proto(item) for item in lessons]
        result.append(WeekDayProto(date=day_date.isoformat(), lessons=proto_lessons))

    return result


def exam_item_to_proto(exam: ExamItem) -> ExamItemProto:
    """
    Конвертирует ExamItem в Protobuf-сообщение ExamItemProto.

    Транслирует список номеров недель проведения и форму аттестации.

    Возвращает объект ExamItemProto.
    """
    return ExamItemProto(
        subject=exam.subject,
        exam_type=exam.exam_type,
        teacher=exam.teacher,
        room=exam.room,
        address=exam.address,
        weeks=list(exam.weeks),
        subgroup=exam.subgroup,
        format_str=exam.format_str,
        exam_date=exam.exam_date.isoformat() if exam.exam_date else "",
        pair_number=exam.pair_number or 0,
        time_str=exam.time_str or "",
        is_preliminary=exam.is_preliminary,
    )


def proto_to_exam_item(proto: ExamItemProto) -> ExamItem:
    """
    Конвертирует ExamItemProto в доменную Pydantic-модель ExamItem.

    Восстанавливает типизацию списков недель и текстовых полей аудиторий.

    Возвращает валидированный экземпляр ExamItem.
    """
    return ExamItem(
        subject=proto.subject,
        exam_type=proto.exam_type,
        teacher=proto.teacher,
        room=proto.room,
        address=proto.address,
        weeks=list(proto.weeks),
        subgroup=proto.subgroup,
        format_str=proto.format_str,
        # proto3 не различает «не задано» и пустое значение — пустое считаем None
        exam_date=date.fromisoformat(proto.exam_date) if proto.exam_date else None,
        pair_number=proto.pair_number or None,
        time_str=proto.time_str or None,
        is_preliminary=proto.is_preliminary,
    )


def teachers_dict_to_proto(raw: dict[str, dict[str, Any]]) -> TeachersResponse:
    """
    Конвертирует словарь преподавателей в Protobuf-ответ TeachersResponse.

    Формирует отображение строковых фамилий на элементы TeacherItemProto.

    Возвращает объект TeachersResponse.
    """
    teachers_map: dict[str, TeacherItemProto] = {}

    for name, data in raw.items():
        teachers_map[name] = TeacherItemProto(
            full_name=data.get("full_name", name),
            link_info=data.get("link_info", ""),
        )

    return TeachersResponse(count=len(teachers_map), teachers=teachers_map)
