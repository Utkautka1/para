"""
Модульные тесты для реверс-прокси Jaeger UI и вкладок в Telegram Mini App.

Зачем существует этот модуль:
Гарантирует защиту /jaeger через verify_api_or_tester, корректную пересылку
запросов к Jaeger UI бэкенду и целостность верстки 2-х вкладок в Mini App.
"""

import gzip
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from api import create_app
from config import API_SECRET_KEY


@pytest.fixture
def app():
    """Фикстура создания FastAPI приложения para-api."""
    return create_app()


@pytest.mark.asyncio
async def test_jaeger_proxy_unauthorized(app) -> None:
    """Проверяет, что неавторизованные пользователи не имеют доступа к /jaeger."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/jaeger/")
        assert resp.status_code in {401, 403}


@pytest.mark.asyncio
async def test_jaeger_proxy_redirect_root(app) -> None:
    """Проверяет редирект с /jaeger на /jaeger/ для авторизованного администратора."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/jaeger", headers={"X-API-Key": API_SECRET_KEY}, follow_redirects=False)
        assert resp.status_code == 307
        assert resp.headers["location"] == "/jaeger/"


@pytest.mark.asyncio
async def test_jaeger_proxy_authorized_forward(app) -> None:
    """Проверяет успешное проксирование HTML-ответа от бэкенда Jaeger UI."""
    raw_html = b"<!doctype html><html><body>Jaeger UI Mock</body></html>"
    compressed = gzip.compress(raw_html)
    mock_response = httpx.Response(
        status_code=200,
        headers={"content-type": "text/html; charset=utf-8", "content-encoding": "gzip"},
        content=compressed,
    )

    mock_client = MagicMock()
    mock_client.request = AsyncMock(return_value=mock_response)

    with patch("api.router.jaeger._get_client", return_value=mock_client):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/jaeger/", headers={"X-API-Key": API_SECRET_KEY})
            assert resp.status_code == 200
            assert "Jaeger UI Mock" in resp.text


@pytest.mark.asyncio
async def test_jaeger_proxy_service_unavailable(app) -> None:
    """Проверяет отдачу 503 Service Unavailable при ошибке сети до контейнера jaeger."""
    mock_client = MagicMock()
    mock_client.request = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

    with patch("api.router.jaeger._get_client", return_value=mock_client):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/jaeger/api/services", headers={"X-API-Key": API_SECRET_KEY})
            assert resp.status_code == 503
            data = resp.json()
            assert "error" in data


@pytest.mark.asyncio
async def test_jaeger_proxy_strips_credentials(app) -> None:
    """Ключ API, Bearer и куки не уходят во внутренний Jaeger."""
    mock_client = MagicMock()
    mock_client.request = AsyncMock(return_value=httpx.Response(status_code=200, content=b"{}"))
    headers = {"X-API-Key": API_SECRET_KEY, "Cookie": "para_session=s", "Accept": "application/json"}

    with patch("api.router.jaeger._get_client", return_value=mock_client):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.get("/jaeger/api/services", headers=headers)

    forwarded = {k.lower() for k in mock_client.request.call_args.kwargs["headers"]}
    assert forwarded.isdisjoint({"x-api-key", "cookie", "authorization"})
    assert "accept" in forwarded


def test_miniapp_html_tabs_structure() -> None:
    """Проверяет наличие табов рейтинга и скрытых по умолчанию табов Swagger/Jaeger."""
    html_content = Path("data/api/miniapp.html").read_text(encoding="utf-8")
    assert "tab-leaderboard" in html_content
    assert "tab-achievements" in html_content
    assert "tab-profile" in html_content
    assert "tab-swagger" in html_content
    assert "tab-jaeger" in html_content
    assert "swagger-frame" in html_content
    assert "jaeger-frame" in html_content
