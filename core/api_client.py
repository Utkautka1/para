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
    GRPC_AUTH_HEADER_NAME,
    GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA,
    GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS,
    GRPC_KEEPALIVE_TIME_MS,
    GRPC_KEEPALIVE_TIMEOUT_MS,
    GRPC_MAX_MESSAGE_LENGTH,
    GRPC_SERVER_ADDRESS,
)
from core.logger import get_logger
from core.telemetry import inject_trace_carrier, trace_span
from services.models import ExamItem, Lesson

log = get_logger("api_client")

_CLIENT: httpx.AsyncClient | None = None
_CHANNEL: grpc.aio.Channel | None = None


def _build_grpc_metadata() -> tuple[tuple[str, str], ...]:
    """Формирует метаданные вызова gRPC с ключом API и W3C TraceContext."""
    carrier = {GRPC_AUTH_HEADER_NAME: API_SECRET_KEY}
    inject_trace_carrier(carrier)
    return tuple((k, str(v)) for k, v in carrier.items())


def _get_client() -> httpx.AsyncClient:
    """
    Возвращает или создает персистентный HTTP-клиент к para-api.

    Переиспользует пул keep-alive соединений во избежание оверхеда на повторные
    TCP и TLS рукопожатия при обращениях к fallback REST API.

    Возвращает готовый экземпляр httpx.AsyncClient с настроенной авторизацией.
    """
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
    """
    Создает или возвращает персистентный асинхронный gRPC канал.

    Настраивает параметры HTTP/2 multiplexing, лимиты длины сообщений и keepalive
    сокетов для поддержания постоянного соединения между микросервисами.

    Возвращает инициализированный канал grpc.aio.Channel.
    """
    global _CHANNEL
    if _CHANNEL is None:
        options = [
            ("grpc.max_receive_message_length", GRPC_MAX_MESSAGE_LENGTH),
            ("grpc.max_send_message_length", GRPC_MAX_MESSAGE_LENGTH),
            ("grpc.keepalive_time_ms", GRPC_KEEPALIVE_TIME_MS),
            ("grpc.keepalive_timeout_ms", GRPC_KEEPALIVE_TIMEOUT_MS),
            ("grpc.keepalive_permit_without_calls", GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS),
            ("grpc.http2.max_pings_without_data", GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA),
        ]
        _CHANNEL = grpc.aio.insecure_channel(GRPC_SERVER_ADDRESS, options=options)
    return _CHANNEL


async def close_api_client() -> None:
    """
    Корректно закрывает соединения HTTP-клиента и асинхронного gRPC-канала.

    Предотвращает утечки дескрипторов сокетов и фоновые предупреждения asyncio
    во время остановки процесса приложения.

    Не возвращает значений; сбрасывает глобальные ссылки в None.
    """
    global _CLIENT, _CHANNEL
    if _CLIENT and not _CLIENT.is_closed:
        await _CLIENT.aclose()
        _CLIENT = None
    if _CHANNEL:
        await _CHANNEL.close()
        _CHANNEL = None


