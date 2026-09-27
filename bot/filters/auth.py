"""
Фильтр авторизации пользователей.

Проверяет, соответствует ли Telegram ID отправителя единственному
разрешенному пользователю из конфигурации (ALLOWED_USER_ID).
"""

from typing import Union
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message
from config import ALLOWED_USER_ID


class AuthFilter(Filter):
    """Фильтр доступа по Telegram ID."""

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        """
        Проверяет ID пользователя на соответствие ALLOWED_USER_ID.

        :param event: Входящее сообщение или callback Telegram
        :return: True, если доступ разрешен
        """
        user = getattr(event, "from_user", None)
        if not user:
            return False
        return user.id == ALLOWED_USER_ID

