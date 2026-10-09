"""
Unit-тесты модуля bot/commands.py.

Проверяет:
  1. Корректность списков команд пользователей и старосты (get_default_user_commands, get_admin_commands)
  2. Регистрацию команд в Telegram API через bot.set_my_commands с нужными областями (scopes)
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import BotCommandScopeChat, BotCommandScopeDefault

from bot.commands import (
    get_admin_commands,
    get_default_user_commands,
    register_bot_commands,
)
from config import ALLOWED_USER_ID


def test_get_default_user_commands():
    """Проверяет наличие базовых команд для студентов."""
    cmds = get_default_user_commands()
    cmd_names = [c.command for c in cmds]
    assert "today" in cmd_names
    assert "notice" in cmd_names
    assert "my_attendance" in cmd_names
    assert "help" in cmd_names
    assert "admin" not in cmd_names


def test_get_admin_commands():
    """Проверяет расширенный набор команд для старосты группы."""
    cmds = get_admin_commands()
    cmd_names = [c.command for c in cmds]
    assert "today" in cmd_names
    assert "admin" in cmd_names
    assert "attendance" in cmd_names
    assert "all" in cmd_names
    assert "testers" in cmd_names
    assert "swagger" in cmd_names


@pytest.mark.asyncio
async def test_register_bot_commands_success():
    """Проверяет вызовы bot.set_my_commands с default и chat scopes."""
    bot = MagicMock()
    bot.set_my_commands = AsyncMock()

    await register_bot_commands(bot)

    assert bot.set_my_commands.call_count == 2
    first_call = bot.set_my_commands.call_args_list[0]
    second_call = bot.set_my_commands.call_args_list[1]

    assert isinstance(first_call.kwargs["scope"], BotCommandScopeDefault)
    assert isinstance(second_call.kwargs["scope"], BotCommandScopeChat)
    assert second_call.kwargs["scope"].chat_id == ALLOWED_USER_ID


@pytest.mark.asyncio
async def test_register_bot_commands_handles_exception():
    """Проверяет, что сбой Telegram API при регистрации команд не роняет бота."""
    bot = MagicMock()
    bot.set_my_commands = AsyncMock(side_effect=Exception("Telegram Network Error"))

    # Должен перехватить исключение и не вызывать падения
    await register_bot_commands(bot)
