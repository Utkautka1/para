"""
Тесты для сервиса аутентификации и разовой регистрации одногруппников.

Проверяет:
  - Поиск студентов по ID и юзернейму
  - Разовую фиксацию цифрового Telegram ID при первом входе
  - Запрет повторной регистрации или перезаписи чужого ID
  - Разграничение прав администратора и одногруппников
"""

from unittest.mock import MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Message, User

from bot.filters.auth import ClassmateAuthFilter
from config import ALLOWED_USER_ID
from services.classmates_auth import (
    find_classmate_by_tg_id,
    find_unregistered_by_username,
    is_authorized_user,
    load_classmates_registry,
    process_user_auth,
    update_classmate_tg_id,
)

SAMPLE_REGISTRY = [
    {
        "full_name": "Калинкевич Арсений",
        "username": "etow0ndes",
        "tg_id": None,
    },
    {
        "full_name": "Мазур Арсений",
        "username": "Arseniymazur",
        "tg_id": 1859089085,
    },
]


def test_load_classmates_registry() -> None:
    """Проверяет загрузку реестра студентов через sync_load_json."""
    with patch("services.classmates_auth.sync_load_json", return_value=SAMPLE_REGISTRY):
        registry = load_classmates_registry()
        assert len(registry) == 2
        assert registry[0]["username"] == "etow0ndes"


def test_find_classmate_by_tg_id() -> None:
    """Проверяет поиск студента по числовому Telegram ID."""
    with patch("services.classmates_auth.load_classmates_registry", return_value=SAMPLE_REGISTRY):
        student = find_classmate_by_tg_id(1859089085)
        assert student is not None
        assert student["full_name"] == "Мазур Арсений"

        missing = find_classmate_by_tg_id(999999999)
        assert missing is None


def test_find_unregistered_by_username_found() -> None:
    """Проверяет поиск студента с tg_id=None по юзернейму без учета регистра."""
    with patch("services.classmates_auth.load_classmates_registry", return_value=SAMPLE_REGISTRY):
        student = find_unregistered_by_username("@Etow0ndes")
        assert student is not None
        assert student["full_name"] == "Калинкевич Арсений"


def test_find_unregistered_already_registered() -> None:
    """Проверяет, что студент с уже известным tg_id не считается незарегистрированным."""
    with patch("services.classmates_auth.load_classmates_registry", return_value=SAMPLE_REGISTRY):
        student = find_unregistered_by_username("Arseniymazur")
        assert student is None


def test_update_classmate_tg_id_success() -> None:
    """Проверяет разовую фиксацию ID и сохранение в файл и кэш."""
    import copy

    reg_copy = copy.deepcopy(SAMPLE_REGISTRY)
    with (
        patch("services.classmates_auth.load_classmates_registry", return_value=reg_copy),
        patch("services.classmates_auth.sync_atomic_save_json") as mock_save,
        patch("services.classmates_auth.add_user_to_cache") as mock_cache,
    ):
        updated = update_classmate_tg_id("etow0ndes", 555666777)
        assert updated is not None
        assert updated["tg_id"] == 555666777
        mock_save.assert_called_once()
        mock_cache.assert_called_once_with("etow0ndes", 555666777)


def test_update_classmate_tg_id_already_registered_fails() -> None:
    """Проверяет запрет перезаписи ID для уже зафиксированного пользователя."""
    with (
        patch("services.classmates_auth.load_classmates_registry", return_value=SAMPLE_REGISTRY),
        patch("services.classmates_auth.sync_atomic_save_json") as mock_save,
    ):
        res = update_classmate_tg_id("arseniymazur", 999111222)
        assert res is None
        mock_save.assert_not_called()


def test_is_authorized_user_admin() -> None:
    """Проверяет, что Главный Администратор всегда авторизован."""
    admin_user = User(id=ALLOWED_USER_ID, is_bot=False, first_name="Admin")
    assert is_authorized_user(admin_user) is True
    assert is_authorized_user(None) is False


def test_is_authorized_user_classmates() -> None:
    """Проверяет авторизацию зарегистрированного студента и отклонение постороннего."""
    with patch("services.classmates_auth.load_classmates_registry", return_value=SAMPLE_REGISTRY):
        student_user = User(id=1859089085, is_bot=False, first_name="Arseniy")
        assert is_authorized_user(student_user) is True

        stranger = User(id=777888999, is_bot=False, first_name="Stranger")
        assert is_authorized_user(stranger) is False


def test_process_user_auth_unregistered_rejected() -> None:
    """Проверяет, что студент без привязанного старостой ID не авторизуется автоматически."""
    with patch("services.classmates_auth.find_classmate_by_tg_id", return_value=None):
        user = User(id=12345, is_bot=False, first_name="Arseniy", username="etow0ndes")
        is_auth, is_just_reg, student = process_user_auth(user)
        assert is_auth is False
        assert is_just_reg is False
        assert student is None


