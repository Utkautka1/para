"""
Роутер API академической геймификации, рейтинга и 80 достижений.

Предоставляет эндпоинты для:
  1. Выгрузки лидерборда группы 1-КПД-3 для Telegram Mini App
  2. Получения персонального профиля студента по ФИО
  3. Получения каталога всех 80 достижений с категориями и наградами
"""

from fastapi import APIRouter, HTTPException, Query, status

from api.schemas.gamification import (
    AchievementsCatalogResponse,
    AchievementSchema,
    LeaderboardResponse,
    StudentProfileSchema,
)
from core.logger import get_logger
from services.gamification import get_group_leaderboard, get_student_profile_by_fio
from services.gamification_registry import RANKS, get_all_achievements

log = get_logger("gamification_router")

router = APIRouter(tags=["Gamification & Leaderboard"], prefix="/gamification")


def _calculate_group_pulse(profiles: list) -> float:
    """Вычисляет средний пульс академической посещаемости группы."""
    if not profiles:
        return 0.0
    return round(sum(p.attendance_pct for p in profiles) / len(profiles), 1)


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard_endpoint() -> LeaderboardResponse:
    """
    Возвращает актуальный рейтинг всех 26 студентов группы 1-КПД-3.

    Сортирует участников по проценту посещаемости, очкам опыта и активности.
    """
    profiles = await get_group_leaderboard()
    pulse = _calculate_group_pulse(profiles)
    return LeaderboardResponse(
        total_students=len(profiles),
        group_pulse=pulse,
        leaderboard=[StudentProfileSchema.model_validate(p) for p in profiles],
    )


@router.get("/profile", response_model=StudentProfileSchema)
async def get_student_profile_endpoint(
    fio: str = Query(..., min_length=2, description="Фамилия или полное ФИО студента")
) -> StudentProfileSchema:
    """
    Возвращает персональный профиль студента с рангом, опытом и списком ачивок.

    Выполняет нечеткий поиск по списку группы 1-КПД-3.
    """
    profile = await get_student_profile_by_fio(fio)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент '{fio}' не найден в реестре группы 1-КПД-3",
        )
    return StudentProfileSchema.model_validate(profile)


@router.get("/achievements", response_model=AchievementsCatalogResponse)
async def get_achievements_catalog_endpoint() -> AchievementsCatalogResponse:
    """
    Возвращает полный каталог из 80 достижений с категориями, редкостью и XP.

    Используется для рендеринга витрины бейджей в Telegram Mini App.
    """
    all_defs = get_all_achievements()
    schemas = [
        AchievementSchema(
            id=d.id,
            title=d.title,
            description=d.description,
            icon=d.icon,
            category=d.category.value,
            rarity=d.rarity.value,
            xp_reward=d.xp_reward,
        )
        for d in all_defs
    ]
    return AchievementsCatalogResponse(total_count=len(schemas), achievements=schemas)


@router.get("/ranks")
async def get_ranks_catalog_endpoint() -> list[dict[str, str]]:
    """Возвращает каталог всех академических рангов системы."""
    return [
        {"name": r.name, "icon": r.icon, "description": r.description}
        for r in RANKS
    ]
