"""
Клиент для обращения к сервису para-api по протоколу gRPC (с HTTP fallback).

Используется ботом, воркером и решателем ДЗ. Переиспользует постоянный асинхронный
gRPC-канал через HTTP/2 multiplexing для максимальной производительности.
"""

import asyncio
from datetime import date
from typing import Any

import grpc
import httpx

from api.grpc.converters import proto_to_exam_item, proto_to_lesson
from api.proto import (
    exams_pb2,
    exams_pb2_grpc,
    schedule_pb2,
    schedule_pb2_grpc,
    teachers_pb2,
    teachers_pb2_grpc,
)
from config import (
    API_BASE_URL,
    API_SECRET_KEY,
    GRPC_MAX_MESSAGE_LENGTH,
    GRPC_SERVER_ADDRESS,
)
from core.logger import get_logger
from services.models import ExamItem, Lesson

log = get_logger("api_client")

_CLIENT: httpx.AsyncClient | None = None
_CHANNEL: grpc.aio.Channel | None = None


def _get_client() -> httpx.AsyncClient:
    """Возвращает или создает персистентный HTTP-клиент к para-api."""
    global _CLIENT
    if _CLIENT is None or _CLIENT.is_closed:
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=20, keepalive_expiry=30.0)
        _CLIENT = httpx.AsyncClient(
            base_url=API_BASE_URL,
            headers={"X-API-Key": API_SECRET_KEY},
            timeout=35.0,
            limits=limits,
        )
    return _CLIENT


def _get_grpc_channel() -> grpc.aio.Channel:
    """Возвращает или создает персистентный асинхронный gRPC канал."""
    global _CHANNEL
    if _CHANNEL is None:
        options = [
            ("grpc.max_receive_message_length", GRPC_MAX_MESSAGE_LENGTH),
            ("grpc.max_send_message_length", GRPC_MAX_MESSAGE_LENGTH),
        ]
        _CHANNEL = grpc.aio.insecure_channel(GRPC_SERVER_ADDRESS, options=options)
    return _CHANNEL


async def close_api_client() -> None:
    """Закрывает HTTP-клиент и gRPC канал при остановке сервиса."""
    global _CLIENT, _CHANNEL
    if _CLIENT and not _CLIENT.is_closed:
        await _CLIENT.aclose()
        _CLIENT = None
    if _CHANNEL:
        await _CHANNEL.close()
        _CHANNEL = None


