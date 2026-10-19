"""
Роутер дней рождения — GET /birthdays, upcoming, today.

Предоставляет календарь и расчёт дней до дня рождения одногруппников.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from api.deps import verify_api_or_tester
from api.schemas.birthdays import (
    BirthdayItem,
    BirthdaysCalendarResponse,
    TodayBirthdaysResponse,
    UpcomingBirthdaysResponse,
)
from config import TIMEZONE
from services.birthday_manager import calculate_days_and_age
from services.classmates_auth import load_classmates_registry

router = APIRouter(tags=["Birthdays"], prefix="/birthdays", dependencies=[Depends(verify_api_or_tester)])


def _map_calculated_to_dto(c: dict) -> BirthdayItem:
    """
    Преобразует словарь с расчетом возраста в строгий Pydantic объект BirthdayItem.

    Форматирует дату рождения в строку ДД.ММ и подставляет дефолтные значения.
    Служит единой точкой трансформации доменных данных в API схему.

    Возвращает валидный объект BirthdayItem.
    """

    b_date = f"{c.get('day', 1):02d}.{c.get('month', 1):02d}"

    return BirthdayItem(
        fio=c.get("fio", "Неизвестно"),
        birth_date=b_date,
        year=c.get("year", 2005),
        turning_age=c.get("turning_age", 20),
        days_until=c.get("days_until", 0),
        is_today=c.get("is_today", False),
    )


@router.get("", response_model=BirthdaysCalendarResponse)
async def get_birthdays_calendar() -> BirthdaysCalendarResponse:
    """
    Возвращает полный календарь дней рождения одногруппников на весь год.

    Сортирует список по возрастанию количества дней до следующего праздника.
    Использует часовой пояс колледжа для точного вычисления возраста.

    Возвращает BirthdaysCalendarResponse с отсортированным списком студентов.
    """

    registry = load_classmates_registry()
    today = datetime.now(TIMEZONE).date()
    calculated = [calculate_days_and_age(s, today) for s in registry]
    calculated.sort(key=lambda x: x["days_until"])
    items = [_map_calculated_to_dto(c) for c in calculated]

    return BirthdaysCalendarResponse(count=len(items), birthdays=items)


@router.get("/upcoming", response_model=UpcomingBirthdaysResponse)
async def get_upcoming_birthdays(
    days: int = Query(default=30, ge=1, le=365, description="Горизонт поиска (дней)"),
) -> UpcomingBirthdaysResponse:
    """
    Возвращает список студентов, у которых день рождения наступит в ближайшие N дней.

    Фильтрует реестр по условию 0 <= days_until <= days и сортирует по дате.
    Используется ботом и Mini App для предупреждения группы о праздниках.

    Возвращает UpcomingBirthdaysResponse с отфильтрованными именинниками.
    """

    registry = load_classmates_registry()
    today = datetime.now(TIMEZONE).date()
    calculated = [calculate_days_and_age(s, today) for s in registry]
    filtered = [c for c in calculated if 0 <= c["days_until"] <= days]
    filtered.sort(key=lambda x: x["days_until"])
    items = [_map_calculated_to_dto(c) for c in filtered]

    return UpcomingBirthdaysResponse(threshold_days=days, count=len(items), upcoming=items)


@router.get("/today", response_model=TodayBirthdaysResponse)
async def get_today_birthdays() -> TodayBirthdaysResponse:
    """
    Возвращает список одногруппников, празднующих день рождения прямо сегодня.

    Вычисляет флаг is_today на основе сегодняшней даты по МСК.
    Служит источником для ежедневных утренних поздравлений в чате группы.

    Возвращает TodayBirthdaysResponse со списком виновников торжества.
    """

    registry = load_classmates_registry()
    today = datetime.now(TIMEZONE).date()
    calculated = [calculate_days_and_age(s, today) for s in registry]
    today_items = [c for c in calculated if c["is_today"]]
    items = [_map_calculated_to_dto(c) for c in today_items]

    return TodayBirthdaysResponse(count=len(items), celebrants=items)
