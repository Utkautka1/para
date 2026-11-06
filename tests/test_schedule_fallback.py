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


def test_extract_base_url():
    """Проверяет корректное извлечение origin из URL с путем и без него."""
    from services.schedule_parser import _extract_base_url

    assert _extract_base_url("https://raspisanie-ktmu.ru/api/storage/schedule-data-v2") == "https://raspisanie-ktmu.ru"
    assert _extract_base_url("https://example.com:8080/path?q=1") == "https://example.com:8080"
    assert _extract_base_url("https://plain.example.com") == "https://plain.example.com"


@pytest.mark.asyncio
async def test_fetch_public_bundle_success():
    """Проверяет успешное объединение публичного индекса и шарда группы."""
    from services.schedule_parser import _fetch_public_bundle

    idx_payload = {"publishedAt": "2026-11-06T00:00:00Z", "data": {"config": {"semesterStart": "2026-09-01"}, "subjects": []}}
    shard_payload = {"schedule": {"instances": []}, "dataPatch": {"loads": [], "substitutions": []}}

    r_idx = httpx.Response(200, json=idx_payload, headers={"etag": "idx_etag"}, request=httpx.Request("GET", "http://t/idx"))
    r_shard = httpx.Response(200, json=shard_payload, headers={"etag": "shard_etag"}, request=httpx.Request("GET", "http://t/shard"))

    client = AsyncMock()
    client.get = AsyncMock(side_effect=[r_idx, r_shard])

    with patch("services.schedule_parser.get_http_client", return_value=client):
        res = await _fetch_public_bundle("https://example.com", {}, httpx.Timeout(5.0))
        assert res is not None
        assert res.status_code == 200
        assert res.headers["etag"] == "shard_etag"
        data = res.json()
        assert data["publishedAt"] == "2026-11-06T00:00:00Z"
        assert "config" in data


@pytest.mark.asyncio
async def test_fetch_public_bundle_cached_304():
    """Проверяет возврат HTTP 304, когда оба публичных эндпоинта не изменились."""
    from services.schedule_parser import _fetch_public_bundle

    r_idx = httpx.Response(304, request=httpx.Request("GET", "http://t/idx"))
    r_shard = httpx.Response(304, request=httpx.Request("GET", "http://t/shard"))

    client = AsyncMock()
    client.get = AsyncMock(side_effect=[r_idx, r_shard])

    with patch("services.schedule_parser.get_http_client", return_value=client):
        res = await _fetch_public_bundle("https://example.com", {}, httpx.Timeout(5.0))
        assert res is not None
        assert res.status_code == 304


@pytest.mark.asyncio
async def test_fetch_public_bundle_index_200_shard_304():
    """Проверяет сборку бандла при неизменном шарде группы (304) и обновлённом индексе (200)."""
    from services.schedule_parser import _fetch_public_bundle

    idx_payload = {"publishedAt": "2026-11-06T00:00:00Z", "data": {"config": {}, "subjects": []}}
    cached_shard = {"schedule": {"instances": [{"id": 1}]}, "dataPatch": {"loads": []}}

    r_idx = httpx.Response(200, json=idx_payload, headers={"etag": "idx_new"}, request=httpx.Request("GET", "http://t/idx"))
    r_shard = httpx.Response(304, headers={"etag": "shard_cached"}, request=httpx.Request("GET", "http://t/shard"))

    client = AsyncMock()
    client.get = AsyncMock(side_effect=[r_idx, r_shard])

    with (
        patch("services.schedule_parser.get_http_client", return_value=client),
        patch("services.schedule_parser._CACHED_SHARD_RAW", cached_shard),
        patch("services.schedule_parser._LAST_SHARD_ETAG", "shard_cached"),
    ):
        res = await _fetch_public_bundle("https://example.com", timeout=httpx.Timeout(5.0))
        assert res is not None
        assert res.status_code == 200
        assert res.json()["schedule"]["instances"] == [{"id": 1}]


@pytest.mark.asyncio
async def test_fetch_public_bundle_index_304_shard_200():
    """Проверяет сборку бандла при неизменном индексе (304) и новом шарде группы (200)."""
    from services.schedule_parser import _fetch_public_bundle

    cached_idx = {"publishedAt": "2026-11-05T00:00:00Z", "data": {"config": {"sem": 1}, "subjects": []}}
    new_shard = {"schedule": {"instances": [{"id": 2}]}, "dataPatch": {"loads": []}}

    r_idx = httpx.Response(304, headers={"etag": "idx_cached"}, request=httpx.Request("GET", "http://t/idx"))
    r_shard = httpx.Response(200, json=new_shard, headers={"etag": "shard_new"}, request=httpx.Request("GET", "http://t/shard"))

    client = AsyncMock()
    client.get = AsyncMock(side_effect=[r_idx, r_shard])

    with (
        patch("services.schedule_parser.get_http_client", return_value=client),
        patch("services.schedule_parser._CACHED_INDEX_RAW", cached_idx),
        patch("services.schedule_parser._LAST_INDEX_ETAG", "idx_cached"),
    ):
        res = await _fetch_public_bundle("https://example.com", timeout=httpx.Timeout(5.0))
        assert res is not None
        assert res.status_code == 200
        assert res.json()["schedule"]["instances"] == [{"id": 2}]
        assert res.json()["config"] == {"sem": 1}
