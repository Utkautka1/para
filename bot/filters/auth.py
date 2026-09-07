"""
Фильтр авторизации пользователей.

Проверяет, соответствует ли Telegram ID отправителя единственному
разрешенному пользователю из конфигурации (ALLOWED_USER_ID).
"""

from aiogram.filters import Filter
from aiogram.types import Message
from config import ALLOWED_USER_ID


class AuthFilter(Filter):
    """Фильтр доступа по Telegram ID."""

    async def __call__(self, message: Message) -> bool:
        """
        Проверяет ID пользователя на соответствие ALLOWED_USER_ID.

        :param message: Входящее сообщение Telegram
        :return: True, если доступ разрешен
        """
        if not message.from_user:
            return False
        return message.from_user.id == ALLOWED_USER_ID
