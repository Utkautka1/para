"""
Роутер расписания — GET /schedule (day, today, tomorrow, week, current, refresh).

Предоставляет чистые данные расписания занятий группы 1-КПД-3
с валидацией прав тестера или API-ключа.
"""

from datetime import date, datetime, timedelta

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
    """
    Вычисляет календарную дату понедельника текущей недели.

    Определяет смещение через today.weekday() по часовому поясу колледжа.
    Служит точкой отсчёта для недельного расписания по умолчанию.

    Возвращает объект date понедельника текущей недели.
    """

    today = datetime.now(TIMEZONE).date()

    return today - timedelta(days=today.weekday())


@router.get("/day", response_model=DayScheduleResponse)
async def schedule_day(
    target_date: date | None = Query(default=None, description="YYYY-MM-DD, по умолчанию сегодня"),
    force_refresh: bool = Query(default=False),
) -> DayScheduleResponse:
    """
    Возвращает расписание занятий на конкретную указанную дату.

    Если target_date не передан, использует сегодняшнее число по часовому поясу колледжа.
    Поддерживает флаг force_refresh для обхода локального кэша парсинга.

    Возвращает DayScheduleResponse с датой и списком занятий.
    """

    day = target_date or datetime.now(TIMEZONE).date()
    lessons = await get_schedule_for_date(day, force_refresh=force_refresh)

    return DayScheduleResponse(date=day, lessons=lessons)


@router.get("/today", response_model=DayScheduleResponse)
async def schedule_today(force_refresh: bool = Query(default=False)) -> DayScheduleResponse:
    """
    Возвращает расписание занятий группы на сегодняшний день.

    Служит удобным шорткатом для клиентов без необходимости передачи query-параметров.
    Применяет мгновенное извлечение из Redis-кэша.

    Возвращает DayScheduleResponse на текущую дату.
    """

    today = datetime.now(TIMEZONE).date()
    lessons = await get_schedule_for_date(today, force_refresh=force_refresh)

    return DayScheduleResponse(date=today, lessons=lessons)


@router.get("/tomorrow", response_model=DayScheduleResponse)
async def schedule_tomorrow(force_refresh: bool = Query(default=False)) -> DayScheduleResponse:
    """
    Возвращает расписание занятий группы на завтрашний день.

    Вычисляет дату завтра через timedelta(days=1) относительно часового пояса колледжа.
    Используется ботом и Mini App для вечернего планирования пар.

    Возвращает DayScheduleResponse на завтрашний день.
    """

    tomorrow = datetime.now(TIMEZONE).date() + timedelta(days=1)
    lessons = await get_schedule_for_date(tomorrow, force_refresh=force_refresh)

    return DayScheduleResponse(date=tomorrow, lessons=lessons)


@router.get("/week", response_model=WeekScheduleResponse)
async def schedule_week(
    monday: date | None = Query(default=None, description="Понедельник недели (YYYY-MM-DD)"),
    force_refresh: bool = Query(default=False),
) -> WeekScheduleResponse:
    """
    Возвращает полное расписание занятий на 6 учебных дней недели (пн-сб).

    Если дата понедельника не указана, вычисляет понедельник текущей недели.
    Агрегирует списки пар по каждому учебному дню в единый ответ.

    Возвращает WeekScheduleResponse с понедельником и днями недели.
    """

    mon = monday or _current_monday()
    raw = await get_week_schedule(mon, force_refresh=force_refresh)
    days = [WeekDayItem(date=d, lessons=ls) for d, ls in raw]

    return WeekScheduleResponse(monday=mon, days=days)


def _match_lesson_interval(lesson: Lesson, now_time: str) -> tuple[bool, bool]:
    """
    Проверяет, идёт ли пара прямо сейчас или начнётся в будущем.

    Парсит временной интервал пары (например, '09:00 - 10:30') и сравнивает с now_time.
    Защищает от некорректных форматов времени при частичной синхронизации.

    Возвращает кортеж (is_current, is_future).
    """

    times = lesson.time_str.split("-") if "-" in lesson.time_str else []
    if len(times) != 2:
        return False, False

    start, end = times[0].strip(), times[1].strip()

    return (start <= now_time <= end), (now_time < start)


def _find_current_and_next(lessons: list[Lesson], now_time: str) -> tuple[Lesson | None, Lesson | None]:
    """
    Находит текущую активную пару и ближайшую следующую по времени.

    Итерируется по отсортированному списку пар дня и вызывает интервальную проверку.
    Останавливает поиск следующей пары на первом найденном совпадении.

    Возвращает кортеж (current_lesson, next_lesson) или None для отсутствующих.
    """

    curr, nxt = None, None
    for item in sorted(lessons, key=lambda x: x.period):
        is_cur, is_fut = _match_lesson_interval(item, now_time)
        if is_cur:
            curr = item
        elif is_fut and nxt is None:
            nxt = item

    return curr, nxt


@router.get("/current", response_model=CurrentLessonResponse)
async def schedule_current() -> CurrentLessonResponse:
    """
    Определяет текущую активную пару и следующую пару в реальном времени.

    Используется виджетом Telegram Mini App для динамического статуса 'Сейчас идёт'.
    Опирается на серверное время в таймзоне колледжа Europe/Moscow.

    Возвращает CurrentLessonResponse с текущим и следующим занятием.
    """

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
    """
    Принудительно сбрасывает кэш расписания в Redis и оперативной памяти.

    Удаляет все ключи по маске 'sched:*' и сбрасывает локальные структуры парсера.
    Защищён verify_admin_access от несанкционированного сброса.

    Возвращает ScheduleRefreshResponse с количеством сброшенных ключей.
    """

    deleted = await cache_flush(pattern="sched:*")
    now_str = datetime.now(TIMEZONE).isoformat()

    return ScheduleRefreshResponse(status="ok", flushed_keys=deleted, timestamp=now_str)
