"""
Модуль криптографической аутентификации Telegram Mini App и сессий тестеров.

Реализует официальный алгоритм валидации Telegram.WebApp.initData через HMAC-SHA256,
проверку срока действия auth_date для защиты от replay-атак и генерацию подписанных
сессионных токенов для безопасного тестирования API через Swagger UI.
"""

import hashlib
import hmac
import json
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qsl

from config import API_SECRET_KEY, BOT_TOKEN, SESSION_MAX_AGE_SECONDS
from core.logger import get_logger

log = get_logger("miniapp_auth")



def _build_data_check_string(parsed_data: dict[str, str]) -> str:
    """Формирует каноническую строку для проверки подписи initData."""
    sorted_items = sorted(
        (k, v) for k, v in parsed_data.items() if k != "hash"
    )
    return "\n".join(f"{k}={v}" for k, v in sorted_items)


def _compute_init_data_hash(data_check_str: str) -> str:
    """Вычисляет HMAC-SHA256 хеш данных initData с секретом бота."""
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    return hmac.new(secret_key, data_check_str.encode(), hashlib.sha256).hexdigest()


def _is_auth_date_valid(auth_date_str: str, max_age: int = SESSION_MAX_AGE_SECONDS) -> bool:
    """Проверяет актуальность auth_date для защиты от replay-атак."""
    try:
        auth_ts = int(auth_date_str)
        now_ts = int(datetime.now(UTC).timestamp())
        return 0 <= (now_ts - auth_ts) <= max_age
    except (ValueError, TypeError):
        return False


def validate_telegram_init_data(init_data: str) -> dict[str, Any] | None:
    """
    Валидирует строку initData от Telegram WebApp.

    Проверяет HMAC-подпись хеша и время генерации данных.
    Возвращает словарь с данными пользователя или None при ошибке.
    """
    if not init_data:
        return None
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.get("hash")
    if not received_hash or not _is_auth_date_valid(parsed.get("auth_date", "")):
        return None
    data_check_str = _build_data_check_string(parsed)
    expected_hash = _compute_init_data_hash(data_check_str)
    if not hmac.compare_digest(received_hash, expected_hash):
        log.warning("⚠️ Невалидная подпись Telegram initData")
        return None
    try:
        user_data = json.loads(parsed.get("user", "{}"))
        return user_data if isinstance(user_data, dict) else None
    except json.JSONDecodeError:
        return None


def generate_tester_session(user_id: int) -> str:
    """Генерирует криптографически подписанный сессионный токен для тестера."""
    ts = int(datetime.now(UTC).timestamp())
    payload = f"{user_id}:{ts}"
    signature = hmac.new(API_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def verify_tester_session(token: str, max_age: int = SESSION_MAX_AGE_SECONDS) -> int | None:
    """
    Проверяет валидность сессионного токена тестера.

    Сверяет цифровую подпись токена и срок жизни сессии.
    Возвращает Telegram user_id тестера или None при невалидности.
    """
    if not token or token.count(":") != 2:
        return None
    raw_uid, raw_ts, signature = token.split(":")
    payload = f"{raw_uid}:{raw_ts}"
    expected_sig = hmac.new(API_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        return None
    if not _is_auth_date_valid(raw_ts, max_age=max_age):
        return None
    try:
        return int(raw_uid)
    except ValueError:
        return None
