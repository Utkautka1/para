"""
Надёжная очередь заданий решателя ДЗ в Redis (паттерн Reliable Queue).

Жизненный цикл задания:
  1. push_hw_task — сразу в hw:tasks:queue, либо schedule_hw_task — в отложенный zset
     на окно уточнений (реплай студента склеивается с заданием через take_pending_hw_task)
  2. promote_due_hw_tasks переносит созревшие отложенные задания в очередь
  3. pop_hw_task атомарно (BLMOVE) перекладывает задание в hw:tasks:processing
  4. ack_hw_task снимает его из processing, nack_hw_task — возвращает в очередь
     или после HW_MAX_TASK_RETRIES отправляет в DLQ
  5. recover_stale_hw_tasks при старте solver возвращает зависшее в processing

ack/nack ищут задание в processing по JSON-строке (LREM), поэтому сериализация
везде одна — json.dumps(task, ensure_ascii=False), и до LREM задание не меняют.
"""

import json
import time

from config import (
    HW_DELAYED_KEY,
    HW_DLQ_KEY,
    HW_PENDING_PREFIX,
    HW_PROCESSING_KEY,
    HW_QUEUE_KEY,
)
from core.logger import get_logger
from core.redis import init_redis

log = get_logger("hw_queue")


async def push_hw_task(task_data: dict) -> bool:
    """
    Добавляет сериализованную задачу на решение ДЗ в конец очереди Redis.

    Обеспечивает надежную буферизацию задач для воркера-решателя с гарантией
    сохранения порядка поступления (FIFO).

    Возвращает True в случае успешной вставки, False при сетевой ошибке.
    """
    try:
        client = await init_redis()
        if client:
            payload = json.dumps(task_data, ensure_ascii=False)
            await client.rpush(HW_QUEUE_KEY, payload)
            msg_id = task_data.get("message_id")
            log.info("Задача ДЗ (msg_id=%s) добавлена в очередь %s", msg_id, HW_QUEUE_KEY)
            return True
    except Exception as e:
        log.error("Ошибка добавления задачи ДЗ в Redis: %s", e)
    return False


# Переносит созревшие отложенные задания в очередь одной атомарной операцией:
# ZREM внутри Lua гарантирует, что задание, забранное на замену, не уйдёт в solver
LUA_PROMOTE_DUE = """
local due = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ARGV[1])
for _, payload in ipairs(due) do
    redis.call('ZREM', KEYS[1], payload)
    redis.call('RPUSH', KEYS[2], payload)
end
return #due
"""


async def schedule_hw_task(task_data: dict, delay_seconds: int) -> bool:
    """
    Откладывает задание ДЗ на delay_seconds — окно для уточнений реплаем.

    Индекс hw:tasks:pending:<message_id> позволяет найти задание по сообщению,
    на которое ответил студент. TTL индекса с запасом переживает окно.

    Возвращает True при успешной постановке.
    """
    try:
        client = await init_redis()
        if not client:
            return False
        payload = json.dumps(task_data, ensure_ascii=False)
        await client.zadd(HW_DELAYED_KEY, {payload: time.time() + delay_seconds})
        await client.set(f"{HW_PENDING_PREFIX}{task_data.get('message_id')}", payload, ex=delay_seconds * 4)
        log.info("Задача ДЗ (msg_id=%s) ждёт уточнений %s сек", task_data.get("message_id"), delay_seconds)
        return True
    except Exception as e:
        log.error("Ошибка откладывания задачи ДЗ в Redis: %s", e)
        return False


async def take_pending_hw_task(message_id: int) -> dict | None:
    """
    Забирает ещё не отправленное в solver задание по id его сообщения.

    Успешный ZREM означает, что задание не успело уйти в очередь: дальше его
    заменит склеенное с уточнением. Если ZREM ничего не удалил — задание уже решается.

    Возвращает задание или None, если окно уточнений закрыто.
    """
    try:
        client = await init_redis()
        if not client:
            return None
        payload = await client.getdel(f"{HW_PENDING_PREFIX}{message_id}")
        if payload and await client.zrem(HW_DELAYED_KEY, payload):
            return json.loads(payload)
    except Exception as e:
        log.error("Ошибка поиска отложенной задачи ДЗ (msg_id=%s): %s", message_id, e)
    return None


async def promote_due_hw_tasks() -> int:
    """
    Отправляет в очередь solver задания, у которых закончилось окно уточнений.

    Возвращает количество перенесённых заданий.
    """
    try:
        client = await init_redis()
        if client:
            moved = int(await client.eval(LUA_PROMOTE_DUE, 2, HW_DELAYED_KEY, HW_QUEUE_KEY, time.time()))
            if moved:
                log.info("В очередь solver ушло отложенных задач ДЗ: %s", moved)
            return moved
    except Exception as e:
        log.error("Ошибка переноса отложенных задач ДЗ: %s", e)
    return 0


