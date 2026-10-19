# Component Reference: `services/notifier.py`
> **File Path**: [`services/notifier.py`](../../services/notifier.py)
> **Subsystem**: `Notification Dispatcher`
> **Architecture Layer**: `Enterprise Microservice Subsystem`
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`
> **Persistence Backend**: `Redis 7 Persistent Store`
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `services/notifier.py` module implements core operational logic for the `Notification Dispatcher` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

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
| [`build_missing_teacher_alert`](#build_missing_teacher_alert) | Function | L40–L60 | `tuple[str, InlineKeyboardMarkup]` | Executes core domain logic for `build_missing_teacher_a... |
| [`notify_missing_teacher`](#notify_missing_teacher) | Function | L63–L78 | `None` | Executes core domain logic for `notify_missing_teacher`... |
| [`send_to_user`](#send_to_user) | Function | L81–L93 | `None` | Dispatches notification message via Telegram API for `s... |
| [`parse_lesson_start_time`](#parse_lesson_start_time) | Function | L96–L112 | `dtime | None` | Parses and extracts structured entities from `parse_les... |
| [`parse_lesson_end_time`](#parse_lesson_end_time) | Function | L115–L131 | `dtime | None` | Parses and extracts structured entities from `parse_les... |
| [`_send_reminder_to_chat`](#_send_reminder_to_chat) | Function | L134–L153 | `None` | Executes core domain logic for `_send_reminder_to_chat`... |
| [`send_single_reminder`](#send_single_reminder) | Function | L156–L175 | `None` | Dispatches notification message via Telegram API for `s... |
| [`_add_lesson_reminder_job`](#_add_lesson_reminder_job) | Function | L178–L193 | `None` | Executes core domain logic for `_add_lesson_reminder_jo... |
| [`schedule_lesson_reminder`](#schedule_lesson_reminder) | Function | L196–L212 | `None` | Executes core domain logic for `schedule_lesson_reminde... |
| [`_send_attendance_to_admin`](#_send_attendance_to_admin) | Function | L215–L231 | `None` | Executes core domain logic for `_send_attendance_to_adm... |
| [`send_attendance_prompt`](#send_attendance_prompt) | Function | L234–L247 | `None` | Dispatches notification message via Telegram API for `s... |
| [`auto_close_attendance_session`](#auto_close_attendance_session) | Function | L250–L267 | `None` | Executes core domain logic for `auto_close_attendance_s... |
| [`_schedule_attendance_poll_job`](#_schedule_attendance_poll_job) | Function | L270–L286 | `None` | Executes core domain logic for `_schedule_attendance_po... |
| [`_schedule_attendance_close_job`](#_schedule_attendance_close_job) | Function | L289–L304 | `None` | Executes core domain logic for `_schedule_attendance_cl... |
| [`schedule_attendance_poll`](#schedule_attendance_poll) | Function | L307–L325 | `None` | Executes core domain logic for `schedule_attendance_pol... |
| [`daily_schedule_dispatch`](#daily_schedule_dispatch) | Function | L328–L348 | `None` | Executes core domain logic for `daily_schedule_dispatch... |
| [`setup_scheduler`](#setup_scheduler) | Function | L351–L370 | `AsyncIOScheduler` | Executes core domain logic for `setup_scheduler`. |

---

## 3. Comprehensive Function Specifications

### `build_missing_teacher_alert`
```python
def build_missing_teacher_alert(raw_teacher: str, subj_name: str) -> tuple[str, InlineKeyboardMarkup]
```

- **Source Reference**: [`services/notifier.py#L40-L60`](../../services/notifier.py#L40-L60)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, InlineKeyboardMarkup]`

#### Overview & Architectural Purpose
Executes core domain logic for `build_missing_teacher_alert`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw_teacher` | `str` | Yes | Parameter `raw_teacher` of type `str`. |
| `subj_name` | `str` | Yes | Parameter `subj_name` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import build_missing_teacher_alert

# Execute call
result = build_missing_teacher_alert(raw_teacher=..., subj_name=...)
```

---

### `notify_missing_teacher`
```python
async def notify_missing_teacher(raw_teacher: str, subj_name: str) -> None
```

- **Source Reference**: [`services/notifier.py#L63-L78`](../../services/notifier.py#L63-L78)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `notify_missing_teacher`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw_teacher` | `str` | Yes | Parameter `raw_teacher` of type `str`. |
| `subj_name` | `str` | Yes | Parameter `subj_name` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import notify_missing_teacher

# Execute call
result = await notify_missing_teacher(raw_teacher=..., subj_name=...)
```

---

### `send_to_user`
```python
async def send_to_user(text: str, reply_markup: Any = None) -> None
```

- **Source Reference**: [`services/notifier.py#L81-L93`](../../services/notifier.py#L81-L93)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Dispatches notification message via Telegram API for `send_to_user`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `reply_markup` | `Any` | Yes | Parameter `reply_markup` of type `Any`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.notifier import send_to_user

# Execute call
result = await send_to_user(text=..., reply_markup=...)
```

---

### `parse_lesson_start_time`
```python
def parse_lesson_start_time(time_str: str) -> dtime | None
```

- **Source Reference**: [`services/notifier.py#L96-L112`](../../services/notifier.py#L96-L112)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dtime | None`

#### Overview & Architectural Purpose
Parses and extracts structured entities from `parse_lesson_start_time`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `time_str` | `str` | Yes | Parameter `time_str` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.notifier import parse_lesson_start_time

# Execute call
result = parse_lesson_start_time(time_str=...)
```

---

### `parse_lesson_end_time`
```python
def parse_lesson_end_time(time_str: str) -> dtime | None
```

- **Source Reference**: [`services/notifier.py#L115-L131`](../../services/notifier.py#L115-L131)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dtime | None`

#### Overview & Architectural Purpose
Parses and extracts structured entities from `parse_lesson_end_time`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `time_str` | `str` | Yes | Parameter `time_str` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.notifier import parse_lesson_end_time

# Execute call
result = parse_lesson_end_time(time_str=...)
```

---

### `_send_reminder_to_chat`
```python
async def _send_reminder_to_chat( chat_id: int, text: str, lesson: Lesson, sem: asyncio.Semaphore, ) -> None
```

- **Source Reference**: [`services/notifier.py#L134-L153`](../../services/notifier.py#L134-L153)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_send_reminder_to_chat`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |
| `sem` | `asyncio.Semaphore` | Yes | Parameter `sem` of type `asyncio.Semaphore`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.notifier import _send_reminder_to_chat

# Execute call
result = await _send_reminder_to_chat(chat_id=..., text=..., lesson=...)
```

---

### `send_single_reminder`
```python
async def send_single_reminder(lesson: Lesson) -> None
```

- **Source Reference**: [`services/notifier.py#L156-L175`](../../services/notifier.py#L156-L175)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Dispatches notification message via Telegram API for `send_single_reminder`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import send_single_reminder

# Execute call
result = await send_single_reminder(lesson=...)
```

---

### `_add_lesson_reminder_job`
```python
def _add_lesson_reminder_job(today: date, lesson: Lesson, remind_dt: datetime) -> None
```

- **Source Reference**: [`services/notifier.py#L178-L193`](../../services/notifier.py#L178-L193)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_add_lesson_reminder_job`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `today` | `date` | Yes | Parameter `today` of type `date`. |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |
| `remind_dt` | `datetime` | Yes | Parameter `remind_dt` of type `datetime`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import _add_lesson_reminder_job

# Execute call
result = _add_lesson_reminder_job(today=..., lesson=..., remind_dt=...)
```

---

### `schedule_lesson_reminder`
```python
def schedule_lesson_reminder(today: date, lesson: Lesson, now_dt: datetime) -> None
```

- **Source Reference**: [`services/notifier.py#L196-L212`](../../services/notifier.py#L196-L212)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `schedule_lesson_reminder`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `today` | `date` | Yes | Parameter `today` of type `date`. |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import schedule_lesson_reminder

# Execute call
result = schedule_lesson_reminder(today=..., lesson=..., now_dt=...)
```

---

### `_send_attendance_to_admin`
```python
async def _send_attendance_to_admin( user_id: int, text: str, kb: Any, sem: asyncio.Semaphore, ) -> None
```

- **Source Reference**: [`services/notifier.py#L215-L231`](../../services/notifier.py#L215-L231)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_send_attendance_to_admin`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |
| `sem` | `asyncio.Semaphore` | Yes | Parameter `sem` of type `asyncio.Semaphore`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.notifier import _send_attendance_to_admin

# Execute call
result = await _send_attendance_to_admin(user_id=..., text=..., kb=...)
```

---

### `send_attendance_prompt`
```python
async def send_attendance_prompt(lesson: Lesson) -> None
```

- **Source Reference**: [`services/notifier.py#L234-L247`](../../services/notifier.py#L234-L247)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Dispatches notification message via Telegram API for `send_attendance_prompt`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import send_attendance_prompt

# Execute call
result = await send_attendance_prompt(lesson=...)
```

---

### `auto_close_attendance_session`
```python
async def auto_close_attendance_session(lesson_num: int) -> None
```

- **Source Reference**: [`services/notifier.py#L250-L267`](../../services/notifier.py#L250-L267)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `auto_close_attendance_session`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import auto_close_attendance_session

# Execute call
result = await auto_close_attendance_session(lesson_num=...)
```

---

### `_schedule_attendance_poll_job`
```python
def _schedule_attendance_poll_job(today: date, lesson: Lesson, poll_dt: datetime, now_dt: datetime) -> None
```

- **Source Reference**: [`services/notifier.py#L270-L286`](../../services/notifier.py#L270-L286)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_schedule_attendance_poll_job`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `today` | `date` | Yes | Parameter `today` of type `date`. |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |
| `poll_dt` | `datetime` | Yes | Parameter `poll_dt` of type `datetime`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import _schedule_attendance_poll_job

# Execute call
result = _schedule_attendance_poll_job(today=..., lesson=..., poll_dt=...)
```

---

### `_schedule_attendance_close_job`
```python
def _schedule_attendance_close_job(today: date, lesson: Lesson, end_dt: datetime, now_dt: datetime) -> None
```

- **Source Reference**: [`services/notifier.py#L289-L304`](../../services/notifier.py#L289-L304)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_schedule_attendance_close_job`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `today` | `date` | Yes | Parameter `today` of type `date`. |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |
| `end_dt` | `datetime` | Yes | Parameter `end_dt` of type `datetime`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import _schedule_attendance_close_job

# Execute call
result = _schedule_attendance_close_job(today=..., lesson=..., end_dt=...)
```

---

### `schedule_attendance_poll`
```python
def schedule_attendance_poll(today: date, lesson: Lesson, now_dt: datetime) -> None
```

- **Source Reference**: [`services/notifier.py#L307-L325`](../../services/notifier.py#L307-L325)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `schedule_attendance_poll`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `today` | `date` | Yes | Parameter `today` of type `date`. |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import schedule_attendance_poll

# Execute call
result = schedule_attendance_poll(today=..., lesson=..., now_dt=...)
```

---

### `daily_schedule_dispatch`
```python
async def daily_schedule_dispatch() -> None
```

- **Source Reference**: [`services/notifier.py#L328-L348`](../../services/notifier.py#L328-L348)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `daily_schedule_dispatch`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import daily_schedule_dispatch

# Execute call
result = await daily_schedule_dispatch()
```

---

### `setup_scheduler`
```python
def setup_scheduler() -> AsyncIOScheduler
```

- **Source Reference**: [`services/notifier.py#L351-L370`](../../services/notifier.py#L351-L370)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `AsyncIOScheduler`

#### Overview & Architectural Purpose
Executes core domain logic for `setup_scheduler`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.notifier import setup_scheduler

# Execute call
result = setup_scheduler()
```

---
