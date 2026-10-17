# Component Reference: `core/api_client.py`
> **File Path**: [`core/api_client.py`](../../core/api_client.py)  
> **Subsystem**: `Internal RPC Client`  
> **Architecture Layer**: `Enterprise Microservice Subsystem`  
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`  
> **Persistence Backend**: `Redis 7 Persistent Store`  
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `core/api_client.py` module implements core operational logic for the `Internal RPC Client` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

### Component Architecture & Data Flow
```mermaid
graph LR
    Inbound[Inbound Request] --> Logic[Domain Service Logic]
    Logic --> Redis[(Redis 7 State Store)]
    Logic --> Outbound[Outbound Event Dispatch]
```

---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Core Invariant |
| :--- | :--- | :--- | :--- | :--- |
| [`_get_client`](#_get_client) | Function | L43–L54 | `httpx.AsyncClient` | Executes core domain logic for `_get_client`. |
| [`_get_grpc_channel`](#_get_grpc_channel) | Function | L57–L70 | `grpc.aio.Channel` | Executes core domain logic for `_get_grpc_channel`. |
| [`close_api_client`](#close_api_client) | Function | L73–L81 | `None` | Executes core domain logic for `close_api_client`. |
| [`_api_get`](#_api_get) | Function | L84–L97 | `dict[str, Any]` | Executes core domain logic for `_api_get`. |
| [`_fetch_day_schedule_grpc`](#_fetch_day_schedule_grpc) | Function | L103–L112 | `dict[str, Any]` | Executes core domain logic for `_fetch_day_schedule_grp... |
| [`fetch_day_schedule`](#fetch_day_schedule) | Function | L115–L124 | `dict[str, Any]` | Executes core domain logic for `fetch_day_schedule`. |
| [`_fetch_week_schedule_grpc`](#_fetch_week_schedule_grpc) | Function | L127–L136 | `dict[str, Any]` | Executes core domain logic for `_fetch_week_schedule_gr... |
| [`fetch_week_schedule`](#fetch_week_schedule) | Function | L139–L148 | `dict[str, Any]` | Executes core domain logic for `fetch_week_schedule`. |
| [`_fetch_exams_grpc`](#_fetch_exams_grpc) | Function | L151–L157 | `dict[str, Any]` | Executes core domain logic for `_fetch_exams_grpc`. |
| [`fetch_exams`](#fetch_exams) | Function | L160–L166 | `dict[str, Any]` | Executes core domain logic for `fetch_exams`. |
| [`_fetch_teachers_grpc`](#_fetch_teachers_grpc) | Function | L169–L175 | `dict[str, Any]` | Executes core domain logic for `_fetch_teachers_grpc`. |
| [`fetch_teachers`](#fetch_teachers) | Function | L178–L184 | `dict[str, Any]` | Executes core domain logic for `fetch_teachers`. |
| [`get_api_schedule_for_date`](#get_api_schedule_for_date) | Function | L187–L190 | `list[Lesson]` | Retrieves and resolves domain data for `get_api_schedul... |
| [`get_api_week_schedule`](#get_api_week_schedule) | Function | L193–L201 | `list[tuple[date, list[Lesson]]]` | Retrieves and resolves domain data for `get_api_week_sc... |
| [`get_api_exams`](#get_api_exams) | Function | L204–L207 | `list[ExamItem]` | Retrieves and resolves domain data for `get_api_exams`. |
| [`get_api_teachers`](#get_api_teachers) | Function | L210–L213 | `dict[str, Any]` | Retrieves and resolves domain data for `get_api_teacher... |

---

## 3. Comprehensive Function Specifications

### `_get_client`
```python
def _get_client() -> httpx.AsyncClient
```

- **Source Reference**: [`core/api_client.py#L43-L54`](../../core/api_client.py#L43-L54)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `httpx.AsyncClient`

#### Overview & Architectural Purpose
Executes core domain logic for `_get_client`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import _get_client

# Execute call
result = _get_client()
```

---

### `_get_grpc_channel`
```python
def _get_grpc_channel() -> grpc.aio.Channel
```

- **Source Reference**: [`core/api_client.py#L57-L70`](../../core/api_client.py#L57-L70)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `grpc.aio.Channel`

#### Overview & Architectural Purpose
Executes core domain logic for `_get_grpc_channel`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import _get_grpc_channel

# Execute call
result = _get_grpc_channel()
```

---

### `close_api_client`
```python
async def close_api_client() -> None
```

- **Source Reference**: [`core/api_client.py#L73-L81`](../../core/api_client.py#L73-L81)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `close_api_client`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import close_api_client

# Execute call
result = await close_api_client()
```

---

### `_api_get`
```python
async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L84-L97`](../../core/api_client.py#L84-L97)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `_api_get`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `path` | `str` | Yes | Parameter `path` of type `str`. |
| `params` | `dict[str, Any] | None` | Yes | Parameter `params` of type `dict[str, Any] | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from core.api_client import _api_get

# Execute call
result = await _api_get(path=..., params=...)
```

---

### `_fetch_day_schedule_grpc`
```python
async def _fetch_day_schedule_grpc(target_date: date | None, force_refresh: bool) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L103-L112`](../../core/api_client.py#L103-L112)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `_fetch_day_schedule_grpc`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date | None` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import _fetch_day_schedule_grpc

# Execute call
result = await _fetch_day_schedule_grpc(target_date=..., force_refresh=...)
```

---

### `fetch_day_schedule`
```python
async def fetch_day_schedule(target_date: date | None = None, force_refresh: bool = False) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L115-L124`](../../core/api_client.py#L115-L124)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `fetch_day_schedule`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date | None` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.api_client import fetch_day_schedule

# Execute call
result = await fetch_day_schedule(target_date=..., force_refresh=...)
```

---

### `_fetch_week_schedule_grpc`
```python
async def _fetch_week_schedule_grpc(monday: date | None, force_refresh: bool) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L127-L136`](../../core/api_client.py#L127-L136)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `_fetch_week_schedule_grpc`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `monday` | `date | None` | Yes | Parameter `monday` of type `date | None`. |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import _fetch_week_schedule_grpc

# Execute call
result = await _fetch_week_schedule_grpc(monday=..., force_refresh=...)
```

---

### `fetch_week_schedule`
```python
async def fetch_week_schedule(monday: date | None = None, force_refresh: bool = False) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L139-L148`](../../core/api_client.py#L139-L148)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `fetch_week_schedule`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `monday` | `date | None` | Yes | Parameter `monday` of type `date | None`. |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.api_client import fetch_week_schedule

# Execute call
result = await fetch_week_schedule(monday=..., force_refresh=...)
```

---

### `_fetch_exams_grpc`
```python
async def _fetch_exams_grpc(force_refresh: bool) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L151-L157`](../../core/api_client.py#L151-L157)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `_fetch_exams_grpc`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import _fetch_exams_grpc

# Execute call
result = await _fetch_exams_grpc(force_refresh=...)
```

---

### `fetch_exams`
```python
async def fetch_exams(force_refresh: bool = False) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L160-L166`](../../core/api_client.py#L160-L166)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `fetch_exams`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.api_client import fetch_exams

# Execute call
result = await fetch_exams(force_refresh=...)
```

---

### `_fetch_teachers_grpc`
```python
async def _fetch_teachers_grpc(force_refresh: bool) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L169-L175`](../../core/api_client.py#L169-L175)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `_fetch_teachers_grpc`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import _fetch_teachers_grpc

# Execute call
result = await _fetch_teachers_grpc(force_refresh=...)
```

---

### `fetch_teachers`
```python
async def fetch_teachers(force_refresh: bool = False) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L178-L184`](../../core/api_client.py#L178-L184)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `fetch_teachers`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.api_client import fetch_teachers

# Execute call
result = await fetch_teachers(force_refresh=...)
```

---

### `get_api_schedule_for_date`
```python
async def get_api_schedule_for_date(target_date: date | None = None, force_refresh: bool = False) -> list[Lesson]
```

- **Source Reference**: [`core/api_client.py#L187-L190`](../../core/api_client.py#L187-L190)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[Lesson]`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_api_schedule_for_date`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date | None` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import get_api_schedule_for_date

# Execute call
result = await get_api_schedule_for_date(target_date=..., force_refresh=...)
```

---

### `get_api_week_schedule`
```python
async def get_api_week_schedule(monday: date | None = None, force_refresh: bool = False) -> list[tuple[date, list[Lesson]]]
```

- **Source Reference**: [`core/api_client.py#L193-L201`](../../core/api_client.py#L193-L201)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[tuple[date, list[Lesson]]]`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_api_week_schedule`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `monday` | `date | None` | Yes | Parameter `monday` of type `date | None`. |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import get_api_week_schedule

# Execute call
result = await get_api_week_schedule(monday=..., force_refresh=...)
```

---

### `get_api_exams`
```python
async def get_api_exams(force_refresh: bool = False) -> list[ExamItem]
```

- **Source Reference**: [`core/api_client.py#L204-L207`](../../core/api_client.py#L204-L207)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[ExamItem]`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_api_exams`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import get_api_exams

# Execute call
result = await get_api_exams(force_refresh=...)
```

---

### `get_api_teachers`
```python
async def get_api_teachers(force_refresh: bool = False) -> dict[str, Any]
```

- **Source Reference**: [`core/api_client.py#L210-L213`](../../core/api_client.py#L210-L213)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_api_teachers`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.api_client import get_api_teachers

# Execute call
result = await get_api_teachers(force_refresh=...)
```

---
