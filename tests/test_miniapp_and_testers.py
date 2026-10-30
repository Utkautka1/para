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
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from api import create_app
from config import ALLOWED_USER_ID, API_SECRET_KEY, BOT_TOKEN, DEPUTY_USER_ID
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
    now_ts = int(datetime.now(UTC).timestamp())
    raw = _build_test_init_data({"id": 12345, "first_name": "Test"}, now_ts)
    user_data = validate_telegram_init_data(raw)
    assert user_data is not None
    assert user_data["id"] == 12345
    assert user_data["first_name"] == "Test"


def test_init_data_tampered_hash_rejected() -> None:
    """Проверяет отклонение initData с поддельным хешем подписи."""
    now_ts = int(datetime.now(UTC).timestamp())
    raw = _build_test_init_data({"id": 12345}, now_ts, tamper_hash=True)
    assert validate_telegram_init_data(raw) is None


def test_init_data_expired_replay_rejected() -> None:
    """Проверяет защиту от replay-атак при устаревшем auth_date (> 86400s)."""
    old_ts = int(datetime.now(UTC).timestamp()) - 100000
    raw = _build_test_init_data({"id": 12345}, old_ts)
    assert validate_telegram_init_data(raw) is None


def test_tester_session_lifecycle() -> None:
    """Проверяет генерацию и верификацию сессионного токена тестера."""
    token = generate_tester_session(777888)
    assert verify_tester_session(token) == 777888
    # Подделка токена
    parts = token.split(":")
    fake_token = f"{parts[0]}:{parts[1]}:{'f' * 64}"
    assert verify_tester_session(fake_token) is None


@pytest.mark.asyncio
async def test_testers_manager_add_and_check() -> None:
    """Проверяет добавление тестеров и проверку прав доступа."""
    mock_redis = AsyncMock()
    mock_redis.sadd = AsyncMock(return_value=1)
    mock_redis.sismember = AsyncMock(return_value=True)
    with patch("services.testers_manager.get_redis", return_value=mock_redis):
        assert await add_tester(555) is True
        mock_redis.sadd.assert_called_once()
        assert await is_tester_allowed(ALLOWED_USER_ID) is True
        assert await is_tester_allowed(DEPUTY_USER_ID) is True
        assert await is_tester_allowed(555) is True


@pytest.mark.asyncio
async def test_testers_manager_remove_and_list() -> None:
    """Проверяет удаление тестеров и защиту администраторов."""
    mock_redis = AsyncMock()
    mock_redis.srem = AsyncMock(return_value=1)
    mock_redis.smembers = AsyncMock(return_value={b"555", b"666"})
    with patch("services.testers_manager.get_redis", return_value=mock_redis):
        assert await remove_tester(ALLOWED_USER_ID) is False
        assert await remove_tester(555) is True
        all_uids = await get_all_testers()
        assert ALLOWED_USER_ID in all_uids
        assert 555 in all_uids


