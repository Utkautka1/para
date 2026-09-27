"""
Репозиторий операций с коллекциями MongoDB.

Инкапсулирует CRUD-логику для пользователей, состояния топиков
и истории поздравлений старосты.
"""

from typing import Any, Dict, List, Optional
from core.logger import get_logger
from core.mongo import init_mongo

log = get_logger("mongo_crud")


async def get_state_doc(key: str) -> Optional[Dict[str, Any]]:
    """Получает документ состояния из коллекции topic_state по ключу."""
    try:
        db = await init_mongo()
        return await db.topic_state.find_one({"key": key})
    except Exception as e:
        log.error(f"Ошибка чтения topic_state ({key}): {e}")
        return None


async def save_state_doc(key: str, data: Dict[str, Any]) -> bool:
    """Атомарно обновляет или создает документ состояния по ключу (upsert)."""
    try:
        db = await init_mongo()
        doc = {"$set": {**data, "key": key}}
        await db.topic_state.update_one({"key": key}, doc, upsert=True)
        return True
    except Exception as e:
        log.error(f"Ошибка записи topic_state ({key}): {e}")
        return False


async def get_starosta_history() -> List[int]:
    """Получает список использованных индексов поздравлений старосты."""
    doc = await get_state_doc("starosta_history")
    return doc.get("used_indices", []) if doc else []


async def save_starosta_history(used_indices: List[int]) -> bool:
    """Сохраняет список использованных индексов поздравлений старосты."""
    return await save_state_doc("starosta_history", {"used_indices": used_indices})
