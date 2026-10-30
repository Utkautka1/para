"""
Одноразовые токены входа в Mini App и Swagger UI по ссылке из бота.

Раньше бот вставлял в ссылки постоянный API-ключ (`?key=...`), и он оседал
в логах uvicorn, истории браузера и Referer. Теперь бот выпускает короткоживущий
токен, а API обменивает его на сессионную куку ровно один раз:
  1. issue_login_token кладёт token -> user_id в Redis с TTL
  2. consume_login_token атомарно читает и удаляет его через GETDEL,
     поэтому повторное открытие той же ссылки уже не авторизует
"""

import secrets

from config import LOGIN_TOKEN_TTL_SECONDS, MINIAPP_URL, REDIS_LOGIN_TOKEN_PREFIX
from core.logger import get_logger
from core.redis import get_redis

log = get_logger("login_tokens")

# Куда можно перенаправить после входа — whitelist против open redirect
LOGIN_REDIRECT_TARGETS: dict[str, str] = {"miniapp": "/miniapp", "docs": "/docs"}


async def issue_login_token(user_id: int) -> str | None:
    """
    Выпускает одноразовый токен входа для пользователя.

    Возвращает токен или None, если Redis недоступен.
    """
    r = await get_redis()
    if not r:
        log.error("❌ Redis недоступен — токен входа для %s не выпущен", user_id)
        return None
    token = secrets.token_urlsafe(32)
    await r.set(f"{REDIS_LOGIN_TOKEN_PREFIX}{token}", str(user_id), ex=LOGIN_TOKEN_TTL_SECONDS)
    log.debug("Выпущен токен входа для user_id=%s, TTL=%s сек", user_id, LOGIN_TOKEN_TTL_SECONDS)
    return token


async def consume_login_token(token: str) -> int | None:
    """
    Погашает токен входа и возвращает user_id владельца.

    GETDEL вместо GET + DELETE — между ними второй запрос с той же ссылкой
    успел бы получить сессию.

    Возвращает user_id или None, если токен не найден, истёк или Redis недоступен.
    """
    r = await get_redis()
    if not r or not token:
        return None
    raw = await r.getdel(f"{REDIS_LOGIN_TOKEN_PREFIX}{token}")
    if not raw:
        log.debug("Токен входа не найден или уже использован")
        return None
    uid_str = raw.decode() if isinstance(raw, bytes) else str(raw)
    return int(uid_str) if uid_str.isdigit() else None


async def build_login_url(user_id: int, target: str = "miniapp") -> str | None:
    """
    Формирует ссылку одноразового входа с перенаправлением на target.

    Возвращает URL или None, если токен выпустить не удалось.
    """
    token = await issue_login_token(user_id)
    if not token:
        return None
    return f"{MINIAPP_URL}/login?t={token}&next={target}"