@pytest.mark.asyncio
async def test_miniapp_auth_endpoint() -> None:
    """Проверяет HTTP-эндпоинт /miniapp/auth с выдачей сессионной куки."""
    app = create_app()
    now_ts = int(datetime.now(UTC).timestamp())
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
async def test_docs_protected_swagger() -> None:
    """Проверяет защиту маршрута /docs со Swagger UI: 401 без ключа и 200 с ключом."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp_unauth = await client.get("/docs")
        assert resp_unauth.status_code == 401

        resp_auth = await client.get("/docs", headers={"X-API-Key": API_SECRET_KEY})
        assert resp_auth.status_code == 200
        assert "swagger-ui" in resp_auth.text.lower()


def test_miniapp_html_lightweight_and_clean() -> None:
    """Проверяет, что тяжелый Swagger UI вынесен из клиентского HTML MiniApp."""
    from pathlib import Path

    html_content = Path("data/api/miniapp.html").read_text(encoding="utf-8")
    assert "swagger-ui-bundle.js" not in html_content
    assert "swagger-ui.css" not in html_content
    assert "Promise.allSettled" in html_content


@pytest.mark.asyncio
async def test_docs_query_key_rejected_and_action() -> None:
    """Проверяет, что ?key= больше не авторизует /docs, и вызов /miniapp/action по initData."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/docs?key={API_SECRET_KEY}")
        assert resp.status_code == 401
        assert "para_session" not in resp.cookies

        now_ts = int(datetime.now(UTC).timestamp())
        init_data = _build_test_init_data({"id": ALLOWED_USER_ID, "first_name": "Admin"}, now_ts)
        action_resp = await client.post(
            "/miniapp/action",
            json={"action": "matrix_theme", "init_data": init_data},
        )
        assert action_resp.status_code == 200
        data = action_resp.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_dev_login_removed() -> None:
    """Проверяет, что вход по постоянному ключу в URL (/miniapp/dev-login) удалён."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/miniapp/dev-login?key={API_SECRET_KEY}")
        assert resp.status_code in {404, 405}


@pytest.mark.asyncio
async def test_login_by_one_time_token() -> None:
    """Проверяет обмен одноразового токена на куку, whitelist next и отказ при повторе."""
    app = create_app()
    consume = AsyncMock(side_effect=[ALLOWED_USER_ID, ALLOWED_USER_ID, None])
    with patch("api.router.miniapp.consume_login_token", consume):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/miniapp/login?t=tok&next=docs")
            assert resp.status_code == 303
            assert resp.headers["location"] == "/docs"
            assert "para_session" in resp.cookies

            evil = await client.get("/miniapp/login?t=tok&next=https://evil.example")
            assert evil.headers["location"] == "/miniapp"

            reused = await client.get("/miniapp/login?t=tok")
            assert reused.status_code == 401


@pytest.mark.asyncio
async def test_login_tokens_issue_and_consume() -> None:
    """Проверяет выпуск токена с TTL и его атомарное погашение через GETDEL."""
    from config import LOGIN_TOKEN_TTL_SECONDS, MINIAPP_URL
    from services.login_tokens import build_login_url, consume_login_token

    mock_redis = AsyncMock()
    mock_redis.getdel = AsyncMock(side_effect=["555", None])
    with patch("services.login_tokens.get_redis", return_value=mock_redis):
        url = await build_login_url(555, "docs")
        assert url is not None
        assert url.startswith(f"{MINIAPP_URL}/login?t=")
        assert url.endswith("&next=docs")
        assert mock_redis.set.call_args.kwargs["ex"] == LOGIN_TOKEN_TTL_SECONDS

        assert await consume_login_token("tok") == 555
        assert await consume_login_token("tok") is None


@pytest.mark.asyncio
async def test_auth_by_tester_key() -> None:
    """Проверяет аутентификацию в MiniApp по персональному ключу тестера."""
    app = create_app()
    transport = ASGITransport(app=app)
    tester_uid = 403378239
    tester_key = "api_tester_testkey12345"

    with (
        patch("api.router.miniapp.get_tester_by_key", new_callable=AsyncMock) as mock_get_tester,
        patch("api.router.miniapp.is_tester_allowed", new_callable=AsyncMock) as mock_allowed,
    ):
        mock_get_tester.return_value = tester_uid
        mock_allowed.return_value = True

        async with AsyncClient(transport=transport, base_url="https://test") as client:
            resp = await client.post("/miniapp/auth", json={"api_key": tester_key})
            assert resp.status_code == 200
            assert resp.json()["user_id"] == tester_uid
            assert "para_session" in resp.cookies

            status_resp = await client.get("/miniapp/status")
            assert status_resp.status_code == 200
            assert status_resp.json()["authenticated"] is True
            assert status_resp.json()["is_tester"] is True


@pytest.mark.asyncio
async def test_auth_by_non_ascii_or_invalid_key_rejected() -> None:
    """Проверяет отклонение случайных и не-ASCII ключей со статусом 401 без падения сервера."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as client:
        resp_cyrillic = await client.post("/miniapp/auth", json={"api_key": "рандомный ключ 123"})
        assert resp_cyrillic.status_code == 401
        assert resp_cyrillic.json()["detail"] == "Invalid API Key"

        resp_garbage = await client.post("/miniapp/auth", json={"api_key": "invalid_token_xyz"})
        assert resp_garbage.status_code == 401


@pytest.mark.asyncio
async def test_action_rejects_non_member_init_data() -> None:
    """Валидный initData постороннего пользователя Telegram не даёт ачивок группы."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        now_ts = int(datetime.now(UTC).timestamp())
        init_data = _build_test_init_data({"id": 999000111, "first_name": "Stranger"}, now_ts)
        with patch("api.router.miniapp.find_classmate_by_tg_id", return_value=None):
            resp = await client.post("/miniapp/action", json={"action": "matrix_theme", "init_data": init_data})
        assert resp.status_code == 403
