"""
Роутер экзаменов — GET /exams, GET /exams/upcoming, POST /exams/refresh.

Возвращает контрольные мероприятия (зачёты, экзамены, курсовые)
с привязкой к неделям семестра.
"""

from datetime import datetime

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
    """
    Возвращает полный реестр экзаменов и зачётов текущего семестра.

    Извлекает нормализованные данные из кэша расписания КТМУ.
    Используется веб-клиентами и ботом для вывода итоговой сессии.

    Возвращает ExamsResponse со списком всех экзаменов и их количеством.
    """

    exams = await get_group_exams()

    return ExamsResponse(count=len(exams), exams=exams)


async def _resolve_current_week() -> int:
    """
    Вычисляет номер текущей учебной недели семестра.

    Берёт дату начала семестра из конфигурации расписания и сопоставляет с сегодняшним днем.
    Использует часовой пояс колледжа для исключения расхождений в полночь.

    Возвращает целочисленный номер текущей недели (1-25).
    """

    data = await fetch_schedule_data(force_refresh=False)
    sem_start = data.get("config", {}).get("semesterStart", "2026-09-01") if data else "2026-09-01"
    today = datetime.now(TIMEZONE).date()

    return calculate_week_number(today, sem_start)


@router.get("/upcoming", response_model=UpcomingExamsResponse)
async def upcoming_exams(
    weeks_ahead: int = Query(default=4, ge=1, le=20, description="Горизонт планирования (недель)"),
) -> UpcomingExamsResponse:
    """
    Возвращает список ближайших контрольных мероприятий на N недель вперёд.

    Фильтрует сессионные экзамены по диапазону [cur_week, cur_week + weeks_ahead].
    Предотвращает перегрузку интерфейса лишними событиями конца семестра.

    Возвращает UpcomingExamsResponse с отфильтрованными экзаменами.
    """

    cur_week = await _resolve_current_week()
    exams = await get_group_exams()
    filtered: list[ExamItem] = [
        e for e in exams if any(cur_week <= w <= cur_week + weeks_ahead for w in e.weeks)
    ]

    return UpcomingExamsResponse(current_week=cur_week, count=len(filtered), upcoming_exams=filtered)


@router.post("/refresh", response_model=ExamsRefreshResponse, dependencies=[Depends(verify_admin_access)])
async def refresh_exams() -> ExamsRefreshResponse:
    """
    Выполняет принудительное обновление расписания экзаменов из API колледжа.

    Инвалидирует кэши и заново парсит актуальный JSON с внешнего сервера.
    Защищён зависимостью verify_admin_access от несанкционированного спама.

    Возвращает ExamsRefreshResponse со статусом 'ok' и количеством экзаменов.
    """

    await fetch_schedule_data(force_refresh=True)
    exams = await get_group_exams()

    return ExamsRefreshResponse(status="ok", updated_count=len(exams))

