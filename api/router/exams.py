"""
Роутер экзаменов — GET /exams, GET /exams/upcoming, POST /exams/refresh.

Возвращает контрольные мероприятия (зачёты, экзамены, курсовые)
с привязкой к неделям семестра.
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.exams import ExamsRefreshResponse, ExamsResponse, UpcomingExamsResponse
from config import TIMEZONE
from services.exam_parser import get_group_exams
from services.models import ExamItem
from services.schedule_parser import calculate_week_number, fetch_schedule_data

router = APIRouter(tags=["Exams"], prefix="/exams", dependencies=[Depends(verify_api_or_tester)])


@router.get("", response_model=ExamsResponse)
async def list_exams() -> ExamsResponse:
    """Полный список аттестаций и экзаменов группы."""
    exams = await get_group_exams()
    return ExamsResponse(count=len(exams), exams=exams)


async def _resolve_current_week() -> int:
    """Определяет номер текущей учебной недели семестра."""
    data = await fetch_schedule_data(force_refresh=False)
    sem_start = data.get("config", {}).get("semesterStart", "2026-09-01") if data else "2026-09-01"
    today = datetime.now(TIMEZONE).date()
    return calculate_week_number(today, sem_start)


@router.get("/upcoming", response_model=UpcomingExamsResponse)
async def upcoming_exams(
    weeks_ahead: int = Query(default=4, ge=1, le=20, description="Горизонт планирования (недель)"),
) -> UpcomingExamsResponse:
    """Ближайшие предстоящие экзамены и зачёты."""
    cur_week = await _resolve_current_week()
    exams = await get_group_exams()
    filtered: List[ExamItem] = [
        e for e in exams if any(cur_week <= w <= cur_week + weeks_ahead for w in e.weeks)
    ]
    return UpcomingExamsResponse(current_week=cur_week, count=len(filtered), upcoming_exams=filtered)


@router.post("/refresh", response_model=ExamsRefreshResponse, dependencies=[Depends(verify_admin_access)])
async def refresh_exams() -> ExamsRefreshResponse:
    """Принудительное обновление расписания экзаменов (Admin only)."""
    await fetch_schedule_data(force_refresh=True)
    exams = await get_group_exams()
    return ExamsRefreshResponse(status="ok", updated_count=len(exams))
