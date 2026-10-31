# Component Reference: `services/backup_manager.py`
> **File Path**: [`services/backup_manager.py`](../../services/backup_manager.py)
> **Subsystem**: `Automated Backup Engine`
> **Architecture Layer**: `Enterprise Microservice Subsystem`
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`
> **Persistence Backend**: `Redis 7 Persistent Store`
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `services/backup_manager.py` module implements core operational logic for the `Automated Backup Engine` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

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
| [`backup_sqlite_online`](#backup_sqlite_online) | Function | L29–L40 | `bool` | Executes core domain logic for `backup_sqlite_online`. |
| [`_trigger_redis_save`](#_trigger_redis_save) | Function | L43–L51 | `None` | Executes core domain logic for `_trigger_redis_save`. |
| [`_create_tar_archive`](#_create_tar_archive) | Function | L54–L63 | `bool` | Executes core domain logic for `_create_tar_archive`. |
| [`_rotate_old_backups`](#_rotate_old_backups) | Function | L66–L80 | `int` | Executes core domain logic for `_rotate_old_backups`. |
| [`_send_backup_to_telegram`](#_send_backup_to_telegram) | Function | L83–L95 | `bool` | Executes core domain logic for `_send_backup_to_telegra... |
| [`run_backup_pipeline`](#run_backup_pipeline) | Function | L98–L118 | `bool` | Executes core domain logic for `run_backup_pipeline`. |

---

## 3. Comprehensive Function Specifications

### `backup_sqlite_online`
```python
def backup_sqlite_online(dest_path: str) -> bool
```

- **Source Reference**: [`services/backup_manager.py#L29-L40`](../../services/backup_manager.py#L29-L40)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `backup_sqlite_online`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `dest_path` | `str` | Yes | Parameter `dest_path` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.backup_manager import backup_sqlite_online

# Execute call
result = backup_sqlite_online(dest_path=...)
```

---

### `_trigger_redis_save`
```python
async def _trigger_redis_save() -> None
```

- **Source Reference**: [`services/backup_manager.py#L43-L51`](../../services/backup_manager.py#L43-L51)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_trigger_redis_save`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.backup_manager import _trigger_redis_save

# Execute call
result = await _trigger_redis_save()
```

---

### `_create_tar_archive`
```python
def _create_tar_archive(staging_dir: str, archive_path: str) -> bool
```

- **Source Reference**: [`services/backup_manager.py#L54-L63`](../../services/backup_manager.py#L54-L63)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_create_tar_archive`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `staging_dir` | `str` | Yes | Parameter `staging_dir` of type `str`. |
| `archive_path` | `str` | Yes | Parameter `archive_path` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.backup_manager import _create_tar_archive

# Execute call
result = _create_tar_archive(staging_dir=..., archive_path=...)
```

---

### `_rotate_old_backups`
```python
def _rotate_old_backups(backup_dir: str, retention_days: int) -> int
```

- **Source Reference**: [`services/backup_manager.py#L66-L80`](../../services/backup_manager.py#L66-L80)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Executes core domain logic for `_rotate_old_backups`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `backup_dir` | `str` | Yes | Parameter `backup_dir` of type `str`. |
| `retention_days` | `int` | Yes | Parameter `retention_days` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.backup_manager import _rotate_old_backups

# Execute call
result = _rotate_old_backups(backup_dir=..., retention_days=...)
```

---

### `_send_backup_to_telegram`
```python
async def _send_backup_to_telegram(archive_path: str) -> bool
```

- **Source Reference**: [`services/backup_manager.py#L83-L95`](../../services/backup_manager.py#L83-L95)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_send_backup_to_telegram`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `archive_path` | `str` | Yes | Parameter `archive_path` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.backup_manager import _send_backup_to_telegram

# Execute call
result = await _send_backup_to_telegram(archive_path=...)
```

---

### `run_backup_pipeline`
```python
async def run_backup_pipeline() -> bool
```

- **Source Reference**: [`services/backup_manager.py#L98-L118`](../../services/backup_manager.py#L98-L118)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `run_backup_pipeline`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.backup_manager import run_backup_pipeline

# Execute call
result = await run_backup_pipeline()
```

---
