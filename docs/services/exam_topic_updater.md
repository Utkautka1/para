# Component Reference: `services/exam_topic_updater.py`
> **File Path**: [`services/exam_topic_updater.py`](../../services/exam_topic_updater.py)  
> **Subsystem**: `Examination Topic`  
> **Architecture Layer**: `Enterprise Microservice Subsystem`  
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`  
> **Persistence Backend**: `Redis 7 Persistent Store`  
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `services/exam_topic_updater.py` module implements core operational logic for the `Examination Topic` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

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
| [`get_default_semester_start`](#get_default_semester_start) | Function | L31–L35 | `date` | Retrieves and resolves domain data for `get_default_sem... |
| [`get_effective_semester_start`](#get_effective_semester_start) | Function | L41–L52 | `date` | Retrieves and resolves domain data for `get_effective_s... |
| [`load_exam_topic_state`](#load_exam_topic_state) | Function | L55–L58 | `int | None` | Executes core domain logic for `load_exam_topic_state`. |
| [`save_exam_topic_state`](#save_exam_topic_state) | Function | L61–L63 | `None` | Saves serialized entity data to storage for `save_exam_... |
| [`get_week_date_range_str`](#get_week_date_range_str) | Function | L66–L75 | `str` | Retrieves and resolves domain data for `get_week_date_r... |
| [`format_exam_card`](#format_exam_card) | Function | L78–L97 | `str` | Formats message payload and presentation markup for `fo... |
| [`format_exams_schedule_message`](#format_exams_schedule_message) | Function | L101–L111 | `str` | Formats message payload and presentation markup for `fo... |
| [`_pin_exam_silently`](#_pin_exam_silently) | Function | L114–L122 | `None` | Executes core domain logic for `_pin_exam_silently`. |
| [`create_exam_message`](#create_exam_message) | Function | L125–L135 | `int` | Initializes and constructs a new instance of `create_ex... |
| [`handle_exam_edit_error`](#handle_exam_edit_error) | Function | L138–L152 | `bool` | Executes core domain logic for `handle_exam_edit_error`... |
| [`send_or_edit_exam_msg`](#send_or_edit_exam_msg) | Function | L155–L173 | `bool` | Dispatches notification message via Telegram API for `s... |
| [`recreate_exam_topic_message`](#recreate_exam_topic_message) | Function | L176–L192 | `bool` | Executes core domain logic for `recreate_exam_topic_mes... |
| [`sync_exam_topic_message`](#sync_exam_topic_message) | Function | L195–L212 | `bool` | Executes core domain logic for `sync_exam_topic_message... |
| [`exam_topic_sync_loop`](#exam_topic_sync_loop) | Function | L215–L225 | `None` | Executes core domain logic for `exam_topic_sync_loop`. |

---

## 3. Comprehensive Function Specifications

### `get_default_semester_start`
```python
def get_default_semester_start() -> date
```

- **Source Reference**: [`services/exam_topic_updater.py#L31-L35`](../../services/exam_topic_updater.py#L31-L35)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `date`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_default_semester_start`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.exam_topic_updater import get_default_semester_start

# Execute call
result = get_default_semester_start()
```

---

### `get_effective_semester_start`
```python
async def get_effective_semester_start() -> date
```

- **Source Reference**: [`services/exam_topic_updater.py#L41-L52`](../../services/exam_topic_updater.py#L41-L52)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `date`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_effective_semester_start`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.exam_topic_updater import get_effective_semester_start

# Execute call
result = await get_effective_semester_start()
```

---

### `load_exam_topic_state`
```python
def load_exam_topic_state() -> int | None
```

- **Source Reference**: [`services/exam_topic_updater.py#L55-L58`](../../services/exam_topic_updater.py#L55-L58)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Executes core domain logic for `load_exam_topic_state`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.exam_topic_updater import load_exam_topic_state

# Execute call
result = load_exam_topic_state()
```

---

### `save_exam_topic_state`
```python
def save_exam_topic_state(msg_id: int | None) -> None
```

- **Source Reference**: [`services/exam_topic_updater.py#L61-L63`](../../services/exam_topic_updater.py#L61-L63)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Saves serialized entity data to storage for `save_exam_topic_state`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg_id` | `int | None` | Yes | Parameter `msg_id` of type `int | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.exam_topic_updater import save_exam_topic_state

# Execute call
result = save_exam_topic_state(msg_id=...)
```

---

### `get_week_date_range_str`
```python
def get_week_date_range_str(week_num: int, semester_start: date | None = None) -> str
```

- **Source Reference**: [`services/exam_topic_updater.py#L66-L75`](../../services/exam_topic_updater.py#L66-L75)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_week_date_range_str`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `week_num` | `int` | Yes | Parameter `week_num` of type `int`. |
| `semester_start` | `date | None` | Yes | Parameter `semester_start` of type `date | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.exam_topic_updater import get_week_date_range_str

# Execute call
result = get_week_date_range_str(week_num=..., semester_start=...)
```

---

### `format_exam_card`
```python
def format_exam_card(ex: ExamItem, semester_start: date | None = None) -> str
```

- **Source Reference**: [`services/exam_topic_updater.py#L78-L97`](../../services/exam_topic_updater.py#L78-L97)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_exam_card`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `ex` | `ExamItem` | Yes | Parameter `ex` of type `ExamItem`. |
| `semester_start` | `date | None` | Yes | Parameter `semester_start` of type `date | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.exam_topic_updater import format_exam_card

# Execute call
result = format_exam_card(ex=..., semester_start=...)
```

---

### `format_exams_schedule_message`
```python
def format_exams_schedule_message(exams: list[ExamItem], semester_start: date | None = None) -> str
```

- **Source Reference**: [`services/exam_topic_updater.py#L101-L111`](../../services/exam_topic_updater.py#L101-L111)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_exams_schedule_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `exams` | `list[ExamItem]` | Yes | Parameter `exams` of type `list[ExamItem]`. |
| `semester_start` | `date | None` | Yes | Parameter `semester_start` of type `date | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.exam_topic_updater import format_exams_schedule_message

# Execute call
result = format_exams_schedule_message(exams=..., semester_start=...)
```

---

### `_pin_exam_silently`
```python
async def _pin_exam_silently(message_id: int) -> None
```

- **Source Reference**: [`services/exam_topic_updater.py#L114-L122`](../../services/exam_topic_updater.py#L114-L122)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_pin_exam_silently`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message_id` | `int` | Yes | Parameter `message_id` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.exam_topic_updater import _pin_exam_silently

# Execute call
result = await _pin_exam_silently(message_id=...)
```

---

### `create_exam_message`
```python
async def create_exam_message(text: str) -> int
```

- **Source Reference**: [`services/exam_topic_updater.py#L125-L135`](../../services/exam_topic_updater.py#L125-L135)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Initializes and constructs a new instance of `create_exam_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.exam_topic_updater import create_exam_message

# Execute call
result = await create_exam_message(text=...)
```

---

### `handle_exam_edit_error`
```python
async def handle_exam_edit_error(text: str, err_str: str, retry: bool) -> bool
```

- **Source Reference**: [`services/exam_topic_updater.py#L138-L152`](../../services/exam_topic_updater.py#L138-L152)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `handle_exam_edit_error`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `err_str` | `str` | Yes | Parameter `err_str` of type `str`. |
| `retry` | `bool` | Yes | Parameter `retry` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.exam_topic_updater import handle_exam_edit_error

# Execute call
result = await handle_exam_edit_error(text=..., err_str=..., retry=...)
```

---

### `send_or_edit_exam_msg`
```python
async def send_or_edit_exam_msg(text: str, _retry: bool = False) -> bool
```

- **Source Reference**: [`services/exam_topic_updater.py#L155-L173`](../../services/exam_topic_updater.py#L155-L173)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Dispatches notification message via Telegram API for `send_or_edit_exam_msg`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `_retry` | `bool` | Yes | Parameter `_retry` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.exam_topic_updater import send_or_edit_exam_msg

# Execute call
result = await send_or_edit_exam_msg(text=..., _retry=...)
```

---

### `recreate_exam_topic_message`
```python
async def recreate_exam_topic_message() -> bool
```

- **Source Reference**: [`services/exam_topic_updater.py#L176-L192`](../../services/exam_topic_updater.py#L176-L192)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `recreate_exam_topic_message`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.exam_topic_updater import recreate_exam_topic_message

# Execute call
result = await recreate_exam_topic_message()
```

---

### `sync_exam_topic_message`
```python
async def sync_exam_topic_message() -> bool
```

- **Source Reference**: [`services/exam_topic_updater.py#L195-L212`](../../services/exam_topic_updater.py#L195-L212)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `sync_exam_topic_message`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.exam_topic_updater import sync_exam_topic_message

# Execute call
result = await sync_exam_topic_message()
```

---

### `exam_topic_sync_loop`
```python
async def exam_topic_sync_loop() -> None
```

- **Source Reference**: [`services/exam_topic_updater.py#L215-L225`](../../services/exam_topic_updater.py#L215-L225)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `exam_topic_sync_loop`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.exam_topic_updater import exam_topic_sync_loop

# Execute call
result = await exam_topic_sync_loop()
```

---
