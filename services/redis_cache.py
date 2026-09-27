"""
Сервис быстрых операций с кэшем Redis.

Отвечает за сохранение и извлечение кэшированных данных кнопок бота.
"""

import json
from typing import Optional
from config import REDIS_CACHE_TTL_SECONDS
from core.logger import get_logger
from core.redis import init_redis

log = get_logger("redis_cache")
HW_QUEUE_KEY = "hw:tasks:queue"


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


async def cache_flush(pattern: str = "sched:*") -> int:
    """
    Безопасно удаляет из Redis только ключи расписания.

    Используем scan_iter вместо flushdb, чтобы не затереть хэши
    решённых ДЗ и антиспам счётчики пользователей.

    :param pattern: Паттерн удаляемых ключей
    :return: Количество удалённых ключей
    """
    deleted = 0
    try:
        client = await init_redis()
        if client:
            keys = [k async for k in client.scan_iter(match=pattern)]
            if keys:
                deleted = await client.delete(*keys)
            log.info(f"Очищен кэш расписания ({deleted} ключей по {pattern})")
    except Exception as e:
        log.error(f"Ошибка точечной очистки кэша Redis ({pattern}): {e}")
    return deleted


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


async def push_hw_task(task_data: dict) -> bool:
    """
    Помещает задачу на решение ДЗ в конец очереди Redis.

    :param task_data: Словарь с параметрами сообщения и задания
    :return: True в случае успешной вставки
    """
    try:
        client = await init_redis()
        if client:
            payload = json.dumps(task_data, ensure_ascii=False)
            await client.rpush(HW_QUEUE_KEY, payload)
            msg_id = task_data.get("message_id")
            log.info(f"Задача ДЗ (msg_id={msg_id}) добавлена в очередь {HW_QUEUE_KEY}")
            return True
    except Exception as e:
        log.error(f"Ошибка добавления задачи ДЗ в Redis: {e}")
    return False


async def pop_hw_task(timeout: int = 2) -> Optional[dict]:
    """
    Атомарно извлекает задачу решения ДЗ из начала очереди Redis.

    :param timeout: Время ожидания в секундах
    :return: Словарь задачи или None
    """
    try:
        client = await init_redis()
        if client:
            res = await client.blpop(HW_QUEUE_KEY, timeout=timeout)
            if res:
                _, data_str = res
                return json.loads(data_str)
    except Exception as e:
        log.error(f"Ошибка извлечения задачи ДЗ из Redis: {e}")
    return None


