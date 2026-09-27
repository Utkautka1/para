"""
Клиент и подключение к базе данных MongoDB.

Предоставляет синглтоны mongo_client и mongo_db.
Использует Motor (AsyncIOMotorClient) для высокопроизводительного
асинхронного взаимодействия со всеми коллекциями проекта.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import config
from core.logger import get_logger

log = get_logger("mongo")

mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None


async def init_mongo() -> AsyncIOMotorDatabase:
    """
    Проверяет соединение и настраивает уникальные индексы в MongoDB.

    serverSelectionTimeoutMS=5000 — быстрое падение при недоступности базы.
    """
    global mongo_client, mongo_db
    if mongo_db is not None:
        return mongo_db
    try:
        mongo_client = AsyncIOMotorClient(
            config.MONGO_URL,
            serverSelectionTimeoutMS=5000
        )
        await mongo_client.admin.command("ping")
        mongo_db = mongo_client[config.MONGO_DB_NAME]
        log.info(f"Подключение к MongoDB — OK (база: {config.MONGO_DB_NAME})")
        await mongo_db.users.create_index("tg_id", unique=True)
        await mongo_db.topic_state.create_index("key", unique=True)
        return mongo_db
    except Exception as e:
        log.error(f"Не удалось подключиться к MongoDB: {e}")
        raise


async def close_mongo() -> None:
    """Корректно закрывает клиентское соединение с сервером MongoDB."""
    global mongo_client, mongo_db
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        mongo_db = None
        log.info("Соединение с MongoDB успешно закрыто.")
