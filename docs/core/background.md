# Component Reference: `core/background.py`
> **File Path**: [`core/background.py`](../../core/background.py)
> **Subsystem**: `Background Tasks`

## 1. Purpose
Запуск фоновых задач «выстрелил и забыл» без потери задач и ошибок.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_on_done`](#_on_done) | Function | L27–L33 | `None` | Снимает ссылку на завершённую задачу и логирует её искл... |
| [`spawn`](#spawn) | Function | L36–L45 | `asyncio.Task[Any]` | Запускает корутину фоновой задачей и держит на неё ссыл... |
| [`drain_background`](#drain_background) | Function | L48–L63 | `None` | Ждёт завершения фоновых задач при остановке сервиса, ос... |

---

## 3. Comprehensive Function Specifications

### `_on_done`
```python
def _on_done(task: asyncio.Task[Any]) -> None
```

- **Source Reference**: [`core/background.py#L27-L33`](../../core/background.py#L27-L33)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Снимает ссылку на завершённую задачу и логирует её исключение.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `task` | `asyncio.Task[Any]` | Yes | Parameter `task` of type `asyncio.Task[Any]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.background import _on_done

# Execute call
result = _on_done(task=...)
```

---

### `spawn`
```python
def spawn(coro: Coroutine[Any, Any, Any], name: str | None = None) -> asyncio.Task[Any]
```

- **Source Reference**: [`core/background.py#L36-L45`](../../core/background.py#L36-L45)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `asyncio.Task[Any]`

#### Overview & Architectural Purpose
Запускает корутину фоновой задачей и держит на неё ссылку до завершения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `coro` | `Coroutine[Any, Any, Any]` | Yes | Parameter `coro` of type `Coroutine[Any, Any, Any]`. |
| `name` | `str | None` | Yes | Parameter `name` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.background import spawn

# Execute call
result = spawn(coro=..., name=...)
```

---

### `drain_background`
```python
async def drain_background(timeout: float = 10.0) -> None
```

- **Source Reference**: [`core/background.py#L48-L63`](../../core/background.py#L48-L63)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Ждёт завершения фоновых задач при остановке сервиса, остальные отменяет.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `timeout` | `float` | Yes | Parameter `timeout` of type `float`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.background import drain_background

# Execute call
result = await drain_background(timeout=...)
```

---
