"""
Хэндлер обработки сообщений от неавторизованных пользователей.

Срабатывает, если Telegram ID отправителя не совпадает с ALLOWED_USER_ID.
"""

from aiogram import Router, F
from aiogram.types import Message
from core.logger import get_logger

from services.classmates_auth import is_authorized_user

log = get_logger("auth_fallback")

router = Router()


@router.message(F.chat.type == "private")
async def unauth_fallback(message: Message) -> None:
    """
    Информирует посторонних пользователей об ограничении доступа в ЛС.

    Пропускает авторизованных студентов и главного администратора.
    """
    user = message.from_user
    if user and not is_authorized_user(user):
        uid = user.id
        uname = f"@{user.username}" if user.username else "нет username"
        log.warning(f"⛔ Доступ ограничен: id={uid}, username={uname}")
        await message.answer(
            "⛔ <b>Доступ ограничен.</b>\n"
            "Этот бот работает исключительно для студентов группы 1-КПД-3.\n\n"
            f"Ваш Telegram ID: <code>{uid}</code>\n"
            "<i>Если вы учитесь в 1-КПД-3, но не можете войти — отправьте этот ID старосте.</i>"
        )

