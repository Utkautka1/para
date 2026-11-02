# Component Reference: `services/attendance_manager.py`
> **File Path**: [`services/attendance_manager.py`](../../services/attendance_manager.py)
> **Subsystem**: `Attendance Operations`
> **Architecture Layer**: `Domain Business Service`
> **Concurrency Model**: `AsyncIO Event Loop + Redis Distributed Locks`
> **Persistence Backend**: `Redis L2 Append-Only + WOPI Cloud Spreadsheets`
> **Service Level Objective**: `Sub-10ms Cache Writes / 3s WOPI Roundtrip`

## 1. Purpose
Менеджер интерактивной сессии отметки посещаемости.

### Component Architecture & Data Flow
```mermaid
graph TD
    A[Admin Telegram Client] -->|Mark Event| B[bot.handlers.admin.attendance]
    B -->|record_mark| C[services.attendance_manager]
    C -->|Optimistic UI| D[(Redis L2 Cache)]
    C -->|Topic Sync| E[Telegram Supergroup Topic]
    C -->|Async WOPI Commit| F[OnlyOffice Document Server]
```

---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`save_session_to_redis`](#save_session_to_redis) | Function | L60–L80 | `None` | Сериализует и сохраняет состояние активной сессии опрос... |
| [`get_active_session`](#get_active_session) | Function | L83–L105 | `AttendanceSession \| None` | Считывает и десериализует активную сессию опроса из Red... |
| [`clear_session`](#clear_session) | Function | L108–L119 | `None` | Удаляет активную сессию опроса посещаемости из Redis. |
| [`_fetch_students_from_wopi`](#_fetch_students_from_wopi) | Function | L122–L138 | `list[tuple[int, str]]` | Скачивает таблицу через WOPI протокол и считывает списо... |
| [`_read_cached_students`](#_read_cached_students) | Function | L141–L157 | `list[tuple[int, str]] \| None` | Считывает список студентов из кэша Redis. |
| [`fetch_target_students`](#fetch_target_students) | Function | L160–L179 | `list[tuple[int, str]]` | Возвращает список студентов с кэшированием в Redis для ... |
| [`_assert_no_initiator_conflict`](#_assert_no_initiator_conflict) | Function | L182–L190 | `None` | Проверяет отсутствие конфликта параллельных инициаторов... |
| [`create_attendance_session`](#create_attendance_session) | Function | L193–L217 | `AttendanceSession` | Инициализирует новую сессию опроса посещаемости и фикси... |
| [`record_student_mark`](#record_student_mark) | Function | L220–L237 | `AttendanceSession \| None` | Записывает отметку для текущего студента и сдвигает ука... |
| [`step_back`](#step_back) | Function | L240–L257 | `AttendanceSession \| None` | Возвращает опрос на один шаг назад для исправления ошиб... |
| [`mark_all_remaining_present`](#mark_all_remaining_present) | Function | L260–L280 | `AttendanceSession \| None` | Массово проставляет статус 'П' (присутствует) всем оста... |
| [`ensure_summary_headers`](#ensure_summary_headers) | Function | L283–L300 | `None` | Гарантирует сохранение текстовых заголовков и кодов в с... |
| [`apply_marks_to_sheet`](#apply_marks_to_sheet) | Function | L303–L312 | `None` | Записывает все собранные отметки сессии в колонку даты ... |
| [`_prepare_updated_workbook`](#_prepare_updated_workbook) | Function | L315–L335 | `Any` | Скачивает книгу и проставляет отметки сессии в колонку ... |
| [`_try_commit_once`](#_try_commit_once) | Function | L338–L360 | `bool` | Выполняет одну итерацию сохранения: скачать -> применит... |
| [`_post_commit_sync`](#_post_commit_sync) | Function | L363–L380 | `None` | Выполняет контрольную сверку реестра с Яндекс Документа... |
| [`_execute_commit_attempts`](#_execute_commit_attempts) | Function | L383–L401 | `bool` | Выполняет цикл повторных попыток выгрузки журнала с экс... |
| [`commit_session_to_table`](#commit_session_to_table) | Function | L404–L422 | `bool` | Выгружает все зафиксированные отметки сессии в Яндекс Д... |
| [`calculate_summary_stats`](#calculate_summary_stats) | Function | L425–L439 | `dict[str, int]` | Подсчитывает итоговые количества отметок по категориям ... |

---

## 3. Comprehensive Function Specifications

## Class Model: `AttendanceSession`

Модель активной сессии отметки посещаемости пары.

### `save_session_to_redis`
```python
async def save_session_to_redis(session: AttendanceSession) -> None
```

- **Source Reference**: [`services/attendance_manager.py#L60-L80`](../../services/attendance_manager.py#L60-L80)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сериализует и сохраняет состояние активной сессии опроса в Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Serializes entity state into JSON using Pydantic V2 engine.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import save_session_to_redis

# Execute call
result = await save_session_to_redis(session=...)
```

---

### `get_active_session`
```python
async def get_active_session() -> AttendanceSession | None
```

- **Source Reference**: [`services/attendance_manager.py#L83-L105`](../../services/attendance_manager.py#L83-L105)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AttendanceSession | None`

#### Overview & Architectural Purpose
Считывает и десериализует активную сессию опроса из Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_manager import get_active_session

# Execute call
result = await get_active_session()
```

---

### `clear_session`
```python
async def clear_session() -> None
```

- **Source Reference**: [`services/attendance_manager.py#L108-L119`](../../services/attendance_manager.py#L108-L119)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет активную сессию опроса посещаемости из Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import clear_session

# Execute call
result = await clear_session()
```

---

### `_fetch_students_from_wopi`
```python
async def _fetch_students_from_wopi(target_date: date) -> list[tuple[int, str]]
```

- **Source Reference**: [`services/attendance_manager.py#L122-L138`](../../services/attendance_manager.py#L122-L138)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[tuple[int, str]]`

#### Overview & Architectural Purpose
Скачивает таблицу через WOPI протокол и считывает список студентов.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from services.attendance_manager import _fetch_students_from_wopi

# Execute call
result = await _fetch_students_from_wopi(target_date=...)
```

---

### `_read_cached_students`
```python
async def _read_cached_students(client) -> list[tuple[int, str]] | None
```

- **Source Reference**: [`services/attendance_manager.py#L141-L157`](../../services/attendance_manager.py#L141-L157)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[tuple[int, str]] | None`

#### Overview & Architectural Purpose
Считывает список студентов из кэша Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `client` | `Any` | Yes | Active asynchronous Redis client or HTTP connection pool instance. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_manager import _read_cached_students

# Execute call
result = await _read_cached_students(client=...)
```

---

### `fetch_target_students`
```python
async def fetch_target_students(target_date: date) -> list[tuple[int, str]]
```

- **Source Reference**: [`services/attendance_manager.py#L160-L179`](../../services/attendance_manager.py#L160-L179)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[tuple[int, str]]`

#### Overview & Architectural Purpose
Возвращает список студентов с кэшированием в Redis для мгновенного отклика.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import fetch_target_students

# Execute call
result = await fetch_target_students(target_date=...)
```

---

### `_assert_no_initiator_conflict`
```python
async def _assert_no_initiator_conflict(initiator_id: int) -> None
```

- **Source Reference**: [`services/attendance_manager.py#L182-L190`](../../services/attendance_manager.py#L182-L190)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Проверяет отсутствие конфликта параллельных инициаторов опроса.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `initiator_id` | `int` | Yes | Parameter `initiator_id` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from services.attendance_manager import _assert_no_initiator_conflict

# Execute call
result = await _assert_no_initiator_conflict(initiator_id=...)
```

---

### `create_attendance_session`
```python
async def create_attendance_session( target_date: date, lesson_num: int, lesson_title: str, initiator_id: int ) -> AttendanceSession
```

- **Source Reference**: [`services/attendance_manager.py#L193-L217`](../../services/attendance_manager.py#L193-L217)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AttendanceSession`

#### Overview & Architectural Purpose
Инициализирует новую сессию опроса посещаемости и фиксирует её в Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `lesson_title` | `str` | Yes | Parameter `lesson_title` of type `str`. |
| `initiator_id` | `int` | Yes | Parameter `initiator_id` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import create_attendance_session

# Execute call
result = await create_attendance_session(target_date=..., lesson_num=..., lesson_title=...)
```

---

### `record_student_mark`
```python
async def record_student_mark(mark: str) -> AttendanceSession | None
```

- **Source Reference**: [`services/attendance_manager.py#L220-L237`](../../services/attendance_manager.py#L220-L237)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AttendanceSession | None`

#### Overview & Architectural Purpose
Записывает отметку для текущего студента и сдвигает указатель на следующего.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `mark` | `str` | Yes | Attendance evaluation symbol assigned to the student. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import record_student_mark

# Execute call
result = await record_student_mark(mark=...)
```

---

### `step_back`
```python
async def step_back() -> AttendanceSession | None
```

- **Source Reference**: [`services/attendance_manager.py#L240-L257`](../../services/attendance_manager.py#L240-L257)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AttendanceSession | None`

#### Overview & Architectural Purpose
Возвращает опрос на один шаг назад для исправления ошибочной отметки.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import step_back

# Execute call
result = await step_back()
```

---

### `mark_all_remaining_present`
```python
async def mark_all_remaining_present() -> AttendanceSession | None
```

- **Source Reference**: [`services/attendance_manager.py#L260-L280`](../../services/attendance_manager.py#L260-L280)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AttendanceSession | None`

#### Overview & Architectural Purpose
Массово проставляет статус 'П' (присутствует) всем оставшимся студентам.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import mark_all_remaining_present

# Execute call
result = await mark_all_remaining_present()
```

---

### `ensure_summary_headers`
```python
def ensure_summary_headers(sheet) -> None
```

- **Source Reference**: [`services/attendance_manager.py#L283-L300`](../../services/attendance_manager.py#L283-L300)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Гарантирует сохранение текстовых заголовков и кодов в сводных колонках.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Any` | Yes | Parameter `sheet` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import ensure_summary_headers

# Execute call
result = ensure_summary_headers(sheet=...)
```

---

### `apply_marks_to_sheet`
```python
def apply_marks_to_sheet(sheet, session: AttendanceSession, col: int) -> None
```

- **Source Reference**: [`services/attendance_manager.py#L303-L312`](../../services/attendance_manager.py#L303-L312)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Записывает все собранные отметки сессии в колонку даты в рабочем листе Excel.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Any` | Yes | Parameter `sheet` of type `Any`. |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |
| `col` | `int` | Yes | Parameter `col` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import apply_marks_to_sheet

# Execute call
result = apply_marks_to_sheet(sheet=..., session=..., col=...)
```

---

### `_prepare_updated_workbook`
```python
async def _prepare_updated_workbook( wopi, t_date: date, session: AttendanceSession, )
```

- **Source Reference**: [`services/attendance_manager.py#L315-L335`](../../services/attendance_manager.py#L315-L335)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Скачивает книгу и проставляет отметки сессии в колонку пары.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `wopi` | `Any` | Yes | Parameter `wopi` of type `Any`. |
| `t_date` | `date` | Yes | Parameter `t_date` of type `date`. |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from services.attendance_manager import _prepare_updated_workbook

# Execute call
result = await _prepare_updated_workbook(wopi=..., t_date=..., session=...)
```

---

### `_try_commit_once`
```python
async def _try_commit_once(session: AttendanceSession, t_date: date) -> bool
```

- **Source Reference**: [`services/attendance_manager.py#L338-L360`](../../services/attendance_manager.py#L338-L360)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Выполняет одну итерацию сохранения: скачать -> применить -> залить -> проверить.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |
| `t_date` | `date` | Yes | Parameter `t_date` of type `date`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import _try_commit_once

# Execute call
result = await _try_commit_once(session=..., t_date=...)
```

---

### `_post_commit_sync`
```python
async def _post_commit_sync() -> None
```

- **Source Reference**: [`services/attendance_manager.py#L363-L380`](../../services/attendance_manager.py#L363-L380)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Выполняет контрольную сверку реестра с Яндекс Документами после сохранения.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_manager import _post_commit_sync

# Execute call
result = await _post_commit_sync()
```

---

### `_execute_commit_attempts`
```python
async def _execute_commit_attempts(session: AttendanceSession, t_date: date) -> bool
```

- **Source Reference**: [`services/attendance_manager.py#L383-L401`](../../services/attendance_manager.py#L383-L401)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Выполняет цикл повторных попыток выгрузки журнала с экспоненциальной паузой.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |
| `t_date` | `date` | Yes | Parameter `t_date` of type `date`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_manager import _execute_commit_attempts

# Execute call
result = await _execute_commit_attempts(session=..., t_date=...)
```

---

### `commit_session_to_table`
```python
async def commit_session_to_table(session: AttendanceSession) -> bool
```

- **Source Reference**: [`services/attendance_manager.py#L404-L422`](../../services/attendance_manager.py#L404-L422)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Выгружает все зафиксированные отметки сессии в Яндекс Документы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import commit_session_to_table

# Execute call
result = await commit_session_to_table(session=...)
```

---

### `calculate_summary_stats`
```python
def calculate_summary_stats(marks: dict[str, str]) -> dict[str, int]
```

- **Source Reference**: [`services/attendance_manager.py#L425-L439`](../../services/attendance_manager.py#L425-L439)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, int]`

#### Overview & Architectural Purpose
Подсчитывает итоговые количества отметок по категориям (П, О, У, Н).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `marks` | `dict[str, str]` | Yes | Parameter `marks` of type `dict[str, str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_manager import calculate_summary_stats

# Execute call
result = calculate_summary_stats(marks=...)
```

---
