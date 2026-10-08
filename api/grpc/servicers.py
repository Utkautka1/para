"""
Сервисеры gRPC (ScheduleService, ExamsService, TeachersService).

Обрабатывают входящие RPC-вызовы от микросервисов бота и воркера,
транслируя Protobuf-запросы во внутренние асинхронные парсеры с кэшированием.
"""

from datetime import date, datetime, timedelta

import grpc

from api.grpc.converters import (
    exam_item_to_proto,
    lesson_to_proto,
    teachers_dict_to_proto,
    week_days_to_proto,
)
from api.proto import (
    exams_pb2,
    exams_pb2_grpc,
    schedule_pb2,
    schedule_pb2_grpc,
    teachers_pb2,
    teachers_pb2_grpc,
)
from config import TIMEZONE
from core.logger import get_logger
from integrations.docx_parser import get_teacher_links
from services.exam_parser import get_group_exams
from services.schedule_parser import get_schedule_for_date, get_week_schedule

log = get_logger("grpc_servicers")


def _resolve_day(raw_date: str) -> date:
    """Парсит ISO дату или возвращает сегодняшнюю дату по МСК."""
    if raw_date:
        return date.fromisoformat(raw_date)
    return datetime.now(TIMEZONE).date()


def _resolve_monday(raw_monday: str) -> date:
    """Парсит дату понедельника или вычисляет текущий понедельник."""
    if raw_monday:
        return date.fromisoformat(raw_monday)
    today = datetime.now(TIMEZONE).date()
    return today - timedelta(days=today.weekday())


class ScheduleServicer(schedule_pb2_grpc.ScheduleServiceServicer):
    """Серверный обработчик gRPC-запросов расписания."""

    async def GetDaySchedule(
        self,
        request: schedule_pb2.DayScheduleRequest,
        context: grpc.aio.ServicerContext,
    ) -> schedule_pb2.DayScheduleResponse:
        """
        Возвращает расписание занятий на день.

        Использует кэш L1/L2 расписания и отдает типизированный Protobuf-ответ.
        Возвращает DayScheduleResponse со списком уроков.
        """
        log.debug(f"gRPC GetDaySchedule: date='{request.target_date}', refresh={request.force_refresh}")
        target = _resolve_day(request.target_date)
        lessons = await get_schedule_for_date(target, force_refresh=request.force_refresh)
        proto_lessons = [lesson_to_proto(item) for item in lessons]
        return schedule_pb2.DayScheduleResponse(date=target.isoformat(), lessons=proto_lessons)

    async def GetWeekSchedule(
        self,
        request: schedule_pb2.WeekScheduleRequest,
        context: grpc.aio.ServicerContext,
    ) -> schedule_pb2.WeekScheduleResponse:
        """
        Возвращает недельное расписание занятий.

        Парсит неделю и возвращает список дней от понедельника до субботы.
        Возвращает WeekScheduleResponse с вложенными днями и парами.
        """
        log.debug(f"gRPC GetWeekSchedule: monday='{request.monday}', refresh={request.force_refresh}")
        mon = _resolve_monday(request.monday)
        raw_days = await get_week_schedule(mon, force_refresh=request.force_refresh)
        days_proto = week_days_to_proto(raw_days)
        return schedule_pb2.WeekScheduleResponse(monday=mon.isoformat(), days=days_proto)


class ExamsServicer(exams_pb2_grpc.ExamsServiceServicer):
    """Серверный обработчик gRPC-запросов экзаменов."""

    async def GetExams(
        self,
        request: exams_pb2.ExamsRequest,
        context: grpc.aio.ServicerContext,
    ) -> exams_pb2.ExamsResponse:
        """
        Возвращает список контрольных мероприятий и экзаменов.

        Вызывает парсер экзаменов с поддержкой принудительного обновления.
        Возвращает ExamsResponse с массивом ExamItemProto.
        """
        log.debug(f"gRPC GetExams: refresh={request.force_refresh}")
        exams = await get_group_exams()
        proto_exams = [exam_item_to_proto(item) for item in exams]
        return exams_pb2.ExamsResponse(count=len(proto_exams), exams=proto_exams)


class TeachersServicer(teachers_pb2_grpc.TeachersServiceServicer):
    """Серверный обработчик gRPC-запросов преподавателей."""

    async def GetTeachers(
        self,
        request: teachers_pb2.TeachersRequest,
        context: grpc.aio.ServicerContext,
    ) -> teachers_pb2.TeachersResponse:
        """
        Возвращает контакты преподавателей из справочника.

        Загружает файл преподавателей из Яндекс Диска через docx_parser.
        Возвращает TeachersResponse с отображением фамилий на ссылки.
        """
        log.debug(f"gRPC GetTeachers: refresh={request.force_refresh}")
        raw_map = await get_teacher_links(force_refresh=request.force_refresh)
        return teachers_dict_to_proto(raw_map)
