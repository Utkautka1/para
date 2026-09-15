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


async def is_message_processed(message_id: int) -> bool:
    """
    Проверяет, было ли сообщение с ДЗ уже решено и отправлено ранее.

    :param message_id: Telegram ID сообщения
    :return: True если решено, иначе False
    """
    key = f"hw_processed:{message_id}"
    val = await cache_get(key)
    return val == "1"


async def mark_message_processed(message_id: int) -> None:
    """
    Отмечает сообщение с ДЗ как обработанное на 30 дней в Redis.

    :param message_id: Telegram ID сообщения
    """
    key = f"hw_processed:{message_id}"
    await cache_set(key, "1", ttl=2592000)


async def check_user_rate_limit(user_id: int) -> bool:
    """
    Проверяет лимит запросов пользователя (максимум 3 запроса в минуту).

    :param user_id: Telegram ID пользователя
    :return: True если лимит не превышен, иначе False
    """
    key = f"hw_rate:{user_id}"
    try:
        client = await init_redis()
        if client:
            count = await client.incr(key)
            if count == 1:
                await client.expire(key, 60)
            return count <= 3
    except Exception as e:
        log.error(f"Ошибка проверки rate-limit в Redis ({user_id}): {e}")
    return True


async def is_hash_processed(content_hash: str) -> bool:
    """
    Проверяет, отправлялось ли аналогичное задание (хэш текста/картинки) в последние 24 часа.

    :param content_hash: SHA256 хэш контента
    :return: True если такой контент уже решен
    """
    key = f"hw_hash:{content_hash}"
    val = await cache_get(key)
    return val == "1"


async def mark_hash_processed(content_hash: str) -> None:
    """
    Сохраняет хэш выполненного задания на 24 часа.

    :param content_hash: SHA256 хэш
    """
    key = f"hw_hash:{content_hash}"
    await cache_set(key, "1", ttl=86400)


