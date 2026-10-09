"""
Unit-тесты для хэндлера обработки неавторизованных пользователей (bot/handlers/user/auth_fallback.py).

Проверяет:
  1. Вывод сообщения об отказе в доступе с корректным telegram_id для постороннего пользователя.
  2. Игнорирование хэндлера для подтвержденного одногруппника (авторизован).
  3. Игнорирование хэндлера для зарегистрированного тестировщика API.
  4. Корректную обработку случая без message.from_user.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.user.auth_fallback import unauth_fallback


@pytest.mark.asyncio
async def test_unauth_fallback_shows_id_to_stranger() -> None:
    """Проверяет отправку ID и сообщения об отказе постороннему пользователю."""
    message = MagicMock()
    user = MagicMock()
    user.id = 987654321
    user.username = "unknown_user"
    message.from_user = user
    message.answer = AsyncMock()

    with patch("bot.handlers.user.auth_fallback.is_authorized_user", return_value=False), \
         patch("bot.handlers.user.auth_fallback.is_tester_allowed", new=AsyncMock(return_value=False)):
        await unauth_fallback(message)

    message.answer.assert_awaited_once()
    called_text = message.answer.call_args[0][0]
    assert "987654321" in called_text
    assert "Доступ ограничен" in called_text


@pytest.mark.asyncio
async def test_unauth_fallback_ignores_authorized_user() -> None:
    """Проверяет, что авторизованный одногруппник пропускается без ответа."""
    message = MagicMock()
    user = MagicMock()
    user.id = 12345
    message.from_user = user
    message.answer = AsyncMock()

    with patch("bot.handlers.user.auth_fallback.is_authorized_user", return_value=True):
        await unauth_fallback(message)

    message.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_unauth_fallback_ignores_tester() -> None:
    """Проверяет, что авторизованный тестер пропускается без вывода отказа."""
    message = MagicMock()
    user = MagicMock()
    user.id = 55555
    message.from_user = user
    message.answer = AsyncMock()

    with patch("bot.handlers.user.auth_fallback.is_authorized_user", return_value=False), \
         patch("bot.handlers.user.auth_fallback.is_tester_allowed", new=AsyncMock(return_value=True)):
        await unauth_fallback(message)

    message.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_unauth_fallback_no_user() -> None:
    """Проверяет корректный пропуск сообщения, если from_user отсутствует."""
    message = MagicMock()
    message.from_user = None
    message.answer = AsyncMock()

    await unauth_fallback(message)
    message.answer.assert_not_awaited()