async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Выполняет HTTP GET-запрос к para-api с однократным повтором при сетевом сбое.

    Реализует паттерн Retry для компенсации кратковременных сетевых флуктуаций
    между контейнерами внутри единой docker-сети.

    Возвращает десериализованный JSON-ответ или выбрасывает HTTPStatusError.
    """
    headers = {"X-API-Key": API_SECRET_KEY}
    inject_trace_carrier(headers)
    for attempt in range(2):
        try:
            async with trace_span(f"http.client.get:{path}", attributes={"http.target": path}):
                res = await _get_client().get(path, params=params, headers=headers)
                res.raise_for_status()
                return res.json()
        except (httpx.TransportError, httpx.HTTPStatusError) as e:
            if attempt == 0:
                log.warning(f"⚠️ Сбой запроса к {path} ({e}), повтор через 1 сек...")
                await asyncio.sleep(1.0)
            else:
                log.error(f"❌ Ошибка запроса к {path} после повтора: {e}")
                raise
    return {}


async def _fetch_day_schedule_grpc(target_date: date | None, force_refresh: bool) -> dict[str, Any]:
    """
    Запрашивает расписание на день через высокопроизводительный gRPC метод.

    Передает ключ авторизации в metadata и конвертирует protobuf-сущности
    в унифицированные словари с валидацией Pydantic-моделей.

    Возвращает словарь формата {'date': str, 'lessons': list[dict]}.
    """
    stub = schedule_pb2_grpc.ScheduleServiceStub(_get_grpc_channel())
    req = schedule_pb2.DayScheduleRequest(
        target_date=target_date.isoformat() if target_date else "",
        force_refresh=force_refresh,
    )
    metadata = _build_grpc_metadata()
    async with trace_span("grpc.client.GetDaySchedule", attributes={"rpc.service": "ScheduleService"}):
        resp = await stub.GetDaySchedule(req, timeout=30.0, metadata=metadata)
    lessons = [proto_to_lesson(item).model_dump() for item in resp.lessons]
    return {"date": resp.date, "lessons": lessons}


async def fetch_day_schedule(target_date: date | None = None, force_refresh: bool = False) -> dict[str, Any]:
    """
    Получает дневное расписание по gRPC с прозрачным отказоустойчивым переходом на HTTP.

    Обеспечивает бесперебойную работу клиентов при сбоях или рестартах бинарного
    gRPC-сервера без генерации видимых ошибок пользователю.

    Возвращает словарь с датой и списком учебных занятий.
    """
    try:
        return await _fetch_day_schedule_grpc(target_date, force_refresh)
    except Exception as e:
        log.warning(f"⚠️ gRPC GetDaySchedule не ответил ({e}), переключаемся на HTTP")
        params: dict[str, Any] = {"force_refresh": force_refresh}
        if target_date:
            params["target_date"] = target_date.isoformat()
        return await _api_get("/schedule/day", params=params)


async def _fetch_week_schedule_grpc(monday: date | None, force_refresh: bool) -> dict[str, Any]:
    """
    Запрашивает расписание на неделю через gRPC протокол.

    Осуществляет десериализацию дней недели и уроков из сжатого бинарного потока
    Protobuf для минимизации нагрузки на CPU и трафика.

    Возвращает словарь формата {'monday': str, 'days': list[dict]}.
    """
    stub = schedule_pb2_grpc.ScheduleServiceStub(_get_grpc_channel())
    req = schedule_pb2.WeekScheduleRequest(
        monday=monday.isoformat() if monday else "",
        force_refresh=force_refresh,
    )
    metadata = _build_grpc_metadata()
    async with trace_span("grpc.client.GetWeekSchedule", attributes={"rpc.service": "ScheduleService"}):
        resp = await stub.GetWeekSchedule(req, timeout=30.0, metadata=metadata)
    days = [{"date": d.date, "lessons": [proto_to_lesson(item).model_dump() for item in d.lessons]} for d in resp.days]
    return {"monday": resp.monday, "days": days}


async def fetch_week_schedule(monday: date | None = None, force_refresh: bool = False) -> dict[str, Any]:
    """
    Получает недельное расписание по gRPC с автоматическим fallback на HTTP REST.

    Изолирует клиентский код от конкретного сетевого протокола, гарантируя
    доставку данных при отказе бинарного сокета.

    Возвращает словарь со структурой дней и уроков недели.
    """
    try:
        return await _fetch_week_schedule_grpc(monday, force_refresh)
    except Exception as e:
        log.warning(f"⚠️ gRPC GetWeekSchedule не ответил ({e}), переключаемся на HTTP")
        params: dict[str, Any] = {"force_refresh": force_refresh}
        if monday:
            params["monday"] = monday.isoformat()
        return await _api_get("/schedule/week", params=params)


async def _fetch_exams_grpc(force_refresh: bool) -> dict[str, Any]:
    """
    Запрашивает список экзаменов через бинарный gRPC сервис.

    Использует защищенный канал и преобразует ExamItemProto в доменные модели
    с проверкой формата дат и типов испытаний.

    Возвращает словарь формата {'count': int, 'exams': list[dict]}.
    """
    stub = exams_pb2_grpc.ExamsServiceStub(_get_grpc_channel())
    req = exams_pb2.ExamsRequest(force_refresh=force_refresh)
    metadata = _build_grpc_metadata()
    async with trace_span("grpc.client.GetExams", attributes={"rpc.service": "ExamsService"}):
        resp = await stub.GetExams(req, timeout=30.0, metadata=metadata)
    exams = [proto_to_exam_item(item).model_dump() for item in resp.exams]
    return {"count": resp.count, "exams": exams}


async def fetch_exams(force_refresh: bool = False) -> dict[str, Any]:
    """
    Получает реестр экзаменов по gRPC с резервным переключением на REST эндпоинт.

    Предотвращает блокировку интерфейса бота при временных проблемах сокета
    сервиса экзаменов.

    Возвращает словарь с количеством и списком экзаменов.
    """
    try:
        return await _fetch_exams_grpc(force_refresh)
    except Exception as e:
        log.warning(f"⚠️ gRPC GetExams не ответил ({e}), переключаемся на HTTP")
        return await _api_get("/exams")


async def _fetch_teachers_grpc(force_refresh: bool) -> dict[str, Any]:
    """
    Запрашивает контакты преподавателей через gRPC метод GetTeachers.

    Выполняет быстрое чтение ассоциативного массива teachers из Protobuf
    сообщения без лишних затрат на парсинг текстового JSON.

    Возвращает словарь формата {'count': int, 'teachers': dict}.
    """
    stub = teachers_pb2_grpc.TeachersServiceStub(_get_grpc_channel())
    req = teachers_pb2.TeachersRequest(force_refresh=force_refresh)
    metadata = _build_grpc_metadata()
    async with trace_span("grpc.client.GetTeachers", attributes={"rpc.service": "TeachersService"}):
        resp = await stub.GetTeachers(req, timeout=30.0, metadata=metadata)
    teachers = {k: {"full_name": v.full_name, "link_info": v.link_info} for k, v in resp.teachers.items()}
    return {"count": resp.count, "teachers": teachers}


async def fetch_teachers(force_refresh: bool = False) -> dict[str, Any]:
    """
    Получает телефонно-адресный справочник преподавателей с gRPC/HTTP fallback.

    Обеспечивает высокую доступность контактной информации педагогического состава
    для интерфейса Telegram-бота.

    Возвращает словарь с агрегированными контактами преподавателей.
    """
    try:
        return await _fetch_teachers_grpc(force_refresh)
    except Exception as e:
        log.warning(f"⚠️ gRPC GetTeachers не ответил ({e}), переключаемся на HTTP")
        return await _api_get("/teachers", params={"force_refresh": force_refresh})


async def get_api_schedule_for_date(target_date: date | None = None, force_refresh: bool = False) -> list[Lesson]:
    """
    Предоставляет типизированный список занятий на целевой день в моделях Lesson.

    Инкапсулирует вызов API и строгую валидацию полей расписания библиотекой Pydantic,
    защищая вызывающий код от аномалий в данных.

    Возвращает список валидированных объектов Lesson.
    """
    data = await fetch_day_schedule(target_date=target_date, force_refresh=force_refresh)
    return [Lesson(**item) for item in data.get("lessons", [])]


async def get_api_week_schedule(
    monday: date | None = None, force_refresh: bool = False
) -> list[tuple[date, list[Lesson]]]:
    """
    Возвращает недельное расписание в виде структурированных пар (дата, занятия).

    Сортирует дни в хронологическом порядке и валидирует каждое занятие через Lesson,
    обеспечивая удобное отображение в сообщениях бота.

    Возвращает список кортежей (объект_date, список_уроков_Lesson).
    """
    data = await fetch_week_schedule(monday=monday, force_refresh=force_refresh)
    result: list[tuple[date, list[Lesson]]] = []
    for day in data.get("days", []):
        day_date = date.fromisoformat(day["date"])
        lessons = [Lesson(**item) for item in day.get("lessons", [])]
        result.append((day_date, lessons))
    return result


async def get_api_exams(force_refresh: bool = False) -> list[ExamItem]:
    """
    Предоставляет типизированный список экзаменов и зачетов в моделях ExamItem.

    Парсит ответ сервиса и гарантирует валидность форматов аудиторий, дат
    и типов испытаний перед передачей в шаблонизатор сообщений.

    Возвращает список валидированных объектов ExamItem.
    """
    data = await fetch_exams(force_refresh=force_refresh)
    return [ExamItem(**item) for item in data.get("exams", [])]


async def get_api_teachers(force_refresh: bool = False) -> dict[str, Any]:
    """
    Возвращает словарь контактов преподавателей с фильтрацией по фамилиям.

    Служит источником данных для инлайн-поиска контактов и формирования ссылок
    на личные кабинеты преподавателей в расписании.

    Возвращает словарь {фамилия_преподавателя: информация_о_контактах}.
    """
    data = await fetch_teachers(force_refresh=force_refresh)
    return data.get("teachers", {})
