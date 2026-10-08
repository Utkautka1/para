"""
Менеджер белого списка тестировщиков para-api.

Хранит идентификаторы пользователей в множестве Redis для O(1) проверки доступа
к Swagger UI и эндпоинтам API. Администратор и замстаросты включены по умолчанию.
"""


from config import ALLOWED_USER_ID, DEPUTY_USER_ID, REDIS_TESTERS_KEY
from core.logger import get_logger
from core.redis import get_redis

log = get_logger("testers_manager")

ADMIN_TESTERS: set[int] = {ALLOWED_USER_ID, DEPUTY_USER_ID}


async def add_tester(user_id: int) -> bool:
    """
    Добавляет Telegram ID пользователя в белый список тестеров API.

    Сохраняет ID в множестве Redis и логирует действие администратора.
    Возвращает True при успешном добавлении.
    """
    try:
        r = await get_redis()
        if not r:
            return False
        await r.sadd(REDIS_TESTERS_KEY, str(user_id))
        log.info(f"✅ Пользователь {user_id} добавлен в тестеры API")
        return True
    except Exception as e:
        log.error(f"❌ Ошибка добавления тестера {user_id}: {e}")
        return False


async def remove_tester(user_id: int) -> bool:
    """
    Удаляет Telegram ID пользователя из белого списка тестеров API.

    Удаляет ID из множества Redis, кроме постоянных администраторов.
    Возвращает True при успешном удалении.
    """
    if user_id in ADMIN_TESTERS:
        log.warning(f"⚠️ Попытка удалить администратора {user_id} из тестеров")
        return False
    try:
        r = await get_redis()
        if not r:
            return False
        await r.srem(REDIS_TESTERS_KEY, str(user_id))
        log.info(f"🗑️ Пользователь {user_id} удален из тестеров API")
        return True
    except Exception as e:
        log.error(f"❌ Ошибка удаления тестера {user_id}: {e}")
        return False


async def is_tester_allowed(user_id: int) -> bool:
    """
    Проверяет, разрешен ли пользователю доступ к тестированию Swagger UI.

    Сверяет сначала встроенный набор администраторов, затем множество Redis.
    Возвращает True, если доступ разрешен.
    """
    if user_id in ADMIN_TESTERS:
        return True
    try:
        r = await get_redis()
        if not r:
            return False
        return bool(await r.sismember(REDIS_TESTERS_KEY, str(user_id)))
    except Exception as e:
        log.error(f"❌ Ошибка проверки статуса тестера {user_id}: {e}")
        return False


async def get_all_testers() -> list[int]:
    """
    Возвращает полный список ID пользователей, имеющих доступ к тестированию.

    Объединяет встроенных администраторов и динамический список из Redis.
    Возвращает отсортированный список целочисленных ID.
    """
    testers: set[int] = set(ADMIN_TESTERS)
    try:
        r = await get_redis()
        if r:
            members = await r.smembers(REDIS_TESTERS_KEY)
            for m in members:
                item_str = m.decode() if isinstance(m, bytes) else str(m)
                if item_str.isdigit():
                    testers.add(int(item_str))
    except Exception as e:
        log.error(f"❌ Ошибка получения списка тестеров: {e}")
    return sorted(testers)
