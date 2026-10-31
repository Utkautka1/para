"""
Pydantic-схемы данных для подсистемы академической геймификации.

Определяет:
  1. Схемы паспортов достижений (AchievementSchema)
  2. Схемы профилей студентов с рангами и очками опыта (StudentProfileSchema)
  3. Схемы ответов турнирной таблицы и каталога 80 ачивок
"""

from pydantic import BaseModel, ConfigDict, Field


class AchievementSchema(BaseModel):
    """Схема описания достижения в API."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Уникальный строковый идентификатор")
    title: str = Field(..., description="Название достижения")
    description: str = Field(..., description="Условие получения")
    icon: str = Field(..., description="Эмодзи-иконка")
    category: str = Field(..., description="Категория")
    rarity: str = Field(..., description="Степень редкости")
    xp_reward: int = Field(..., description="Награда в очках опыта")


class StudentProfileSchema(BaseModel):
    """Схема профиля студента с рангом и ачивками."""

    model_config = ConfigDict(from_attributes=True)

    fio: str = Field(..., description="Полное каноническое ФИО")
    short_fio: str = Field(..., description="Краткое имя (Фамилия Имя)")
    attendance_pct: float = Field(..., description="Процент посещаемости")
    total_classes: int = Field(..., description="Всего учебных занятий")
    present_count: int = Field(..., description="Присутствовал (П)")
    late_count: int = Field(..., description="Опозданий (О)")
    excused_count: int = Field(..., description="По справке (У)")
    unexcused_count: int = Field(..., description="Прогулов (Н)")
    rank_name: str = Field(..., description="Текущий академический ранг")
    rank_icon: str = Field(..., description="Эмодзи ранга")
    rank_description: str = Field(..., description="Описание статуса")
    xp: int = Field(..., description="Суммарные очки опыта")
    unlocked_achievements: list[str] = Field(default_factory=list, description="Список ID открытых ачивок")
    guild_points: int = Field(0, description="Очки гильдии: XP + 10 за пару − 10 за «Н» после сброса")


class LeaderboardResponse(BaseModel):
    """Схема ответа лидерборда группы 1-КПД-3."""

    total_students: int
    group_pulse: float
    leaderboard: list[StudentProfileSchema]
    starosta: StudentProfileSchema | None = None


class AchievementsCatalogResponse(BaseModel):
    """Схема ответа каталога всех 80 достижений системы."""

    total_count: int
    achievements: list[AchievementSchema]
