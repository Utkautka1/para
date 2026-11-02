# Component Reference: `services/backup_manager.py`
> **File Path**: [`services/backup_manager.py`](../../services/backup_manager.py)
> **Subsystem**: `Automated Backup Engine`

## 1. Purpose
Менеджер автоматизированного резервного копирования базы данных SQLite и снимков Redis.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`backup_sqlite_online`](#backup_sqlite_online) | Function | L29–L40 | `bool` | Создает консистентный снимок SQLite без блокировки чита... |
| [`_trigger_redis_save`](#_trigger_redis_save) | Function | L43–L51 | `None` | Инициирует фоновый снимок Redis в RDB файл при наличии ... |
| [`_create_tar_archive`](#_create_tar_archive) | Function | L54–L63 | `bool` | Упаковывает файлы промежуточной директории в .tar.gz ар... |
| [`_rotate_old_backups`](#_rotate_old_backups) | Function | L66–L80 | `int` | Удаляет архивы бэкапов старше заданного количества дней... |
| [`_send_backup_to_telegram`](#_send_backup_to_telegram) | Function | L83–L95 | `bool` | Отправляет сжатый архив бэкапа администратору в Telegra... |
| [`run_backup_pipeline`](#run_backup_pipeline) | Function | L98–L118 | `bool` | Оркестрирует полный процесс создания бэкапа SQLite и Re... |

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
Создает консистентный снимок SQLite без блокировки читателей и писателей.

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
Инициирует фоновый снимок Redis в RDB файл при наличии подключения.

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
Упаковывает файлы промежуточной директории в .tar.gz архив.

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
Удаляет архивы бэкапов старше заданного количества дней.

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
Отправляет сжатый архив бэкапа администратору в Telegram.

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
Оркестрирует полный процесс создания бэкапа SQLite и Redis, ротацию и отправку.

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
