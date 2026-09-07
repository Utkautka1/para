"""
Хэндлер обработки сообщений от неавторизованных пользователей.

Срабатывает, если Telegram ID отправителя не совпадает с ALLOWED_USER_ID.
"""

from aiogram import Router, F
from aiogram.types import Message
from config import ALLOWED_USER_ID

router = Router()


@router.message(F.chat.type == "private")
async def unauth_fallback(message: Message) -> None:
    """
    Информирует посторонних пользователей об ограничении доступа в ЛС.

    :param message: Входящее сообщение
    """
    if message.from_user and message.from_user.id != ALLOWED_USER_ID:
        await message.answer(
            "⛔ <b>Доступ ограничен.</b>\n"
            "Этот бот работает персонально в приватном режиме."
        )
