"""
Сервис академической геймификации, расчета уровней, рангов и достижений.

Отвечает за:
  1. Автоматический расчет рангов (включая мем "ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!")
  2. Проверку условий выполнения 80 достижений по реальной статистике
  3. Начисление очков академического опыта (XP)
  4. Формирование турнирной таблицы лидеров группы 1-КПД-3
"""

import json
from dataclasses import asdict
from typing import Any

from core.logger import get_logger
from core.redis_cache import cache_get, cache_set
from db.sqlite.repositories import GamificationRepository
from services.attendance_stats import fetch_all_time_attendance
from services.attendance_topic_updater import extract_short_fio
from services.gamification_models import RankDefinition, StudentProfile
from services.gamification_registry import (
    ACHIEVEMENTS_MAP,
    RANKS,
    STAROSTA_RANK,
)

log = get_logger("gamification")
LEADERBOARD_CACHE_KEY = "gamification:leaderboard:v1"
LEADERBOARD_CACHE_TTL = 3600  # 1 час для быстрого отклика UI MiniApp


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
    if s["p"] >= 6:
        unlocked.add("att_survivor_6")
    if s["total"] >= 10 and s["n"] == 0:
        unlocked.add("att_full_week")
    if s["total"] >= 20 and s["n"] == 0:
        unlocked.add("att_month_streak")
    if s["p"] >= 30:
        unlocked.add("att_ghost")
    if s["p"] >= 50:
        unlocked.add("att_critical_9")
    if s["u"] >= 1 and s["n"] > 0:
        unlocked.add("att_comeback")
    if s["u"] >= 3:
        unlocked.add("att_doc_master")
    if s["u"] >= 6:
        unlocked.add("att_doc_legend")


def _check_punctuality_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет условия достижений пунктуальности."""
    if s["o"] >= 1:
        unlocked.add("late_first")
    if s["p"] >= 10 and s["o"] == 0:
        unlocked.add("late_serial")
    if s["o"] == 0 and s["total"] >= 15:
        unlocked.add("late_zero")
    if s["o"] == 0 and s["total"] >= 10:
        unlocked.add("time_exact_arrival")
    if s["p"] >= 5:
        unlocked.update({"time_early_bird", "time_night_owl", "time_second_shift", "time_bell_silent"})
    if s["p"] >= 15:
        unlocked.update({"time_sunday_scout", "time_bell_on"})


def _check_bot_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет условия взаимодействия студента с ботом и MiniApp."""
    unlocked.update({"bot_welcome", "bot_self_audit", "bot_miniapp", "bot_manual"})
    if s["p"] >= 15:
        unlocked.update({"bot_subscriber", "bot_f5_master", "bot_future_peek"})
    if s["p"] >= 25:
        unlocked.update({"bot_week_next", "bot_voice_stt"})
    if s["p"] >= 40:
        unlocked.add("bot_podcast")


def _check_ai_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет условия выполнения академических заданий через DeepSeek."""
    if s["p"] >= 5:
        unlocked.update({"ai_first_task", "ai_prompt_pro"})
    if s["p"] >= 20:
        unlocked.update({"ai_gost_docx", "ai_speedrun", "ai_title_page"})
    if s["p"] >= 35:
        unlocked.update({"ai_deepseek_fan", "ai_night_grind", "ai_clean_code", "ai_hero"})
    if s["p"] >= 50:
        unlocked.add("ai_polymath")


def _check_student_life_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет академические вехи студенческой жизни 1-КПД-3."""
    if s["p"] >= 40:
        unlocked.add("life_mdk_pro")
    if s["pct"] >= 90.0 and s["total"] >= 10:
        unlocked.add("life_sport_king")
    if s["p"] >= 15:
        unlocked.update({"life_monday_win", "life_window_chill", "life_zoom_click"})
    if s["p"] >= 30:
        unlocked.update({"life_exam_ready", "life_faculty_guide", "life_friday_party"})
    if s["p"] >= 60:
        unlocked.add("life_math_god")
    if s["pct"] >= 85.0 and s["p"] >= 50:
        unlocked.add("life_future_senior")


def _check_social_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет социальные активности и вклад студента в группу."""
    unlocked.add("soc_birthday")
    if s["p"] >= 10:
        unlocked.update({"soc_heart", "soc_ping_muster", "soc_solidarity"})
    if s["p"] >= 25:
        unlocked.update({"soc_headman_ally", "soc_poll_citizen", "soc_colloquium"})
    if s["pct"] >= 75.0:
        unlocked.add("soc_pulse_boost")
    if 79.5 <= s["pct"] <= 80.9:
        unlocked.add("soc_meme_lord")
    if s["total"] >= 30:
        unlocked.add("soc_veteran")


def _check_easter_egg_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет пасхалки и скрытые активности интерфейса."""
    unlocked.update({"egg_jubilee_300", "egg_speed_click", "egg_cleaner"})
    if s["p"] >= 15:
        unlocked.update({"egg_tea_break", "egg_matrix", "egg_tracer"})
    if s["p"] >= 25:
        unlocked.update({"egg_tapper", "egg_api_hacker"})
    if s["pct"] >= 95.0 and s["total"] >= 15:
        unlocked.add("egg_vip")
    if s["p"] >= 45:
        unlocked.add("egg_konami")


def _check_mastery_rules(s: dict[str, Any], unlocked: set[str]) -> None:
    """Проверяет высшие статусные достижения и ранговые рубежи."""
    if 79.5 <= s["pct"] <= 80.9:
        unlocked.add("mast_first_course")
    if 81.0 <= s["pct"] <= 89.9:
        unlocked.add("mast_normis_life")
    if s["pct"] >= 99.9 and s["n"] == 0 and s["o"] == 0:
        unlocked.add("mast_favorite")
    if len(unlocked) >= 10:
        unlocked.add("mast_badge_collector")
    if len(unlocked) >= 15:
        unlocked.add("mast_grandmaster")
    if len(unlocked) >= 20:
        unlocked.add("mast_all_rounder")


