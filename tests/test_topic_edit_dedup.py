"""
Тесты пропуска неизменных правок поста расписания в топике.

Проверяет:
  1. Повтор того же текста и клавиатуры не вызывает edit_message_text.
  2. Изменённый текст редактируется сразу.
  3. Раз в _FORCE_EDIT_EVERY_SECONDS правка уходит даже без изменений.
  4. Ответ 'not modified' тоже запоминается как подтверждённое состояние.
"""

from unittest.mock import AsyncMock, patch

import pytest
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import services.topic_updater as tu

_KB = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄", callback_data="sched:refresh")]])


@pytest.fixture(autouse=True)
def _topic_state():
    """Изолирует глобальное состояние поста между тестами."""
    tu._TOPIC_MAIN_MSG_ID = 100
    tu._LAST_SENT = None
    yield
    tu._TOPIC_MAIN_MSG_ID = None
    tu._LAST_SENT = None


@pytest.mark.asyncio
async def test_identical_payload_skips_telegram_call() -> None:
    """Второй вызов с тем же содержимым не идёт в Telegram."""
    edit = AsyncMock()
    with patch.object(tu.bot, "edit_message_text", edit):
        assert await tu.update_topic_message_payload("пары", _KB)
        assert await tu.update_topic_message_payload("пары", _KB)
    assert edit.await_count == 1


@pytest.mark.asyncio
async def test_changed_text_is_edited() -> None:
    """Изменение текста (таймер до пары) редактируется сразу."""
    edit = AsyncMock()
    with patch.object(tu.bot, "edit_message_text", edit):
        await tu.update_topic_message_payload("через 5 мин", _KB)
        await tu.update_topic_message_payload("через 4 мин", _KB)
    assert edit.await_count == 2


@pytest.mark.asyncio
async def test_periodic_forced_edit_detects_deleted_message() -> None:
    """Спустя _FORCE_EDIT_EVERY_SECONDS правка уходит даже без изменений."""
    edit = AsyncMock()
    with patch.object(tu.bot, "edit_message_text", edit):
        await tu.update_topic_message_payload("пары", _KB)
        msg_id, fp, sent_at = tu._LAST_SENT
        tu._LAST_SENT = (msg_id, fp, sent_at - tu._FORCE_EDIT_EVERY_SECONDS - 1)
        await tu.update_topic_message_payload("пары", _KB)
    assert edit.await_count == 2


@pytest.mark.asyncio
async def test_not_modified_response_is_remembered() -> None:
    """После 'message is not modified' повтор того же содержимого не отправляется."""
    err = TelegramBadRequest(method=AsyncMock(), message="Bad Request: message is not modified")
    edit = AsyncMock(side_effect=[err])
    with patch.object(tu.bot, "edit_message_text", edit):
        assert await tu.update_topic_message_payload("пары", _KB)
        assert await tu.update_topic_message_payload("пары", _KB)
    assert edit.await_count == 1
