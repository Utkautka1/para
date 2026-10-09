"""
Роутер системной диагностики — GET /system/info, POST /system/cache/flush.
"""

from datetime import datetime

from fastapi import APIRouter, Depends

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.system import (
    CacheFlushRequest,
    CacheFlushResponse,
    SystemInfoResponse,
)
from config import TIMEZONE
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


@router.post("/cache/flush", response_model=CacheFlushResponse, dependencies=[Depends(verify_admin_access)])
async def flush_cache(payload: CacheFlushRequest) -> CacheFlushResponse:
    """Принудительная очистка ключей Redis по маске (Admin only)."""
    count = await cache_flush(pattern=payload.pattern)
    return CacheFlushResponse(status="ok", pattern=payload.pattern, deleted_keys=count)
