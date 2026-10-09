"""
Модуль регистрации интерактивного меню команд Telegram (bot.set_my_commands).

Настраивает видимость команд через BotCommandScope:
  - BotCommandScopeDefault: базовые команды для всех студентов группы
  - BotCommandScopeChat: расширенные команды управления для старосты (ALLOWED_USER_ID)
"""

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from config import ALLOWED_USER_ID
from core.logger import get_logger

log = get_logger("bot_commands")


def get_default_user_commands() -> list[BotCommand]:
    """Возвращает список общедоступных команд для студентов группы."""
    return [
        BotCommand(command="today", description="📅 Расписание на сегодня"),
        BotCommand(command="notice", description="🔔 Настройка напоминаний"),
        BotCommand(command="my_attendance", description="📊 Моя посещаемость"),
        BotCommand(command="help", description="❓ Справка по боту"),
    ]


def get_admin_commands() -> list[BotCommand]:
    """Возвращает расширенный список команд для старосты группы."""
    return [
        *get_default_user_commands(),
        BotCommand(command="admin", description="⚙️ Панель управления старосты"),
        BotCommand(command="attendance", description="📋 Отметка посещаемости"),
        BotCommand(command="all", description="📢 Общий пинг группы"),
        BotCommand(command="testers", description="🧪 Управление тестерами API"),
        BotCommand(command="swagger", description="🚀 Портал Swagger UI"),
    ]


async def register_bot_commands(bot: Bot) -> None:
    """Регистрирует меню команд в Telegram API для пользователей и администратора."""
    try:
        await bot.set_my_commands(get_default_user_commands(), scope=BotCommandScopeDefault())
        await bot.set_my_commands(get_admin_commands(), scope=BotCommandScopeChat(chat_id=ALLOWED_USER_ID))
        log.info("✅ Системное меню команд бота успешно зарегистрировано в Telegram")
    except Exception as e:  # noqa: BLE001
        log.warning(f"⚠️ Не удалось зарегистрировать системное меню команд: {e}")
