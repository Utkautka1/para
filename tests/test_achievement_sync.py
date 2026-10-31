"""
Тесты фоновой выдачи журнальных ачивок в worker (services/achievement_sync.py).

Проверяет:
  1. Уже открытые ачивки не выдаются повторно, нарушенное условие их не отзывает
  2. Новые ачивки сохраняются под ФИО из реестра и приходят ОДНИМ сообщением
  3. Студент без Telegram получает ачивки, но без уведомления
  4. После сброса отметки до точки отсчёта в ачивки не идут, места и пульс — по новым
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from config import TIMEZONE
from services import achievement_sync as sync
from services.achievement_rules import build_student_stat
from services.gamification import build_student_profile
from services.gamification_registry import ACHIEVEMENTS_MAP


def _raw(p: int, n: int = 0) -> dict:
    return {"total": {"П": p, "О": 0, "У": 0, "Н": n}, "months": {"ОКТ": {"П": p, "Н": n}}}


def test_compute_new_skips_owned_and_never_revokes() -> None:
    raw = _raw(30, n=10)
    profile = build_student_profile("Иванов Иван", raw, extra={"att_100", "att_ghost"})
    with patch.object(sync, "find_classmate_by_fio", return_value=None):
        new = sync.compute_new_achievements(profile, build_student_stat(raw), places={}, pulse=50.0)
    # «Клуб 100%» уже открыт и при 75% не отзывается; «Учебный рывок» не дублируется
    assert "att_100" not in new and "att_ghost" not in new
    assert "soc_pulse_boost" in new


@pytest.mark.asyncio
async def test_sync_sends_single_digest_per_student() -> None:
    stats = {"Иванов Иван": _raw(26), "Петров Пётр": _raw(26)}
    registry = {
        "Иванов Иван": {"full_name": "Иванов Иван Иванович", "tg_id": 111, "day": 1},
        "Петров Пётр": {"full_name": "Петров Пётр"},
    }
    unlock = AsyncMock(side_effect=lambda fio, aid: ACHIEVEMENTS_MAP[aid])
    send = AsyncMock()
    with (
        patch.object(sync.AchievementResetRepository, "get_baselines", AsyncMock(return_value={})),
        patch.object(sync, "fetch_all_time_attendance", AsyncMock(return_value=stats)),
        patch("services.gamification.GamificationRepository.get_all_unlocked_map", AsyncMock(return_value={})),
        patch.object(sync, "find_classmate_by_fio", side_effect=lambda fio: registry.get(fio)),
        patch.object(sync, "unlock_for_fio", unlock),
        patch.object(sync, "send_achievement_message", send),
        patch.object(sync, "invalidate_leaderboard_cache", AsyncMock()),
    ):
        granted = await sync.sync_stat_achievements(bot=object())
    owners = {c.args[0] for c in unlock.await_args_list}
    assert owners == {"Иванов Иван Иванович", "Петров Пётр"}
    assert granted == unlock.await_count
    send.assert_awaited_once()
    assert send.await_args.args[1] == 111


@pytest.mark.asyncio
async def test_baseline_hides_marks_before_reset() -> None:
    stats = {"Иванов Иван": _raw(30), "Петров Пётр": _raw(30, n=20)}
    # Иванов набрал всё до сброса, Петров после сброса пришёл на 3 пары
    baselines = {"Иванов Иван": _raw(30), "Петров Пётр": _raw(27, n=20)}
    unlock = AsyncMock(side_effect=lambda fio, aid: ACHIEVEMENTS_MAP[aid])
    with (
        patch.object(sync.AchievementResetRepository, "get_baselines", AsyncMock(return_value=baselines)),
        patch.object(sync, "fetch_all_time_attendance", AsyncMock(return_value=stats)),
        patch("services.gamification.GamificationRepository.get_all_unlocked_map", AsyncMock(return_value={})),
        patch.object(sync, "find_classmate_by_fio", return_value=None),
        patch.object(sync, "unlock_for_fio", unlock),
        patch.object(sync, "invalidate_leaderboard_cache", AsyncMock()),
    ):
        await sync.sync_stat_achievements(bot=None)
    granted = {(c.args[0], c.args[1]) for c in unlock.await_args_list}
    assert not [aid for fio, aid in granted if fio == "Иванов Иван"]
    assert ("Петров Пётр", "att_ghost") not in granted


def test_group_context_uses_board_order_and_fresh_pulse() -> None:
    board = [
        build_student_profile("Петров Пётр", _raw(10)),
        build_student_profile("Иванов Иван", _raw(20)),
        build_student_profile("Стрыгин Дмитрий", _raw(25)),
    ]
    deltas = {
        "Иванов Иван": build_student_stat(_raw(20)),
        "Петров Пётр": build_student_stat(_raw(10, n=10)),
        "Сидоров Сидор": build_student_stat({}),
    }
    places, pulse = sync._group_context(board, deltas)
    # Места — ровно порядок лидерборда, староста вне рейтинга
    assert places == {"Петров Пётр": 1, "Иванов Иван": 2}
    assert pulse == pytest.approx((100 + 50) / 2)


@pytest.mark.parametrize(
    ("classmate", "expected"),
    [
        ({"day": 1, "month": 11}, True),
        ({"day": 2, "month": 11}, False),
        ({"full_name": "Без даты"}, False),
        (None, False),
    ],
)
def test_birthday_only_on_the_day(classmate: dict | None, expected: bool) -> None:
    fake_now = datetime(2026, 11, 1, 12, 0, tzinfo=TIMEZONE)
    with patch.object(sync, "datetime", wraps=datetime) as dt:
        dt.now.return_value = fake_now
        assert sync._is_birthday_today(classmate) is expected
