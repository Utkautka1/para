"""
Unit-тесты для Telegram Mini App аутентификации и управления тестерами.

Проверяет:
  1. Валидацию Telegram.WebApp.initData и защиту от подделки/replay атак.
  2. Генерацию и проверку криптографических сессий тестеров.
  3. Управление белым списком тестеров в Redis и защиту админов.
  4. Эндпоинты /miniapp/auth, /miniapp/status, /miniapp/testers.
"""

import hashlib
import hmac
import json
import urllib.parse
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from api import create_app
from config import ALLOWED_USER_ID, BOT_TOKEN, DEPUTY_USER_ID
from services.testers_manager import (
    add_tester,
    get_all_testers,
    is_tester_allowed,
    remove_tester,
)
from utils.miniapp_auth import (
    generate_tester_session,
    validate_telegram_init_data,
    verify_tester_session,
)


def _build_test_init_data(user_dict: dict, auth_ts: int, tamper_hash: bool = False) -> str:
    """Генерирует валидную или поврежденную строку Telegram initData."""
    user_str = json.dumps(user_dict, separators=(",", ":"))
    params = {"auth_date": str(auth_ts), "user": user_str}
    data_check_str = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    sig = hmac.new(secret_key, data_check_str.encode(), hashlib.sha256).hexdigest()
    if tamper_hash:
        sig = "0" * 64
    encoded_user = urllib.parse.quote(user_str)
    return f"auth_date={auth_ts}&user={encoded_user}&hash={sig}"


def test_init_data_validation_success() -> None:
    """Проверяет успешную валидацию корректной строки initData."""
    now_ts = int(datetime.now(timezone.utc).timestamp())
    raw = _build_test_init_data({"id": 12345, "first_name": "Test"}, now_ts)
    user_data = validate_telegram_init_data(raw)
    assert user_data is not None
    assert user_data["id"] == 12345
    assert user_data["first_name"] == "Test"


def test_init_data_tampered_hash_rejected() -> None:
    """Проверяет отклонение initData с поддельным хешем подписи."""
    now_ts = int(datetime.now(timezone.utc).timestamp())
    raw = _build_test_init_data({"id": 12345}, now_ts, tamper_hash=True)
    assert validate_telegram_init_data(raw) is None


def test_init_data_expired_replay_rejected() -> None:
    """Проверяет защиту от replay-атак при устаревшем auth_date (> 86400s)."""
    old_ts = int(datetime.now(timezone.utc).timestamp()) - 100000
    raw = _build_test_init_data({"id": 12345}, old_ts)
    assert validate_telegram_init_data(raw) is None


def test_tester_session_lifecycle() -> None:
    """Проверяет генерацию и верификацию сессионного токена тестера."""
    token = generate_tester_session(777888)
    assert verify_tester_session(token) == 777888
    # Подделка токена
    parts = token.split(":")
    fake_token = f"{parts[0]}:{parts[1]}:{'f'*64}"
    assert verify_tester_session(fake_token) is None


@pytest.mark.asyncio
async def test_testers_manager_logic() -> None:
    """Проверяет добавление, удаление тестеров и защиту администраторов."""
    mock_redis = AsyncMock()
    mock_redis.sadd = AsyncMock(return_value=1)
    mock_redis.srem = AsyncMock(return_value=1)
    mock_redis.sismember = AsyncMock(return_value=True)
    mock_redis.smembers = AsyncMock(return_value={b"555", b"666"})

    with patch("services.testers_manager.get_redis", return_value=mock_redis):
        # Добавление
        assert await add_tester(555) is True
        mock_redis.sadd.assert_called_once()

        # Проверка админа (без обращения в Redis)
        assert await is_tester_allowed(ALLOWED_USER_ID) is True
        assert await is_tester_allowed(DEPUTY_USER_ID) is True

        # Проверка обычного тестера (через Redis)
        assert await is_tester_allowed(555) is True

        # Защита админа от удаления
        assert await remove_tester(ALLOWED_USER_ID) is False

        # Удаление обычного тестера
        assert await remove_tester(555) is True

        # Получение полного списка
        all_uids = await get_all_testers()
        assert ALLOWED_USER_ID in all_uids
        assert 555 in all_uids


@pytest.mark.asyncio
async def test_miniapp_auth_endpoint() -> None:
    """Проверяет HTTP-эндпоинт /miniapp/auth с выдачей сессионной куки."""
    app = create_app()
    now_ts = int(datetime.now(timezone.utc).timestamp())
    valid_raw = _build_test_init_data({"id": ALLOWED_USER_ID, "first_name": "Admin"}, now_ts)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Успешная авторизация админа/тестера
        resp = await client.post("/miniapp/auth", json={"init_data": valid_raw})
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == ALLOWED_USER_ID
        assert "para_session" in resp.cookies

        # Попытка авторизации с битой подписью
        bad_raw = _build_test_init_data({"id": 111}, now_ts, tamper_hash=True)
        bad_resp = await client.post("/miniapp/auth", json={"init_data": bad_raw})
        assert bad_resp.status_code == 401

        # Попытка авторизации пользователя не из списка
        with patch("api.router.miniapp.is_tester_allowed", new=AsyncMock(return_value=False)):
            stranger_raw = _build_test_init_data({"id": 999999}, now_ts)
            forbidden_resp = await client.post("/miniapp/auth", json={"init_data": stranger_raw})
            assert forbidden_resp.status_code == 403


@pytest.mark.asyncio
async def test_openapi_spec_protection_and_servers_masking() -> None:
    """Проверяет защиту /openapi.json от неавторизованного доступа и маскирование хостов."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Анонимный доступ блокируется
        unauth_resp = await client.get("/openapi.json")
        assert unauth_resp.status_code == 401

        # 2. Авторизованный доступ по X-API-Key отдаёт спецификацию
        from config import API_SECRET_KEY
        auth_resp = await client.get("/openapi.json", headers={"X-API-Key": API_SECRET_KEY})
        assert auth_resp.status_code == 200
        schema = auth_resp.json()
        assert schema["servers"] == [{"url": "/", "description": "API Gateway"}]
        raw_schema = json.dumps(schema)
        assert "45-81-154-175" not in raw_schema
        assert "sslip.io" not in raw_schema


@pytest.mark.asyncio
async def test_docs_redirect_to_miniapp() -> None:
    """Проверяет перенаправление со стандартного /docs на защищенный /miniapp."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as client:
        resp = await client.get("/docs")
        assert resp.status_code == 307
        assert resp.headers["location"] == "/miniapp"


def test_miniapp_html_security_elements() -> None:
    """Проверяет правила скрытия ссылки openapi.json и IP-маскирования в miniapp.html."""
    from pathlib import Path
    html_content = Path("data/api/miniapp.html").read_text(encoding="utf-8")
    assert ".swagger-ui .info .url" in html_content
    assert "CleanSwaggerPlugin" in html_content
    assert "InfoUrl" in html_content
    assert "req.url = req.url.replace" in html_content
    assert "hostSanitizer" in html_content
