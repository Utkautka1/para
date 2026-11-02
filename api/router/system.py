"""
Роутер системной диагностики — GET /system/info, POST /system/cache/flush.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.system import (
    BackupTriggerResponse,
    CacheFlushRequest,
    CacheFlushResponse,
    IncidentItem,
    IncidentListResponse,
    SystemInfoResponse,
)
from config import SAFE_CACHE_FLUSH_PREFIXES, TIMEZONE
from core.redis import init_redis
from core.redis_cache import cache_flush
from db.sqlite.repositories import IncidentRepository
from services.backup_manager import run_backup_pipeline
from services.schedule_parser import clear_resolved_day_cache

router = APIRouter(tags=["System"], prefix="/system", dependencies=[Depends(verify_api_or_tester)])


@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info() -> SystemInfoResponse:
    """
    Возвращает диагностическую сводку о состоянии сервиса и подсистем.

    Опрашивает статус соединения с Redis и формирует список активных модулей.
    Используется в панели администратора для оперативного мониторинга.

    Возвращает SystemInfoResponse с версией, таймзоной и фичами.
    """

    client = await init_redis()
    redis_alive = client is not None
    now_str = datetime.now(TIMEZONE).isoformat()
    feats = {
        "grpc": True,
        "swagger_ui": True,
        "telegram_miniapp": True,
        "redis_caching": redis_alive,
        "sqlite_database": True,
        "automated_backups": True,
        "yandex_docs": True,
        "deepseek_solver": True,
    }

    return SystemInfoResponse(
        service="para-api",
        version="3.0.0",
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
    """Выполняет принудительную очистку ключей Redis по безопасной маске (Admin only)."""
    _validate_flush_pattern(payload.pattern)
    if payload.pattern.startswith("sched:"):
        clear_resolved_day_cache()

    count = await cache_flush(pattern=payload.pattern)

    return CacheFlushResponse(status="ok", pattern=payload.pattern, deleted_keys=count)


@router.get("/incidents", response_model=IncidentListResponse, dependencies=[Depends(verify_admin_access)])
async def list_system_incidents(limit: int = 50, unresolved_only: bool = False) -> IncidentListResponse:
    """Возвращает журнал системных инцидентов и сетевых сбоев из SQLite (Admin only)."""

    records = await IncidentRepository.get_recent_incidents(limit=limit, unresolved_only=unresolved_only)
    items = [
        IncidentItem(
            id=r.id,
            incident_type=r.incident_type,
            severity=r.severity,
            title=r.title,
            description=r.description,
            trace_id=r.trace_id,
            resolved=r.resolved,
            created_at=r.created_at.isoformat(),
        )
        for r in records
    ]

    return IncidentListResponse(count=len(items), incidents=items)


@router.post("/backup", response_model=BackupTriggerResponse, dependencies=[Depends(verify_admin_access)])
async def trigger_system_backup() -> BackupTriggerResponse:
    """Запускает процесс резервного копирования SQLite и Redis (Admin only)."""

    ok = await run_backup_pipeline()
    if not ok:
        raise HTTPException(status_code=500, detail="Backup execution failed")
    return BackupTriggerResponse(status="ok", message="Automated backup completed and dispatched to admin")
