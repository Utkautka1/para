"""
Unit-тесты глобального обработчика ошибок (bot/handlers/errors.py).

Проверяет:
  1. Корректное гашение спиннера для callback_query с show_alert=True
  2. Отправку информативного сообщения пользователю при сбое в обработке message
  3. Отсутствие падения при сетевых сбоях отправки уведомлений об ошибке
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import CallbackQuery, ErrorEvent, Message, Update

from bot.handlers.errors import global_error_handler


@pytest.mark.asyncio
async def test_global_error_handler_callback_query():
    """Проверяет обработку ошибки для callback_query с модальным алертом."""
    cb = MagicMock(spec=CallbackQuery)
    cb.answer = AsyncMock()
    update = MagicMock(spec=Update, callback_query=cb, message=None)
    event = ErrorEvent(update=update, exception=ValueError("Test crash"))

    result = await global_error_handler(event)

    assert result is True
    cb.answer.assert_awaited_once()
    assert "Временный сбой" in cb.answer.call_args[0][0]
    assert cb.answer.call_args.kwargs.get("show_alert") is True


@pytest.mark.asyncio
async def test_global_error_handler_message():
    """Проверяет отправку сообщения при ошибке в текстовом сообщении."""
    msg = MagicMock(spec=Message)
    msg.answer = AsyncMock()
    update = MagicMock(spec=Update, callback_query=None, message=msg)
    event = ErrorEvent(update=update, exception=RuntimeError("Logic error"))

    result = await global_error_handler(event)

    assert result is True
    msg.answer.assert_awaited_once()
    assert "Произошла ошибка" in msg.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_global_error_handler_suppresses_send_failure():
    """Проверяет, что сбой Telegram API при ответе на ошибку не вызывает Unhandled exception."""
    cb = MagicMock(spec=CallbackQuery)
    cb.answer = AsyncMock(side_effect=Exception("Network Timeout"))
    update = MagicMock(spec=Update, callback_query=cb, message=None)
    event = ErrorEvent(update=update, exception=ValueError("Initial failure"))

    result = await global_error_handler(event)
    assert result is True


@pytest.mark.asyncio
async def test_stale_callback_is_warning_without_alert():
    """Устаревшее нажатие после простоя бота — warning без алерта админу и без ответа пользователю."""
    from unittest.mock import patch

    from aiogram.exceptions import TelegramBadRequest

    cb = MagicMock(spec=CallbackQuery)
    cb.answer = AsyncMock()
    update = MagicMock(spec=Update, callback_query=cb, message=None)
    exc = TelegramBadRequest(method=MagicMock(), message="Bad Request: query is too old and response timeout expired")
    event = ErrorEvent(update=update, exception=exc)

    with patch("bot.handlers.errors._dispatch_error_alert", AsyncMock()) as alert:
        assert await global_error_handler(event) is True
    alert.assert_not_called()
    cb.answer.assert_not_called()
