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


async def get_redis() -> Optional[Redis]:
    """
    Возвращает синглтон клиента Redis, подключаясь при необходимости.

    Позволяет безопасно получать активное соединение из любых модулей
    без риска захвата неинициализированной ссылки во время импорта.
    """
    global redis_client
    if redis_client is None:
        await init_redis()
    return redis_client


async def close_redis() -> None:
    """Освобождает соединение с Redis при завершении работы сервиса."""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
        log.info("Соединение с Redis успешно закрыто")
