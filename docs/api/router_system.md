# Component Reference: `api/router/system.py`
> **File Path**: [`api/router/system.py`](../../api/router/system.py)
> **Subsystem**: `System Admin API`

## 1. Purpose
Роутер системной диагностики — GET /system/info, POST /system/cache/flush.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_collect_system_features`](#_collect_system_features) | Function | L28–L39 | `dict[str, bool]` | Формирует словарь активных возможностей и интеграций си... |
| [`get_system_info`](#get_system_info) | Function | L43–L62 | `SystemInfoResponse` | Возвращает диагностическую сводку о состоянии сервиса и... |
| [`_validate_flush_pattern`](#_validate_flush_pattern) | Function | L65–L72 | `None` | Проверяет безопасность маски для предотвращения сброса ... |
| [`flush_cache`](#flush_cache) | Function | L76–L84 | `CacheFlushResponse` | Выполняет принудительную очистку ключей Redis по безопа... |
| [`list_system_incidents`](#list_system_incidents) | Function | L88–L106 | `IncidentListResponse` | Возвращает журнал системных инцидентов и сетевых сбоев ... |
| [`trigger_system_backup`](#trigger_system_backup) | Function | L110–L116 | `BackupTriggerResponse` | Запускает процесс резервного копирования SQLite и Redis... |

---

## 3. Comprehensive Function Specifications

### `_collect_system_features`
```python
def _collect_system_features(redis_alive: bool) -> dict[str, bool]
```

- **Source Reference**: [`api/router/system.py#L28-L39`](../../api/router/system.py#L28-L39)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, bool]`

#### Overview & Architectural Purpose
Формирует словарь активных возможностей и интеграций системы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `redis_alive` | `bool` | Yes | Parameter `redis_alive` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.system import _collect_system_features

# Execute call
result = _collect_system_features(redis_alive=...)
```

---

### `get_system_info`
```python
async def get_system_info() -> SystemInfoResponse
```

- **Source Reference**: [`api/router/system.py#L43-L62`](../../api/router/system.py#L43-L62)
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

- **Source Reference**: [`api/router/system.py#L65-L72`](../../api/router/system.py#L65-L72)
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

- **Source Reference**: [`api/router/system.py#L76-L84`](../../api/router/system.py#L76-L84)
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

- **Source Reference**: [`api/router/system.py#L88-L106`](../../api/router/system.py#L88-L106)
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

- **Source Reference**: [`api/router/system.py#L110-L116`](../../api/router/system.py#L110-L116)
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
