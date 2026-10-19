"""
Pydantic-схемы для календаря дней рождения группы 1-КПД-3.
"""

from pydantic import BaseModel, Field


class BirthdayItem(BaseModel):
    """Информация о дне рождения студента."""

    fio: str = Field(..., description="ФИО студента", examples=["Петров Петр"])
    birth_date: str = Field(..., description="Дата рождения (ДД.ММ)", examples=["22.11"])
    year: int = Field(..., description="Год рождения", examples=[2005])
    turning_age: int = Field(..., description="Исполняющийся возраст", examples=[21])
    days_until: int = Field(..., description="Дней до дня рождения", examples=[44])
    is_today: bool = Field(..., description="День рождения сегодня", examples=[False])


class BirthdaysCalendarResponse(BaseModel):
    """Полный календарь дней рождения группы с расчётом дней."""

    count: int = Field(..., description="Количество записей в календаре")
    birthdays: list[BirthdayItem] = Field(default_factory=list, description="Список дней рождения")


class UpcomingBirthdaysResponse(BaseModel):
    """Список ближайших именинников."""

    threshold_days: int = Field(..., description="Горизонт поиска (дней)")
    count: int = Field(..., description="Количество именинников")
    upcoming: list[BirthdayItem] = Field(default_factory=list, description="Именинники в ближайшие дни")


class TodayBirthdaysResponse(BaseModel):
    """Именинники сегодняшнего дня."""

    count: int = Field(..., description="Количество именинников сегодня")
    celebrants: list[BirthdayItem] = Field(default_factory=list, description="Список именинников")
