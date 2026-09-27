"""
Зависимости FastAPI: авторизация по X-API-Key.

Все эндпоинты para-api защищены статическим API-ключом,
который передается в заголовке X-API-Key. Ключ одинаковый
для bot, worker и solver — они в одной Docker-сети.
"""

import hmac

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from config import API_SECRET_KEY
from core.logger import get_logger

log = get_logger("api_auth")

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str = Security(_api_key_header)) -> str:
    """
    Валидирует API-ключ из заголовка запроса.

    Сравнение через hmac.compare_digest защищает от timing attacks
    при анализе времени ответа на стороне клиента.

    :return: Валидный ключ авторизации
    """
    if not key or not hmac.compare_digest(key, API_SECRET_KEY):
        log.warning("⚠️  Отклонён запрос с невалидным или отсутствующим API-ключом")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return key

