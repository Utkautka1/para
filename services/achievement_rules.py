"""
Правила достижений, которые вычисляются из журнала посещаемости и рейтинга.

Два вида правил:
  1. Журнальные (STAT_RULES) — смотрят только на отметки П/О/У/Н студента,
     суммарно и по месяцам. Журнал хранит суммы по месяцам, поэтому условий
     «за день» или «за неделю» здесь нет и быть не может.
  2. Мета-правила (evaluate_meta_rules) — зависят от уже открытых ачивок,
     XP и места в рейтинге, поэтому считаются после журнальных.

Модуль чистый: без БД и сети — его вызывает achievement_sync в worker.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import pairwise
from typing import Any

from integrations.yandex_docs import MONTH_SHEET_MAP
from services.gamification_registry import ACHIEVEMENTS_MAP

# Учебный год начинается в сентябре — порядок нужен для «камбэка» (месяц за месяцем)
ACADEMIC_MONTHS: tuple[int, ...] = (9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8)

# Минимум отметок, чтобы процентные ачивки не выдавались за 2–3 пары в начале семестра
MIN_MARKS = 20
STRICT_MIN_MARKS = 30

# Месяц считается «полным» для месячных ачивок при таком числе отметок
FULL_MONTH_MARKS = 20


@dataclass(frozen=True)
class MonthStat:
    """Отметки студента за один месяц журнала."""

    p: int
    o: int
    u: int
    n: int

    @property
    def total(self) -> int:
        return self.p + self.o + self.u + self.n

    @property
    def pct(self) -> float:
        # «У» — уважительная причина, в процент посещаемости идёт как присутствие
        return (self.p + self.o + self.u) / self.total * 100.0 if self.total else 0.0


@dataclass(frozen=True)
class StudentStat:
    """Срез журнала студента, достаточный для всех журнальных правил."""

    overall: MonthStat
    # Месяцы с отметками в порядке учебного года
    months: list[MonthStat] = field(default_factory=list)
    in_birthdays: bool = False

    @property
    def visited(self) -> int:
        return self.overall.p + self.overall.o


def _month_from_counts(counts: dict[str, int]) -> MonthStat:
    """Собирает MonthStat из словаря {'П': .., 'О': .., 'У': .., 'Н': ..}."""
    return MonthStat(counts.get("П", 0), counts.get("О", 0), counts.get("У", 0), counts.get("Н", 0))


def build_student_stat(raw: dict[str, Any], in_birthdays: bool = False) -> StudentStat:
    """
    Преобразует запись fetch_all_time_attendance в StudentStat.

    Пустые месяцы (лист есть, отметок нет) отбрасываются, остальные
    упорядочиваются по учебному году, а не по порядку листов в книге.

    Возвращает StudentStat.
    """
    by_sheet = raw.get("months", {})
    ordered = [
        _month_from_counts(by_sheet[MONTH_SHEET_MAP[m]]) for m in ACADEMIC_MONTHS if MONTH_SHEET_MAP[m] in by_sheet
    ]
    months = [m for m in ordered if m.total > 0]
    return StudentStat(_month_from_counts(raw.get("total", {})), months, in_birthdays)


def _full_months(s: StudentStat, *banned: str) -> int:
    """Считает «полные» месяцы без отметок указанных типов ('n', 'o')."""
    return sum(1 for m in s.months if m.total >= FULL_MONTH_MARKS and all(getattr(m, b) == 0 for b in banned))


def _has_comeback(s: StudentStat) -> bool:
    """Проверяет, был ли месяц ниже 75%, за которым сразу шёл месяц на 90%+."""
    return any(a.pct < 75.0 and b.pct >= 90.0 and b.total >= 10 for a, b in pairwise(s.months))


def _pct_between(s: StudentStat, low: float, high: float, min_marks: int = MIN_MARKS) -> bool:
    """Проверяет, что процент посещаемости в диапазоне и отметок достаточно."""
    return s.overall.total >= min_marks and low <= s.overall.pct <= high


StatRule = Callable[[StudentStat], bool]

STAT_RULES: dict[str, StatRule] = {
    "att_ghost": lambda s: s.visited >= 25,
    "att_critical_9": lambda s: s.visited >= 50,
    "att_century": lambda s: s.visited >= 100,
    "att_100": lambda s: _pct_between(s, 99.95, 100.0),
    "att_no_unexcused": lambda s: s.overall.total >= MIN_MARKS and s.overall.n == 0,
    "att_clean_month": lambda s: _full_months(s, "n") >= 1,
    "att_month_streak": lambda s: _full_months(s, "n") >= 2,
    "att_comeback": _has_comeback,
    "att_doc_master": lambda s: s.overall.u >= 3,
    "att_doc_legend": lambda s: s.overall.u >= 6,
    "late_first": lambda s: s.overall.o >= 1,
    "late_serial": lambda s: s.visited >= 50 and s.overall.o <= 2,
    "late_zero": lambda s: s.visited >= 30 and s.overall.o == 0,
    "time_exact_arrival": lambda s: _full_months(s, "n", "o") >= 1,
    "life_mdk_pro": lambda s: s.visited >= 75,
    "life_math_god": lambda s: s.visited >= 150,
    "life_sport_king": lambda s: _pct_between(s, 90.0, 100.0, STRICT_MIN_MARKS),
    "life_future_senior": lambda s: s.visited >= 50 and s.overall.pct >= 85.0,
    "soc_birthday": lambda s: s.in_birthdays,
    "soc_veteran": lambda s: len(s.months) >= 3,
    "egg_vip": lambda s: _pct_between(s, 95.0, 100.0, STRICT_MIN_MARKS),
    "mast_first_course": lambda s: _pct_between(s, 79.5, 80.9),
    "mast_normis_life": lambda s: _pct_between(s, 81.0, 89.9),
    "mast_favorite": lambda s: _pct_between(s, 99.95, 100.0, STRICT_MIN_MARKS) and s.overall.o == 0,
}


def evaluate_stat_rules(s: StudentStat) -> set[str]:
    """Возвращает id журнальных ачивок, условия которых выполнены."""
    return {aid for aid, rule in STAT_RULES.items() if rule(s)}


@dataclass(frozen=True)
class MetaContext:
    """Положение студента в группе для мета-правил."""

    # place — место в рейтинге без старосты (1 — лидер), None — вне рейтинга
    place: int | None
    pct: float
    total_marks: int
    # group_pulse — средняя посещаемость группы (%)
    group_pulse: float


def _categories_count(unlocked: set[str]) -> int:
    """Считает, в скольких категориях у студента есть открытые ачивки."""
    return len({ACHIEVEMENTS_MAP[a].category for a in unlocked if a in ACHIEVEMENTS_MAP})


def _xp_of(unlocked: set[str]) -> int:
    """Суммирует XP открытых ачивок."""
    return sum(ACHIEVEMENTS_MAP[a].xp_reward for a in unlocked if a in ACHIEVEMENTS_MAP)


def _meta_pass(unlocked: set[str], ctx: MetaContext) -> set[str]:
    """Один проход мета-правил по текущему набору ачивок."""
    ranked = ctx.place is not None and ctx.total_marks >= MIN_MARKS
    checks = {
        "mast_xp_1000": _xp_of(unlocked) >= 1000,
        "mast_xp_2500": _xp_of(unlocked) >= 2500,
        "mast_all_rounder": _categories_count(unlocked) >= 6,
        "mast_badge_collector": len(unlocked) >= 10,
        "mast_grandmaster": len(unlocked) >= 25,
        "mast_top3": ranked and ctx.place <= 3,
        "mast_top1": ranked and ctx.place == 1,
        "soc_pulse_boost": ctx.total_marks >= MIN_MARKS and ctx.pct > ctx.group_pulse,
    }
    return {aid for aid, ok in checks.items() if ok}


def evaluate_meta_rules(unlocked: set[str], ctx: MetaContext) -> set[str]:
    """
    Возвращает мета-ачивки, которые открываются поверх уже открытых.

    Мета-ачивки сами дают XP и увеличивают счёт бейджей, поэтому проходы
    повторяются до неподвижной точки (обычно 2–3 итерации).

    Возвращает множество новых id (без уже открытых).
    """
    current = set(unlocked)
    while True:
        gained = _meta_pass(current, ctx) - current
        if not gained:
            return current - unlocked
        current |= gained
