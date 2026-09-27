"""
Фоновый сервис парсинга и синхронизации расписания КТМУ.

Отвечает за:
  1. Загрузку и парсинг расписания с API сайта КТМУ (каждые 60 сек)
  2. Парсинг изменений из DOCX на Яндекс.Диске
  3. Сохранение расписания в Redis и MongoDB
  4. Обновление главного интерактивного сообщения в топике Telegram
"""

import asyncio
from core.bot import bot
from core.logger import get_logger
from core.mongo import close_mongo, init_mongo
from core.redis import init_redis, redis_client
from services.topic_updater import topic_sync_loop

log = get_logger("parser_main")


async def shutdown_parser() -> None:
    """Освобождает сетевые ресурсы и соединения при остановке парсера."""
    log.info("Остановка para-parser: закрытие соединений...")
    if redis_client:
        await redis_client.aclose()
    from services.schedule_parser import _HTTP_CLIENT
    if _HTTP_CLIENT and not _HTTP_CLIENT.is_closed:
        await _HTTP_CLIENT.aclose()
    await close_mongo()
    await bot.session.close()
    log.info("Сервис para-parser успешно остановлен.")


async def main() -> None:
    """Точка входа фонового сервиса-парсера."""
    log.info("=" * 60)
    log.info("ЗАПУСК Фонового Парсера Расписания (para-parser)")
    log.info("=" * 60)
    await init_redis()
    await init_mongo()
    try:
        await topic_sync_loop()
    except asyncio.CancelledError:
        log.info("Получен сигнал завершения работы para-parser.")
    except Exception as e:
        log.error(f"❌ Критическая ошибка в работе para-parser: {e}")
    finally:
        await shutdown_parser()


if __name__ == "__main__":
    asyncio.run(main())
