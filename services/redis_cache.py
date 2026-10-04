"""
Сервис быстрых операций с кэшем Redis.

Отвечает за сохранение и извлечение кэшированных данных кнопок бота.
"""

import json
import time
from typing import List, Optional, Tuple
from config import ALLOWED_USER_ID, REDIS_CACHE_TTL_SECONDS
from core.logger import get_logger
from core.redis import init_redis

log = get_logger("redis_cache")
HW_QUEUE_KEY = "hw:tasks:queue"
HW_PROCESSING_KEY = "hw:tasks:processing"
SNAPSHOT_KEY = "sched:group:snapshot"
SNAPSHOT_META_KEY = "sched:group:meta"
TOPIC_CLEANUP_KEY = "topic:cleanup_messages"


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


async def cache_set(key: str, value: str, ttl: Optional[int] = REDIS_CACHE_TTL_SECONDS) -> None:
    """
    Сохраняет строковое значение в Redis с опциональным TTL (сек).

    :param key: Ключ записи
    :param value: Сохраняемая строка
    :param ttl: Время жизни в секундах (None / 0 для бессрочного)
    """
    try:
        client = await init_redis()
        if client:
            if ttl and ttl > 0:
                await client.set(key, value, ex=ttl)
            else:
                await client.set(key, value)
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

    Для администратора (ALLOWED_USER_ID) лимиты полностью отключены.
    :param user_id: Telegram ID пользователя
    :return: True если лимит не превышен или пользователь — админ
    """
    if user_id == ALLOWED_USER_ID:
        return True
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
    """Атомарно перемещает задачу из очереди в processing и возвращает словарь."""
    try:
        client = await init_redis()
        if client:
            raw = await client.blmove(
                HW_QUEUE_KEY, HW_PROCESSING_KEY,
                timeout=timeout, wherefrom="LEFT", whereto="RIGHT"
            )
            return json.loads(raw) if raw else None
    except Exception as e:
        log.error(f"Ошибка извлечения задачи ДЗ из Redis: {e}")
    return None


async def ack_hw_task(task_data: dict) -> None:
    """Удаляет завершенную задачу из processing очереди после успешного решения."""
    try:
        client = await init_redis()
        if client:
            payload = json.dumps(task_data, ensure_ascii=False)
            await client.lrem(HW_PROCESSING_KEY, 1, payload)
            log.debug(f"Задача ДЗ {task_data.get('message_id')} подтверждена (ack)")
    except Exception as e:
        log.error(f"Ошибка подтверждения задачи ДЗ в Redis: {e}")


async def recover_stale_hw_tasks() -> int:
    """Возвращает зависшие задачи из processing обратно в очередь при старте."""
    recovered = 0
    try:
        client = await init_redis()
        if client:
            while await client.rpoplpush(HW_PROCESSING_KEY, HW_QUEUE_KEY):
                recovered += 1
            if recovered > 0:
                log.warning(f"⚠️ Восстановлено {recovered} зависших задач ДЗ из processing")
    except Exception as e:
        log.error(f"Ошибка восстановления зависших задач ДЗ: {e}")
    return recovered


async def clear_hw_queue() -> int:
    """Очищает основную и processing очереди задач ДЗ в Redis."""
    try:
        client = await init_redis()
        if client:
            deleted = await client.delete(HW_QUEUE_KEY, HW_PROCESSING_KEY)
            log.info(f"Очереди задач ДЗ очищены (deleted={deleted})")
            return deleted
    except Exception as e:
        log.error(f"Ошибка очистки очереди ДЗ в Redis: {e}")
    return 0


async def save_schedule_snapshot(snapshot: dict, meta: dict, ttl: int = 86400) -> None:
    """Сохраняет отфильтрованный срез расписания группы и метаданные в Redis."""
    try:
        client = await init_redis()
        if client:
            p_snap = json.dumps(snapshot, ensure_ascii=False)
            p_meta = json.dumps(meta, ensure_ascii=False)
            async with client.pipeline(transaction=True) as pipe:
                pipe.set(SNAPSHOT_KEY, p_snap, ex=ttl)
                pipe.set(SNAPSHOT_META_KEY, p_meta, ex=ttl)
                await pipe.execute()
            log.info("Срез расписания группы успешно сохранен в кэш Redis")
    except Exception as e:
        log.error(f"Ошибка сохранения снимка расписания в Redis: {e}")


async def load_schedule_snapshot() -> Tuple[Optional[dict], Optional[dict]]:
    """Загружает сохраненный срез расписания и метаданные из Redis."""
    try:
        client = await init_redis()
        if client:
            snap_raw = await client.get(SNAPSHOT_KEY)
            meta_raw = await client.get(SNAPSHOT_META_KEY)
            if snap_raw and meta_raw:
                log.debug("Снимок расписания успешно загружен из Redis")
                return json.loads(snap_raw), json.loads(meta_raw)
    except Exception as e:
        log.error(f"Ошибка чтения снимка расписания из Redis: {e}")
    return None, None


async def is_reminder_sent(rem_key: str) -> bool:
    """Проверяет, было ли уже отправлено напоминание с данным ключом сегодня."""
    val = await cache_get(f"rem:sent:{rem_key}")
    return val == "1"


async def mark_reminder_sent(rem_key: str, ttl: int = 86400) -> None:
    """Отмечает напоминание как отправленное в Redis с суточным TTL."""
    await cache_set(f"rem:sent:{rem_key}", "1", ttl=ttl)


async def get_topic_state_redis(key: str = "topic:main_msg_id") -> Optional[int]:
    """Извлекает сохраненный ID сообщения топика из Redis."""
    val = await cache_get(key)
    return int(val) if val and val.isdigit() else None


async def set_topic_state_redis(val: int, key: str = "topic:main_msg_id") -> None:
    """Сохраняет ID главного сообщения топика в Redis без экспирации."""
    await cache_set(key, str(val), ttl=0)


async def register_message_for_cleanup(chat_id: int, msg_id: int, delay_sec: int = 900) -> None:
    """Регистрирует сообщение в ZSET для гарантированного удаления через delay_sec."""
    try:
        client = await init_redis()
        if client:
            target_ts = time.time() + delay_sec
            await client.zadd(TOPIC_CLEANUP_KEY, {f"{chat_id}:{msg_id}": target_ts})
            log.debug(f"Сообщение {chat_id}:{msg_id} запланировано на удаление через {delay_sec}с")
    except Exception as e:
        log.error(f"Ошибка регистрации сообщения на удаление: {e}")


async def get_expired_messages_for_cleanup() -> List[Tuple[int, int]]:
    """Извлекает и удаляет из ZSET сообщения, чей срок хранения истёк."""
    results: List[Tuple[int, int]] = []
    try:
        client = await init_redis()
        if client:
            now_ts = time.time()
            expired = await client.zrangebyscore(TOPIC_CLEANUP_KEY, min=0, max=now_ts)
            if expired:
                await client.zrem(TOPIC_CLEANUP_KEY, *expired)
                results = [(int(i.split(":")[0]), int(i.split(":")[1])) for i in expired]
    except Exception as e:
        log.error(f"Ошибка извлечения сообщений для очистки: {e}")
    return results


