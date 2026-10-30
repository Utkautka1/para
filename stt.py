"""
Точка входа микросервиса распознавания речи (para-stt).

Единственный владелец GPU и модели faster-whisper: прогревает модель при старте
и разбирает Redis-очередь заданий от бота (services/stt_queue.py). Вынесен из бота,
чтобы образ бота не тащил CUDA (~5 ГБ), а перезапуск бота не перегружал модель в VRAM.
"""

import asyncio

import config
from core.logger import get_logger
from core.redis import close_redis, init_redis
from core.telemetry import setup_telemetry
from services.stt_queue import stt_worker_loop
from services.transcriber import transcriber_service

log = get_logger("stt_entrypoint")


async def _warmup_model() -> None:
    """
    Загружает модель в память GPU до первого задания.

    Ошибку прогрева не считаем фатальной: модель загрузится лениво на первом задании.

    Ничего не возвращает.
    """
    try:
        await transcriber_service.warmup()
        log.info("✅ STT модель (faster-whisper) прогрета и готова к работе")
    except Exception as e:
        log.warning("⚠️  Ошибка прогрева STT модели: %s", e)


async def main() -> None:
    """
    Инициализирует Redis и модель, затем бесконечно обрабатывает очередь распознавания.

    Ничего не возвращает.
    """
    log.info("=" * 60)
    log.info("ЗАПУСК Сервиса распознавания речи (para-stt)")
    log.info("  Модель: %s на %s (%s)", config.WHISPER_MODEL_NAME, config.WHISPER_DEVICE, config.WHISPER_COMPUTE_TYPE)
    log.info("=" * 60)
    setup_telemetry("para-stt")
    await init_redis()
    await _warmup_model()
    try:
        await stt_worker_loop(transcriber_service.transcribe_file)
    finally:
        await close_redis()
        log.info("Сервис para-stt корректно остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
