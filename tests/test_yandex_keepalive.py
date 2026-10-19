"""
Unit-тесты для модуля поддержания сессии и управления Cookie Яндекс Документов.

Проверяет:
  1. Корректное слияние строк Cookie (merge_cookie_header)
  2. Получение и кэширование эффективных Cookie из Redis (get_effective_yandex_cookie)
  3. Сохранение Cookie в Redis с TTL (save_effective_yandex_cookie)
  4. Обновление Cookie из заголовка ответа сервера (update_cookies_from_response)
  5. Проверку живости сессии (ping_yandex_session)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import REDIS_COOKIE_TTL_SECONDS, REDIS_YANDEX_COOKIE_KEY
from integrations.yandex_docs import (
    get_effective_yandex_cookie,
    merge_cookie_header,
    save_effective_yandex_cookie,
    update_cookies_from_response,
)
from integrations.yandex_keepalive import ping_yandex_session


def test_merge_cookie_header_basic() -> None:
    """Проверяет слияние имеющихся кук с обновленными значениями."""
    initial = "Session_id=old_session; _yasc=token1; i=id1"
    new_cookies = {"_yasc": "token2", "extra": "val1"}
    merged = merge_cookie_header(initial, new_cookies)
    assert "Session_id=old_session" in merged
    assert "_yasc=token2" in merged
    assert "extra=val1" in merged


def test_merge_cookie_header_empty_initial() -> None:
    """Проверяет формирование строки кук при пустом исходном значении."""
    new_cookies = {"Session_id": "sess_123", "i": "val_i"}
    merged = merge_cookie_header("", new_cookies)
    assert "Session_id=sess_123" in merged
    assert "i=val_i" in merged


@pytest.mark.asyncio
async def test_get_effective_cookie_from_redis() -> None:
    """Проверяет приоритетное чтение Cookie из Redis."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = "Session_id=cached_value"

    with patch("core.redis.get_redis", return_value=mock_redis):
        cookie = await get_effective_yandex_cookie()
        assert cookie == "Session_id=cached_value"
        mock_redis.get.assert_awaited_once_with(REDIS_YANDEX_COOKIE_KEY)


@pytest.mark.asyncio
async def test_get_effective_cookie_fallback() -> None:
    """Проверяет fallback на .env, если в Redis пусто."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    with (
        patch("core.redis.get_redis", return_value=mock_redis),
        patch("integrations.yandex_docs.get_yandex_cookie_header", return_value="Session_id=env_val"),
    ):
        cookie = await get_effective_yandex_cookie()
        assert cookie == "Session_id=env_val"


@pytest.mark.asyncio
async def test_save_effective_yandex_cookie() -> None:
    """Проверяет сохранение строки Cookie в Redis с заданным TTL."""
    mock_redis = AsyncMock()

    with patch("core.redis.get_redis", return_value=mock_redis):
        await save_effective_yandex_cookie("Session_id=test")
        mock_redis.set.assert_awaited_once_with(REDIS_YANDEX_COOKIE_KEY, "Session_id=test", ex=REDIS_COOKIE_TTL_SECONDS)


@pytest.mark.asyncio
async def test_update_cookies_from_response() -> None:
    """Проверяет сохранение объединенных кук при наличии Set-Cookie в ответе."""
    res = MagicMock()
    res.cookies = {"_yasc": "new_yasc_token"}

    with patch("integrations.yandex_docs.save_effective_yandex_cookie", new_callable=AsyncMock) as mock_save:
        await update_cookies_from_response(res, "Session_id=123; _yasc=old")
        mock_save.assert_awaited_once_with("Session_id=123; _yasc=new_yasc_token")


@pytest.mark.asyncio
async def test_ping_yandex_session_success() -> None:
    """Проверяет успешный пинг сессии при валидном client-config."""
    with (
        patch("integrations.yandex_keepalive.fetch_page_dom", return_value="<html>ok</html>"),
        patch(
            "integrations.yandex_keepalive.extract_client_config",
            return_value={"officeActionData": {"resource_url": "https://test"}},
        ),
    ):
        ok = await ping_yandex_session()
        assert ok is True


@pytest.mark.asyncio
async def test_ping_yandex_session_failure() -> None:
    """Проверяет возврат False при сбое пинга сессии."""
    with patch("integrations.yandex_keepalive.fetch_page_dom", side_effect=RuntimeError("HTTP 403")):
        ok = await ping_yandex_session()
        assert ok is False
