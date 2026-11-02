# Component Reference: `api/router/solver.py`
> **File Path**: [`api/router/solver.py`](../../api/router/solver.py)
> **Subsystem**: `HW Solver API`

## 1. Purpose
Роутер AI-решения задач — GET /solver/status, task/{msg_id}, POST /solver/solve, queue/clear.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_solver_queue_status`](#get_solver_queue_status) | Function | L36–L56 | `SolverQueueStatusResponse` | Возвращает текущую длину очередей решения домашних зада... |
| [`_decode_image_payload`](#_decode_image_payload) | Function | L59–L76 | `bytes \| None` | Декодирует строку Base64 в бинарные данные изображения. |
| [`_check_solver_rate_limit`](#_check_solver_rate_limit) | Function | L79–L95 | `None` | Ограничивает частоту вызовов DeepSeek API фиксированным... |
| [`solve_task_direct`](#solve_task_direct) | Function | L99–L118 | `DirectSolveResponse` | Выполняет прямое решение учебной задачи через нейросеть... |
| [`check_task_status`](#check_task_status) | Function | L122–L135 | `TaskStatusResponse` | Проверяет статус решения задачи по ID сообщения Telegra... |
| [`clear_solver_queue`](#clear_solver_queue) | Function | L139–L151 | `ClearQueueResponse` | Полностью очищает очереди нерешённых задач и DLQ в Redi... |

---

## 3. Comprehensive Function Specifications

### `get_solver_queue_status`
```python
async def get_solver_queue_status() -> SolverQueueStatusResponse
```

- **Source Reference**: [`api/router/solver.py#L36-L56`](../../api/router/solver.py#L36-L56)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `SolverQueueStatusResponse`

#### Overview & Architectural Purpose
Возвращает текущую длину очередей решения домашних заданий в Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.solver import get_solver_queue_status

# Execute call
result = await get_solver_queue_status()
```

---

### `_decode_image_payload`
```python
def _decode_image_payload(b64: str | None) -> bytes | None
```

- **Source Reference**: [`api/router/solver.py#L59-L76`](../../api/router/solver.py#L59-L76)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bytes | None`

#### Overview & Architectural Purpose
Декодирует строку Base64 в бинарные данные изображения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `b64` | `str | None` | Yes | Parameter `b64` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from api.router.solver import _decode_image_payload

# Execute call
result = _decode_image_payload(b64=...)
```

---

### `_check_solver_rate_limit`
```python
async def _check_solver_rate_limit(identity: str) -> None
```

- **Source Reference**: [`api/router/solver.py#L79-L95`](../../api/router/solver.py#L79-L95)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Ограничивает частоту вызовов DeepSeek API фиксированным окном в Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `identity` | `str` | Yes | Parameter `identity` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.solver import _check_solver_rate_limit

# Execute call
result = await _check_solver_rate_limit(identity=...)
```

---

### `solve_task_direct`
```python
async def solve_task_direct( payload: DirectSolveRequest, identity: str = Depends(verify_api_or_tester), ) -> DirectSolveResponse
```

- **Source Reference**: [`api/router/solver.py#L99-L118`](../../api/router/solver.py#L99-L118)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `DirectSolveResponse`

#### Overview & Architectural Purpose
Выполняет прямое решение учебной задачи через нейросеть DeepSeek.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `payload` | `DirectSolveRequest` | Yes | Parameter `payload` of type `DirectSolveRequest`. |
| `identity` | `str` | Yes | Parameter `identity` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.solver import solve_task_direct

# Execute call
result = await solve_task_direct(payload=..., identity=...)
```

---

### `check_task_status`
```python
async def check_task_status(message_id: int) -> TaskStatusResponse
```

- **Source Reference**: [`api/router/solver.py#L122-L135`](../../api/router/solver.py#L122-L135)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TaskStatusResponse`

#### Overview & Architectural Purpose
Проверяет статус решения задачи по ID сообщения Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message_id` | `int` | Yes | Parameter `message_id` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.solver import check_task_status

# Execute call
result = await check_task_status(message_id=...)
```

---

### `clear_solver_queue`
```python
async def clear_solver_queue() -> ClearQueueResponse
```

- **Source Reference**: [`api/router/solver.py#L139-L151`](../../api/router/solver.py#L139-L151)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `ClearQueueResponse`

#### Overview & Architectural Purpose
Полностью очищает очереди нерешённых задач и DLQ в Redis (Admin only).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.solver import clear_solver_queue

# Execute call
result = await clear_solver_queue()
```

---