def test_process_user_auth_stranger_rejected() -> None:
    """Проверяет отказ в доступе постороннему лицу."""
    with (
        patch("services.classmates_auth.find_classmate_by_tg_id", return_value=None),
        patch("services.classmates_auth.update_classmate_tg_id", return_value=None),
    ):
        stranger = User(id=999888, is_bot=False, first_name="Bob", username="stranger_bob")
        is_auth, is_just_reg, student = process_user_auth(stranger)
        assert is_auth is False
        assert is_just_reg is False
        assert student is None


@pytest.mark.asyncio
async def test_classmate_auth_filter_allows_authorized() -> None:
    """Проверяет работу aiogram фильтра ClassmateAuthFilter для авторизованных."""
    filt = ClassmateAuthFilter()
    with patch("services.classmates_auth.is_authorized_user", return_value=True):
        msg = MagicMock(spec=Message)
        msg.from_user = User(id=1859089085, is_bot=False, first_name="Arseniy")
        assert await filt(msg) is True


@pytest.mark.asyncio
async def test_classmate_auth_filter_blocks_stranger() -> None:
    """Проверяет работу aiogram фильтра ClassmateAuthFilter при блокировке посторонних."""
    filt = ClassmateAuthFilter()
    with patch("services.classmates_auth.is_authorized_user", return_value=False):
        cb = MagicMock(spec=CallbackQuery)
        cb.from_user = User(id=999888, is_bot=False, first_name="Stranger")
        assert await filt(cb) is False


@pytest.mark.asyncio
async def test_send_single_reminder_subscribers_only() -> None:
    """Проверяет, что напоминание отправляется исключительно активным подписчикам."""
    from unittest.mock import AsyncMock

    from services.models import Lesson
    from services.notifier import send_single_reminder

    lesson = Lesson(
        subject="Математика",
        teacher="Иванов И.И.",
        room="101",
        time_str="10:00-11:30",
        period=0,
        is_remote=False,
        lesson_type="Пр",
        address="Корпус 1",
    )
    with (
        patch("db.subscribers.load_subscribers", return_value={1000965210}),
        patch("services.notifier.bot.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await send_single_reminder(lesson)
        assert mock_send.call_count == 1
        assert mock_send.call_args[0][0] == 1000965210


@pytest.mark.asyncio
async def test_cb_toggle_notify() -> None:
    """Проверяет реакцию хэндлера cb_toggle_notify на переключение подписки."""
    from unittest.mock import AsyncMock

    from bot.handlers.user.schedule import cb_toggle_notify

    cb = MagicMock(spec=CallbackQuery)
    cb.from_user = User(id=12345, is_bot=False, first_name="User")
    cb.answer = AsyncMock()
    cb.message = MagicMock(spec=Message)
    cb.message.edit_reply_markup = AsyncMock()
    with (
        patch("bot.handlers.user.schedule.toggle_subscriber", return_value=True),
        patch("bot.handlers.user.schedule.get_api_schedule_for_date", return_value=[]),
    ):
        await cb_toggle_notify(cb)
        cb.answer.assert_called_once_with("🔔 Напоминания за 10 мин включены!")
        cb.message.edit_reply_markup.assert_called_once()


@pytest.mark.asyncio
async def test_cmd_notice_authorized() -> None:
    """Проверяет команду /notice для авторизованного пользователя."""
    from unittest.mock import AsyncMock

    from bot.handlers.user.schedule import cmd_notice

    msg = MagicMock(spec=Message)
    msg.from_user = User(id=12345, is_bot=False, first_name="User")
    msg.answer = AsyncMock()
    with (
        patch("bot.handlers.user.schedule.is_authorized_user", return_value=True),
        patch("bot.handlers.user.schedule.is_subscribed", return_value=True),
    ):
        await cmd_notice(msg)
        msg.answer.assert_called_once()
        assert "НАСТРОЙКИ УВЕДОМЛЕНИЙ" in msg.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_cmd_notice_stranger_rejected() -> None:
    """Проверяет отказ на команду /notice для постороннего пользователя."""
    from unittest.mock import AsyncMock

    from bot.handlers.user.schedule import cmd_notice

    msg = MagicMock(spec=Message)
    msg.from_user = User(id=99999, is_bot=False, first_name="Stranger")
    msg.answer = AsyncMock()
    with patch("bot.handlers.user.schedule.is_authorized_user", return_value=False):
        await cmd_notice(msg)
        msg.answer.assert_called_once()
        assert "Доступ ограничен" in msg.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_cb_notice_toggle() -> None:
    """Проверяет callback notice:toggle переключения подписки."""
    from unittest.mock import AsyncMock

    from bot.handlers.user.schedule import cb_notice_toggle

    cb = MagicMock(spec=CallbackQuery)
    cb.from_user = User(id=12345, is_bot=False, first_name="User")
    cb.answer = AsyncMock()
    cb.message = MagicMock(spec=Message)
    cb.message.edit_text = AsyncMock()
    with patch("bot.handlers.user.schedule.toggle_subscriber", return_value=False):
        await cb_notice_toggle(cb)
        cb.answer.assert_called_once_with("🔕 Уведомления отключены.")
        cb.message.edit_text.assert_called_once()
