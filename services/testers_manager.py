"""
Менеджер белого списка тестировщиков и персональных API-ключей para-api.

Хранит ID тестеров в Redis и генерирует уникальные API-ключи для каждого тестера
для персонального аудита запросов в логах системы.
"""

import secrets

from config import (
    ALLOWED_USER_ID,
    API_TESTER_KEY_PREFIX,
    DEPUTY_USER_ID,
    REDIS_TESTER_KEY_TO_UID_PREFIX,
    REDIS_TESTER_UID_TO_KEY_PREFIX,
    REDIS_TESTERS_KEY,
)
from core.logger import get_logger
from core.redis import get_redis

log = get_logger("testers_manager")

ADMIN_TESTERS: set[int] = {ALLOWED_USER_ID, DEPUTY_USER_ID}


async def generate_or_get_tester_key(user_id: int) -> str | None:
    """Генерирует или возвращает существующий персональный API-ключ тестера."""
    r = await get_redis()
    if not r:
        return None
    existing = await r.get(f"{REDIS_TESTER_UID_TO_KEY_PREFIX}{user_id}")
    if existing:
        return existing.decode() if isinstance(existing, bytes) else str(existing)
    new_key = f"{API_TESTER_KEY_PREFIX}{secrets.token_hex(16)}"
    async with r.pipeline(transaction=True) as pipe:
        pipe.set(f"{REDIS_TESTER_UID_TO_KEY_PREFIX}{user_id}", new_key)
        pipe.set(f"{REDIS_TESTER_KEY_TO_UID_PREFIX}{new_key}", str(user_id))
        await pipe.execute()
    log.info(f"🔑 Сгенерирован персональный API-ключ для тестера {user_id}")
    return new_key


async def get_tester_by_key(api_key: str) -> int | None:
    """Возвращает Telegram ID тестера по переданному персональному API-ключу."""
    if not api_key or not api_key.startswith(API_TESTER_KEY_PREFIX):
        return None
    r = await get_redis()
    if not r:
        return None
    uid_raw = await r.get(f"{REDIS_TESTER_KEY_TO_UID_PREFIX}{api_key}")
    if not uid_raw:
        return None
    uid_str = uid_raw.decode() if isinstance(uid_raw, bytes) else str(uid_raw)
    return int(uid_str) if uid_str.isdigit() else None


async def add_tester(user_id: int) -> bool:
    """Добавляет ID в белый список и сразу генерирует персональный API-ключ."""
    r = await get_redis()
    if not r:
        return False
    await r.sadd(REDIS_TESTERS_KEY, str(user_id))
    await generate_or_get_tester_key(user_id)
    log.info(f"✅ Пользователь {user_id} добавлен в тестеры API с персональным ключом")
    return True


async def remove_tester(user_id: int) -> bool:
    """Удаляет тестера и аннулирует его персональный API-ключ."""
    if user_id in ADMIN_TESTERS:
        log.warning(f"⚠️ Попытка удалить администратора {user_id} из тестеров")
        return False
    r = await get_redis()
    if not r:
        return False
    key = await r.get(f"{REDIS_TESTER_UID_TO_KEY_PREFIX}{user_id}")
    if key:
        key_str = key.decode() if isinstance(key, bytes) else str(key)
        await r.delete(f"{REDIS_TESTER_KEY_TO_UID_PREFIX}{key_str}", f"{REDIS_TESTER_UID_TO_KEY_PREFIX}{user_id}")
    await r.srem(REDIS_TESTERS_KEY, str(user_id))
    log.info(f"🗑️ Пользователь {user_id} и его API-ключ удалены")
    return True


async def is_tester_allowed(user_id: int) -> bool:
    """Проверяет доступ пользователя к тестированию Swagger UI."""
    if user_id in ADMIN_TESTERS:
        return True
    r = await get_redis()
    if not r:
        return False
    return bool(await r.sismember(REDIS_TESTERS_KEY, str(user_id)))


async def get_all_testers() -> list[int]:
    """Возвращает отсортированный список всех авторизованных тестеров."""
    testers: set[int] = set(ADMIN_TESTERS)
    r = await get_redis()
    if r:
        for m in await r.smembers(REDIS_TESTERS_KEY):
            s = m.decode() if isinstance(m, bytes) else str(m)
            if s.isdigit():
                testers.add(int(s))
    return sorted(testers)
