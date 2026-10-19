"""
Конфигурация pytest и фикстуры для тестирования aiogram 3.

Предоставляет мок-объекты Bot, Message, CallbackQuery, User и Chat
для изолированного unit-тестирования без обращения к Telegram API.
"""

import os
from unittest.mock import AsyncMock

# Отключаем отправку трейсов по сети во время выполнения unit-тестов
os.environ.setdefault("OTEL_ENABLED", "false")

import pytest
from aiogram import Bot
from aiogram.types import Chat, Message, User

from config import ALLOWED_USER_ID, TOPIC_CHAT_ID


@pytest.fixture
def mock_bot() -> AsyncMock:
    """Создает мок-экземпляр Bot для проверки вызовов API Telegram."""
    bot = AsyncMock(spec=Bot)
    bot.id = 123456789
    return bot


@pytest.fixture
def auth_user() -> User:
    """Создает тестового пользователя с правами администратора (ALLOWED_USER_ID)."""
    return User(id=ALLOWED_USER_ID, is_bot=False, first_name="Admin", username="admin_user")


@pytest.fixture
def stranger_user() -> User:
    """Создает тестового постороннего пользователя без прав доступа."""
    return User(id=999999999, is_bot=False, first_name="Stranger", username="stranger_user")


@pytest.fixture
def group_chat() -> Chat:
    """Создает тестовый объект супергруппы с TOPIC_CHAT_ID."""
    return Chat(id=TOPIC_CHAT_ID, type="supergroup", title="KTMC Group")


@pytest.fixture
def mock_message(mock_bot: AsyncMock, auth_user: User, group_chat: Chat) -> AsyncMock:
    """Создает мок-сообщение Telegram со всеми стандартными атрибутами."""
    msg = AsyncMock(spec=Message)
    msg.bot = mock_bot
    msg.message_id = 42
    msg.from_user = auth_user
    msg.chat = group_chat
    msg.text = "/today"
    msg.caption = None
    msg.photo = []
    msg.document = None
    msg.reply_to_message = None
    msg.message_thread_id = None
    msg.answer = AsyncMock()
    return msg
