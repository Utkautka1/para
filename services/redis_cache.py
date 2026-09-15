"""
Сервис быстрых операций с кэшем Redis.

Отвечает за сохранение и извлечение кэшированных данных кнопок бота.
"""

from typing import Optional
from config import REDIS_CACHE_TTL_SECONDS
from core.logger import get_logger
from core.redis import init_redis

log = get_logger("redis_cache")


async def cache_get(key: str) -> Optional[str]:
    """
    Извлекает строковое значение из Redis по ключу.

    :param key: Ключ записи
    :return: Строка или None
    """
    try:
        client = await init_redis()
        if client:
            val = await client.get(key)
            if val:
                log.debug(f"Redis hit [key={key}]")
                return val
    except Exception as e:
        log.error(f"Ошибка чтения из Redis ({key}): {e}")
    return None


async def cache_set(key: str, value: str, ttl: int = REDIS_CACHE_TTL_SECONDS) -> None:
    """
    Сохраняет строковое значение в Redis с TTL (по умолчанию 600 сек / 10 мин).

    :param key: Ключ записи
    :param value: Сохраняемая строка
    :param ttl: Время жизни в секундах
    """
    try:
        client = await init_redis()
        if client:
            await client.set(key, value, ex=ttl)
            log.debug(f"Сохранено в Redis [key={key}, ttl={ttl}s]")
    except Exception as e:
        log.error(f"Ошибка записи в Redis ({key}): {e}")


async def cache_flush() -> None:
    """
    Очищает весь кэш в Redis при принудительном обновлении.
    """
    try:
        client = await init_redis()
        if client:
            await client.flushdb()
            log.info("Кэш Redis полностью очищен!")
    except Exception as e:
        log.error(f"Ошибка очистки Redis: {e}")
