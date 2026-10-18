"""
Модуль инициализации и подключения к Redis.

Предоставляет синглтон клиента Redis для асинхронного кэширования.
Управляет пулом сетевых соединений ConnectionPool и жизненным циклом сокетов.
"""

from redis.asyncio import ConnectionPool, Redis

from config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from core.logger import get_logger

log = get_logger("redis")
redis_client: Redis | None = None
_pool: ConnectionPool | None = None


def get_redis_pool() -> ConnectionPool:
    """
    Возвращает синглтон пула сетевых соединений к Redis с лимитом сокетов.

    Конфигурирует тайм-ауты, keepalive сокетов и фоновый healthcheck для
    предотвращения зависаний ввода-вывода и утечек дескрипторов соединений.

    Возвращает инициализированный экземпляр redis.asyncio.ConnectionPool.
    """
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
    Инициализирует асинхронное подключение к серверу Redis через пул.

    Проверяет доступность узла ping-запросом и логирует статус, исключая падение
    приложения при временной недоступности базы данных в момент старта.

    Возвращает подключенный клиент Redis или None при возникновении сетевой ошибки.
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
    Предоставляет активный синглтон клиента Redis с ленивой инициализацией.

    Позволяет безопасно получать соединение из обработчиков и сервисов без
    риска обращения к неинициализированной глобальной переменной.

    Возвращает активный экземпляр клиента Redis или None при отсутствии связи.
    """
    if redis_client is None:
        await init_redis()
    return redis_client


async def close_redis() -> None:
    """
    Корректно закрывает активный клиент и освобождает пул сокетов Redis.

    Предотвращает утечки дескрипторов соединений (file descriptors) и предупреждения
    asyncio при graceful shutdown процесса сервиса.

    Не возвращает значений; сбрасывает ссылки на глобальные объекты в None.
    """
    global redis_client, _pool
    if redis_client:
        await redis_client.aclose()
        redis_client = None
    if _pool:
        await _pool.disconnect()
        _pool = None
    log.info("Соединение и пул соединений с Redis успешно закрыты")
