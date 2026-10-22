"""
Тесты подсистемы академической геймификации, рангов и достижений.

Проверяет:
  1. Корректность шкалы рангов (включая мемный ранг 80% и Любимчика старосты)
  2. Реестр из ровно 80 уникальных достижений в 8 категориях
  3. Расчет очков опыта (XP) и автоматическое открытие ачивок
  4. Сортировку турнирной таблицы лидеров группы
  5. Эндпоинты FastAPI роутера /gamification
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from api import create_app
from services.gamification import (
    build_student_profile,
    calculate_student_xp,
    get_group_leaderboard,
    resolve_student_rank,
)
from services.gamification_models import AchievementCategory
from services.gamification_registry import (
    ACHIEVEMENTS_MAP,
    RANKS,
    get_all_achievements,
)


def test_ranks_hierarchy_and_meme_rank() -> None:
    """Проверяет шкалу рангов, включая культовый ранг 80% первого курса."""
    assert len(RANKS) == 10
    fav = resolve_student_rank(100.0, n_count=0, o_count=0)
    assert fav.name == "Любимчик старосты" and fav.icon == "👑"

    exc = resolve_student_rank(100.0, n_count=0, o_count=1)
    assert exc.name == "Легальный отличник"

    meme = resolve_student_rank(80.0, n_count=5, o_count=0)
    assert meme.name == "ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!" and meme.icon == "🎯"


def test_lower_ranks_hierarchy() -> None:
    """Проверяет нижние уровни рангов от нормиса до призрака."""
    normis = resolve_student_rank(85.0, n_count=4, o_count=0)
    assert normis.name == "Нормис"

    risk = resolve_student_rank(45.0, n_count=15, o_count=0)
    assert risk.name == "Кандидат на отчисление"

    ghost = resolve_student_rank(10.0, n_count=30, o_count=0)
    assert ghost.name == "Призрак КТМУ"


def test_registry_contains_exactly_80_achievements() -> None:
    """Проверяет целостность и количество всех 80 достижений."""
    achs = get_all_achievements()
    assert len(achs) == 80
    assert len(ACHIEVEMENTS_MAP) == 80

    categories = {a.category for a in achs}
    assert len(categories) == 8
    assert AchievementCategory.ATTENDANCE in categories
    assert AchievementCategory.EASTER_EGGS in categories

    for ach in achs:
        assert len(ach.title) > 0
        assert len(ach.description) > 0
        assert len(ach.icon) > 0
        assert ach.xp_reward > 0


def test_student_profile_and_xp_calculation() -> None:
    """Проверяет генерацию профиля студента и начисление очков опыта."""
    raw_data = {
        "total": {"П": 50, "О": 1, "У": 2, "Н": 0},
    }
    profile = build_student_profile("Конышев Сергей", raw_data)

    assert profile.fio == "Конышев Сергей"
    assert profile.short_fio == "Конышев Сергей"
    assert profile.attendance_pct == 100.0
    assert profile.rank_name == "Легальный отличник"
    assert "att_100" in profile.unlocked_achievements
    assert "late_first" in profile.unlocked_achievements
    assert "egg_jubilee_300" in profile.unlocked_achievements
    assert profile.xp > 500


def test_calculate_xp_rewards_and_penalties() -> None:
    """Проверяет формулу начисления и штрафов очков академического опыта."""
    stat = {"p": 10, "u": 2, "n": 4}
    unlocked = ["att_survivor_6"]  # 50 XP
    xp = calculate_student_xp(stat, unlocked)
    assert xp == 140


def test_starosta_privileges_all_80_achievements() -> None:
    """Проверяет, что Староста получает все 80 ачивок и максимальный ранг."""
    raw = {"total": {"П": 34, "О": 0, "У": 2, "Н": 0}}
    p = build_student_profile("Стрыгин Дмитрий Вячеславович", raw)
    assert p.rank_name == "Староста группы" and p.rank_icon == "👑"
    assert len(p.unlocked_achievements) == 80 and p.xp > 10000


@pytest.mark.asyncio
async def test_get_group_leaderboard_sorting() -> None:
    """Проверяет сортировку лидерборда с 1-м местом Старосты."""
    fake_stats = {
        "Иванов Иван": {"total": {"П": 10, "О": 0, "У": 0, "Н": 10}},
        "Петров Петр": {"total": {"П": 30, "О": 0, "У": 0, "Н": 0}},
        "Стрыгин Дмитрий": {"total": {"П": 34, "О": 0, "У": 2, "Н": 0}},
    }
    board = await get_group_leaderboard(fake_stats)
    assert len(board) == 3
    assert board[0].fio == "Стрыгин Дмитрий"
    assert len(board[0].unlocked_achievements) == 80


@pytest.mark.asyncio
async def test_gamification_api_leaderboard() -> None:
    """Проверяет эндпоинты лидерборда и каталога ачивок через FastAPI."""
    app = create_app()
    fake_stats = {"Конышев Сергей": {"total": {"П": 40, "О": 0, "У": 0, "Н": 0}}}
    with patch("services.gamification.fetch_all_time_attendance", AsyncMock(return_value=fake_stats)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_lb = await client.get("/gamification/leaderboard")
            assert resp_lb.status_code == 200
            data_lb = resp_lb.json()
            assert data_lb["total_students"] == 1 and data_lb["group_pulse"] == 100.0

            resp_ach = await client.get("/gamification/achievements")
            assert resp_ach.status_code == 200
            assert resp_ach.json()["total_count"] == 80


@pytest.mark.asyncio
async def test_gamification_api_profile_and_ranks() -> None:
    """Проверяет эндпоинты рангов и профиля студента."""
    app = create_app()
    fake_stats = {"Конышев Сергей": {"total": {"П": 40, "О": 0, "У": 0, "Н": 0}}}
    with patch("services.gamification.fetch_all_time_attendance", AsyncMock(return_value=fake_stats)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_ranks = await client.get("/gamification/ranks")
            assert resp_ranks.status_code == 200 and len(resp_ranks.json()) == 10

            resp_prof = await client.get("/gamification/profile?fio=Конышев")
            assert resp_prof.status_code == 200
            assert resp_prof.json()["fio"] == "Конышев Сергей"
