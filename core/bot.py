"""
Инициализация aiogram Bot и Dispatcher.

Создает синглтоны bot и dp с HTML форматированием
и отключенным предпросмотром ссылок (link preview) по умолчанию.
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from config import BOT_TOKEN, PROXY_URL
from core.logger import get_logger

log = get_logger("bot_core")


def create_bot_session() -> AiohttpSession:
    """
    Создает сессию сетевого взаимодействия aiohttp для Telegram Bot API.

    Ограничивает пул соединений до 50 сокетов и при наличии PROXY_URL настраивает
    проксирование запросов через SOCKS5 для обхода блокировок.

    Возвращает сконфигурированный экземпляр aiogram.client.session.aiohttp.AiohttpSession.
    """
    if PROXY_URL:
        log.info("SOCKS5 Прокси подключен для Telegram API (limit=50, timeout=45s)")
        return AiohttpSession(proxy=PROXY_URL, limit=50, timeout=45.0)
    return AiohttpSession(limit=50, timeout=45.0)


def create_fsm_storage():
    """
    Создает постоянное хранилище состояний FSM диалогов на базе Redis.

    Обеспечивает сохранение пользовательского контекста между рестартами контейнера
    с защитным fallback на локальный MemoryStorage при сетевой недоступности Redis.

    Возвращает экземпляр BaseStorage (RedisStorage или fallback MemoryStorage).
    """
    try:
        from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
        from redis.asyncio import Redis

        from core.redis import get_redis_pool

        pool = get_redis_pool()
        r = Redis(connection_pool=pool)
        key_builder = DefaultKeyBuilder(prefix="fsm")
        log.info("FSM Storage: подключено персистентное хранилище RedisStorage")
        return RedisStorage(redis=r, key_builder=key_builder)
    except Exception as e:
        log.warning(f"⚠️ Не удалось подключить RedisStorage ({e}), используется MemoryStorage")
        from aiogram.fsm.storage.memory import MemoryStorage

        return MemoryStorage()


session = create_bot_session()

bot = Bot(
    token=BOT_TOKEN,
    session=session,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=True,
    ),
)

dp = Dispatcher(storage=create_fsm_storage())
