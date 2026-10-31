"""
Тесты журнальных и мета-правил ачивок (services/achievement_rules.py) и целостности каталога.

Проверяет:
  1. Каждая публичная ачивка достижима: её id используется хотя бы одним
     правилом, триггером или хэндлером — нет «мёртвых» ачивок, как раньше
  2. Пороги журнальных правил (25/50/100 посещённых, минимум отметок для процентов)
  3. Месячные правила и «камбэк» в порядке учебного года
  4. Мета-правила доходят до неподвижной точки (XP мета-ачивок открывает следующие)
"""

from pathlib import Path

import pytest

from services.achievement_rules import (
    STAT_RULES,
    MetaContext,
    MonthStat,
    StudentStat,
    build_student_stat,
    evaluate_meta_rules,
    evaluate_stat_rules,
)
from services.gamification_registry import SECRET_IDS, get_all_achievements

ROOT = Path(__file__).resolve().parents[1]

# Где может «жить» условие ачивки: правила, триггеры, события, хэндлеры и Mini App
_SOURCES = [*(ROOT / "services").glob("achievement_*.py"), *(ROOT / "bot" / "handlers").rglob("*.py")]
_SOURCES += [ROOT / "api" / "router" / "miniapp.py", ROOT / "api" / "router" / "pulse.py"]


def _stat(p: int = 0, o: int = 0, u: int = 0, n: int = 0, months: list[MonthStat] | None = None) -> StudentStat:
    """Студент с заданными суммарными отметками."""
    return StudentStat(MonthStat(p, o, u, n), months or [])


@pytest.mark.parametrize("ach", get_all_achievements(), ids=lambda a: a.id)
def test_every_catalog_achievement_is_reachable(ach) -> None:
    code = "\n".join(path.read_text(encoding="utf-8") for path in _SOURCES)
    assert f'"{ach.id}"' in code, f"{ach.id} нигде не выдаётся"


def test_secret_achievements_are_not_in_catalog() -> None:
    assert SECRET_IDS.isdisjoint({a.id for a in get_all_achievements()})


def test_catalog_descriptions_have_no_legacy_wording() -> None:
    # «более N» в старом каталоге расходилось с проверкой «>= N»
    assert not [a.id for a in get_all_achievements() if "более" in a.description.lower()]


@pytest.mark.parametrize(
    ("visited", "expected"),
    [(24, set()), (25, {"att_ghost"}), (50, {"att_ghost", "att_critical_9"}), (100, {"att_century"})],
)
def test_visit_thresholds(visited: int, expected: set[str]) -> None:
    got = evaluate_stat_rules(_stat(p=visited, n=visited))
    assert expected <= got
    assert ("att_century" in got) == (visited >= 100)


def test_percent_rules_need_enough_marks() -> None:
    # 100% за 5 пар в начале семестра — не «Клуб 100%»
    assert "att_100" not in evaluate_stat_rules(_stat(p=5))
    assert {"att_100", "att_no_unexcused"} <= evaluate_stat_rules(_stat(p=20))


@pytest.mark.parametrize(
    ("p", "n", "rule", "expected"),
    [
        (80, 20, "mast_first_course", True),
        (16, 4, "mast_first_course", True),
        (8, 2, "mast_first_course", False),
        (85, 15, "mast_normis_life", True),
        (95, 5, "egg_vip", True),
        (28, 1, "egg_vip", False),
    ],
)
def test_percent_ranges(p: int, n: int, rule: str, expected: bool) -> None:
    assert STAT_RULES[rule](_stat(p=p, n=n)) is expected


def test_full_months_and_punctuality() -> None:
    clean = MonthStat(20, 0, 2, 0)
    late = MonthStat(18, 2, 0, 0)
    s = _stat(p=38, o=2, u=2, months=[clean, late])
    got = evaluate_stat_rules(s)
    assert {"att_clean_month", "att_month_streak", "time_exact_arrival", "late_first"} <= got


def test_comeback_requires_consecutive_months() -> None:
    bad, good = MonthStat(10, 0, 0, 10), MonthStat(19, 0, 0, 1)
    assert STAT_RULES["att_comeback"](_stat(months=[bad, good]))
    assert not STAT_RULES["att_comeback"](_stat(months=[good, bad]))


def test_build_student_stat_orders_academic_year() -> None:
    raw = {
        "total": {"П": 3, "О": 0, "У": 0, "Н": 0},
        "months": {"ЯНВ": {"П": 1}, "СЕНТ": {"П": 2}, "ДЕК": {}},
    }
    stat = build_student_stat(raw)
    assert [m.p for m in stat.months] == [2, 1]
    assert stat.visited == 3


def test_meta_rules_reach_fixed_point() -> None:
    # 9 ачивок по 100+ XP: «Коллекционер» (10-я) открывается сам и тянет XP-рубеж
    base = {"att_century", "att_100", "att_no_unexcused", "late_zero", "life_math_god"}
    base |= {"egg_vip", "mast_favorite", "egg_jubilee_300", "att_month_streak"}
    ctx = MetaContext(place=1, pct=100.0, total_marks=40, group_pulse=70.0)
    gained = evaluate_meta_rules(base, ctx)
    assert {"mast_badge_collector", "mast_top1", "mast_top3", "soc_pulse_boost", "mast_xp_1000"} <= gained
    assert gained.isdisjoint(base)


def test_meta_top_requires_rating_place() -> None:
    ctx = MetaContext(place=None, pct=100.0, total_marks=40, group_pulse=70.0)
    assert "mast_top1" not in evaluate_meta_rules(set(), ctx)
    few_marks = MetaContext(place=1, pct=100.0, total_marks=5, group_pulse=70.0)
    assert "mast_top1" not in evaluate_meta_rules(set(), few_marks)
