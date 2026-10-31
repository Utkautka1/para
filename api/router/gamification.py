"""
Роутер API академической геймификации, рейтинга и 80 достижений.

Предоставляет эндпоинты для:
  1. Выгрузки лидерборда группы 1-КПД-3 для Telegram Mini App
  2. Получения персонального профиля студента по ФИО
  3. Получения каталога всех 80 достижений с категориями и наградами

Лидерборд и профили содержат ФИО и посещаемость студентов — это персональные
данные, поэтому они доступны только одногруппникам и тестерам (verify_api_or_tester).
Каталоги достижений и рангов статичны и остаются публичными.
Секретные ачивки в каталог не входят и вырезаются из чужих профилей —
их видит только владелец (зритель определяется по сессии Mini App).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.deps import verify_api_or_tester
from api.schemas.gamification import (
    AchievementsCatalogResponse,
    AchievementSchema,
    LeaderboardResponse,
    StudentProfileSchema,
)
from core.logger import get_logger
from services.classmates_auth import find_classmate_by_tg_id
from services.gamification import (
    get_group_leaderboard,
    get_student_profile_by_fio,
    hide_secret_achievements,
    is_starosta,
)
from services.gamification_models import StudentProfile
from services.gamification_registry import RANKS, get_all_achievements

log = get_logger("gamification_router")

router = APIRouter(tags=["Gamification & Leaderboard"], prefix="/gamification")


def _calculate_group_pulse(profiles: list) -> float:
    """Вычисляет средний пульс академической посещаемости группы."""
    if not profiles:
        return 0.0
    return round(sum(p.attendance_pct for p in profiles) / len(profiles), 1)


def _resolve_target_fio(fio: str | None, tg_id: int | None) -> str | None:
    """
    Разрешает ФИО студента по переданному параметру fio или идентификатору Telegram.

    Возвращает строку с ФИО или None, если параметры не переданы или tg_id не найден.
    Не подставляет дефолтных пользователей во избежание утечки чужих данных.
    """
    if fio and fio.strip():
        return fio.strip()
    if tg_id:
        classmate = find_classmate_by_tg_id(tg_id)
        if classmate and classmate.get("full_name"):
            return str(classmate["full_name"])
    return None


def _viewer_fio(identity: str) -> str | None:
    """
    Определяет ФИО зрителя по идентичности из verify_api_or_tester.

    Сессия Mini App даёт 'tester:<tg_id>'; мастер-ключ и прочие — без ФИО,
    такие зрители секретных ачивок не видят ни у кого.
    """
    if not identity.startswith("tester:"):
        return None
    classmate = find_classmate_by_tg_id(int(identity.split(":", 1)[1]))
    return str(classmate["full_name"]) if classmate and classmate.get("full_name") else None


def _public_schema(profile: StudentProfile, viewer: str | None) -> StudentProfileSchema:
    """Сериализует профиль, скрывая секретные ачивки от чужих глаз."""
    return StudentProfileSchema.model_validate(hide_secret_achievements(profile, viewer))


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard_endpoint(identity: str = Depends(verify_api_or_tester)) -> LeaderboardResponse:
    """
    Возвращает рейтинг соревнующихся студентов с выделенным старостой вне конкурса.

    Разделение позволяет студентам честно соревноваться за 1-3 места на подиуме,
    в то время как староста группы вынесен в отдельный почетный блок.
    """
    profiles = await get_group_leaderboard()
    viewer = _viewer_fio(identity)
    pulse = _calculate_group_pulse(profiles)
    starosta_prof = next((p for p in profiles if is_starosta(p.fio)), None)
    competing = [p for p in profiles if not is_starosta(p.fio)]
    return LeaderboardResponse(
        total_students=len(profiles),
        group_pulse=pulse,
        leaderboard=[_public_schema(p, viewer) for p in competing],
        starosta=_public_schema(starosta_prof, viewer) if starosta_prof else None,
    )


@router.get("/profile", response_model=StudentProfileSchema)
async def get_student_profile_endpoint(
    fio: str | None = Query(default=None, description="Фамилия или ФИО студента"),
    tg_id: int | None = Query(default=None, description="Telegram ID студента"),
    identity: str = Depends(verify_api_or_tester),
) -> StudentProfileSchema:
    """Возвращает персональный профиль студента по ФИО или Telegram ID."""
    target_fio = _resolve_target_fio(fio, tg_id)
    if not target_fio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать параметр 'fio' или 'tg_id'",
        )
    profile = await get_student_profile_by_fio(target_fio)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент '{target_fio}' не найден в реестре группы 1-КПД-3",
        )
    return _public_schema(profile, _viewer_fio(identity))


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
    return [{"name": r.name, "icon": r.icon, "description": r.description} for r in RANKS]
