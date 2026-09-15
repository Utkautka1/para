"""
Модуль инициализации и подключения к Redis.

Предоставляет синглтон клиента Redis для асинхронного кэширования.
"""

from typing import Optional
from redis.asyncio import Redis
from config import REDIS_HOST, REDIS_PORT
from core.logger import get_logger

log = get_logger("redis")
redis_client: Optional[Redis] = None


async def init_redis() -> Redis:
    """
    Инициализирует асинхронное подключение к Redis.

    :return: Объект Redis
    """
    global redis_client
    if redis_client is None:
        try:
            redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            await redis_client.ping()
            log.info(f"Успешное подключение к Redis ({REDIS_HOST}:{REDIS_PORT})")
        except Exception as e:
            log.error(f"Ошибка подключения к Redis ({REDIS_HOST}:{REDIS_PORT}): {e}")
            redis_client = None
    return redis_client
