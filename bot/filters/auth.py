"""
Фильтр авторизации пользователей.

Проверяет, соответствует ли Telegram ID отправителя единственному
разрешенному пользователю из конфигурации (ALLOWED_USER_ID).
"""

from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from config import ADMIN_USER_IDS, ALLOWED_ATTENDANCE_USER_IDS
from services.classmates_auth import is_authorized_user


class AuthFilter(Filter):
    """Фильтр доступа по Telegram ID исключительно для Главного Администратора."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        """
        Проверяет ID пользователя на соответствие главному администратору проекта.

        Используется в защищенных роутерах панели управления старосты.
        Защищает от выполнения административных команд посторонними лицами.

        Возвращает True, если user.id входит в ADMIN_USER_IDS, иначе False.
        """

        user = getattr(event, "from_user", None)
        if not user:
            return False

        return user.id in ADMIN_USER_IDS


class ClassmateAuthFilter(Filter):
    """Фильтр доступа для администратора и авторизованных студентов группы."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        """
        Проверяет, авторизован ли пользователь как студент группы 1-КПД-3.

        Сверяет числовой Telegram ID с реестром одногруппников и ID старосты.
        Username не учитывается: его можно сменить и занять чужой.
        Обеспечивает приватность расписания и материалов группы.

        Возвращает True, если пользователь подтверждён в реестре, иначе False.
        """

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

        user = getattr(event, "from_user", None)
        if not user:
            return False

        return user.id in ALLOWED_ATTENDANCE_USER_IDS