async def pop_hw_task(timeout: int = 2) -> dict | None:
    """
    Атомарно извлекает задачу из очереди и переносит в буфер processing.

    Использует BLMOVE для защиты от потери задач при внезапном падении воркера
    в момент обработки (паттерн Reliable Queue).

    Возвращает десериализованный словарь задачи или None по таймауту.
    """
    try:
        client = await init_redis()
        if client:
            raw = await client.blmove(HW_QUEUE_KEY, HW_PROCESSING_KEY, timeout, "LEFT", "RIGHT")
            return json.loads(raw) if raw else None
    except Exception as e:
        log.error("Ошибка извлечения задачи ДЗ из Redis: %s", e)
    return None


async def ack_hw_task(task_data: dict) -> None:
    """
    Подтверждает успешное завершение задачи ДЗ и удаляет её из processing очереди.

    Завершает транзакционный цикл обработки задачи воркером, подтверждая
    доставку решения в целевой топик Telegram.

    Не возвращает значений; удаляет один элемент из списка HW_PROCESSING_KEY.
    """
    try:
        client = await init_redis()
        if client:
            payload = json.dumps(task_data, ensure_ascii=False)
            await client.lrem(HW_PROCESSING_KEY, 1, payload)
            log.debug("Задача ДЗ %s подтверждена (ack)", task_data.get("message_id"))
    except Exception as e:
        log.error("Ошибка подтверждения задачи ДЗ в Redis: %s", e)


async def recover_stale_hw_tasks() -> int:
    """
    Возвращает зависшие задачи из буфера processing обратно в основную очередь.

    Вызывается супервизором при старте контейнера, устраняя последствия
    аварийного завершения предыдущего процесса воркера.

    Возвращает количество успешно восстановленных задач.
    """
    recovered = 0
    try:
        client = await init_redis()
        if client:
            while await client.rpoplpush(HW_PROCESSING_KEY, HW_QUEUE_KEY):
                recovered += 1
            if recovered > 0:
                log.warning("⚠️ Восстановлено %s зависших задач ДЗ из processing", recovered)
    except Exception as e:
        log.error("Ошибка восстановления зависших задач ДЗ: %s", e)
    return recovered


async def clear_hw_queue() -> int:
    """
    Атомарно очищает основную и processing очереди задач решения ДЗ.

    Сбрасывает скопившиеся и зависшие задачи при проведении тестов
    или ручном вмешательстве администратора.

    Возвращает количество удаленных структур ключей очередей.
    """
    try:
        client = await init_redis()
        if client:
            deleted = await client.delete(HW_QUEUE_KEY, HW_PROCESSING_KEY, HW_DELAYED_KEY)
            log.info("Очереди задач ДЗ очищены (deleted=%s)", deleted)
            return deleted
    except Exception as e:
        log.error("Ошибка очистки очереди ДЗ в Redis: %s", e)
    return 0


# Перекладывает задачу из processing в очередь/DLQ одной атомарной операцией.
# Отдельные LREM + RPUSH при падении воркера между ними теряли бы задачу
# либо оставляли её дубль в processing, который recover_stale_hw_tasks вернул бы снова.
LUA_REQUEUE = """
redis.call('LREM', KEYS[1], 1, ARGV[1])
redis.call('RPUSH', KEYS[2], ARGV[2])
return 1
"""


async def nack_hw_task(task_data: dict, max_retries: int = 3) -> bool:
    """
    Обрабатывает ошибку выполнения задачи ДЗ, отправляя её на повтор или в DLQ.

    Инкрементирует счетчик попыток и при превышении лимита переносит задачу в
    Dead Letter Queue (HW_DLQ_KEY) для последующего ручного анализа инцидента.

    Возвращает True, если задача возвращена в очередь на retry, иначе False (DLQ).
    """
    client = await init_redis()
    if not client:
        return False
    # Снимок до инкремента: в processing лежит именно эта строка, по ней и снимаем LREM
    original = json.dumps(task_data, ensure_ascii=False)
    retries = task_data.get("retries", 0) + 1
    task_data["retries"] = retries
    retried = retries <= max_retries
    target = HW_QUEUE_KEY if retried else HW_DLQ_KEY
    payload = json.dumps(task_data, ensure_ascii=False)
    await client.eval(LUA_REQUEUE, 2, HW_PROCESSING_KEY, target, original, payload)
    if retried:
        log.warning("⚠️ Задача ДЗ %s на повтор (#%s/%s)", task_data.get("message_id"), retries, max_retries)
    else:
        log.error("❌ Задача ДЗ %s превысила %s попыток -> DLQ", task_data.get("message_id"), max_retries)
    return retried