async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Выполняет GET-запрос к para-api с retry при временном сбое."""
    for attempt in range(2):
        try:
            res = await _get_client().get(path, params=params)
            res.raise_for_status()
            return res.json()
        except (httpx.TransportError, httpx.HTTPStatusError) as e:
            if attempt == 0:
                log.warning(f"⚠️ Сбой запроса к {path} ({e}), повтор через 1 сек...")
                await asyncio.sleep(1.0)
            else:
                log.error(f"❌ Ошибка запроса к {path} после повтора: {e}")
                raise


async def _fetch_day_schedule_grpc(target_date: date | None, force_refresh: bool) -> dict[str, Any]:
    """Вызывает gRPC метод ScheduleService.GetDaySchedule."""
    stub = schedule_pb2_grpc.ScheduleServiceStub(_get_grpc_channel())
    req = schedule_pb2.DayScheduleRequest(
        target_date=target_date.isoformat() if target_date else "",
        force_refresh=force_refresh,
    )
    resp = await stub.GetDaySchedule(req, timeout=30.0)
    lessons = [proto_to_lesson(item).model_dump() for item in resp.lessons]
    return {"date": resp.date, "lessons": lessons}


async def fetch_day_schedule(target_date: date | None = None, force_refresh: bool = False) -> dict[str, Any]:
    """Запрашивает расписание на день через gRPC с fallback на HTTP."""
    try:
        return await _fetch_day_schedule_grpc(target_date, force_refresh)
    except Exception as e:
        log.warning(f"⚠️ gRPC GetDaySchedule не ответил ({e}), переключаемся на HTTP")
        params: dict[str, Any] = {"force_refresh": force_refresh}
        if target_date:
            params["target_date"] = target_date.isoformat()
        return await _api_get("/schedule/day", params=params)


async def _fetch_week_schedule_grpc(monday: date | None, force_refresh: bool) -> dict[str, Any]:
    """Вызывает gRPC метод ScheduleService.GetWeekSchedule."""
    stub = schedule_pb2_grpc.ScheduleServiceStub(_get_grpc_channel())
    req = schedule_pb2.WeekScheduleRequest(
        monday=monday.isoformat() if monday else "",
        force_refresh=force_refresh,
    )
    resp = await stub.GetWeekSchedule(req, timeout=30.0)
    days = [{"date": d.date, "lessons": [proto_to_lesson(item).model_dump() for item in d.lessons]} for d in resp.days]
    return {"monday": resp.monday, "days": days}


async def fetch_week_schedule(monday: date | None = None, force_refresh: bool = False) -> dict[str, Any]:
    """Запрашивает расписание на неделю через gRPC с fallback на HTTP."""
    try:
        return await _fetch_week_schedule_grpc(monday, force_refresh)
    except Exception as e:
        log.warning(f"⚠️ gRPC GetWeekSchedule не ответил ({e}), переключаемся на HTTP")
        params: dict[str, Any] = {"force_refresh": force_refresh}
        if monday:
            params["monday"] = monday.isoformat()
        return await _api_get("/schedule/week", params=params)


async def _fetch_exams_grpc(force_refresh: bool) -> dict[str, Any]:
    """Вызывает gRPC метод ExamsService.GetExams."""
    stub = exams_pb2_grpc.ExamsServiceStub(_get_grpc_channel())
    req = exams_pb2.ExamsRequest(force_refresh=force_refresh)
    resp = await stub.GetExams(req, timeout=30.0)
    exams = [proto_to_exam_item(item).model_dump() for item in resp.exams]
    return {"count": resp.count, "exams": exams}


async def fetch_exams(force_refresh: bool = False) -> dict[str, Any]:
    """Запрашивает список экзаменов через gRPC с fallback на HTTP."""
    try:
        return await _fetch_exams_grpc(force_refresh)
    except Exception as e:
        log.warning(f"⚠️ gRPC GetExams не ответил ({e}), переключаемся на HTTP")
        return await _api_get("/exams")


async def _fetch_teachers_grpc(force_refresh: bool) -> dict[str, Any]:
    """Вызывает gRPC метод TeachersService.GetTeachers."""
    stub = teachers_pb2_grpc.TeachersServiceStub(_get_grpc_channel())
    req = teachers_pb2.TeachersRequest(force_refresh=force_refresh)
    resp = await stub.GetTeachers(req, timeout=30.0)
    teachers = {k: {"full_name": v.full_name, "link_info": v.link_info} for k, v in resp.teachers.items()}
    return {"count": resp.count, "teachers": teachers}


async def fetch_teachers(force_refresh: bool = False) -> dict[str, Any]:
    """Запрашивает контакты преподавателей через gRPC с fallback на HTTP."""
    try:
        return await _fetch_teachers_grpc(force_refresh)
    except Exception as e:
        log.warning(f"⚠️ gRPC GetTeachers не ответил ({e}), переключаемся на HTTP")
        return await _api_get("/teachers", params={"force_refresh": force_refresh})


async def get_api_schedule_for_date(target_date: date | None = None, force_refresh: bool = False) -> list[Lesson]:
    """Запрашивает расписание на день и десериализует в модели Lesson."""
    data = await fetch_day_schedule(target_date=target_date, force_refresh=force_refresh)
    return [Lesson(**item) for item in data.get("lessons", [])]


async def get_api_week_schedule(monday: date | None = None, force_refresh: bool = False) -> list[tuple[date, list[Lesson]]]:
    """Запрашивает расписание на неделю и возвращает пары (дата, уроки)."""
    data = await fetch_week_schedule(monday=monday, force_refresh=force_refresh)
    result: list[tuple[date, list[Lesson]]] = []
    for day in data.get("days", []):
        day_date = date.fromisoformat(day["date"])
        lessons = [Lesson(**item) for item in day.get("lessons", [])]
        result.append((day_date, lessons))
    return result


async def get_api_exams(force_refresh: bool = False) -> list[ExamItem]:
    """Запрашивает список экзаменов и десериализует в модели ExamItem."""
    data = await fetch_exams(force_refresh=force_refresh)
    return [ExamItem(**item) for item in data.get("exams", [])]


async def get_api_teachers(force_refresh: bool = False) -> dict[str, Any]:
    """Запрашивает контакты преподавателей (словарь фамилия -> контакты)."""
    data = await fetch_teachers(force_refresh=force_refresh)
    return data.get("teachers", {})
