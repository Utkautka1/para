"""
Роутер AI-решения задач — GET /solver/status, task/{msg_id}, POST /solver/solve, queue/clear.

Предоставляет прямое взаимодействие с DeepSeek API и очередями Redis.
"""

import base64
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.solver import (
    ClearQueueResponse,
    DirectSolveRequest,
    DirectSolveResponse,
    SolverQueueStatusResponse,
    TaskStatusResponse,
)
from config import DEEPSEEK_MODEL_NAME, HW_DLQ_KEY, HW_PROCESSING_KEY, HW_QUEUE_KEY
from core.redis import init_redis
from core.redis_cache import clear_hw_queue, is_message_processed
from integrations.deepseek import solve_homework

router = APIRouter(tags=["AI Homework Solver"], prefix="/solver", dependencies=[Depends(verify_api_or_tester)])


@router.get("/status", response_model=SolverQueueStatusResponse)
async def get_solver_queue_status() -> SolverQueueStatusResponse:
    """Мониторинг очередей задач домашнего задания в Redis."""
    client = await init_redis()
    q_len = await client.llen(HW_QUEUE_KEY) if client else 0
    p_len = await client.llen(HW_PROCESSING_KEY) if client else 0
    d_len = await client.llen(HW_DLQ_KEY) if client else 0
    return SolverQueueStatusResponse(pending_tasks=q_len, processing_tasks=p_len, dlq_tasks=d_len, worker_online=client is not None)


def _decode_image_payload(b64: Optional[str]) -> Optional[bytes]:
    """Декодирует строку Base64 в бинарные данные изображения."""
    if not b64:
        return None
    try:
        clean = b64.split(",", 1)[1] if "," in b64 else b64
        return base64.b64decode(clean)
    except Exception:
        return None


@router.post("/solve", response_model=DirectSolveResponse)
async def solve_task_direct(payload: DirectSolveRequest) -> DirectSolveResponse:
    """Прямое решение задачи через DeepSeek API."""
    img_bytes = _decode_image_payload(payload.image_base64)
    solution = await solve_homework(image_bytes=img_bytes, text_prompt=payload.prompt)
    if not solution or "Не удалось получить решение" in solution:
        raise HTTPException(status_code=502, detail="DeepSeek service failed to provide answer")
    return DirectSolveResponse(status="ok", solution_text=solution, model=DEEPSEEK_MODEL_NAME)


@router.get("/task/{message_id}", response_model=TaskStatusResponse)
async def check_task_status(message_id: int) -> TaskStatusResponse:
    """Проверка статуса обработки задания по ID сообщения Telegram."""
    done = await is_message_processed(message_id)
    lbl = "Выполнено (отправлено в топик решений)" if done else "В очереди или не поступало"
    return TaskStatusResponse(message_id=message_id, is_processed=done, status_label=lbl)


@router.post("/queue/clear", response_model=ClearQueueResponse, dependencies=[Depends(verify_admin_access)])
async def clear_solver_queue() -> ClearQueueResponse:
    """Полная очистка очереди нерешённых задач в Redis (Admin only)."""
    deleted = await clear_hw_queue()
    return ClearQueueResponse(status="ok", deleted_count=deleted)
