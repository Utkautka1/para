"""
Зависимости FastAPI: авторизация по X-API-Key и сессиям Telegram тестеров.

Позволяет сервисам авторизоваться статическим API_SECRET_KEY,
а пользователям Telegram Mini App — через валидированную сессионную куку.
"""

import hmac

from fastapi import Cookie, Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from config import API_SECRET_KEY
from core.logger import get_logger
from services.testers_manager import is_tester_allowed
from utils.miniapp_auth import verify_tester_session

log = get_logger("api_auth")

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str = Security(_api_key_header)) -> str:
    """
    Валидирует статический API-ключ из заголовка запроса.

    Сравнение через hmac.compare_digest защищает от timing attacks.
    Возвращает ключ или возбуждает 403 Forbidden.
    """
    if not key or not hmac.compare_digest(key, API_SECRET_KEY):
        log.warning("⚠️ Отклонён запрос с невалидным или отсутствующим API-ключом")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return key


async def _extract_tester_id(session_cookie: str | None, auth_header: str | None) -> int | None:
    """Извлекает и проверяет ID тестера из куки или Bearer заголовка."""
    token = session_cookie
    if not token and auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    if not token:
        return None
    user_id = verify_tester_session(token)
    if user_id and await is_tester_allowed(user_id):
        return user_id
    return None


async def verify_api_or_tester(
    key: str | None = Security(_api_key_header),
    para_session: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
) -> str:
    """
    Универсальная авторизация для API и Swagger UI.

    Разрешает доступ по X-API-Key либо активной сессии авторизованного тестера.
    Возвращает строку идентификатора авторизации.
    """
    if key and hmac.compare_digest(key, API_SECRET_KEY):
        return key
    tester_id = await _extract_tester_id(para_session, authorization)
    if tester_id is not None:
        return f"tester:{tester_id}"
    log.warning("⚠️ Отклонён запрос без валидного API-ключа или сессии тестера")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: valid API key or tester session required",
    )
