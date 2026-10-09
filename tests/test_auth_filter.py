"""
Unit-тесты для AuthFilter (фильтра авторизации по Telegram ID).

Проверяет:
  1. Доступ разрешен для ALLOWED_USER_ID (Message и CallbackQuery)
  2. Доступ запрещен для чужих ID
  3. Корректная обработка событий без from_user (сервисные сообщения)
"""

from unittest.mock import MagicMock

import pytest
from aiogram.types import CallbackQuery, Message, User

from bot.filters.auth import AuthFilter


@pytest.mark.asyncio
async def test_auth_filter_allows_authorized_message(auth_user: User):
    """Проверяет, что сообщение от разрешенного пользователя проходит фильтр."""
    filter_obj = AuthFilter()
    msg = MagicMock(spec=Message)
    msg.from_user = auth_user
    assert await filter_obj(msg) is True


@pytest.mark.asyncio
async def test_auth_filter_denies_stranger_message(stranger_user: User):
    """Проверяет, что сообщение от постороннего пользователя блокируется."""
    filter_obj = AuthFilter()
    msg = MagicMock(spec=Message)
    msg.from_user = stranger_user
    assert await filter_obj(msg) is False


@pytest.mark.asyncio
async def test_auth_filter_allows_authorized_callback(auth_user: User):
    """Проверяет, что CallbackQuery от разрешенного пользователя проходит фильтр."""
    filter_obj = AuthFilter()
    cb = MagicMock(spec=CallbackQuery)
    cb.from_user = auth_user
    assert await filter_obj(cb) is True


@pytest.mark.asyncio
async def test_auth_filter_denies_stranger_callback(stranger_user: User):
    """Проверяет, что CallbackQuery от постороннего пользователя блокируется."""
    filter_obj = AuthFilter()
    cb = MagicMock(spec=CallbackQuery)
    cb.from_user = stranger_user
    assert await filter_obj(cb) is False


@pytest.mark.asyncio
async def test_auth_filter_handles_none_user():
    """Проверяет, что событие без from_user (анонимный канал) отклоняется без ошибки."""
    filter_obj = AuthFilter()
    event = MagicMock(spec=Message)
    event.from_user = None
    assert await filter_obj(event) is False
