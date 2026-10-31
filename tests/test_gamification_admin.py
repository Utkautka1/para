"""
Тесты ручного управления ачивками и очками из админ-панели.

Проверяет:
  1. Репозиторий: атомарная правка бонуса, снятие ачивки под любым ФИО студента
  2. Сервис: начисление/списание бонуса и выдача/снятие ачивки с уведомлением студента
  3. Шаблоны: callback_data всех кнопок укладывается в лимит Telegram (64 байта),
     категории покрывают весь каталог, включая секретные ачивки
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from bot.templates.admin import gamification as tgame
from db.sqlite.repositories import CounterRepository, GamificationRepository
from services import gamification_admin as admin
from services.gamification import build_student_profile
from services.gamification_registry import ACHIEVEMENTS_MAP

# Лимит Telegram на длину callback_data (байты)
CALLBACK_DATA_LIMIT = 64


@pytest_asyncio.fixture
async def temp_db(tmp_path: Path):
    """Чистая SQLite-база на время теста."""
    import core.database as db_mod

    db_file = tmp_path / "admin.db"
    with (
        patch("core.database.SQLITE_DB_PATH", str(db_file)),
        patch("core.database.DATABASE_URL", f"sqlite+aiosqlite:///{db_file}"),
        patch("core.database.SUBSCRIBERS_FILE_PATH", str(tmp_path / "none.json")),
    ):
        db_mod._engine = None
        db_mod._session_factory = None
        await db_mod.init_db()
        yield
        await db_mod.get_database_engine().dispose()
        db_mod._engine = None
        db_mod._session_factory = None


def _target(unlocked: set[str] | None = None, tg_id: int | None = 111) -> admin.StudentTarget:
    profile = build_student_profile("Иванов Иван Иванович", {"total": {"П": 5}}, extra=unlocked)
    return admin.StudentTarget(profile, "Иванов Иван", tg_id)


@pytest.mark.asyncio
async def test_add_value_and_revoke(temp_db) -> None:
    assert await CounterRepository.add_value("Иванов Иван", "guild_bonus", 100) == 100
    assert await CounterRepository.add_value("Иванов Иван", "guild_bonus", -130) == -30
    await GamificationRepository.unlock_achievement("Иванов Иван Иванович", "att_100")
    removed = await GamificationRepository.revoke_achievement({"Иванов Иван", "Иванов Иван Иванович"}, "att_100")
    assert removed == 1
    assert await GamificationRepository.get_all_unlocked_map() == {}


@pytest.mark.asyncio
async def test_adjust_bonus_notifies_student() -> None:
    bot = MagicMock()
    with (
        patch.object(admin.CounterRepository, "add_value", AsyncMock(return_value=-10)) as add,
        patch.object(admin, "invalidate_leaderboard_cache", AsyncMock()),
        patch.object(admin, "send_achievement_message", AsyncMock()) as send,
    ):
        assert await admin.adjust_bonus(bot, _target(), "guild", -10) == -10
    add.assert_awaited_once_with("Иванов Иван", "guild_bonus", -10)
    assert "списал 10 очков гильдии" in send.await_args.args[2]


@pytest.mark.asyncio
async def test_toggle_grants_then_revokes() -> None:
    with (
        patch.object(admin, "unlock_for_fio", AsyncMock()) as unlock,
        patch.object(admin.GamificationRepository, "revoke_achievement", AsyncMock(return_value=1)) as revoke,
        patch.object(admin, "invalidate_leaderboard_cache", AsyncMock()),
        patch.object(admin, "send_achievement_message", AsyncMock()) as send,
    ):
        assert await admin.toggle_achievement(None, _target(), "egg_dino") is True
        assert await admin.toggle_achievement(None, _target({"egg_dino"}), "egg_dino") is False
    unlock.assert_awaited_once_with("Иванов Иван", "egg_dino")
    revoke.assert_awaited_once_with({"Иванов Иван", "Иванов Иван Иванович"}, "egg_dino")
    # bot=None — уведомлять некуда, но выдача и снятие всё равно прошли
    send.assert_not_awaited()


def _callback_lengths(markup) -> list[int]:
    return [len(b.callback_data.encode()) for row in markup.inline_keyboard for b in row if b.callback_data]


def test_callback_data_fits_telegram_limit() -> None:
    every = set(ACHIEVEMENTS_MAP)
    lengths = _callback_lengths(tgame.student_card_ikb(99)) + _callback_lengths(tgame.categories_ikb(99, []))
    for category in tgame.CATEGORY_TITLES:
        lengths += _callback_lengths(tgame.category_ikb(99, category, list(every)))
    assert max(lengths) <= CALLBACK_DATA_LIMIT


def test_categories_cover_whole_catalog() -> None:
    covered = [aid for category in tgame.CATEGORY_TITLES for aid in tgame.category_achievements(category)]
    assert sorted(covered) == sorted(ACHIEVEMENTS_MAP)


def test_student_card_text_shows_level_and_bonuses() -> None:
    text = tgame.student_card_text(_target({"bot_welcome"}).profile, 29100, -50)
    assert "+29100" in text and "-50" in text and "уровень 1" in text


@pytest.mark.asyncio
async def test_bonus_and_toggle_buttons_round_trip() -> None:
    """Кнопки карточки и категории разбираются хэндлерами в те же параметры, что упакованы."""
    from bot.handlers.admin import gamification as handlers

    target = _target()
    card_btn = tgame.student_card_ikb(3).inline_keyboard[1][0]
    cat_btn = tgame.category_ikb(3, "secret", []).inline_keyboard[0][0]
    call = MagicMock(answer=AsyncMock(), bot=MagicMock())
    with (
        patch.object(handlers.admin, "get_student", AsyncMock(return_value=target)),
        patch.object(handlers.admin, "adjust_bonus", AsyncMock(return_value=-1000)) as adjust,
        patch.object(handlers.admin, "toggle_achievement", AsyncMock(return_value=True)) as toggle,
        patch.object(handlers, "_show_card", AsyncMock()),
        patch.object(handlers, "_show_category", AsyncMock()),
    ):
        await handlers.game_bonus(call, tgame.GameAdminCallback.unpack(card_btn.callback_data))
        await handlers.game_toggle(call, tgame.GameAdminCallback.unpack(cat_btn.callback_data))
    adjust.assert_awaited_once_with(call.bot, target, "xp", -1000)
    toggle.assert_awaited_once_with(call.bot, target, "egg_dino")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("500", (False, 500)),
        ("+500", (False, 500)),
        ("-30", (False, -30)),
        ("=1000", (True, 1000)),
        ("= -5", (True, -5)),
        ("=0", (True, 0)),
        ("1 000", (False, 1000)),
        ("0", None),
        ("abc", None),
        ("", None),
        ("99999999", None),
    ],
)
def test_parse_amount(text: str, expected: tuple[bool, int] | None) -> None:
    assert tgame.parse_amount(text) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(("text", "setter"), [("+250", "adjust_bonus"), ("=1000", "set_bonus")])
async def test_enter_amount_applies_and_clears_state(text: str, setter: str) -> None:
    from bot.handlers.admin import gamification as handlers

    target = _target()
    data = {"idx": 2, "kind": "guild", "message_id": 77}
    state = MagicMock(get_data=AsyncMock(return_value=data), clear=AsyncMock())
    message = MagicMock(text=text, delete=AsyncMock(), bot=MagicMock())
    with (
        patch.object(handlers.admin, "get_student", AsyncMock(return_value=target)),
        patch.object(handlers.admin, setter, AsyncMock()) as apply,
        patch.object(handlers, "_edit_card", AsyncMock()) as card,
    ):
        await handlers.game_enter_amount(message, state)
    apply.assert_awaited_once_with(message.bot, target, "guild", tgame.parse_amount(text)[1])
    state.clear.assert_awaited_once()
    # Ввод удалён, а карточка вернулась на место запроса — в то же сообщение
    message.delete.assert_awaited_once()
    card.assert_awaited_once_with(message, 77, 2)


@pytest.mark.asyncio
async def test_enter_amount_rejects_garbage_and_keeps_state() -> None:
    from bot.handlers.admin import gamification as handlers

    state = MagicMock(get_data=AsyncMock(return_value={"idx": 2, "kind": "xp", "message_id": 77}), clear=AsyncMock())
    message = MagicMock(text="много", delete=AsyncMock())
    with patch.object(handlers, "_edit_panel", AsyncMock()) as panel:
        await handlers.game_enter_amount(message, state)
    message.delete.assert_awaited_once()
    assert panel.await_args.args[1:3] == (77, tgame.incorrect_amount_text)
    state.clear.assert_not_awaited()
