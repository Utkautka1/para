"""
Тесты выдачи событийных ачивок (services/achievement_events.py) и счётчиков SQLite.

Проверяет:
  1. Атомарный счётчик: обычный и «раз в день» (CounterRepository на временной БД)
  2. Пороги накопительных ачивок выдаются при «>=» — догоняют пропущенные
  3. Реплаи в чате: старосте, одногруппнику, боту и самому себе
  4. Посторонние пользователи не попадают в счётчики
  5. «Солидарность» не засчитывает свой профиль и повторы
"""

from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from config import ALLOWED_USER_ID
from db.sqlite.repositories import CounterRepository
from services import achievement_events as ev

CLASSMATE_ID = 111
OTHER_ID = 222


@pytest_asyncio.fixture
async def temp_db(tmp_path: Path):
    """Чистая SQLite-база на время теста."""
    import core.database as db_mod

    db_file = tmp_path / "ach.db"
    with (
        patch("core.database.SQLITE_DB_PATH", str(db_file)),
        patch("core.database.DATABASE_URL", f"sqlite+aiosqlite:///{db_file}"),
        patch("core.database.SUBSCRIBERS_FILE_PATH", str(tmp_path / "none.json")),
    ):
        db_mod._engine = None
        db_mod._session_factory = None
        await db_mod.init_db()
        yield
        db_mod._engine = None
        db_mod._session_factory = None


@pytest.fixture
def members():
    """Одногруппники: CLASSMATE_ID и OTHER_ID; остальные — посторонние."""
    registry = {CLASSMATE_ID: {"full_name": "Иванов Иван"}, OTHER_ID: {"full_name": "Петров Пётр"}}
    with (
        patch("services.achievement_events.find_classmate_by_tg_id", side_effect=registry.get),
        patch("services.achievement_service.find_classmate_by_tg_id", side_effect=registry.get),
    ):
        yield


@pytest.mark.asyncio
async def test_counter_increment_and_daily(temp_db) -> None:
    assert [await CounterRepository.increment("Иванов", "x") for _ in range(3)] == [1, 2, 3]
    today = date(2026, 11, 2)
    assert await CounterRepository.increment("Иванов", "days", today) == 1
    assert await CounterRepository.increment("Иванов", "days", today) == 1
    assert await CounterRepository.increment("Иванов", "days", date(2026, 11, 3)) == 2


@pytest.mark.asyncio
async def test_counter_count_keys(temp_db) -> None:
    for kind in ("text", "photo", "photo"):
        await CounterRepository.increment("Иванов", f"hw_kind:{kind}")
    assert await CounterRepository.count_keys("Иванов", "hw_kind:") == 2
    assert await CounterRepository.count_keys("Петров", "hw_kind:") == 0


@pytest.mark.asyncio
async def test_bump_counter_awards_reached_thresholds(members) -> None:
    award = AsyncMock(return_value=True)
    with (
        patch.object(ev.CounterRepository, "increment", AsyncMock(return_value=12)),
        patch.object(ev, "award_achievement", award),
    ):
        await ev.bump_counter(CLASSMATE_ID, "hw_tasks", None, None)
    assert {c.args[1] for c in award.await_args_list} == {"ai_gost_docx", "ai_deepseek_fan"}


@pytest.mark.asyncio
async def test_strangers_are_not_counted(members) -> None:
    increment = AsyncMock()
    user = MagicMock(id=999, full_name="Чужой")
    with patch.object(ev.CounterRepository, "increment", increment):
        await ev.on_interaction(user, None)
    increment.assert_not_awaited()


def _group_message(reply_to_id: int | None, is_bot: bool = False) -> MagicMock:
    msg = MagicMock(sticker=None, text="ок", caption=None)
    msg.from_user = MagicMock(id=CLASSMATE_ID, is_bot=False, full_name="Иванов Иван")
    msg.reply_to_message = (
        MagicMock(from_user=MagicMock(id=reply_to_id, is_bot=is_bot)) if reply_to_id is not None else None
    )
    return msg


@pytest.mark.parametrize(
    ("reply_to", "is_bot", "expected"),
    [
        (ALLOWED_USER_ID, False, "soc_headman_ally"),
        (OTHER_ID, False, "chat_replies"),
        (OTHER_ID, True, None),
        (CLASSMATE_ID, False, None),
        (None, False, None),
    ],
)
def test_chat_reply_classification(members, reply_to, is_bot, expected) -> None:
    assert ev._chat_reply_achievement(_group_message(reply_to, is_bot), CLASSMATE_ID) == expected


@pytest.mark.asyncio
async def test_ping_window_awards_muster(members) -> None:
    award = AsyncMock(return_value=True)
    with (
        patch.object(ev, "bump_counter", AsyncMock(return_value=1)),
        patch.object(ev, "award_achievement", award),
        patch.object(ev, "cache_get", AsyncMock(return_value="1")),
    ):
        await ev.on_group_message(_group_message(None), None)
    assert [c.args[1] for c in award.await_args_list] == ["soc_ping_muster"]


@pytest.mark.asyncio
async def test_profile_view_ignores_self_and_counts_distinct(temp_db, members) -> None:
    with patch.object(ev, "award_achievement", AsyncMock(return_value=True)) as award:
        assert await ev.on_profile_view(CLASSMATE_ID, "Иванов Иван") is False
        for fio in ["А А", "Б Б", "В В", "Г Г", "Г Г"]:
            assert await ev.on_profile_view(CLASSMATE_ID, fio) is False
        assert await ev.on_profile_view(CLASSMATE_ID, "Д Д") is True
    award.assert_awaited_once_with(CLASSMATE_ID, "soc_solidarity")
