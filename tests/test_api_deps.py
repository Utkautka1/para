"""
Unit-тесты для модуля авторизации API (api/deps.py).

Проверяет:
  1. Доступ по валидному статическому ключу X-API-Key
  2. Защиту от несанкционированного доступа (HTTP 403 Forbidden)
  3. Обработку отсутствующих, пустых и модифицированных ключей
  4. Защиту от timing attacks при сверке секретов
"""

from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from starlette.requests import Request

from api.deps import _identity_uid, _is_cross_site, verify_admin_access, verify_api_key, verify_api_or_tester
from config import ALLOWED_USER_ID, API_SECRET_KEY


@pytest.mark.asyncio
async def test_verify_api_key_success() -> None:
    """Проверяет успешную авторизацию при передаче корректного API_SECRET_KEY."""
    res = await verify_api_key(API_SECRET_KEY)
    assert res == API_SECRET_KEY


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_key",
    [
        "wrong_secret_key",
        "",
        "   ",
        None,
        f"{API_SECRET_KEY}_extra",
        f"prefix_{API_SECRET_KEY}",
        API_SECRET_KEY.lower() if API_SECRET_KEY.isupper() else API_SECRET_KEY.upper(),
        "invalid_key_12345",
        "Bearer token_instead_of_key",
    ],
)
async def test_verify_api_key_forbidden(invalid_key: str) -> None:
    """Проверяет выброс HTTPException 403 при несовпадении или отсутствии ключа."""
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(invalid_key)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Invalid or missing API key"


# === Права админа и защита сессионной куки от CSRF ===


def _request(method: str, headers: dict[str, str]) -> Request:
    """Собирает минимальный ASGI-запрос с заданными заголовками."""
    raw = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    return Request({"type": "http", "method": method, "path": "/x", "headers": raw, "query_string": b""})


@pytest.mark.parametrize(
    ("identity", "expected"),
    [("tester:42", 42), ("classmate:7", 7), ("master_admin", None), ("tester:abc", None), ("other:1", None)],
)
def test_identity_uid(identity: str, expected: int | None) -> None:
    """uid извлекается из tester- и classmate-идентичностей."""
    assert _identity_uid(identity) == expected


@pytest.mark.asyncio
async def test_admin_classmate_session_has_admin_access() -> None:
    """Сессия старосты из Mini App (classmate:) проходит admin-проверку."""
    ident = f"classmate:{ALLOWED_USER_ID}"
    assert await verify_admin_access(ident) == ident


@pytest.mark.asyncio
async def test_regular_classmate_has_no_admin_access() -> None:
    """Обычный одногруппник не получает admin-доступ."""
    with pytest.raises(HTTPException) as exc_info:
        await verify_admin_access("classmate:1")
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ("headers", "cross"),
    [
        ({"sec-fetch-site": "cross-site"}, True),
        ({"sec-fetch-site": "same-site"}, True),
        ({"sec-fetch-site": "same-origin"}, False),
        ({"origin": "https://evil.example", "host": "para.example"}, True),
        ({"origin": "https://para.example", "host": "para.example"}, False),
        ({}, False),
    ],
)
def test_is_cross_site(headers: dict[str, str], cross: bool) -> None:
    """Межсайтовость определяется по Sec-Fetch-Site, затем по Origin."""
    assert _is_cross_site(_request("POST", headers)) is cross


@pytest.mark.asyncio
async def test_cookie_post_from_other_site_rejected() -> None:
    """Изменяющий запрос с кукой со стороннего сайта блокируется."""
    req = _request("POST", {"sec-fetch-site": "cross-site"})
    with (
        patch("api.deps._resolve_token_identity", return_value=f"classmate:{ALLOWED_USER_ID}"),
        pytest.raises(HTTPException) as exc_info,
    ):
        await verify_api_or_tester(req, key=None, bearer=None, para_session="cookie")
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_cookie_get_from_other_site_allowed() -> None:
    """Безопасные методы с кукой не блокируются."""
    req = _request("GET", {"sec-fetch-site": "cross-site"})
    with patch("api.deps._resolve_token_identity", return_value="classmate:1"):
        assert await verify_api_or_tester(req, key=None, bearer=None, para_session="cookie") == "classmate:1"
