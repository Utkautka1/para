"""
Зависимости FastAPI: авторизация по персональным API-ключам тестеров и сессиям.

Обеспечивает сквозной аудит: логирует кто (ID тестера), когда и какой метод вызвал.
"""

import hmac
from urllib.parse import urlsplit

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

# Методы без побочных эффектов — CSRF для них не опасен
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

# Значения Sec-Fetch-Site, при которых запрос инициирован нашей же страницей или пользователем
_SAME_SITE_FETCH = frozenset({"same-origin", "none"})


async def _resolve_key_identity(key: str | None) -> str | None:
    """
    Определяет владельца API-ключа (мастер-ключ или персональный ключ тестера).

    Использует криптографическое сравнение hmac.compare_digest для мастер-ключа.

    Возвращает строковый идентификатор ('master_admin', 'tester:123') или None.
    """
    if not key:
        return None

    if hmac.compare_digest(key.encode("utf-8"), API_SECRET_KEY.encode("utf-8")):
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
    log.info("🔎 [AUDIT] %s -> %s %s (IP: %s)", identity, request.method, request.url.path, client_ip)


async def _extract_identity_candidates(
    key: str | None, bearer: HTTPAuthorizationCredentials | None, para_session: str | None
) -> tuple[str | None, bool]:
    """
    Извлекает и верифицирует идентификатор из заголовков или cookies.

    Query-параметры (?key=) намеренно не принимаются: ключ из URL оседает в логах
    uvicorn и истории браузера. Вход по ссылке — через одноразовый /miniapp/login.

    Возвращает (идентификатор или None, True — если личность взята из cookie).
    """
    ident = await _resolve_key_identity(key)
    if ident:
        return ident, False
    if bearer:
        return await _resolve_token_identity(bearer.credentials), False
    return await _resolve_token_identity(para_session), True


def _is_cross_site(request: Request) -> bool:
    """
    Определяет, что запрос пришёл со сторонней страницы.

    Sec-Fetch-Site шлют все современные браузеры; Origin — запасная проверка
    для старых. Без обоих заголовков запрос не браузерный (curl, скрипт),
    а такой клиент не может подставить чужую куку — его пропускаем.

    Возвращает True, если источник запроса — другой сайт.
    """
    fetch_site = request.headers.get("sec-fetch-site")
    if fetch_site:
        return fetch_site not in _SAME_SITE_FETCH
    origin = request.headers.get("origin")
    return bool(origin) and urlsplit(origin).netloc != request.headers.get("host")


def _reject_cookie_csrf(request: Request) -> None:
    """
    Блокирует изменяющие запросы со сторонних сайтов, авторизованные кукой.

    Кука para_session выставлена с SameSite=None (нужно для iframe Telegram),
    поэтому браузер прикладывает её и к форме с чужой страницы.
    Заголовки X-API-Key и Bearer чужая страница подставить не может — их не проверяем.

    Ничего не возвращает или выбрасывает HTTP 403.
    """
    if request.method in _SAFE_METHODS or not _is_cross_site(request):
        return
    log.warning("🚫 CSRF: межсайтовый %s %s с сессионной кукой", request.method, request.url.path)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-site request rejected")


async def verify_api_or_tester(
    request: Request,
    key: str | None = Security(_api_key_header),
    bearer: HTTPAuthorizationCredentials | None = Security(_bearer_scheme),
    para_session: str | None = Cookie(default=None),
) -> str:
    """
    Универсальная зависимость авторизации по API-ключу в заголовке, Bearer-токену или cookie.

    Защищает API-эндпоинты и регистрирует аудит-событие для каждого запроса.
    Возвращает строку идентификатора субъекта или вызывает HTTP 401 Unauthorized.
    """
    ident, from_cookie = await _extract_identity_candidates(key, bearer, para_session)
    if ident:
        if from_cookie:
            _reject_cookie_csrf(request)
        _log_audit_access(ident, request)
        return ident

    log.warning("⚠️ Неавторизованный запрос к %s %s", request.method, request.url.path)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key or session")


def _identity_uid(identity: str) -> int | None:
    """
    Достаёт Telegram ID из идентификатора 'tester:<uid>' или 'classmate:<uid>'.

    Староста и зам состоят в реестре группы, поэтому их сессия Mini App
    приходит как classmate, а не tester — учитываем оба префикса.

    Возвращает uid или None для master_admin и неизвестных форматов.
    """
    prefix, _, raw_uid = identity.partition(":")
    if prefix not in {"tester", "classmate"} or not raw_uid.isdigit():
        return None
    return int(raw_uid)


async def verify_admin_access(auth_identity: str = Depends(verify_api_or_tester)) -> str:
    """
    Ограничивает доступ к эндпоинту только системным администраторам и старостату.

    Проверяет принадлежность ID пользователя списку доверенных администраторов.

    Возвращает подтвержденный идентификатор или вызывает HTTP 403 Forbidden.
    """
    if auth_identity == "master_admin" or _identity_uid(auth_identity) in {ALLOWED_USER_ID, DEPUTY_USER_ID}:
        return auth_identity

    log.warning("🚫 Попытка несанкционированного доступа: %s", auth_identity)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


async def verify_api_key(key: str | None = Security(_api_key_header)) -> str:
    """
    Проверяет статический API-ключ мастер-администратора (legacy-совместимость).

    Использует hmac.compare_digest для защиты от атак по времени (timing attacks).

    Возвращает строку ключа или выбрасывает HTTP 403 Forbidden.
    """
    if not key or not hmac.compare_digest(key.encode("utf-8"), API_SECRET_KEY.encode("utf-8")):
        log.warning("⚠️ Неверный или отсутствующий статический API-ключ")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing API key")

    return key
