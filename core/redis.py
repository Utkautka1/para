"""
Модуль инициализации и подключения к Redis.

Предоставляет синглтон клиента Redis для асинхронного кэширования.
"""


from redis.asyncio import ConnectionPool, Redis

from config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from core.logger import get_logger

log = get_logger("redis")
redis_client: Redis | None = None
_pool: ConnectionPool | None = None


def get_redis_pool() -> ConnectionPool:
    """Создает или возвращает синглтон пула соединений к Redis с лимитом сокетов."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
            max_connections=20,
            socket_keepalive=True,
            health_check_interval=30,
            socket_timeout=5.0,
        )
    return _pool


async def init_redis() -> Redis | None:
    """
    Инициализирует подключение к Redis через пул соединений.

    :return: Объект Redis или None при сбое сети
    """
    global redis_client
    if redis_client is None:
        try:
            pool = get_redis_pool()
            redis_client = Redis(connection_pool=pool)
            await redis_client.ping()
            log.info(f"Успешное подключение к Redis ({REDIS_HOST}:{REDIS_PORT}) через ConnectionPool")
        except Exception as e:
            log.error(f"Ошибка подключения к Redis ({REDIS_HOST}:{REDIS_PORT}): {e}")
            redis_client = None
    return redis_client


async def get_redis() -> Redis | None:
    """
    Возвращает синглтон клиента Redis, подключаясь при необходимости.

    Позволяет безопасно получать активное соединение из любых модулей
    без риска захвата неинициализированной ссылки во время импорта.
    """
    if redis_client is None:
        await init_redis()
    return redis_client


async def close_redis() -> None:
    """Освобождает клиент и пул соединений с Redis при завершении сервиса."""
    global redis_client, _pool
    if redis_client:
        await redis_client.aclose()
        redis_client = None
    if _pool:
        await _pool.disconnect()
        _pool = None
    log.info("Соединение и пул соединений с Redis успешно закрыты")
