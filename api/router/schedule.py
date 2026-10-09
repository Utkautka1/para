"""
Роутер расписания — GET /schedule (day, today, tomorrow, week, current, refresh).

Предоставляет чистые данные расписания занятий группы 1-КПД-3
с валидацией прав тестера или API-ключа.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, Query

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.schedule import (
    CurrentLessonResponse,
    DayScheduleResponse,
    ScheduleRefreshResponse,
    WeekDayItem,
    WeekScheduleResponse,
)
from config import TIMEZONE
from core.redis_cache import cache_flush
from services.models import Lesson
from services.schedule_parser import get_schedule_for_date, get_week_schedule

router = APIRouter(tags=["Schedule"], prefix="/schedule", dependencies=[Depends(verify_api_or_tester)])


def _current_monday() -> date:
    """Вычисляет понедельник текущей недели."""
    today = datetime.now(TIMEZONE).date()
    return today - timedelta(days=today.weekday())


@router.get("/day", response_model=DayScheduleResponse)
async def schedule_day(
    target_date: Optional[date] = Query(default=None, description="YYYY-MM-DD, по умолчанию сегодня"),
    force_refresh: bool = Query(default=False),
) -> DayScheduleResponse:
    """Расписание на конкретный учебный день."""
    day = target_date or datetime.now(TIMEZONE).date()
    lessons = await get_schedule_for_date(day, force_refresh=force_refresh)
    return DayScheduleResponse(date=day, lessons=lessons)


@router.get("/today", response_model=DayScheduleResponse)
async def schedule_today(force_refresh: bool = Query(default=False)) -> DayScheduleResponse:
    """Расписание занятий на сегодня."""
    today = datetime.now(TIMEZONE).date()
    lessons = await get_schedule_for_date(today, force_refresh=force_refresh)
    return DayScheduleResponse(date=today, lessons=lessons)


@router.get("/tomorrow", response_model=DayScheduleResponse)
async def schedule_tomorrow(force_refresh: bool = Query(default=False)) -> DayScheduleResponse:
    """Расписание занятий на завтра."""
    tomorrow = datetime.now(TIMEZONE).date() + timedelta(days=1)
    lessons = await get_schedule_for_date(tomorrow, force_refresh=force_refresh)
    return DayScheduleResponse(date=tomorrow, lessons=lessons)


@router.get("/week", response_model=WeekScheduleResponse)
async def schedule_week(
    monday: Optional[date] = Query(default=None, description="Понедельник недели (YYYY-MM-DD)"),
    force_refresh: bool = Query(default=False),
) -> WeekScheduleResponse:
    """Расписание занятий на целую неделю (пн—сб)."""
    mon = monday or _current_monday()
    raw = await get_week_schedule(mon, force_refresh=force_refresh)
    days = [WeekDayItem(date=d, lessons=ls) for d, ls in raw]
    return WeekScheduleResponse(monday=mon, days=days)


def _find_current_and_next(lessons: List[Lesson], now_time: str) -> Tuple[Optional[Lesson], Optional[Lesson]]:
    """Находит текущую и ближайшую следующую пару по текущему времени."""
    curr, nxt = None, None
    for l in sorted(lessons, key=lambda x: x.period):
        times = l.time_str.split("-") if "-" in l.time_str else []
        if len(times) == 2:
            start, end = times[0].strip(), times[1].strip()
            if start <= now_time <= end:
                curr = l
            elif now_time < start and nxt is None:
                nxt = l
    return curr, nxt


@router.get("/current", response_model=CurrentLessonResponse)
async def schedule_current() -> CurrentLessonResponse:
    """Информация о текущем и следующем занятии прямо сейчас."""
    now_dt = datetime.now(TIMEZONE)
    lessons = await get_schedule_for_date(now_dt.date())
    curr, nxt = _find_current_and_next(lessons, now_dt.strftime("%H:%M"))
    return CurrentLessonResponse(
        is_active_now=curr is not None,
        current_lesson=curr,
        next_lesson=nxt,
    )


@router.post("/refresh", response_model=ScheduleRefreshResponse, dependencies=[Depends(verify_admin_access)])
async def schedule_refresh() -> ScheduleRefreshResponse:
    """Принудительная очистка кэша расписания (Admin only)."""
    deleted = await cache_flush(pattern="sched:*")
    now_str = datetime.now(TIMEZONE).isoformat()
    return ScheduleRefreshResponse(status="ok", flushed_keys=deleted, timestamp=now_str)
