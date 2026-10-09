# Module Specification: `api/router/solver.py`
> **Path**: [`api/router/solver.py`](file:///home/u/Рабочий стол/para/api/router/solver.py)  
> **Subsystem**: `HW Solver API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер AI-решения задач — GET /solver/status, task/{msg_id}, POST /solver/solve, queue/clear. Предоставляет прямое взаимодействие с DeepSeek API и очередями Redis.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_solver_queue_status`](#get_solver_queue_status) | Function | L35–L41 | `SolverQueueStatusResponse` | Мониторинг очередей задач домашнего задания в Redis. |
| [`_decode_image_payload`](#_decode_image_payload) | Function | L44–L52 | `bytes | None` | Декодирует строку Base64 в бинарные данные изображения. |
| [`_check_solver_rate_limit`](#_check_solver_rate_limit) | Function | L55–L67 | `None` | Ограничивает частоту вызовов DeepSeek API по лимитам из conf |
| [`solve_task_direct`](#solve_task_direct) | Function | L71–L81 | `DirectSolveResponse` | Прямое решение задачи через DeepSeek API с rate limiting. |
| [`check_task_status`](#check_task_status) | Function | L86–L90 | `TaskStatusResponse` | Проверка статуса обработки задания по ID сообщения Telegram. |
| [`clear_solver_queue`](#clear_solver_queue) | Function | L94–L97 | `ClearQueueResponse` | Полная очистка очереди нерешённых задач в Redis (Admin only) |

---

## 3. Exhaustive Function Specifications

### `get_solver_queue_status`
- **Signature**: `async def get_solver_queue_status() -> SolverQueueStatusResponse`
- **Source Reference**: [api/router/solver.py#L35-L41](file:///home/u/Рабочий стол/para/api/router/solver.py#L35-L41)
- **Async**: `Yes`
- **Return Type**: `SolverQueueStatusResponse`

#### Purpose & Architectural Intent
Мониторинг очередей задач домашнего задания в Redis.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `client = await init_redis()`
2. `q_len = await client.llen(HW_QUEUE_KEY) if client else 0`
3. `p_len = await client.llen(HW_PROCESSING_KEY) if client else 0`
4. `d_len = await client.llen(HW_DLQ_KEY) if client else 0`
5. `return SolverQueueStatusResponse(pending_tasks=q_len, processing_tasks=p_len, dlq_tas`

---

### `_decode_image_payload`
- **Signature**: `def _decode_image_payload(b64: str | None) -> bytes | None`
- **Source Reference**: [api/router/solver.py#L44-L52](file:///home/u/Рабочий стол/para/api/router/solver.py#L44-L52)
- **Async**: `No`
- **Return Type**: `bytes | None`

#### Purpose & Architectural Intent
Декодирует строку Base64 в бинарные данные изображения.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `b64` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not b64:`
2. `try:`

---

### `_check_solver_rate_limit`
- **Signature**: `async def _check_solver_rate_limit(identity: str) -> None`
- **Source Reference**: [api/router/solver.py#L55-L67](file:///home/u/Рабочий стол/para/api/router/solver.py#L55-L67)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Ограничивает частоту вызовов DeepSeek API по лимитам из config.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `identity` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if identity == "master_admin":`
2. `client = await init_redis()`
3. `if client:`

---

### `solve_task_direct`
- **Signature**: `async def solve_task_direct( payload: DirectSolveRequest, identity: str = Depends(verify_api_or_tester) ) -> DirectSolveResponse`
- **Source Reference**: [api/router/solver.py#L71-L81](file:///home/u/Рабочий стол/para/api/router/solver.py#L71-L81)
- **Async**: `Yes`
- **Return Type**: `DirectSolveResponse`

#### Purpose & Architectural Intent
Прямое решение задачи через DeepSeek API с rate limiting.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `payload` | `DirectSolveRequest` | Input parameter |
| `identity` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `await _check_solver_rate_limit(identity)`
2. `img_bytes = _decode_image_payload(payload.image_base64)`
3. `solution = await solve_homework(image_bytes=img_bytes, text_prompt=payload.prompt)`
4. `if not solution or "Не удалось получить решение" in solution:`
5. `return DirectSolveResponse(status="ok", solution_text=solution, model=DEEPSEEK_MODEL_`

---

### `check_task_status`
- **Signature**: `async def check_task_status(message_id: int) -> TaskStatusResponse`
- **Source Reference**: [api/router/solver.py#L86-L90](file:///home/u/Рабочий стол/para/api/router/solver.py#L86-L90)
- **Async**: `Yes`
- **Return Type**: `TaskStatusResponse`

#### Purpose & Architectural Intent
Проверка статуса обработки задания по ID сообщения Telegram.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `done = await is_message_processed(message_id)`
2. `lbl = "Выполнено (отправлено в топик решений)" if done else "В очереди или не поступа`
3. `return TaskStatusResponse(message_id=message_id, is_processed=done, status_label=lbl)`

---

### `clear_solver_queue`
- **Signature**: `async def clear_solver_queue() -> ClearQueueResponse`
- **Source Reference**: [api/router/solver.py#L94-L97](file:///home/u/Рабочий стол/para/api/router/solver.py#L94-L97)
- **Async**: `Yes`
- **Return Type**: `ClearQueueResponse`

#### Purpose & Architectural Intent
Полная очистка очереди нерешённых задач в Redis (Admin only).

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `deleted = await clear_hw_queue()`
2. `return ClearQueueResponse(status="ok", deleted_count=deleted)`

---
