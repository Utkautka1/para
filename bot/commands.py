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
    """
    Возвращает список общедоступных команд бота для студентов группы.

    Отображается в системном меню ввода команд Telegram у всех пользователей.
    Содержит базовые функции просмотра пар, напоминаний и справки.

    Возвращает список объектов BotCommand.
    """

    return [
        BotCommand(command="start", description="🚀 Главное меню"),
        BotCommand(command="profile", description="👤 Мой профиль и ачивки"),
        BotCommand(command="leaderboard", description="🏆 Рейтинг группы 1-КПД-3"),
        BotCommand(command="today", description="📅 Расписание на сегодня"),
        BotCommand(command="notice", description="🔔 Настройка напоминаний"),
        BotCommand(command="my_attendance", description="📊 Моя посещаемость"),
        BotCommand(command="help", description="❓ Справка по боту"),
    ]


def get_admin_commands() -> list[BotCommand]:
    """
    Возвращает расширенный список команд управления для старосты группы.

    Дополняет пользовательские команды функциями журнала, пинга и тестеров.
    Регистрируется персонально в чате администратора через BotCommandScopeChat.

    Возвращает расширенный список объектов BotCommand.
    """

    return [
        *get_default_user_commands(),
        BotCommand(command="admin", description="⚙️ Панель управления старосты"),
        BotCommand(command="attendance", description="📋 Отметка посещаемости"),
        BotCommand(command="all", description="📢 Общий пинг группы"),
        BotCommand(command="testers", description="🧪 Управление тестерами API"),
        BotCommand(command="swagger", description="🚀 Портал Swagger UI"),
    ]


async def register_bot_commands(bot: Bot) -> None:
    """
    Регистрирует меню команд в Telegram API для пользователей и старосты.

    Разделяет видимость команд по области видимости (Default и Chat scope).
    Перехватывает сетевые исключения, не блокируя общий запуск бота.

    Ничего не возвращает.
    """

    try:
        await bot.set_my_commands(get_default_user_commands(), scope=BotCommandScopeDefault())
        await bot.set_my_commands(get_admin_commands(), scope=BotCommandScopeChat(chat_id=ALLOWED_USER_ID))
        from aiogram.types import MenuButtonWebApp, WebAppInfo

        from config import MINIAPP_URL

        if MINIAPP_URL:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(text="🎮 Mini App", web_app=WebAppInfo(url=MINIAPP_URL))
            )
        log.info("✅ Системное меню команд бота и кнопка Mini App успешно зарегистрированы в Telegram")
    except Exception as e:
        log.warning(f"⚠️ Не удалось зарегистрировать системное меню команд: {e}")
