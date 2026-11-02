# Component Reference: `api/router/system.py`
> **File Path**: [`api/router/system.py`](../../api/router/system.py)
> **Subsystem**: `System Admin API`

## 1. Purpose
Роутер системной диагностики — GET /system/info, POST /system/cache/flush.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_system_info`](#get_system_info) | Function | L29–L60 | `SystemInfoResponse` | Возвращает диагностическую сводку о состоянии сервиса и... |
| [`_validate_flush_pattern`](#_validate_flush_pattern) | Function | L63–L70 | `None` | Проверяет безопасность маски для предотвращения сброса ... |
| [`flush_cache`](#flush_cache) | Function | L74–L82 | `CacheFlushResponse` | Выполняет принудительную очистку ключей Redis по безопа... |
| [`list_system_incidents`](#list_system_incidents) | Function | L86–L104 | `IncidentListResponse` | Возвращает журнал системных инцидентов и сетевых сбоев ... |
| [`trigger_system_backup`](#trigger_system_backup) | Function | L108–L114 | `BackupTriggerResponse` | Запускает процесс резервного копирования SQLite и Redis... |

---

## 3. Comprehensive Function Specifications

### `get_system_info`
```python
async def get_system_info() -> SystemInfoResponse
```

- **Source Reference**: [`api/router/system.py#L29-L60`](../../api/router/system.py#L29-L60)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `SystemInfoResponse`

#### Overview & Architectural Purpose
Возвращает диагностическую сводку о состоянии сервиса и подсистем.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.system import get_system_info

# Execute call
result = await get_system_info()
```

---

### `_validate_flush_pattern`
```python
def _validate_flush_pattern(pattern: str) -> None
```

- **Source Reference**: [`api/router/system.py#L63-L70`](../../api/router/system.py#L63-L70)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Проверяет безопасность маски для предотвращения сброса служебных ключей Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `pattern` | `str` | Yes | Parameter `pattern` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.system import _validate_flush_pattern

# Execute call
result = _validate_flush_pattern(pattern=...)
```

---

### `flush_cache`
```python
async def flush_cache(payload: CacheFlushRequest) -> CacheFlushResponse
```

- **Source Reference**: [`api/router/system.py#L74-L82`](../../api/router/system.py#L74-L82)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `CacheFlushResponse`

#### Overview & Architectural Purpose
Выполняет принудительную очистку ключей Redis по безопасной маске (Admin only).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `payload` | `CacheFlushRequest` | Yes | Parameter `payload` of type `CacheFlushRequest`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.system import flush_cache

# Execute call
result = await flush_cache(payload=...)
```

---

### `list_system_incidents`
```python
async def list_system_incidents(limit: int = 50, unresolved_only: bool = False) -> IncidentListResponse
```

- **Source Reference**: [`api/router/system.py#L86-L104`](../../api/router/system.py#L86-L104)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `IncidentListResponse`

#### Overview & Architectural Purpose
Возвращает журнал системных инцидентов и сетевых сбоев из SQLite (Admin only).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `limit` | `int` | Yes | Maximum number of records or results to retrieve. |
| `unresolved_only` | `bool` | Yes | Parameter `unresolved_only` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.system import list_system_incidents

# Execute call
result = await list_system_incidents(limit=..., unresolved_only=...)
```

---

### `trigger_system_backup`
```python
async def trigger_system_backup() -> BackupTriggerResponse
```

- **Source Reference**: [`api/router/system.py#L108-L114`](../../api/router/system.py#L108-L114)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `BackupTriggerResponse`

#### Overview & Architectural Purpose
Запускает процесс резервного копирования SQLite и Redis (Admin only).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.system import trigger_system_backup

# Execute call
result = await trigger_system_backup()
```

---
