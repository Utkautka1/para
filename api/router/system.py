"""
Роутер системной диагностики — GET /system/info, POST /system/cache/flush.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.system import (
    CacheFlushRequest,
    CacheFlushResponse,
    SystemInfoResponse,
)
from config import SAFE_CACHE_FLUSH_PREFIXES, TIMEZONE
from core.redis import init_redis
from core.redis_cache import cache_flush

router = APIRouter(tags=["System"], prefix="/system", dependencies=[Depends(verify_api_or_tester)])


@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info() -> SystemInfoResponse:
    """Сводная информация о состоянии сервиса и вспомогательных подсистем."""
    client = await init_redis()
    redis_alive = client is not None
    now_str = datetime.now(TIMEZONE).isoformat()
    feats = {
        "grpc": True,
        "swagger_ui": True,
        "telegram_miniapp": True,
        "redis_caching": redis_alive,
        "yandex_docs": True,
        "deepseek_solver": True,
    }
    return SystemInfoResponse(
        service="para-api",
        version="2.0.0",
        timezone=str(TIMEZONE),
        server_time=now_str,
        redis_alive=redis_alive,
        features=feats,
    )


def _validate_flush_pattern(pattern: str) -> None:
    """Проверяет безопасность маски для предотвращения сброса служебных ключей Redis."""
    clean = pattern.strip()
    if clean in ("*", "", "*:*") or any(clean.startswith(d) for d in ("api:", "hw:tasks:", "user:")):
        raise HTTPException(status_code=400, detail="Unsafe pattern: flushing critical system keys is forbidden")
    if not any(clean.startswith(p) for p in SAFE_CACHE_FLUSH_PREFIXES):
        raise HTTPException(status_code=400, detail="Pattern must start with safe prefix (sched, att, teachers, exams)")


@router.post("/cache/flush", response_model=CacheFlushResponse, dependencies=[Depends(verify_admin_access)])
async def flush_cache(payload: CacheFlushRequest) -> CacheFlushResponse:
    """Принудительная очистка ключей Redis по безопасной маске (Admin only)."""
    _validate_flush_pattern(payload.pattern)
    if payload.pattern.startswith("sched:"):
        from services.schedule_parser import clear_resolved_day_cache
        clear_resolved_day_cache()
    count = await cache_flush(pattern=payload.pattern)
    return CacheFlushResponse(status="ok", pattern=payload.pattern, deleted_keys=count)

