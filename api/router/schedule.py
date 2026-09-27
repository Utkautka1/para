"""
Роутер расписания — GET /schedule/day и /schedule/week.

Делегирует парсинг и кэширование schedule_parser,
отдаёт чистый JSON без Telegram-форматирования.
"""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query

from api.deps import verify_api_key
from api.schemas.schedule import (
    DayScheduleResponse,
    WeekDayItem,
    WeekScheduleResponse,
)
from config import TIMEZONE
from services.schedule_parser import get_schedule_for_date, get_week_schedule

router = APIRouter(tags=["Schedule"], prefix="/schedule", dependencies=[Depends(verify_api_key)])


@router.get("/day", response_model=DayScheduleResponse)
async def schedule_day(
    target_date: date = Query(default=None, description="YYYY-MM-DD, по умолчанию сегодня"),
    force_refresh: bool = Query(default=False),
) -> DayScheduleResponse:
    """Расписание на указанный день (или сегодня)."""
    day = target_date or datetime.now(TIMEZONE).date()
    lessons = await get_schedule_for_date(day, force_refresh=force_refresh)
    return DayScheduleResponse(date=day, lessons=lessons)


@router.get("/week", response_model=WeekScheduleResponse)
async def schedule_week(
    monday: date = Query(default=None, description="Понедельник недели (YYYY-MM-DD)"),
    force_refresh: bool = Query(default=False),
) -> WeekScheduleResponse:
    """Расписание на целую неделю (пн—сб)."""
    mon = monday or _current_monday()
    raw = await get_week_schedule(mon, force_refresh=force_refresh)
    days = [WeekDayItem(date=d, lessons=ls) for d, ls in raw]
    return WeekScheduleResponse(monday=mon, days=days)


def _current_monday() -> date:
    """Вычисляет понедельник текущей недели."""
    today = datetime.now(TIMEZONE).date()
    return today - timedelta(days=today.weekday())
