"""
Доменные модели и структуры данных подсистемы геймификации.

Определяет:
  1. Перечисление категорий и уровней редкости достижений
  2. Структуру описания достижения (AchievementDefinition)
  3. Структуру статуса достижения конкретного студента (AchievementProgress)
  4. Модель профиля студента и ранга (StudentProfile, RankDefinition)
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AchievementCategory(StrEnum):
    """Категория студенческого достижения."""

    ATTENDANCE = "attendance"
    PUNCTUALITY = "punctuality"
    BOT_INTERACTION = "bot_interaction"
    AI_HOMEWORK = "ai_homework"
    STUDENT_LIFE = "student_life"
    SOCIAL = "social"
    EASTER_EGGS = "easter_eggs"
    MASTERY = "mastery"


class AchievementRarity(StrEnum):
    """Степень редкости достижения."""

    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass(frozen=True)
class RankDefinition:
    """Определение ранга студента в академическом рейтинге."""

    name: str
    icon: str
    description: str
    min_pct: float
    max_pct: float
    min_n: int = 0
    max_n: int = 999
    requires_exact_pct: float | None = None


@dataclass(frozen=True)
class AchievementDefinition:
    """Паспорт достижения в реестре геймификации."""

    id: str
    title: str
    description: str
    icon: str
    category: AchievementCategory
    rarity: AchievementRarity
    xp_reward: int


@dataclass
class StudentProfile:
    """Агрегированный профиль студента с очками опыта и рангом."""

    fio: str
    short_fio: str
    attendance_pct: float
    total_classes: int
    present_count: int
    late_count: int
    excused_count: int
    unexcused_count: int
    rank_name: str
    rank_icon: str
    rank_description: str
    xp: int
    unlocked_achievements: list[str] = field(default_factory=list)
    # guild_points — очки гильдии, по ним сортируется рейтинг (см. calculate_guild_points)
    guild_points: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
