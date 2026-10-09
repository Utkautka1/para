"""
Pydantic-схемы ответов для роутера расписания.

Переиспользует Lesson из schedule_parser напрямую,
дополняет моделями текущей пары, статуса и сброса кэша.
"""

from datetime import date as DateType

from pydantic import BaseModel, Field

from services.models import Lesson


class DayScheduleResponse(BaseModel):
    """Расписание занятий на конкретный учебный день."""
    date: DateType = Field(..., description="Дата учебного дня (YYYY-MM-DD)")
    lessons: list[Lesson] = Field(default_factory=list, description="Список занятий дня")


class WeekDayItem(BaseModel):
    """Один учебный день в недельном расписании."""
    date: DateType = Field(..., description="Дата учебного дня")
    lessons: list[Lesson] = Field(default_factory=list, description="Список занятий дня")


class WeekScheduleResponse(BaseModel):
    """Полное расписание на учебную неделю (пн—сб)."""
    monday: DateType = Field(..., description="Понедельник выбранной недели")
    days: list[WeekDayItem] = Field(default_factory=list, description="Дни недели с занятиями")


class CurrentLessonResponse(BaseModel):
    """Информация о текущем и ближайшем занятии."""
    is_active_now: bool = Field(..., description="Идёт ли пара прямо сейчас")
    current_lesson: Lesson | None = Field(None, description="Текущее занятие")
    next_lesson: Lesson | None = Field(None, description="Следующее занятие")
    time_remaining_minutes: int | None = Field(None, description="Минут до завершения или начала")


class ScheduleRefreshResponse(BaseModel):
    """Результат принудительной инвалидации кэша расписания."""
    status: str = Field(..., description="Статус операции (ok/error)")
    flushed_keys: int = Field(..., description="Количество удалённых ключей кэша")
    timestamp: str = Field(..., description="Время операции")
