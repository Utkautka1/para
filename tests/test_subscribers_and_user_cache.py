"""
Unit-тесты для модулей хранения подписчиков, кэша пользователей и кастомных преподавателей.

Проверяет:
  1. Добавление, удаление и дедупликацию подписчиков (db/subscribers.py)
  2. Кэширование username -> user_id с очисткой '@' и нормализацией регистра (services/user_cache.py)
  3. CRUD-операции кастомных контактов преподавателей (services/custom_teachers.py)
"""

from unittest.mock import patch
import pytest

from db.subscribers import add_subscriber, load_subscribers, remove_subscriber, save_subscribers
from services.custom_teachers import delete_custom_teacher, load_custom_teachers, save_custom_teacher
from services.user_cache import add_user_to_cache, get_cached_user_id, load_user_cache, save_user_cache


def test_subscribers_lifecycle(tmp_path) -> None:
    """Проверяет добавление, удаление и повторное добавление подписчиков."""
    file_path = str(tmp_path / "subs.json")
    with patch("db.subscribers.SUBSCRIBERS_FILE_PATH", file_path):
        assert load_subscribers() == set()
        assert add_subscriber(111) is True
        assert add_subscriber(111) is False  # Повторное добавление
        assert add_subscriber(222) is True
        assert load_subscribers() == {111, 222}

        assert remove_subscriber(111) is True
        assert remove_subscriber(111) is False  # Повторное удаление
        assert load_subscribers() == {222}


def test_subscribers_is_and_toggle(tmp_path) -> None:
    """Проверяет проверку статуса и тумблер переключения подписки."""
    from db.subscribers import is_subscribed, toggle_subscriber
    file_path = str(tmp_path / "subs_toggle.json")
    with patch("db.subscribers.SUBSCRIBERS_FILE_PATH", file_path):
        assert is_subscribed(123) is False
        assert toggle_subscriber(123) is True
        assert is_subscribed(123) is True
        assert toggle_subscriber(123) is False
        assert is_subscribed(123) is False


def test_subscribers_deduplication(tmp_path) -> None:
    """Проверяет сохранение уникального множества подписчиков."""
    file_path = str(tmp_path / "subs_dedup.json")
    with patch("db.subscribers.SUBSCRIBERS_FILE_PATH", file_path):
        save_subscribers({10, 20, 30, 10})
        loaded = load_subscribers()
        assert len(loaded) == 3
        assert loaded == {10, 20, 30}


@pytest.mark.parametrize(
    "input_username,expected_key",
    [
        ("@AdminUser", "adminuser"),
        ("adminuser", "adminuser"),
        ("@TEST_BOT", "test_bot"),
        ("Developer", "developer"),
    ],
)
def test_user_cache_normalization(tmp_path, input_username: str, expected_key: str) -> None:
    """Проверяет удаление символа '@' и приведение к нижнему регистру."""
    file_path = str(tmp_path / "cache.json")
    with patch("services.user_cache.CACHE_FILE_PATH", file_path):
        add_user_to_cache(input_username, 999)
        assert get_cached_user_id(input_username) == 999
        assert get_cached_user_id(expected_key) == 999
        cache = load_user_cache()
        assert expected_key in cache


def test_user_cache_missing_and_empty(tmp_path) -> None:
    """Проверяет возврат None для неизвестного юзера и игнорирование пустых строк."""
    file_path = str(tmp_path / "cache_empty.json")
    with patch("services.user_cache.CACHE_FILE_PATH", file_path):
        assert get_cached_user_id("unknown_person") is None
        add_user_to_cache("", 123)
        assert load_user_cache() == {}


def test_custom_teachers_crud(tmp_path) -> None:
    """Проверяет добавление, обновление и удаление кастомных контактов преподавателей."""
    file_path = str(tmp_path / "teachers.json")
    with patch("services.custom_teachers.CUSTOM_TEACHERS_FILE", file_path):
        assert load_custom_teachers() == {}
        save_custom_teacher("Иванов", "Иванов Иван", "https://zoom.us/j/1")
        data = load_custom_teachers()
        assert "иванов" in data
        assert data["иванов"]["full_name"] == "Иванов Иван"

        # Обновление
        save_custom_teacher("иванов", "Иванов Иван Иванович", "https://telemost.yandex.ru/2")
        data = load_custom_teachers()
        assert data["иванов"]["link_info"] == "https://telemost.yandex.ru/2"

        # Удаление
        delete_custom_teacher("Иванов")
        assert "иванов" not in load_custom_teachers()
