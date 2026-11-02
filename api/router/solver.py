"""
Роутер AI-решения задач — GET /solver/status, task/{msg_id}, POST /solver/solve, queue/clear.

Предоставляет прямое взаимодействие с DeepSeek API и очередями Redis.
"""

import base64

from fastapi import APIRouter, Depends, HTTPException

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.solver import (
    ClearQueueResponse,
    DirectSolveRequest,
    DirectSolveResponse,
    SolverQueueStatusResponse,
    TaskStatusResponse,
)
from config import (
    DEEPSEEK_MODEL_NAME,
    HW_DLQ_KEY,
    HW_PROCESSING_KEY,
    HW_QUEUE_KEY,
    SOLVER_RATE_LIMIT_PER_MINUTE,
    SOLVER_RATE_LIMIT_WINDOW_SECONDS,
)
from core.hw_queue import clear_hw_queue
from core.redis import init_redis
from core.redis_cache import allow_request, is_message_processed
from integrations.deepseek import solve_homework

router = APIRouter(tags=["AI Homework Solver"], prefix="/solver", dependencies=[Depends(verify_api_or_tester)])


@router.get("/status", response_model=SolverQueueStatusResponse)
async def get_solver_queue_status() -> SolverQueueStatusResponse:
    """
    Возвращает текущую длину очередей решения домашних заданий в Redis.

    Отслеживает состояние основной очереди, задач в обработке и DLQ.
    Служит индикатором здоровья фонового воркера нейросетевого решателя.

    Возвращает SolverQueueStatusResponse со статистикой очередей.
    """

    client = await init_redis()
    q_len = await client.llen(HW_QUEUE_KEY) if client else 0
    p_len = await client.llen(HW_PROCESSING_KEY) if client else 0
    d_len = await client.llen(HW_DLQ_KEY) if client else 0

    return SolverQueueStatusResponse(
        pending_tasks=q_len,
        processing_tasks=p_len,
        dlq_tasks=d_len,
        worker_online=client is not None,
    )


def _decode_image_payload(b64: str | None) -> bytes | None:
    """
    Декодирует строку Base64 в бинарные данные изображения.

    Удаляет возможный data URL префикс (например, 'data:image/png;base64,').
    Защищает от сбоев при повреждённом формате base64.

    Возвращает байты изображения или None при пустом входе/ошибке.
    """

    if not b64:
        return None

    try:
        clean = b64.split(",", 1)[1] if "," in b64 else b64
        return base64.b64decode(clean)
    except Exception:
        return None


async def _check_solver_rate_limit(identity: str) -> None:
    """
    Ограничивает частоту вызовов DeepSeek API фиксированным окном в Redis.

    Пропускает без ограничений запросы с ролью 'master_admin'.
    Недоступный Redis трактуется как превышение лимита — см. allow_request.

    Ничего не возвращает (выбрасывает HTTP 429 при превышении квоты).
    """
    if identity == "master_admin":
        return
    key = f"api_rate:solver:{identity}"
    if not await allow_request(key, SOLVER_RATE_LIMIT_PER_MINUTE, SOLVER_RATE_LIMIT_WINDOW_SECONDS):
        detail = (
            f"Too many solver requests (max {SOLVER_RATE_LIMIT_PER_MINUTE} per {SOLVER_RATE_LIMIT_WINDOW_SECONDS}s)"
        )
        raise HTTPException(status_code=429, detail=detail)


@router.post("/solve", response_model=DirectSolveResponse)
async def solve_task_direct(
    payload: DirectSolveRequest,
    identity: str = Depends(verify_api_or_tester),
) -> DirectSolveResponse:
    """
    Выполняет прямое решение учебной задачи через нейросеть DeepSeek.

    Поддерживает опциональное распознавание изображений задач в Base64.
    Применяет индивидуальный лимит частоты запросов для вызывающей стороны.

    Возвращает DirectSolveResponse со сгенерированным текстом решения.
    """

    await _check_solver_rate_limit(identity)
    img_bytes = _decode_image_payload(payload.image_base64)
    solution = await solve_homework(image_bytes=img_bytes, text_prompt=payload.prompt)
    if not solution or "Не удалось получить решение" in solution:
        raise HTTPException(status_code=502, detail="DeepSeek service failed to provide answer")

    return DirectSolveResponse(status="ok", solution_text=solution, model=DEEPSEEK_MODEL_NAME)


@router.get("/task/{message_id}", response_model=TaskStatusResponse)
async def check_task_status(message_id: int) -> TaskStatusResponse:
    """
    Проверяет статус решения задачи по ID сообщения Telegram.

    Сверяет идентификатор с множеством обработанных сообщений в Redis.
    Используется ботом для исключения дубликатов при повторной пересылке.

    Возвращает TaskStatusResponse с булевым статусом и человекочитаемой меткой.
    """

    done = await is_message_processed(message_id)
    lbl = "Выполнено (отправлено в топик решений)" if done else "В очереди или не поступало"

    return TaskStatusResponse(message_id=message_id, is_processed=done, status_label=lbl)


@router.post("/queue/clear", response_model=ClearQueueResponse, dependencies=[Depends(verify_admin_access)])
async def clear_solver_queue() -> ClearQueueResponse:
    """
    Полностью очищает очереди нерешённых задач и DLQ в Redis (Admin only).

    Сбрасывает ключи очереди после устранения сбоев воркера.
    Защищён зависимостью verify_admin_access.

    Возвращает ClearQueueResponse со статусом 'ok' и числом удаленных задач.
    """

    deleted = await clear_hw_queue()

    return ClearQueueResponse(status="ok", deleted_count=deleted)
