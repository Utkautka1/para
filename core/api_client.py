"""
HTTP-клиент для обращения к внутреннему API (para-api).

Используется ботом и воркером вместо прямых вызовов services/*.
Клиент персистентный — переиспользует TCP-соединение через keep-alive.
"""

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import httpx

from config import API_BASE_URL, API_SECRET_KEY
from core.logger import get_logger
from services.models import ExamItem, Lesson

log = get_logger("api_client")

_CLIENT: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    """Возвращает или создает персистентный HTTP-клиент к para-api."""
    global _CLIENT
    if _CLIENT is None or _CLIENT.is_closed:
        _CLIENT = httpx.AsyncClient(
            base_url=API_BASE_URL,
            headers={"X-API-Key": API_SECRET_KEY},
            timeout=30.0,
        )
    return _CLIENT


async def close_api_client() -> None:
    """Закрывает HTTP-клиент при остановке сервиса."""
    global _CLIENT
    if _CLIENT and not _CLIENT.is_closed:
        await _CLIENT.aclose()
        _CLIENT = None


async def fetch_day_schedule(
    target_date: Optional[date] = None,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """
    Запрашивает расписание на день через GET /schedule/day.

    :return: {"date": "...", "lessons": [...]}
    """
    params: Dict[str, Any] = {"force_refresh": force_refresh}
    if target_date:
        params["target_date"] = target_date.isoformat()
    res = await _get_client().get("/schedule/day", params=params)
    res.raise_for_status()
    return res.json()


async def fetch_week_schedule(
    monday: Optional[date] = None,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """
    Запрашивает расписание на неделю через GET /schedule/week.

    :return: {"monday": "...", "days": [...]}
    """
    params: Dict[str, Any] = {"force_refresh": force_refresh}
    if monday:
        params["monday"] = monday.isoformat()
    res = await _get_client().get("/schedule/week", params=params)
    res.raise_for_status()
    return res.json()


async def fetch_exams() -> Dict[str, Any]:
    """
    Запрашивает список экзаменов через GET /exams.

    :return: {"count": N, "exams": [...]}
    """
    res = await _get_client().get("/exams")
    res.raise_for_status()
    return res.json()


async def fetch_teachers(
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """
    Запрашивает контакты преподавателей через GET /teachers.

    :return: {"count": N, "teachers": {...}}
    """
    params = {"force_refresh": force_refresh}
    res = await _get_client().get("/teachers", params=params)
    res.raise_for_status()
    return res.json()


async def get_api_schedule_for_date(
    target_date: Optional[date] = None,
    force_refresh: bool = False,
) -> List[Lesson]:
    """Запрашивает расписание на день и десериализует в модели Lesson."""
    data = await fetch_day_schedule(target_date=target_date, force_refresh=force_refresh)
    return [Lesson(**item) for item in data.get("lessons", [])]


async def get_api_week_schedule(
    monday: Optional[date] = None,
    force_refresh: bool = False,
) -> List[Tuple[date, List[Lesson]]]:
    """Запрашивает расписание на неделю и возвращает пары (дата, уроки)."""
    data = await fetch_week_schedule(monday=monday, force_refresh=force_refresh)
    result: List[Tuple[date, List[Lesson]]] = []
    for day in data.get("days", []):
        day_date = date.fromisoformat(day["date"])
        lessons = [Lesson(**item) for item in day.get("lessons", [])]
        result.append((day_date, lessons))
    return result


async def get_api_exams() -> List[ExamItem]:
    """Запрашивает список экзаменов и десериализует в модели ExamItem."""
    data = await fetch_exams()
    return [ExamItem(**item) for item in data.get("exams", [])]


async def get_api_teachers(force_refresh: bool = False) -> Dict[str, Any]:
    """Запрашивает контакты преподавателей (словарь фамилия -> контакты)."""
    data = await fetch_teachers(force_refresh=force_refresh)
    return data.get("teachers", {})

