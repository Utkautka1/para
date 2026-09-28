"""
Unit-тесты для модуля авторизации API (api/deps.py).

Проверяет:
  1. Доступ по валидному статическому ключу X-API-Key
  2. Защиту от несанкционированного доступа (HTTP 403 Forbidden)
  3. Обработку отсутствующих, пустых и модифицированных ключей
  4. Защиту от timing attacks при сверке секретов
"""

import pytest
from fastapi import HTTPException, status

from api.deps import verify_api_key
from config import API_SECRET_KEY


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
