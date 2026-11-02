# Component Reference: `core/hw_queue.py`
> **File Path**: [`core/hw_queue.py`](../../core/hw_queue.py)
> **Subsystem**: `Solver Queue Processing`

## 1. Purpose
Надёжная очередь заданий решателя ДЗ в Redis (паттерн Reliable Queue).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`push_hw_task`](#push_hw_task) | Function | L33–L52 | `bool` | Добавляет сериализованную задачу на решение ДЗ в конец ... |
| [`schedule_hw_task`](#schedule_hw_task) | Function | L67–L87 | `bool` | Откладывает задание ДЗ на delay_seconds — окно для уточ... |
| [`take_pending_hw_task`](#take_pending_hw_task) | Function | L90–L108 | `dict \| None` | Забирает ещё не отправленное в solver задание по id его... |
| [`promote_due_hw_tasks`](#promote_due_hw_tasks) | Function | L111–L126 | `int` | Отправляет в очередь solver задания, у которых закончил... |
| [`pop_hw_task`](#pop_hw_task) | Function | L129–L145 | `dict \| None` | Атомарно извлекает задачу из очереди и переносит в буфе... |
| [`ack_hw_task`](#ack_hw_task) | Function | L148–L164 | `None` | Подтверждает успешное завершение задачи ДЗ и удаляет её... |
| [`recover_stale_hw_tasks`](#recover_stale_hw_tasks) | Function | L167–L186 | `int` | Возвращает зависшие задачи из буфера processing обратно... |
| [`clear_hw_queue`](#clear_hw_queue) | Function | L189–L206 | `int` | Атомарно очищает основную и processing очереди задач ре... |
| [`nack_hw_task`](#nack_hw_task) | Function | L219–L243 | `bool` | Обрабатывает ошибку выполнения задачи ДЗ, отправляя её ... |

---

## 3. Comprehensive Function Specifications

### `push_hw_task`
```python
async def push_hw_task(task_data: dict) -> bool
```

- **Source Reference**: [`core/hw_queue.py#L33-L52`](../../core/hw_queue.py#L33-L52)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Добавляет сериализованную задачу на решение ДЗ в конец очереди Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `task_data` | `dict` | Yes | Parameter `task_data` of type `dict`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.hw_queue import push_hw_task

# Execute call
result = await push_hw_task(task_data=...)
```

---

### `schedule_hw_task`
```python
async def schedule_hw_task(task_data: dict, delay_seconds: int) -> bool
```

- **Source Reference**: [`core/hw_queue.py#L67-L87`](../../core/hw_queue.py#L67-L87)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Откладывает задание ДЗ на delay_seconds — окно для уточнений реплаем.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `task_data` | `dict` | Yes | Parameter `task_data` of type `dict`. |
| `delay_seconds` | `int` | Yes | Parameter `delay_seconds` of type `int`. |

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.hw_queue import schedule_hw_task

# Execute call
result = await schedule_hw_task(task_data=..., delay_seconds=...)
```

---

### `take_pending_hw_task`
```python
async def take_pending_hw_task(message_id: int) -> dict | None
```

- **Source Reference**: [`core/hw_queue.py#L90-L108`](../../core/hw_queue.py#L90-L108)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict | None`

#### Overview & Architectural Purpose
Забирает ещё не отправленное в solver задание по id его сообщения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message_id` | `int` | Yes | Parameter `message_id` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.hw_queue import take_pending_hw_task

# Execute call
result = await take_pending_hw_task(message_id=...)
```

---

### `promote_due_hw_tasks`
```python
async def promote_due_hw_tasks() -> int
```

- **Source Reference**: [`core/hw_queue.py#L111-L126`](../../core/hw_queue.py#L111-L126)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Отправляет в очередь solver задания, у которых закончилось окно уточнений.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.hw_queue import promote_due_hw_tasks

# Execute call
result = await promote_due_hw_tasks()
```

---

### `pop_hw_task`
```python
async def pop_hw_task(timeout: int = 2) -> dict | None
```

- **Source Reference**: [`core/hw_queue.py#L129-L145`](../../core/hw_queue.py#L129-L145)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict | None`

#### Overview & Architectural Purpose
Атомарно извлекает задачу из очереди и переносит в буфер processing.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `timeout` | `int` | Yes | Parameter `timeout` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.hw_queue import pop_hw_task

# Execute call
result = await pop_hw_task(timeout=...)
```

---

### `ack_hw_task`
```python
async def ack_hw_task(task_data: dict) -> None
```

- **Source Reference**: [`core/hw_queue.py#L148-L164`](../../core/hw_queue.py#L148-L164)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Подтверждает успешное завершение задачи ДЗ и удаляет её из processing очереди.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `task_data` | `dict` | Yes | Parameter `task_data` of type `dict`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.hw_queue import ack_hw_task

# Execute call
result = await ack_hw_task(task_data=...)
```

---

### `recover_stale_hw_tasks`
```python
async def recover_stale_hw_tasks() -> int
```

- **Source Reference**: [`core/hw_queue.py#L167-L186`](../../core/hw_queue.py#L167-L186)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Возвращает зависшие задачи из буфера processing обратно в основную очередь.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.hw_queue import recover_stale_hw_tasks

# Execute call
result = await recover_stale_hw_tasks()
```

---

### `clear_hw_queue`
```python
async def clear_hw_queue() -> int
```

- **Source Reference**: [`core/hw_queue.py#L189-L206`](../../core/hw_queue.py#L189-L206)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Атомарно очищает основную и processing очереди задач решения ДЗ.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.hw_queue import clear_hw_queue

# Execute call
result = await clear_hw_queue()
```

---

### `nack_hw_task`
```python
async def nack_hw_task(task_data: dict, max_retries: int = 3) -> bool
```

- **Source Reference**: [`core/hw_queue.py#L219-L243`](../../core/hw_queue.py#L219-L243)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Обрабатывает ошибку выполнения задачи ДЗ, отправляя её на повтор или в DLQ.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `task_data` | `dict` | Yes | Parameter `task_data` of type `dict`. |
| `max_retries` | `int` | Yes | Parameter `max_retries` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.hw_queue import nack_hw_task

# Execute call
result = await nack_hw_task(task_data=..., max_retries=...)
```

---
