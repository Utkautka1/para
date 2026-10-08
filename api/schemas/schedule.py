"""
Pydantic-схемы ответов для роутера расписания.

Переиспользует Lesson из schedule_parser напрямую (уже Pydantic BaseModel),
здесь только обёртки уровня API.
"""

from datetime import date

from pydantic import BaseModel

from services.models import Lesson


class DayScheduleResponse(BaseModel):
    """Расписание на один день."""
    date: date
    lessons: list[Lesson]


class WeekDayItem(BaseModel):
    """Один день в недельном расписании."""
    date: date
    lessons: list[Lesson]


class WeekScheduleResponse(BaseModel):
    """Расписание на неделю (6 дней, пн—сб)."""
    monday: date
    days: list[WeekDayItem]
