"""
Сервис быстрых операций с кэшем Redis.

Отвечает за сохранение и извлечение кэшированных данных кнопок бота, снимков расписания,
очереди фонового решения домашних заданий и распределенных блокировок.
"""

import hashlib
import json
import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from config import (
    ALLOWED_USER_ID,
    HW_DLQ_KEY,
    HW_PROCESSING_KEY,
    HW_QUEUE_KEY,
    LUA_RELEASE_LOCK,
    REDIS_CACHE_TTL_SECONDS,
    SCHEDULE_REFRESH_REQUEST_KEY,
    SNAPSHOT_KEY,
    SNAPSHOT_META_KEY,
    TOPIC_CLEANUP_KEY,
)
from core.logger import get_logger
from core.redis import init_redis
from core.telemetry import trace_span

log = get_logger("redis_cache")


async def cache_get(key: str) -> str | None:
    """
    Извлекает строковое значение из кэша Redis по ключу.

    Предотвращает падение приложения при недоступности Redis, возвращая None
    и логируя сбои с минимальным оверхедом на дебаг-уровне.

    Возвращает строку со значением из кэша или None при промахе или ошибке.
    """
    async with trace_span("redis.cache_get", attributes={"redis.key": key}):
        try:
            client = await init_redis()
            if client:
                val = await client.get(key)
                if val:
                    log.debug("Redis hit [key=%s]", key)
                    return val
        except Exception as e:
            log.error("Ошибка чтения из Redis (%s): %s", key, e)
        return None


async def cache_set(key: str, value: str, ttl: int | None = REDIS_CACHE_TTL_SECONDS) -> None:
    """
    Сохраняет строковое значение в Redis с настраиваемым временем жизни TTL.

    Автоматически очищает старые записи по истечении TTL во избежание утечки памяти.

    Не возвращает значений; логирует ошибки записи в логгер.
    """
    async with trace_span("redis.cache_set", attributes={"redis.key": key, "redis.ttl": ttl or 0}):
        try:
            client = await init_redis()
            if client:
                await (client.set(key, value, ex=ttl) if ttl and ttl > 0 else client.set(key, value))
                log.debug("Сохранено в Redis [key=%s, ttl=%ss]", key, ttl)
        except Exception as e:
            log.error("Ошибка записи в Redis (%s): %s", key, e)


async def cache_delete(key: str) -> bool:
    """
    Удаляет конкретный ключ из кэша Redis.

    Используется для немедленной инвалидации кэша лидерборда и профилей,
    гарантируя актуальность данных без ожидания истечения TTL.

    Возвращает True если ключ был удален, иначе False.
    """
    async with trace_span("redis.cache_delete", attributes={"redis.key": key}):
        try:
            client = await init_redis()
            if client:
                deleted = await client.delete(key)
                log.debug("Удален ключ из Redis [key=%s, deleted=%s]", key, deleted)
                return bool(deleted)
        except Exception as e:
            log.error("Ошибка удаления из Redis (%s): %s", key, e)
        return False


async def cache_flush(pattern: str = "sched:*") -> int:
    """
    Выполняет безопасную точечную очистку ключей по заданному шаблону.

    Использует неблокирующий scan_iter вместо опасного flushdb, сохраняя
    пользовательские сессии, антиспам-счетчики и очереди задач.

    Возвращает количество успешно удаленных ключей из пространства Redis.
    """
    deleted = 0
    try:
        client = await init_redis()
        if client:
            keys = [k async for k in client.scan_iter(match=pattern)]
            if keys:
                deleted = await client.delete(*keys)
            log.info("Очищен кэш расписания (%s ключей по %s)", deleted, pattern)
    except Exception as e:
        log.error("Ошибка точечной очистки кэша Redis (%s): %s", pattern, e)
    return deleted


async def is_message_processed(message_id: int) -> bool:
    """
    Проверяет, было ли сообщение с домашним заданием уже решено ранее.

    Защищает от повторного запуска тяжелого нейросетевого инференса DeepSeek
    при дублирующих кликах или пересылках одного и того же сообщения.

    Возвращает True, если отметка найдена в кэше, иначе False.
    """
    key = f"hw_processed:{message_id}"
    val = await cache_get(key)
    return val == "1"


async def mark_message_processed(message_id: int) -> None:
    """
    Помечает Telegram-сообщение как обработанное в Redis на 30 дней.

    Хранит признак решения с TTL 30 дней для гарантированного предотвращения
    повторных решений в рамках активного учебного месяца.

    Не возвращает значений; сохраняет ключ hw_processed:{message_id}.
    """
    key = f"hw_processed:{message_id}"
    await cache_set(key, "1", ttl=2592000)


