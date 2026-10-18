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
        Проверяет ID пользователя на соответствие главному администратору проекта.

        Используется в защищенных роутерах панели управления старосты.
        Защищает от выполнения административных команд посторонними лицами.

        Возвращает True, если user.id совпадает с ALLOWED_USER_ID, иначе False.
        """

        user = getattr(event, "from_user", None)
        if not user:
            return False

        return user.id == ALLOWED_USER_ID


class ClassmateAuthFilter(Filter):
    """Фильтр доступа для администратора и авторизованных студентов группы."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        """
        Проверяет, авторизован ли пользователь как студент группы 1-КПД-3.

        Сверяет Telegram ID и username с реестром одногруппников и списком админов.
        Обеспечивает приватность расписания и материалов группы.

        Возвращает True, если пользователь подтверждён в реестре, иначе False.
        """

        from services.classmates_auth import is_authorized_user

        user = getattr(event, "from_user", None)

        return is_authorized_user(user)


class AttendanceAuthFilter(Filter):
    """Фильтр доступа для старосты и замстаросты к отметке посещаемости."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        """
        Проверяет права пользователя на управление журналом посещаемости.

        Сверяет ID отправителя со множеством ALLOWED_ATTENDANCE_USER_IDS.
        Предотвращает несанкционированное редактирование отметок пар.

        Возвращает True, если пользователь староста или замстаросты, иначе False.
        """

        from config import ALLOWED_ATTENDANCE_USER_IDS

        user = getattr(event, "from_user", None)
        if not user:
            return False

        return user.id in ALLOWED_ATTENDANCE_USER_IDS