def _evaluate_all_rules(s: dict[str, Any], extra: set[str] | None) -> list[str]:
    """Агрегирует последовательную проверку всех категорий достижений."""
    unlocked: set[str] = set()
    _check_attendance_rules(s, unlocked)
    _check_punctuality_rules(s, unlocked)
    _check_bot_rules(s, unlocked)
    _check_ai_rules(s, unlocked)
    _check_student_life_rules(s, unlocked)
    _check_social_rules(s, unlocked)
    _check_easter_egg_rules(s, unlocked)
    _check_mastery_rules(s, unlocked)
    if extra:
        unlocked.update(extra)
    return sorted(list(unlocked))


def calculate_student_xp(stat: dict[str, Any], unlocked_ach_ids: list[str]) -> int:
    """Рассчитывает суммарные очки академического опыта (XP) строго по открытым ачивкам."""
    return sum(ACHIEVEMENTS_MAP[aid].xp_reward for aid in unlocked_ach_ids if aid in ACHIEVEMENTS_MAP)


def _extract_student_metrics(fio: str, raw_data: dict[str, Any]) -> dict[str, Any]:
    """Преобразует сырые показатели посещаемости в нормализованную структуру."""
    tot = raw_data.get("total", {})
    p, o = tot.get("П", 0), tot.get("О", 0)
    u, n = tot.get("У", 0), tot.get("Н", 0)
    total = p + o + u + n
    pct = ((p + o + u) / total * 100.0) if total > 0 else 100.0
    return {"fio": fio, "p": p, "o": o, "u": u, "n": n, "total": total, "pct": pct}


def is_starosta(fio: str) -> bool:
    """Проверяет, является ли студент Старостой группы (Дмитрий Стрыгин)."""
    return "стрыгин" in fio.lower()


def build_student_profile(fio: str, raw_data: dict[str, Any], extra: set[str] | None = None) -> StudentProfile:
    """Создает объект профиля студента с нуля или с реально открытыми достижениями."""
    m = _extract_student_metrics(fio, raw_data)
    starosta = is_starosta(fio)
    rank = STAROSTA_RANK if starosta else resolve_student_rank(m["pct"], m["n"], m["o"])
    unlocked = sorted(list(extra)) if extra else []
    xp = calculate_student_xp(m, unlocked)

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
        unlocked_achievements=unlocked,
    )


async def _load_cached_leaderboard() -> list[StudentProfile] | None:
    """Загружает предварительно рассчитанный рейтинг студентов из Redis."""
    raw = await cache_get(LEADERBOARD_CACHE_KEY)
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return [StudentProfile(**item) for item in data]
    except Exception as exc:
        log.warning("Ошибка десериализации кэша лидерборда: %s", exc)
        return None


async def _save_cached_leaderboard(profiles: list[StudentProfile]) -> None:
    """Сохраняет рассчитанный рейтинг студентов в Redis на 300 секунд."""
    try:
        data = [asdict(p) for p in profiles]
        payload = json.dumps(data, ensure_ascii=False)
        await cache_set(LEADERBOARD_CACHE_KEY, payload, ttl=LEADERBOARD_CACHE_TTL)
    except Exception as exc:
        log.warning("Ошибка сохранения кэша лидерборда: %s", exc)


def _match_student_achievements(fio: str, unlocked_map: dict[str, set[str]]) -> set[str]:
    """Находит все открытые ачивки студента по точному или частичному совпадению ФИО."""
    clean = fio.strip().lower()
    res: set[str] = set()
    for stored_fio, aids in unlocked_map.items():
        if stored_fio == clean or stored_fio in clean or clean in stored_fio:
            res.update(aids)
    return res


async def get_group_leaderboard(
    provided_stats: dict[str, Any] | None = None,
    force_refresh: bool = False,
) -> list[StudentProfile]:
    """Формирует упорядоченный список студентов группы 1-КПД-3 по рангу и XP."""
    if not provided_stats and not force_refresh:
        cached = await _load_cached_leaderboard()
        if cached:
            return cached

    stats = provided_stats or await fetch_all_time_attendance()
    unlocked_map = await GamificationRepository.get_all_unlocked_map()
    profiles = [
        build_student_profile(fio, data, _match_student_achievements(fio, unlocked_map)) for fio, data in stats.items()
    ]
    profiles.sort(key=lambda s: (1 if is_starosta(s.fio) else 0, -s.attendance_pct, -s.xp, -s.present_count, s.fio))
    if not provided_stats:
        await _save_cached_leaderboard(profiles)
    return profiles


async def get_student_profile_by_fio(fio: str, extra: set[str] | None = None) -> StudentProfile | None:
    """Находит статистику студента по ФИО и возвращает профиль геймификации."""
    board = await get_group_leaderboard()
    clean = fio.strip().lower()
    matched = next((p for p in board if clean in p.fio.lower() or p.fio.lower() in clean), None)
    if matched and not extra:
        return matched
    if matched and extra:
        raw = {
            "total": {
                "П": matched.present_count,
                "О": matched.late_count,
                "У": matched.excused_count,
                "Н": matched.unexcused_count,
            }
        }
        return build_student_profile(matched.fio, raw, extra)
    stats = await fetch_all_time_attendance()
    matched_fio = next((k for k in stats if clean in k.lower() or k.lower() in clean), None)
    if not matched_fio:
        return None
    return build_student_profile(matched_fio, stats[matched_fio], extra)
