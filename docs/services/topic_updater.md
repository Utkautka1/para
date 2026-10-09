# Component Reference: `services/topic_updater.py`
> **File Path**: [`services/topic_updater.py`](../../services/topic_updater.py)  
> **Subsystem**: `Live Schedule Topic`  
> **Architecture Layer**: `Enterprise Microservice Subsystem`  
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`  
> **Persistence Backend**: `Redis 7 Persistent Store`  
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `services/topic_updater.py` module implements core operational logic for the `Live Schedule Topic` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

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
| [`load_topic_state`](#load_topic_state) | Function | L33–L40 | `int | None` | Executes core domain logic for `load_topic_state`. |
| [`save_topic_state`](#save_topic_state) | Function | L43–L49 | `None` | Saves serialized entity data to storage for `save_topic... |
| [`cleanup_expired_messages`](#cleanup_expired_messages) | Function | L52–L66 | `None` | Executes core domain logic for `cleanup_expired_message... |
| [`send_temp_topic_reminder`](#send_temp_topic_reminder) | Function | L69–L86 | `None` | Dispatches notification message via Telegram API for `s... |
| [`check_and_trigger_reminder`](#check_and_trigger_reminder) | Function | L89–L106 | `None` | Executes core domain logic for `check_and_trigger_remin... |
| [`get_next_working_day`](#get_next_working_day) | Function | L109–L119 | `date` | Retrieves and resolves domain data for `get_next_workin... |
| [`resolve_target_date`](#resolve_target_date) | Function | L122–L144 | `date | None` | Executes core domain logic for `resolve_target_date`. |
| [`is_too_early_to_publish`](#is_too_early_to_publish) | Function | L147–L161 | `bool` | Executes core domain logic for `is_too_early_to_publish... |
| [`update_topic_message_payload`](#update_topic_message_payload) | Function | L164–L186 | `bool` | Synchronizes and updates domain state for `update_topic... |
| [`_send_new_topic_message`](#_send_new_topic_message) | Function | L189–L200 | `bool` | Executes core domain logic for `_send_new_topic_message... |
| [`_pin_silently`](#_pin_silently) | Function | L203–L211 | `None` | Executes core domain logic for `_pin_silently`. |
| [`recreate_topic_message`](#recreate_topic_message) | Function | L214–L238 | `bool` | Executes core domain logic for `recreate_topic_message`... |
| [`_handle_edit_failure`](#_handle_edit_failure) | Function | L241–L259 | `bool` | Executes core domain logic for `_handle_edit_failure`. |
| [`should_skip_topic_update`](#should_skip_topic_update) | Function | L262–L271 | `bool` | Executes core domain logic for `should_skip_topic_updat... |
| [`process_today_reminders`](#process_today_reminders) | Function | L274–L278 | `None` | Executes core domain logic for `process_today_reminders... |
| [`sync_topic_main_message`](#sync_topic_main_message) | Function | L281–L301 | `bool` | Executes core domain logic for `sync_topic_main_message... |
| [`notify_admin_about_api_down`](#notify_admin_about_api_down) | Function | L308–L322 | `None` | Executes core domain logic for `notify_admin_about_api_... |
| [`topic_sync_loop`](#topic_sync_loop) | Function | L325–L346 | `None` | Executes core domain logic for `topic_sync_loop`. |

---

## 3. Comprehensive Function Specifications

### `load_topic_state`
```python
def load_topic_state() -> int | None
```

- **Source Reference**: [`services/topic_updater.py#L33-L40`](../../services/topic_updater.py#L33-L40)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Executes core domain logic for `load_topic_state`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import load_topic_state

# Execute call
result = load_topic_state()
```

---

### `save_topic_state`
```python
def save_topic_state(msg_id: int | None) -> None
```

- **Source Reference**: [`services/topic_updater.py#L43-L49`](../../services/topic_updater.py#L43-L49)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Saves serialized entity data to storage for `save_topic_state`.

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
from services.topic_updater import save_topic_state

# Execute call
result = save_topic_state(msg_id=...)
```

---

### `cleanup_expired_messages`
```python
async def cleanup_expired_messages() -> None
```

- **Source Reference**: [`services/topic_updater.py#L52-L66`](../../services/topic_updater.py#L52-L66)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `cleanup_expired_messages`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import cleanup_expired_messages

# Execute call
result = await cleanup_expired_messages()
```

---

### `send_temp_topic_reminder`
```python
async def send_temp_topic_reminder(lesson: Lesson) -> None
```

- **Source Reference**: [`services/topic_updater.py#L69-L86`](../../services/topic_updater.py#L69-L86)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Dispatches notification message via Telegram API for `send_temp_topic_reminder`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import send_temp_topic_reminder

# Execute call
result = await send_temp_topic_reminder(lesson=...)
```

---

### `check_and_trigger_reminder`
```python
async def check_and_trigger_reminder(lesson: Lesson, now_dt: datetime, today: date) -> None
```

- **Source Reference**: [`services/topic_updater.py#L89-L106`](../../services/topic_updater.py#L89-L106)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `check_and_trigger_reminder`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import check_and_trigger_reminder

# Execute call
result = await check_and_trigger_reminder(lesson=..., now_dt=..., today=...)
```

---

### `get_next_working_day`
```python
def get_next_working_day(target_date: date) -> date
```

- **Source Reference**: [`services/topic_updater.py#L109-L119`](../../services/topic_updater.py#L109-L119)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `date`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_next_working_day`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import get_next_working_day

# Execute call
result = get_next_working_day(target_date=...)
```

---

### `resolve_target_date`
```python
async def resolve_target_date(now_dt: datetime, ignore_restriction: bool) -> date | None
```

- **Source Reference**: [`services/topic_updater.py#L122-L144`](../../services/topic_updater.py#L122-L144)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `date | None`

#### Overview & Architectural Purpose
Executes core domain logic for `resolve_target_date`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `ignore_restriction` | `bool` | Yes | Parameter `ignore_restriction` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import resolve_target_date

# Execute call
result = await resolve_target_date(now_dt=..., ignore_restriction=...)
```

---

### `is_too_early_to_publish`
```python
def is_too_early_to_publish(lessons: list[Lesson], now_dt: datetime, today: date, ignore_restriction: bool) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L147-L161`](../../services/topic_updater.py#L147-L161)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `is_too_early_to_publish`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |
| `ignore_restriction` | `bool` | Yes | Parameter `ignore_restriction` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import is_too_early_to_publish

# Execute call
result = is_too_early_to_publish(lessons=..., now_dt=..., today=...)
```

---

### `update_topic_message_payload`
```python
async def update_topic_message_payload(text: str, kb: Any, _retry: bool = False) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L164-L186`](../../services/topic_updater.py#L164-L186)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Synchronizes and updates domain state for `update_topic_message_payload`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |
| `_retry` | `bool` | Yes | Parameter `_retry` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import update_topic_message_payload

# Execute call
result = await update_topic_message_payload(text=..., kb=..., _retry=...)
```

---

### `_send_new_topic_message`
```python
async def _send_new_topic_message(text: str, kb: Any) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L189-L200`](../../services/topic_updater.py#L189-L200)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_send_new_topic_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _send_new_topic_message

# Execute call
result = await _send_new_topic_message(text=..., kb=...)
```

---

### `_pin_silently`
```python
async def _pin_silently(chat_id: int, message_id: int) -> None
```

- **Source Reference**: [`services/topic_updater.py#L203-L211`](../../services/topic_updater.py#L203-L211)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_pin_silently`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `message_id` | `int` | Yes | Parameter `message_id` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import _pin_silently

# Execute call
result = await _pin_silently(chat_id=..., message_id=...)
```

---

### `recreate_topic_message`
```python
async def recreate_topic_message() -> bool
```

- **Source Reference**: [`services/topic_updater.py#L214-L238`](../../services/topic_updater.py#L214-L238)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `recreate_topic_message`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import recreate_topic_message

# Execute call
result = await recreate_topic_message()
```

---

### `_handle_edit_failure`
```python
async def _handle_edit_failure( e: TelegramBadRequest, text: str, kb: Any, is_retry: bool ) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L241-L259`](../../services/topic_updater.py#L241-L259)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_handle_edit_failure`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `e` | `TelegramBadRequest` | Yes | Parameter `e` of type `TelegramBadRequest`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |
| `is_retry` | `bool` | Yes | Parameter `is_retry` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _handle_edit_failure

# Execute call
result = await _handle_edit_failure(e=..., text=..., kb=...)
```

---

### `should_skip_topic_update`
```python
def should_skip_topic_update( lessons: list, now_dt: datetime, target_date: date, ignore_time_restriction: bool ) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L262-L271`](../../services/topic_updater.py#L262-L271)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `should_skip_topic_update`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list` | Yes | Parameter `lessons` of type `list`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `ignore_time_restriction` | `bool` | Yes | Parameter `ignore_time_restriction` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import should_skip_topic_update

# Execute call
result = should_skip_topic_update(lessons=..., now_dt=..., target_date=...)
```

---

### `process_today_reminders`
```python
async def process_today_reminders(lessons: list, now_dt: datetime, target_date: date) -> None
```

- **Source Reference**: [`services/topic_updater.py#L274-L278`](../../services/topic_updater.py#L274-L278)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `process_today_reminders`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list` | Yes | Parameter `lessons` of type `list`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import process_today_reminders

# Execute call
result = await process_today_reminders(lessons=..., now_dt=..., target_date=...)
```

---

### `sync_topic_main_message`
```python
async def sync_topic_main_message(ignore_time_restriction: bool = False) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L281-L301`](../../services/topic_updater.py#L281-L301)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `sync_topic_main_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `ignore_time_restriction` | `bool` | Yes | Parameter `ignore_time_restriction` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import sync_topic_main_message

# Execute call
result = await sync_topic_main_message(ignore_time_restriction=...)
```

---

### `notify_admin_about_api_down`
```python
async def notify_admin_about_api_down() -> None
```

- **Source Reference**: [`services/topic_updater.py#L308-L322`](../../services/topic_updater.py#L308-L322)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `notify_admin_about_api_down`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import notify_admin_about_api_down

# Execute call
result = await notify_admin_about_api_down()
```

---

### `topic_sync_loop`
```python
async def topic_sync_loop() -> None
```

- **Source Reference**: [`services/topic_updater.py#L325-L346`](../../services/topic_updater.py#L325-L346)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `topic_sync_loop`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import topic_sync_loop

# Execute call
result = await topic_sync_loop()
```

---
