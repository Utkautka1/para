"""
Сервис академической геймификации, расчета уровней, рангов и достижений.

Отвечает за:
  1. Автоматический расчет рангов (включая мем "ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!")
  2. Проверку условий выполнения 80 достижений по реальной статистике
  3. Начисление очков академического опыта (XP)
  4. Формирование турнирной таблицы лидеров группы 1-КПД-3
"""

from typing import Any

from core.logger import get_logger
from services.attendance_stats import fetch_all_time_attendance
from services.attendance_topic_updater import extract_short_fio
from services.gamification_models import RankDefinition, StudentProfile
from services.gamification_registry import ACHIEVEMENTS_MAP, RANKS

log = get_logger("gamification")


def resolve_student_rank(pct: float, n_count: int, o_count: int) -> RankDefinition:
    """
    Определяет актуальный ранг студента по проценту посещаемости и штрафам.

    Выделяет особые ранги для 100% отличников и мемный ранг 80% первого курса.
    """
    if pct >= 99.9 and n_count == 0:
        return RANKS[0] if o_count == 0 else RANKS[1]

    if 79.5 <= pct <= 80.9:
        return RANKS[5]

    for rank in RANKS[2:]:
        if rank.min_pct <= pct <= rank.max_pct:
            return rank

    return RANKS[-1]


def _check_attendance_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет условия достижений посещаемости."""
    if s["pct"] >= 99.9:
        unlocked.add("att_100")
    if s["n"] == 0:
        unlocked.add("att_no_unexcused")
    if s["n"] >= 20:
        unlocked.add("att_ghost")
    if s["n"] == 9:
        unlocked.add("att_critical_9")
    if s["u"] >= 5:
        unlocked.add("att_doc_master")
    if s["u"] >= 10:
        unlocked.add("att_doc_legend")


def _check_punctuality_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет условия достижений пунктуальности."""
    if s["o"] >= 1:
        unlocked.add("late_first")
    if s["o"] >= 3:
        unlocked.add("late_serial")
    if s["o"] == 0:
        unlocked.add("late_zero")


def _check_mastery_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет высшие статусные достижения."""
    if 79.5 <= s["pct"] <= 80.9:
        unlocked.add("mast_first_course")
    if 81.0 <= s["pct"] <= 89.9:
        unlocked.add("mast_normis_life")
    if s["pct"] >= 99.9 and s["n"] == 0 and s["o"] == 0:
        unlocked.add("mast_favorite")


def _evaluate_all_rules(s: dict[str, Any], extra: set[str] | None) -> list[str]:
    """Агрегирует проверку всех правил и добавляет юбилейную ачивку 300."""
    unlocked: set[str] = {"egg_jubilee_300"}
    _check_attendance_rules(s, unlocked)
    _check_punctuality_rules(s, unlocked)
    _check_mastery_rules(s, unlocked)
    if extra:
        unlocked.update(extra)
    return sorted(list(unlocked))


def calculate_student_xp(stat: dict[str, Any], unlocked_ach_ids: list[str]) -> int:
    """
    Рассчитывает суммарные очки академического опыта (XP) студента.

    Учитывает посещенные пары, уважительные справки и награды за ачивки.
    """
    base_xp = stat.get("p", 0) * 10 + stat.get("u", 0) * 5
    penalty = stat.get("n", 0) * 5
    ach_xp = sum(
        ACHIEVEMENTS_MAP[aid].xp_reward
        for aid in unlocked_ach_ids
        if aid in ACHIEVEMENTS_MAP
    )
    return max(0, base_xp - penalty) + ach_xp


def _extract_student_metrics(fio: str, raw_data: dict[str, Any]) -> dict[str, Any]:
    """Преобразует сырые показатели посещаемости в нормализованную структуру."""
    tot = raw_data.get("total", {})
    p, o = tot.get("П", 0), tot.get("О", 0)
    u, n = tot.get("У", 0), tot.get("Н", 0)
    total = p + o + u + n
    pct = ((p + o + u) / total * 100.0) if total > 0 else 100.0
    return {"fio": fio, "p": p, "o": o, "u": u, "n": n, "total": total, "pct": pct}


def build_student_profile(fio: str, raw_data: dict[str, Any], extra: set[str] | None = None) -> StudentProfile:
    """Создает объект профиля студента со званием, ачивками и опытом."""
    m = _extract_student_metrics(fio, raw_data)
    rank = resolve_student_rank(m["pct"], m["n"], m["o"])
    achs = _evaluate_all_rules(m, extra)
    xp = calculate_student_xp(m, achs)

    return StudentProfile(
        fio=fio,
        short_fio=extract_short_fio(fio),
        attendance_pct=round(m["pct"], 1),
        total_classes=m["total"],
        present_count=m["p"],
        late_count=m["o"],
        excused_count=m["u"],
        unexcused_count=m["n"],
        rank_name=rank.name,
        rank_icon=rank.icon,
        rank_description=rank.description,
        xp=xp,
        unlocked_achievements=achs,
    )


async def get_student_profile_by_fio(fio: str, extra: set[str] | None = None) -> StudentProfile | None:
    """Находит статистику студента по ФИО и возвращает профиль геймификации."""
    stats = await fetch_all_time_attendance()
    matched_fio = next((k for k in stats if fio.lower() in k.lower()), None)
    if not matched_fio:
        return None
    return build_student_profile(matched_fio, stats[matched_fio], extra)


async def get_group_leaderboard(provided_stats: dict[str, Any] | None = None) -> list[StudentProfile]:
    """
    Формирует упорядоченный список студентов группы 1-КПД-3 по рангу и XP.

    Возвращает отсортированный по убыванию достижений лидерборд.
    """
    stats = provided_stats or await fetch_all_time_attendance()
    profiles = [build_student_profile(fio, data) for fio, data in stats.items()]
    profiles.sort(key=lambda s: (-s.attendance_pct, -s.xp, -s.present_count, s.fio))
    return profiles