async def check_user_rate_limit(user_id: int) -> bool:
    """
    Проверяет лимит запросов пользователя на решение ДЗ (не более 3 в минуту).

    Защищает API DeepSeek от исчерпания токенов и перегрузки очереди задач,
    делая исключение только для администратора системы.

    Возвращает True, если запрос разрешен, иначе False (троттлинг).
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
        log.error("Ошибка проверки rate-limit в Redis (%s): %s", user_id, e)
    return True


async def is_hash_processed(content_hash: str) -> bool:
    """
    Проверяет, решалось ли идентичное задание за последние 24 часа по SHA256-хэшу.

    Позволяет мгновенно отсекать дубли картинок и текстовых задач от разных
    одногруппников без лишних сетевых затрат.

    Возвращает True, если хэш присутствует в кэше, иначе False.
    """
    key = f"hw_hash:{content_hash}"
    val = await cache_get(key)
    return val == "1"


async def mark_hash_processed(content_hash: str) -> None:
    """
    Сохраняет SHA256-хэш решенного задания в Redis на 24 часа.

    Кэширует признак выполнения контента на одни сутки для дедупликации
    запросов между студентами одной академической группы.

    Не возвращает значений; устанавливает ключ hw_hash:{hash} с TTL 24ч.
    """
    key = f"hw_hash:{content_hash}"
    await cache_set(key, "1", ttl=86400)


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
            deleted = await client.delete(HW_QUEUE_KEY, HW_PROCESSING_KEY)
            log.info("Очереди задач ДЗ очищены (deleted=%s)", deleted)
            return deleted
    except Exception as e:
        log.error("Ошибка очистки очереди ДЗ в Redis: %s", e)
    return 0


async def save_schedule_snapshot(snapshot: dict, meta: dict, ttl: int = 86400) -> None:
    """
    Транзакционно сохраняет срез расписания и его метаданные через Redis Pipeline.

    Гарантирует консистентность данных между телом расписания и метаинформацией
    о времени актуализации даже при параллельных чтениях.

    Не возвращает значений; логирует результат сохранения снимка.
    """
    try:
        client = await init_redis()
        if client:
            p_snap = json.dumps(snapshot, ensure_ascii=False)
            # version — хэш содержимого: читатели перечитывают 650 КБ снапшота только при реальном изменении,
            # fetched_at — время загрузки: по нему читатели понимают, что worker жив
            meta = {
                **meta,
                "version": hashlib.sha256(p_snap.encode("utf-8")).hexdigest()[:16],
                "fetched_at": time.time(),
            }
            p_meta = json.dumps(meta, ensure_ascii=False)
            async with client.pipeline(transaction=True) as pipe:
                pipe.set(SNAPSHOT_KEY, p_snap, ex=ttl)
                pipe.set(SNAPSHOT_META_KEY, p_meta, ex=ttl)
                await pipe.execute()
            log.info("Срез расписания группы успешно сохранен в кэш Redis")
    except Exception as e:
        log.error("Ошибка сохранения снимка расписания в Redis: %s", e)


async def load_schedule_snapshot() -> tuple[dict | None, dict | None]:
    """
    Считывает сохраненный срез расписания и метаданные из постоянного кэша Redis.

    Предоставляет резервную копию расписания при недоступности внешнего сервиса КТМУ,
    обеспечивая бесперебойную отдачу данных клиентам.

    Возвращает кортеж (словарь_расписания, словарь_метаданных) или (None, None).
    """
    try:
        client = await init_redis()
        if client:
            snap_raw = await client.get(SNAPSHOT_KEY)
            meta_raw = await client.get(SNAPSHOT_META_KEY)
            if snap_raw and meta_raw:
                log.debug("Снимок расписания успешно загружен из Redis")
                return json.loads(snap_raw), json.loads(meta_raw)
    except Exception as e:
        log.error("Ошибка чтения снимка расписания из Redis: %s", e)
    return None, None


async def load_schedule_meta() -> dict | None:
    """
    Читает только метаданные снапшота расписания (версия, время загрузки).

    Дешёвая проверка для читателей: сам снапшот (~650 КБ) грузится, лишь если версия сменилась.

    Возвращает словарь метаданных или None, если снапшота нет или Redis недоступен.
    """
    try:
        client = await init_redis()
        raw = await client.get(SNAPSHOT_META_KEY) if client else None
        return json.loads(raw) if raw else None
    except Exception as e:
        log.error("Ошибка чтения метаданных снапшота расписания: %s", e)
        return None


async def request_schedule_refresh() -> bool:
    """
    Ставит флаг «обновить расписание сейчас» для фонового загрузчика в worker.

    TTL 5 минут — если worker лежит, флаг не копится вечно.

    Возвращает True, если флаг поставлен.
    """
    try:
        client = await init_redis()
        if not client:
            return False
        await client.set(SCHEDULE_REFRESH_REQUEST_KEY, "1", ex=300)
        log.debug("Запрошено внеочередное обновление расписания")
        return True
    except Exception as e:
        log.error("Ошибка постановки запроса обновления расписания: %s", e)
        return False


async def pop_schedule_refresh_request() -> bool:
    """
    Атомарно забирает флаг внеочередного обновления расписания (GETDEL).

    Возвращает True, если обновление было запрошено.
    """
    try:
        client = await init_redis()
        return bool(client and await client.getdel(SCHEDULE_REFRESH_REQUEST_KEY))
    except Exception as e:
        log.error("Ошибка чтения запроса обновления расписания: %s", e)
        return False


async def is_reminder_sent(rem_key: str) -> bool:
    """
    Проверяет, отправлялось ли уведомление с указанным ключом в течение суток.

    Используется шедулером утренних и предпарных напоминаний для предотвращения
    повторного спама студентам при перезапусках процессов.

    Возвращает True, если напоминание уже отослано, иначе False.
    """
    val = await cache_get(f"rem:sent:{rem_key}")
    return val == "1"


async def mark_reminder_sent(rem_key: str, ttl: int = 86400) -> None:
    """
    Фиксирует факт отправки напоминания в Redis с суточным временем жизни.

    Устанавливает флаг rem:sent:{key} с автоматическим удалением через 24 часа
    для корректного срабатывания на следующий день.

    Не возвращает значений; сохраняет ключ с TTL.
    """
    await cache_set(f"rem:sent:{rem_key}", "1", ttl=ttl)


async def get_topic_state_redis(key: str = "topic:main_msg_id") -> int | None:
    """
    Извлекает сохраненный Telegram ID главного сообщения топика из Redis.

    Позволяет боту и фоновым демонам обновлять единое закрепленное сообщение
    с расписанием через edit_message вместо засорения чата новыми сообщениями.

    Возвращает целочисленный ID сообщения или None при отсутствии записи.
    """
    val = await cache_get(key)
    return int(val) if val and val.isdigit() else None


async def set_topic_state_redis(val: int, key: str = "topic:main_msg_id") -> None:
    """
    Сохраняет Telegram ID главного сообщения топика без ограничения по сроку жизни.

    Фиксирует идентификатор корневого сообщения расписания для персистентного
    обновления между днями недели и перезапусками сервиса.

    Не возвращает значений; записывает значение в Redis без экспирации.
    """
    await cache_set(key, str(val), ttl=0)


async def register_message_for_cleanup(chat_id: int, msg_id: int, delay_sec: int = 900) -> None:
    """
    Регистрирует временное служебное сообщение в ZSET для отложенного удаления.

    Использует Sorted Set с таймстемпом удаления в качестве score, гарантируя
    чистку информационного шума из топиков без блокировки активного потока.

    Не возвращает значений; сохраняет запись в ключ TOPIC_CLEANUP_KEY.
    """
    try:
        client = await init_redis()
        if client:
            target_ts = time.time() + delay_sec
            await client.zadd(TOPIC_CLEANUP_KEY, {f"{chat_id}:{msg_id}": target_ts})
            log.debug("Сообщение %s:%s запланировано на удаление через %sс", chat_id, msg_id, delay_sec)
    except Exception as e:
        log.error("Ошибка регистрации сообщения на удаление: %s", e)


async def get_expired_messages_for_cleanup() -> list[tuple[int, int]]:
    """
    Извлекает и атомарно удаляет из ZSET все сообщения с истекшим сроком жизни.

    Вызывается фоновым сборщиком мусора, предотвращая накопление устаревших
    служебных сообщений в базе данных и чатах Telegram.

    Возвращает список кортежей (chat_id, message_id) для физического удаления.
    """
    results: list[tuple[int, int]] = []
    try:
        client = await init_redis()
        if client:
            now_ts = time.time()
            expired = await client.zrangebyscore(TOPIC_CLEANUP_KEY, min=0, max=now_ts)
            if expired:
                await client.zrem(TOPIC_CLEANUP_KEY, *expired)
                results = [(int(i.split(":")[0]), int(i.split(":")[1])) for i in expired]
    except Exception as e:
        log.error("Ошибка извлечения сообщений для очистки: %s", e)
    return results


@asynccontextmanager
async def redis_lock(key: str, ttl: int = 20) -> AsyncGenerator[bool, None]:
    """
    Асинхронный контекстный менеджер распределенного замка с Lua-освобождением.

    Генерирует уникальный UUID-токен владельца и освобождает замок через атомарный
    Lua-скрипт, исключая случайное снятие чужого замка при превышении TTL.

    Генерирует булево значение: True если замок захвачен, иначе False.
    """
    client = await init_redis()
    token = str(uuid.uuid4())
    acquired = False
    if client:
        try:
            acquired = bool(await client.set(key, token, nx=True, ex=ttl))
        except Exception as e:
            log.warning("Ошибка захвата лока Redis (%s): %s", key, e)
    try:
        yield acquired
    finally:
        if acquired and client:
            try:
                await client.eval(LUA_RELEASE_LOCK, 1, key, token)
            except Exception as e:
                log.debug("Ошибка освобождения лока Redis (%s): %s", key, e)


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
    retries = task_data.get("retries", 0) + 1
    task_data["retries"] = retries
    raw = json.dumps(task_data, ensure_ascii=False)
    await client.lrem(HW_PROCESSING_KEY, 1, raw)
    if retries <= max_retries:
        await client.rpush(HW_QUEUE_KEY, raw)
        log.warning("⚠️ Задача ДЗ %s на повтор (#%s/%s)", task_data.get("message_id"), retries, max_retries)
        return True
    await client.rpush(HW_DLQ_KEY, raw)
    log.error("❌ Задача ДЗ %s превысила %s попыток -> DLQ", task_data.get("message_id"), max_retries)
    return False
