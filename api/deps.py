"""
Зависимости FastAPI: авторизация по X-API-Key, Bearer токенам и сессиям тестеров.

Зачем существует этот модуль:
Предоставляет гибкую систему доступа: тестеры получают доступ к рабочим эндпоинтам,
а деструктивные и системные методы защищены проверкой статуса администратора.
"""

import hmac
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from config import ALLOWED_USER_ID, API_SECRET_KEY, DEPUTY_USER_ID
from core.logger import get_logger
from services.testers_manager import is_tester_allowed
from utils.miniapp_auth import verify_tester_session

log = get_logger("api_auth")

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_bearer_scheme = HTTPBearer(auto_error=False)


def _is_valid_api_key(key: Optional[str]) -> bool:
    """Безопасно проверяет совпадение статического API-ключа."""
    return bool(key and hmac.compare_digest(key, API_SECRET_KEY))


async def _resolve_tester_id(
    session_cookie: Optional[str],
    bearer_creds: Optional[HTTPAuthorizationCredentials],
) -> Optional[int]:
    """Извлекает и проверяет ID тестера из сессионной куки или Bearer-токена."""
    token = session_cookie
    if not token and bearer_creds:
        token = bearer_creds.credentials
    if not token:
        return None
    user_id = verify_tester_session(token)
    if user_id and await is_tester_allowed(user_id):
        return user_id
    return None


async def verify_api_key(key: Optional[str] = Security(_api_key_header)) -> str:
    """Требует статический API-ключ в заголовке X-API-Key."""
    if not _is_valid_api_key(key):
        log.warning("⚠️ Отклонён запрос: требуется статический API-ключ")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-API-Key",
        )
    return str(key)


async def verify_api_or_tester(
    key: Optional[str] = Security(_api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(_bearer_scheme),
    para_session: Optional[str] = Cookie(default=None),
) -> str:
    """Разрешает доступ владельцам API-ключа либо авторизованным тестерам."""
    if _is_valid_api_key(key):
        return f"apikey:{key[:6]}..."
    tester_id = await _resolve_tester_id(para_session, bearer)
    if tester_id is not None:
        return f"tester:{tester_id}"
    log.warning("⚠️ Отклонён неавторизованный запрос к защищённому эндпоинту")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required: provide X-API-Key, Bearer token, or session cookie",
    )


async def verify_admin_access(
    auth_identity: str = Depends(verify_api_or_tester),
) -> str:
    """Разрешает доступ только администраторам (по X-API-Key или ID старосты)."""
    if auth_identity.startswith("apikey:"):
        return auth_identity
    if auth_identity.startswith("tester:"):
        uid = int(auth_identity.split(":")[1])
        if uid in {ALLOWED_USER_ID, DEPUTY_USER_ID}:
            return auth_identity
    log.warning(f"🚫 Отклонён вызов привилегированного метода: {auth_identity}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Administrator privilege required",
    )
