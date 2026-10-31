"""
Сервис академической геймификации, расчета уровней, рангов и достижений.

Отвечает за:
  1. Автоматический расчет рангов (включая мем "ОХ ПЕРВЫЙ КУРС! ПОНЯЛИ?!")
  2. Начисление очков академического опыта (XP) по открытым ачивкам
  3. Формирование турнирной таблицы лидеров группы 1-КПД-3
  4. Скрытие секретных ачивок из чужих профилей

Условия ачивок здесь не проверяются: журнальные правила живут в achievement_rules
(их выдаёт worker), событийные — в achievement_triggers (их выдают хэндлеры).
"""

import json
from dataclasses import asdict, replace
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
    SECRET_IDS,
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


def hide_secret_achievements(profile: StudentProfile, viewer_fio: str | None) -> StudentProfile:
    """
    Убирает секретные ачивки из профиля, если его смотрит не владелец.

    XP не трогаем: внезапные +404 XP без видимой ачивки — часть загадки,
    а пересчёт XP сломал бы сортировку рейтинга между зрителями.

    Возвращает тот же профиль или копию без секретных id.
    """
    if viewer_fio and _same_student(profile.fio, viewer_fio):
        return profile
    visible = [a for a in profile.unlocked_achievements if a not in SECRET_IDS]
    if len(visible) == len(profile.unlocked_achievements):
        return profile
    return replace(profile, unlocked_achievements=visible)


def _same_student(fio: str, other: str) -> bool:
    """Сравнивает ФИО так же, как поиск профиля: одно имя содержит другое."""
    a, b = fio.strip().lower(), other.strip().lower()
    return bool(a and b) and (a in b or b in a)
