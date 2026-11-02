# Component Reference: `core/database.py`
> **File Path**: [`core/database.py`](../../core/database.py)
> **Subsystem**: `Relational SQLite Engine`

## 1. Purpose
Модуль управления асинхронным подключением к реляционной БД SQLite (SQLAlchemy 2.0).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_set_sqlite_pragmas`](#_set_sqlite_pragmas) | Function | L29–L36 | `None` | Устанавливает оптимальные PRAGMA параметры для SQLite п... |
| [`get_database_engine`](#get_database_engine) | Function | L39–L52 | `AsyncEngine` | Возвращает синглтон асинхронного движка SQLAlchemy для ... |
| [`get_session_factory`](#get_session_factory) | Function | L55–L66 | `async_sessionmaker[AsyncSession]` | Возвращает фабрику асинхронных сессий SQLAlchemy. |
| [`get_async_session`](#get_async_session) | Function | L70–L79 | `AsyncGenerator[AsyncSession, None]` | Контекстный менеджер для безопасной работы с асинхронно... |
| [`_migrate_subscribers_from_json`](#_migrate_subscribers_from_json) | Function | L82–L96 | `None` | Выполняет плавную однократную миграцию подписчиков из s... |
| [`_migrate_attendance_snapshot_columns`](#_migrate_attendance_snapshot_columns) | Function | L99–L108 | `None` | Добавляет недостающие столбцы посещаемости (late_hours,... |
| [`init_db`](#init_db) | Function | L111–L122 | `None` | Создает все необходимые таблицы в SQLite и проводит ста... |

---

## 3. Comprehensive Function Specifications

### `_set_sqlite_pragmas`
```python
def _set_sqlite_pragmas(dbapi_connection: Any, _connection_record: Any) -> None
```

- **Source Reference**: [`core/database.py#L29-L36`](../../core/database.py#L29-L36)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Устанавливает оптимальные PRAGMA параметры для SQLite при каждом новом подключении.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `dbapi_connection` | `Any` | Yes | Parameter `dbapi_connection` of type `Any`. |
| `_connection_record` | `Any` | Yes | Parameter `_connection_record` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.database import _set_sqlite_pragmas

# Execute call
result = _set_sqlite_pragmas(dbapi_connection=..., _connection_record=...)
```

---

### `get_database_engine`
```python
def get_database_engine() -> AsyncEngine
```

- **Source Reference**: [`core/database.py#L39-L52`](../../core/database.py#L39-L52)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `AsyncEngine`

#### Overview & Architectural Purpose
Возвращает синглтон асинхронного движка SQLAlchemy для SQLite.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.database import get_database_engine

# Execute call
result = get_database_engine()
```

---

### `get_session_factory`
```python
def get_session_factory() -> async_sessionmaker[AsyncSession]
```

- **Source Reference**: [`core/database.py#L55-L66`](../../core/database.py#L55-L66)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `async_sessionmaker[AsyncSession]`

#### Overview & Architectural Purpose
Возвращает фабрику асинхронных сессий SQLAlchemy.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.database import get_session_factory

# Execute call
result = get_session_factory()
```

---

### `get_async_session`
```python
async def get_async_session() -> AsyncGenerator[AsyncSession, None]
```

- **Source Reference**: [`core/database.py#L70-L79`](../../core/database.py#L70-L79)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AsyncGenerator[AsyncSession, None]`

#### Overview & Architectural Purpose
Контекстный менеджер для безопасной работы с асинхронной сессией БД.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from core.database import get_async_session

# Execute call
result = await get_async_session()
```

---

### `_migrate_subscribers_from_json`
```python
async def _migrate_subscribers_from_json(session: AsyncSession) -> None
```

- **Source Reference**: [`core/database.py#L82-L96`](../../core/database.py#L82-L96)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Выполняет плавную однократную миграцию подписчиков из subscribers.json в SQLite.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AsyncSession` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.database import _migrate_subscribers_from_json

# Execute call
result = await _migrate_subscribers_from_json(session=...)
```

---

### `_migrate_attendance_snapshot_columns`
```python
def _migrate_attendance_snapshot_columns(conn: Any) -> None
```

- **Source Reference**: [`core/database.py#L99-L108`](../../core/database.py#L99-L108)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет недостающие столбцы посещаемости (late_hours, excused_hours, unexcused_hours).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `conn` | `Any` | Yes | Parameter `conn` of type `Any`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.database import _migrate_attendance_snapshot_columns

# Execute call
result = _migrate_attendance_snapshot_columns(conn=...)
```

---

### `init_db`
```python
async def init_db() -> None
```

- **Source Reference**: [`core/database.py#L111-L122`](../../core/database.py#L111-L122)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Создает все необходимые таблицы в SQLite и проводит стартовую миграцию.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.database import init_db

# Execute call
result = await init_db()
```

---
