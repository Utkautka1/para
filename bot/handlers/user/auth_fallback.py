"""
Хэндлер обработки сообщений от неавторизованных пользователей.

Срабатывает, если Telegram ID отправителя не совпадает с ALLOWED_USER_ID.
"""

from aiogram import Router, F
from aiogram.types import Message
from config import ALLOWED_USER_ID
from core.logger import get_logger

log = get_logger("auth_fallback")

router = Router()


@router.message(F.chat.type == "private")
async def unauth_fallback(message: Message) -> None:
    """
    Информирует посторонних пользователей об ограничении доступа в ЛС.

    :param message: Входящее сообщение
    """
    if message.from_user and message.from_user.id != ALLOWED_USER_ID:
        log.warning(
            f"⛔ Попытка доступа неавторизованного пользователя ЛС: "
            f"id={message.from_user.id}, username=@{message.from_user.username}"
        )
        await message.answer(
            "⛔ <b>Доступ ограничен.</b>\n"
            "Этот бот работает персонально в приватном режиме."
        )

