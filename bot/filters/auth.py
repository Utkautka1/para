"""
Фильтр авторизации пользователей.

Проверяет, соответствует ли Telegram ID отправителя единственному
разрешенному пользователю из конфигурации (ALLOWED_USER_ID).
"""


from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from config import ALLOWED_USER_ID


class AuthFilter(Filter):
    """Фильтр доступа по Telegram ID исключительно для Главного Администратора."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        """
        Проверяет ID пользователя на соответствие ALLOWED_USER_ID.

        :param event: Входящее сообщение или callback Telegram
        :return: True, если доступ разрешен
        """
        user = getattr(event, "from_user", None)
        if not user:
            return False
        return user.id == ALLOWED_USER_ID


class ClassmateAuthFilter(Filter):
    """Фильтр доступа для администратора и авторизованных студентов группы."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        """
        Проверяет, авторизован ли пользователь для доступа к расписанию.

        :param event: Сообщение или callback Telegram
        :return: True, если пользователь админ или подтвержденный одногруппник
        """
        from services.classmates_auth import is_authorized_user
        user = getattr(event, "from_user", None)
        return is_authorized_user(user)


class AttendanceAuthFilter(Filter):
    """Фильтр доступа для старосты и замстаросты к отметке посещаемости."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        """Проверяет принадлежность ID пользователя к списку старост."""
        from config import ALLOWED_ATTENDANCE_USER_IDS
        user = getattr(event, "from_user", None)
        if not user:
            return False
        return user.id in ALLOWED_ATTENDANCE_USER_IDS

