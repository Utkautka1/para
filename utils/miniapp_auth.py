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

from config import BOT_TOKEN, SESSION_MAX_AGE_SECONDS, SESSION_SECRET
from core.logger import get_logger

log = get_logger("miniapp_auth")


def _build_data_check_string(parsed_data: dict[str, str]) -> str:
    """
    Формирует каноническую строку для проверки цифровой подписи initData.

    Сортирует ключи словаря по алфавиту без поля 'hash' согласно спецификации
    Telegram WebApp Auth для детерминированного вычисления HMAC.

    Возвращает строку пар key=value, разделенных символом перевода строки.
    """
    sorted_items = sorted((k, v) for k, v in parsed_data.items() if k != "hash")
    return "\n".join(f"{k}={v}" for k, v in sorted_items)


def _compute_init_data_hash(data_check_str: str) -> str:
    """
    Вычисляет HMAC-SHA256 хеш данных initData с использованием токена бота.

    Создает промежуточный ключ из строки 'WebAppData' и токена бота, после чего
    подписывает проверочную строку по протоколу Telegram.

    Возвращает шестнадцатеричную (hex) строку дайджеста хеша.
    """
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    return hmac.new(secret_key, data_check_str.encode(), hashlib.sha256).hexdigest()


def _is_auth_date_valid(auth_date_str: str, max_age: int = SESSION_MAX_AGE_SECONDS) -> bool:
    """
    Проверяет актуальность метки времени auth_date.

    Сравнивает разницу между текущим UTC временем и временем выдачи с лимитом max_age,
    предотвращая replay-атаки с использованием устаревших или перехваченных токенов.

    Возвращает True, если возраст подписи находится в допустимом окне, иначе False.
    """
    try:
        auth_ts = int(auth_date_str)
        now_ts = int(datetime.now(UTC).timestamp())
        return 0 <= (now_ts - auth_ts) <= max_age
    except (ValueError, TypeError):
        return False


def _extract_user_payload(raw_json: str) -> dict[str, Any] | None:
    """
    Безопасно парсит сериализованный профиль Telegram пользователя из JSON.

    Изолирует десериализацию от основного потока валидации подписи, отсекая
    невалидные типы данных и поврежденные полезные нагрузки.

    Возвращает словарь данных пользователя или None при синтаксической ошибке.
    """
    try:
        data = json.loads(raw_json)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def validate_telegram_init_data(init_data: str) -> dict[str, Any] | None:
    """
    Валидирует строку initData от Telegram WebApp через криптографическую подпись.

    Защищает эндпоинты Mini App от спуфинга параметров и подделки личности пользователя,
    используя constant-time сравнение hmac.compare_digest против timing-атак.

    Возвращает словарь данных пользователя при валидной подписи или None.
    """
    if not init_data:
        return None
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.get("hash")
    if not received_hash or not _is_auth_date_valid(parsed.get("auth_date", "")):
        return None
    expected_hash = _compute_init_data_hash(_build_data_check_string(parsed))
    if not hmac.compare_digest(received_hash, expected_hash):
        log.warning("⚠️ Невалидная подпись Telegram initData")
        return None
    return _extract_user_payload(parsed.get("user", "{}"))


def generate_tester_session(user_id: int) -> str:
    """
    Генерирует подписанный сессионный токен для авторизации тестера в Swagger UI.

    Формирует полезную нагрузку вида user_id:timestamp и подписывает ее секретным
    ключом SESSION_SECRET (отдельным от мастер-ключа API) для прохождения аутентификации.

    Возвращает токен формата '<user_id>:<timestamp>:<signature>'.
    """
    ts = int(datetime.now(UTC).timestamp())
    payload = f"{user_id}:{ts}"
    sig = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def verify_tester_session(token: str, max_age: int = SESSION_MAX_AGE_SECONDS) -> int | None:
    """
    Проверяет валидность и срок жизни сессионного токена тестера.

    Использует криптографическую проверку подписи и контроль TTL токена
    для предотвращения несанкционированного доступа к служебным роутерам.

    Возвращает целочисленный Telegram ID тестера при успехе, иначе None.
    """
    if not token or token.count(":") != 2:
        return None
    raw_uid, raw_ts, signature = token.split(":")
    payload = f"{raw_uid}:{raw_ts}"
    expected_sig = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        return None
    if not _is_auth_date_valid(raw_ts, max_age=max_age):
        return None
    try:
        return int(raw_uid)
    except ValueError:
        return None
