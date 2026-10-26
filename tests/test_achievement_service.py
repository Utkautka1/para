"""
Тесты сервиса выдачи академических достижений и Telegram-уведомлений.
"""

from unittest.mock import AsyncMock, patch

import pytest

from services.achievement_service import (
    award_achievement,
    format_achievement_notification,
    invalidate_leaderboard_cache,
    resolve_student_fio,
)
from services.gamification_registry import ACHIEVEMENTS_MAP


def test_resolve_student_fio_registered() -> None:
    """Проверяет поиск студента в реестре по TG ID."""
    with patch(
        "services.achievement_service.find_classmate_by_tg_id",
        return_value={"full_name": "Скачков Никита", "tg_id": 6427213141},
    ):
        name = resolve_student_fio(6427213141, "Fallback")
        assert "Скачков" in name


def test_resolve_student_fio_fallback() -> None:
    """Проверяет возврат запасного имени для незарегистрированного ID."""
    with patch("services.achievement_service.find_classmate_by_tg_id", return_value=None):
        name = resolve_student_fio(999999999, "Запасной Студент")
        assert name == "Запасной Студент"


def test_format_achievement_notification() -> None:
    """Проверяет форматирование HTML-сообщения об ачивке."""
    ach = ACHIEVEMENTS_MAP["bot_welcome"]
    html_msg = format_achievement_notification(ach)
    assert "НОВОЕ ДОСТИЖЕНИЕ" in html_msg
    assert ach.title in html_msg
    assert str(ach.xp_reward) in html_msg


@pytest.mark.asyncio
async def test_award_achievement_success() -> None:
    """Проверяет успешное открытие достижения с отправкой уведомления."""
    mock_bot = AsyncMock()
    with (
        patch(
            "services.achievement_service.find_classmate_by_tg_id",
            return_value={"full_name": "Скачков Никита", "tg_id": 6427213141},
        ),
        patch(
            "db.sqlite.repositories.GamificationRepository.unlock_achievement", new_callable=AsyncMock
        ) as mock_unlock,
        patch("services.achievement_service.cache_delete", new_callable=AsyncMock) as mock_delete,
    ):
        mock_unlock.return_value = True
        result = await award_achievement(6427213141, "bot_welcome", bot=mock_bot)
        assert result is True
        mock_unlock.assert_awaited_once()
        mock_delete.assert_awaited_once()
        mock_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_award_achievement_already_unlocked() -> None:
    """Проверяет возврат False, если достижение уже было разблокировано ранее."""
    mock_bot = AsyncMock()
    with (
        patch(
            "services.achievement_service.find_classmate_by_tg_id",
            return_value={"full_name": "Скачков Никита", "tg_id": 6427213141},
        ),
        patch(
            "db.sqlite.repositories.GamificationRepository.unlock_achievement", new_callable=AsyncMock
        ) as mock_unlock,
    ):
        mock_unlock.return_value = False
        result = await award_achievement(6427213141, "bot_welcome", bot=mock_bot)
        assert result is False
        mock_bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_invalidate_leaderboard_cache() -> None:
    """Проверяет инвалидацию ключа кэша лидерборда в Redis."""
    with patch("services.achievement_service.cache_delete", new_callable=AsyncMock) as mock_delete:
        await invalidate_leaderboard_cache()
        mock_delete.assert_awaited_once()
