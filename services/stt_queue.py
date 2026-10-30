"""
Очередь распознавания речи между ботом и сервисом stt.

Модель Whisper живёт только в контейнере stt (GPU, CUDA, ~5 ГБ образа), а бот
остаётся лёгким. Обмен через Redis:
  1. бот кладёт аудио в общий tmpfs-том STT_AUDIO_DIR и задание в STT_QUEUE_KEY
  2. stt забирает задание (BLPOP), распознаёт и пишет ответ в stt:result:<job_id>
  3. бот ждёт ответа в своём ключе с тем же TRANSCRIBE_TIMEOUT, что и раньше
Файл удаляет бот (он его создал), stt его только читает.
"""

import asyncio
import json
import os
import time
import uuid

from config import (
    STT_AUDIO_DIR,
    STT_BLPOP_SECONDS,
    STT_QUEUE_KEY,
    STT_RESULT_KEY_PREFIX,
    STT_RESULT_TTL_SECONDS,
    TRANSCRIBE_TIMEOUT,
)
from core.logger import get_logger
from core.redis import get_redis

log = get_logger("stt_queue")


class SttUnavailableError(RuntimeError):
    """Сервис stt не ответил вовремя или вернул ошибку распознавания."""


def resolve_audio_dir() -> str:
    """
    Возвращает общий с сервисом stt каталог для аудио, создавая его при необходимости.

    В контейнерах это tmpfs-том (права 0700, uid бота и stt совпадают);
    локально и в тестах — обычный каталог.
    """
    os.makedirs(STT_AUDIO_DIR, mode=0o700, exist_ok=True)
    return STT_AUDIO_DIR


async def _wait_result(redis, result_key: str, deadline: float) -> dict:
    """
    Ждёт ответ stt короткими BLPOP до дедлайна.

    Возвращает распарсенный ответ или выбрасывает SttUnavailableError по таймауту.
    """
    while time.monotonic() < deadline:
        item = await redis.blpop([result_key], timeout=STT_BLPOP_SECONDS)
        if item:
            return json.loads(item[1])
    raise SttUnavailableError("Сервис распознавания не ответил вовремя")


async def transcribe_via_stt(audio_path: str) -> str:
    """
    Отправляет файл на распознавание в сервис stt и ждёт текст.

    Возвращает распознанный текст; при таймауте или ошибке stt — SttUnavailableError.
    """
    redis = await get_redis()
    if not redis:
        raise SttUnavailableError("Redis недоступен — очередь распознавания не работает")
    job_id = uuid.uuid4().hex
    await redis.rpush(STT_QUEUE_KEY, json.dumps({"job_id": job_id, "path": os.path.abspath(audio_path)}))
    log.debug("Задание STT %s отправлено: %s", job_id[:8], os.path.basename(audio_path))
    result = await _wait_result(redis, f"{STT_RESULT_KEY_PREFIX}{job_id}", time.monotonic() + TRANSCRIBE_TIMEOUT)
    if "error" in result:
        raise SttUnavailableError(result["error"])
    return result["text"]


async def _process_job(redis, raw_job: str, transcribe) -> None:
    """
    Распознаёт одно задание и публикует результат (текст или ошибку) в ключ бота.

    Ничего не возвращает: любые сбои распознавания уходят боту как {"error": ...}.
    """
    job = json.loads(raw_job)
    result_key = f"{STT_RESULT_KEY_PREFIX}{job['job_id']}"
    try:
        payload = {"text": await transcribe(job["path"])}
    except Exception as e:
        log.error("❌ Ошибка распознавания задания %s: %s", job["job_id"][:8], e)
        payload = {"error": f"{type(e).__name__}: {e}"}
    async with redis.pipeline(transaction=True) as pipe:
        pipe.rpush(result_key, json.dumps(payload, ensure_ascii=False))
        pipe.expire(result_key, STT_RESULT_TTL_SECONDS)
        await pipe.execute()


async def stt_worker_loop(transcribe) -> None:
    """
    Бесконечный цикл сервиса stt: забирает задания из очереди и распознаёт по одному.

    transcribe — корутина (путь -> текст), обычно transcriber_service.transcribe_file.
    Задания обрабатываются последовательно: GPU один, семафор внутри transcriber.

    Никогда не завершается штатно при нормальной работе сервиса.
    """
    log.info("Запущен обработчик очереди распознавания речи (%s)", STT_QUEUE_KEY)
    while True:
        try:
            redis = await get_redis()
            item = await redis.blpop([STT_QUEUE_KEY], timeout=STT_BLPOP_SECONDS) if redis else None
            if item:
                await _process_job(redis, item[1], transcribe)
            elif not redis:
                await asyncio.sleep(STT_BLPOP_SECONDS)
        except Exception as e:
            log.error("❌ Ошибка в цикле stt_worker_loop: %s", e)
            await asyncio.sleep(STT_BLPOP_SECONDS)
