"""
Зависимости FastAPI: авторизация по персональным API-ключам тестеров и сессиям.

Обеспечивает сквозной аудит: логирует кто (ID тестера), когда и какой метод вызвал.
"""

import hmac

from fastapi import Cookie, Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from config import (
    ALLOWED_USER_ID,
    API_SECRET_KEY,
    API_TESTER_KEY_PREFIX,
    DEPUTY_USER_ID,
)
from core.logger import get_logger
from services.classmates_auth import find_classmate_by_tg_id
from services.testers_manager import get_tester_by_key, is_tester_allowed
from utils.miniapp_auth import verify_tester_session

log = get_logger("api_auth")

_api_key_header = APIKeyHeader(name="X-API-Key", scheme_name="ApiKeyAuth", auto_error=False)
_bearer_scheme = HTTPBearer(scheme_name="BearerAuth", auto_error=False)


async def _resolve_key_identity(key: str | None) -> str | None:
    """
    Определяет владельца API-ключа (мастер-ключ или персональный ключ тестера).

    Использует криптографическое сравнение hmac.compare_digest для мастер-ключа.

    Возвращает строковый идентификатор ('master_admin', 'tester:123') или None.
    """
    if not key:
        return None

    if hmac.compare_digest(key, API_SECRET_KEY):
        return "master_admin"

    uid = await get_tester_by_key(key)
    if uid and await is_tester_allowed(uid):
        return f"tester:{uid}"

    return None


async def _resolve_token_identity(token: str | None) -> str | None:
    """
    Проверяет токен (сессия Mini App или персональный ключ в заголовке Bearer).

    Валидирует цифровую подпись сессии или проверяет ключ тестера в Redis.

    Возвращает строку идентификатора 'tester:<uid>' или None.
    """
    if not token:
        return None

    if token.startswith(API_TESTER_KEY_PREFIX):
        uid = await get_tester_by_key(token)
        return f"tester:{uid}" if uid and await is_tester_allowed(uid) else None

    uid = verify_tester_session(token)
    if not uid:
        return None
    if uid == ALLOWED_USER_ID or find_classmate_by_tg_id(uid) is not None:
        return f"classmate:{uid}"
    return f"tester:{uid}" if await is_tester_allowed(uid) else None


def _log_audit_access(identity: str, request: Request) -> None:
    """
    Записывает событие успешного доступа в системный журнал аудита безопасности.

    Фиксирует личность инициатора, HTTP-метод, маршрут и IP-адрес клиента.

    Ничего не возвращает.
    """
    client_ip = request.client.host if request.client else "unknown"
    log.info(f"🔎 [AUDIT] {identity} -> {request.method} {request.url.path} (IP: {client_ip})")


async def _extract_identity_candidates(
    request: Request, key: str | None, bearer: HTTPAuthorizationCredentials | None, para_session: str | None
) -> str | None:
    """Извлекает и верифицирует идентификатор из заголовков, query-параметров или cookies."""
    target_key = key or request.query_params.get("key") or request.query_params.get("api_key")
    ident = await _resolve_key_identity(target_key)
    if not ident:
        token = bearer.credentials if bearer else para_session
        ident = await _resolve_token_identity(token)
    return ident


async def verify_api_or_tester(
    request: Request,
    key: str | None = Security(_api_key_header),
    bearer: HTTPAuthorizationCredentials | None = Security(_bearer_scheme),
    para_session: str | None = Cookie(default=None),
) -> str:
    """
    Универсальная зависимость авторизации по API-ключу, query-параметру, токену или cookie.

    Защищает API-эндпоинты и регистрирует аудит-событие для каждого запроса.
    Возвращает строку идентификатора субъекта или вызывает HTTP 401 Unauthorized.
    """
    ident = await _extract_identity_candidates(request, key, bearer, para_session)
    if ident:
        _log_audit_access(ident, request)
        return ident

    log.warning(f"⚠️ Неавторизованный запрос к {request.method} {request.url.path}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key or session")


async def verify_admin_access(auth_identity: str = Depends(verify_api_or_tester)) -> str:
    """
    Ограничивает доступ к эндпоинту только системным администраторам и старостату.

    Проверяет принадлежность ID пользователя списку доверенных администраторов.

    Возвращает подтвержденный идентификатор или вызывает HTTP 403 Forbidden.
    """
    if auth_identity == "master_admin":
        return auth_identity

    if auth_identity.startswith("tester:"):
        uid = int(auth_identity.split(":")[1])
        if uid in {ALLOWED_USER_ID, DEPUTY_USER_ID}:
            return auth_identity

    log.warning(f"🚫 Попытка несанкционированного доступа: {auth_identity}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


async def verify_api_key(key: str | None = Security(_api_key_header)) -> str:
    """
    Проверяет статический API-ключ мастер-администратора (legacy-совместимость).

    Использует hmac.compare_digest для защиты от атак по времени (timing attacks).

    Возвращает строку ключа или выбрасывает HTTP 403 Forbidden.
    """
    if not key or not hmac.compare_digest(key, API_SECRET_KEY):
        log.warning("⚠️ Неверный или отсутствующий статический API-ключ")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing API key")

    return key
