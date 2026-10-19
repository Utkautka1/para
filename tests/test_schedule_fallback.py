"""
Тесты механизма переключения на резервный эндпоинт API расписания КТМУ.

Проверяет бесперебойную работу _fetch_remote_schedule:
  1. Корректный опрос основного API при его доступности.
  2. Переключение на SCHEDULE_FALLBACK_API_URL при таймауте или 5xx ошибке.
  3. Формирование ETag/Last-Modified заголовков для кэширования.
  4. Проброс исключения, если все эндпоинты недоступны.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from services.schedule_parser import (
    _build_cache_headers,
    _fetch_remote_schedule,
)


def test_build_cache_headers_present():
    """Проверяет формирование заголовков кэширования при наличии метаданных."""
    with (
        patch("services.schedule_parser._LAST_ETAG", "etag_123"),
        patch("services.schedule_parser._LAST_MODIFIED", "Wed, 14 Oct 2026"),
    ):
        hdr = _build_cache_headers()
        assert hdr["If-None-Match"] == "etag_123"
        assert hdr["If-Modified-Since"] == "Wed, 14 Oct 2026"


def test_build_cache_headers_empty():
    """Проверяет пустые заголовки кэширования при холодном старте."""
    with patch("services.schedule_parser._LAST_ETAG", None), patch("services.schedule_parser._LAST_MODIFIED", None):
        assert _build_cache_headers() == {}


@pytest.mark.asyncio
async def test_fetch_remote_schedule_primary_success():
    """Проверяет успешное получение данных с основного эндпоинта без вызова резервного."""
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200

    with patch("services.schedule_parser._fetch_single_endpoint", new=AsyncMock(return_value=mock_resp)) as mock_fetch:
        res = await _fetch_remote_schedule()
        assert res.status_code == 200
        assert mock_fetch.call_count == 1


@pytest.mark.asyncio
async def test_fetch_remote_schedule_fallback_on_connect_timeout():
    """Проверяет бесшовное переключение на fallback при таймауте основного API."""
    fallback_resp = MagicMock(spec=httpx.Response)
    fallback_resp.status_code = 200

    mock_fetch = AsyncMock(side_effect=[httpx.ConnectTimeout("connection timed out"), fallback_resp])
    with (
        patch("services.schedule_parser._fetch_single_endpoint", new=mock_fetch),
        patch("services.schedule_parser.SCHEDULE_FALLBACK_API_URL", "https://fallback.example.com/api"),
    ):
        res = await _fetch_remote_schedule()
        assert res.status_code == 200
        assert mock_fetch.call_count == 2


@pytest.mark.asyncio
async def test_fetch_remote_schedule_fallback_on_server_error():
    """Проверяет переход на резервный домен при HTTP 502/503 на основном."""
    err_resp = MagicMock(spec=httpx.Response)
    err_resp.status_code = 502
    ok_resp = MagicMock(spec=httpx.Response)
    ok_resp.status_code = 200

    mock_fetch = AsyncMock(side_effect=[err_resp, ok_resp])
    with (
        patch("services.schedule_parser._fetch_single_endpoint", new=mock_fetch),
        patch("services.schedule_parser.SCHEDULE_FALLBACK_API_URL", "https://fallback.example.com/api"),
    ):
        res = await _fetch_remote_schedule()
        assert res.status_code == 200
        assert mock_fetch.call_count == 2


@pytest.mark.asyncio
async def test_fetch_remote_schedule_all_fail():
    """Проверяет проброс исключения, если оба адреса вернули ошибку сети."""
    mock_fetch = AsyncMock(side_effect=[httpx.ConnectTimeout("err1"), httpx.ConnectError("err2")])
    with (
        patch("services.schedule_parser._fetch_single_endpoint", new=mock_fetch),
        patch("services.schedule_parser.SCHEDULE_FALLBACK_API_URL", "https://fallback.example.com/api"),
        pytest.raises(httpx.ConnectError),
    ):
        await _fetch_remote_schedule()
