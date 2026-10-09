# Component Reference: `services/birthday_manager.py`
> **File Path**: [`services/birthday_manager.py`](../../services/birthday_manager.py)  
> **Subsystem**: `Student Lifecycle`  
> **Architecture Layer**: `Enterprise Microservice Subsystem`  
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`  
> **Persistence Backend**: `Redis 7 Persistent Store`  
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `services/birthday_manager.py` module implements core operational logic for the `Student Lifecycle` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

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
| [`calculate_days_and_age`](#calculate_days_and_age) | Function | L41–L60 | `dict[str, Any]` | Executes core domain logic for `calculate_days_and_age`... |
| [`format_person_tag`](#format_person_tag) | Function | L71–L82 | `str` | Formats message payload and presentation markup for `fo... |
| [`format_days_left_badge`](#format_days_left_badge) | Function | L85–L101 | `str` | Formats message payload and presentation markup for `fo... |
| [`format_today_block`](#format_today_block) | Function | L104–L115 | `list[str]` | Formats message payload and presentation markup for `fo... |
| [`format_age_badge`](#format_age_badge) | Function | L118–L130 | `str` | Formats message payload and presentation markup for `fo... |
| [`format_upcoming_block`](#format_upcoming_block) | Function | L133–L152 | `list[str]` | Formats message payload and presentation markup for `fo... |
| [`season_sort_key`](#season_sort_key) | Function | L155–L159 | `int` | Executes core domain logic for `season_sort_key`. |
| [`format_season_block`](#format_season_block) | Function | L162–L178 | `list[str]` | Formats message payload and presentation markup for `fo... |
| [`format_birthday_registry_text`](#format_birthday_registry_text) | Function | L181–L197 | `str` | Formats message payload and presentation markup for `fo... |
| [`pick_unique_wish`](#pick_unique_wish) | Function | L200–L214 | `str` | Executes core domain logic for `pick_unique_wish`. |
| [`get_person_mention`](#get_person_mention) | Function | L217–L227 | `str` | Retrieves and resolves domain data for `get_person_ment... |
| [`format_starosta_block`](#format_starosta_block) | Function | L230–L237 | `str` | Formats message payload and presentation markup for `fo... |
| [`format_congrats_message`](#format_congrats_message) | Function | L240–L257 | `str` | Formats message payload and presentation markup for `fo... |
| [`_send_congrats_telegram`](#_send_congrats_telegram) | Function | L260–L272 | `None` | Executes core domain logic for `_send_congrats_telegram... |
| [`send_congrats_for_item`](#send_congrats_for_item) | Function | L275–L287 | `None` | Dispatches notification message via Telegram API for `s... |
| [`is_morning_congrats_time`](#is_morning_congrats_time) | Function | L290–L292 | `bool` | Executes core domain logic for `is_morning_congrats_tim... |
| [`check_and_send_birthday_congratulations`](#check_and_send_birthday_congratulations) | Function | L295–L304 | `None` | Executes core domain logic for `check_and_send_birthday... |
| [`_edit_existing_birthday_message`](#_edit_existing_birthday_message) | Function | L307–L317 | `bool` | Executes core domain logic for `_edit_existing_birthday... |
| [`_create_new_birthday_message`](#_create_new_birthday_message) | Function | L320–L335 | `bool` | Executes core domain logic for `_create_new_birthday_me... |
| [`update_birthday_pinned_message`](#update_birthday_pinned_message) | Function | L338–L344 | `bool` | Synchronizes and updates domain state for `update_birth... |
| [`sync_birthdays_topic`](#sync_birthdays_topic) | Function | L347–L359 | `bool` | Executes core domain logic for `sync_birthdays_topic`. |
| [`birthday_sync_loop`](#birthday_sync_loop) | Function | L362–L371 | `None` | Executes core domain logic for `birthday_sync_loop`. |

---

## 3. Comprehensive Function Specifications

### `calculate_days_and_age`
```python
def calculate_days_and_age(item: dict[str, Any], today: date) -> dict[str, Any]
```

- **Source Reference**: [`services/birthday_manager.py#L41-L60`](../../services/birthday_manager.py#L41-L60)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `calculate_days_and_age`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import calculate_days_and_age

# Execute call
result = calculate_days_and_age(item=..., today=...)
```

---

### `format_person_tag`
```python
def format_person_tag(item: dict[str, Any]) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L71-L82`](../../services/birthday_manager.py#L71-L82)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_person_tag`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_person_tag

# Execute call
result = format_person_tag(item=...)
```

---

### `format_days_left_badge`
```python
def format_days_left_badge(days: int) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L85-L101`](../../services/birthday_manager.py#L85-L101)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_days_left_badge`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `days` | `int` | Yes | Parameter `days` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_days_left_badge

# Execute call
result = format_days_left_badge(days=...)
```

---

### `format_today_block`
```python
def format_today_block(today_items: list[dict[str, Any]]) -> list[str]
```

- **Source Reference**: [`services/birthday_manager.py#L104-L115`](../../services/birthday_manager.py#L104-L115)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[str]`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_today_block`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `today_items` | `list[dict[str, Any]]` | Yes | Parameter `today_items` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_today_block

# Execute call
result = format_today_block(today_items=...)
```

---

### `format_age_badge`
```python
def format_age_badge(age: int) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L118-L130`](../../services/birthday_manager.py#L118-L130)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_age_badge`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `age` | `int` | Yes | Parameter `age` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_age_badge

# Execute call
result = format_age_badge(age=...)
```

---

### `format_upcoming_block`
```python
def format_upcoming_block(items: list[dict[str, Any]]) -> list[str]
```

- **Source Reference**: [`services/birthday_manager.py#L133-L152`](../../services/birthday_manager.py#L133-L152)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[str]`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_upcoming_block`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `items` | `list[dict[str, Any]]` | Yes | Parameter `items` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_upcoming_block

# Execute call
result = format_upcoming_block(items=...)
```

---

### `season_sort_key`
```python
def season_sort_key(item: dict[str, Any], months: list[int]) -> int
```

- **Source Reference**: [`services/birthday_manager.py#L155-L159`](../../services/birthday_manager.py#L155-L159)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Executes core domain logic for `season_sort_key`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |
| `months` | `list[int]` | Yes | Parameter `months` of type `list[int]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import season_sort_key

# Execute call
result = season_sort_key(item=..., months=...)
```

---

### `format_season_block`
```python
def format_season_block(title: str, months: list[int], all_items: list[dict[str, Any]]) -> list[str]
```

- **Source Reference**: [`services/birthday_manager.py#L162-L178`](../../services/birthday_manager.py#L162-L178)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[str]`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_season_block`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `months` | `list[int]` | Yes | Parameter `months` of type `list[int]`. |
| `all_items` | `list[dict[str, Any]]` | Yes | Parameter `all_items` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_season_block

# Execute call
result = format_season_block(title=..., months=..., all_items=...)
```

---

### `format_birthday_registry_text`
```python
def format_birthday_registry_text(items: list[dict[str, Any]]) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L181-L197`](../../services/birthday_manager.py#L181-L197)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_birthday_registry_text`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `items` | `list[dict[str, Any]]` | Yes | Parameter `items` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_birthday_registry_text

# Execute call
result = format_birthday_registry_text(items=...)
```

---

### `pick_unique_wish`
```python
def pick_unique_wish(person_key: str, wishes: list[str], history_file: str = HISTORY_FILE) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L200-L214`](../../services/birthday_manager.py#L200-L214)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Executes core domain logic for `pick_unique_wish`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `person_key` | `str` | Yes | Parameter `person_key` of type `str`. |
| `wishes` | `list[str]` | Yes | Parameter `wishes` of type `list[str]`. |
| `history_file` | `str` | Yes | Parameter `history_file` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import pick_unique_wish

# Execute call
result = pick_unique_wish(person_key=..., wishes=..., history_file=...)
```

---

### `get_person_mention`
```python
def get_person_mention(item: dict[str, Any]) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L217-L227`](../../services/birthday_manager.py#L217-L227)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_person_mention`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import get_person_mention

# Execute call
result = get_person_mention(item=...)
```

---

### `format_starosta_block`
```python
def format_starosta_block(starosta_text: str | None) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L230-L237`](../../services/birthday_manager.py#L230-L237)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_starosta_block`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `starosta_text` | `str | None` | Yes | Parameter `starosta_text` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_starosta_block

# Execute call
result = format_starosta_block(starosta_text=...)
```

---

### `format_congrats_message`
```python
def format_congrats_message( item: dict[str, Any], wish_text: str, starosta_text: str | None = None ) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L240-L257`](../../services/birthday_manager.py#L240-L257)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_congrats_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |
| `wish_text` | `str` | Yes | Parameter `wish_text` of type `str`. |
| `starosta_text` | `str | None` | Yes | Parameter `starosta_text` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_congrats_message

# Execute call
result = format_congrats_message(item=..., wish_text=..., starosta_text=...)
```

---

### `_send_congrats_telegram`
```python
async def _send_congrats_telegram( text: str, person_key: str, key: str, state: dict[str, bool] ) -> None
```

- **Source Reference**: [`services/birthday_manager.py#L260-L272`](../../services/birthday_manager.py#L260-L272)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_send_congrats_telegram`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `person_key` | `str` | Yes | Parameter `person_key` of type `str`. |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `state` | `dict[str, bool]` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import _send_congrats_telegram

# Execute call
result = await _send_congrats_telegram(text=..., person_key=..., key=...)
```

---

### `send_congrats_for_item`
```python
async def send_congrats_for_item(item: dict[str, Any], today_str: str) -> None
```

- **Source Reference**: [`services/birthday_manager.py#L275-L287`](../../services/birthday_manager.py#L275-L287)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Dispatches notification message via Telegram API for `send_congrats_for_item`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |
| `today_str` | `str` | Yes | Parameter `today_str` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import send_congrats_for_item

# Execute call
result = await send_congrats_for_item(item=..., today_str=...)
```

---

### `is_morning_congrats_time`
```python
def is_morning_congrats_time(now_dt: datetime) -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L290-L292`](../../services/birthday_manager.py#L290-L292)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `is_morning_congrats_time`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import is_morning_congrats_time

# Execute call
result = is_morning_congrats_time(now_dt=...)
```

---

### `check_and_send_birthday_congratulations`
```python
async def check_and_send_birthday_congratulations(items: list[dict[str, Any]], today: date) -> None
```

- **Source Reference**: [`services/birthday_manager.py#L295-L304`](../../services/birthday_manager.py#L295-L304)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `check_and_send_birthday_congratulations`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `items` | `list[dict[str, Any]]` | Yes | Parameter `items` of type `list[dict[str, Any]]`. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import check_and_send_birthday_congratulations

# Execute call
result = await check_and_send_birthday_congratulations(items=..., today=...)
```

---

### `_edit_existing_birthday_message`
```python
async def _edit_existing_birthday_message(msg_id: int, text: str) -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L307-L317`](../../services/birthday_manager.py#L307-L317)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_edit_existing_birthday_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg_id` | `int` | Yes | Parameter `msg_id` of type `int`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import _edit_existing_birthday_message

# Execute call
result = await _edit_existing_birthday_message(msg_id=..., text=...)
```

---

### `_create_new_birthday_message`
```python
async def _create_new_birthday_message(text: str) -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L320-L335`](../../services/birthday_manager.py#L320-L335)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_create_new_birthday_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import _create_new_birthday_message

# Execute call
result = await _create_new_birthday_message(text=...)
```

---

### `update_birthday_pinned_message`
```python
async def update_birthday_pinned_message(text: str) -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L338-L344`](../../services/birthday_manager.py#L338-L344)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Synchronizes and updates domain state for `update_birthday_pinned_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import update_birthday_pinned_message

# Execute call
result = await update_birthday_pinned_message(text=...)
```

---

### `sync_birthdays_topic`
```python
async def sync_birthdays_topic() -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L347-L359`](../../services/birthday_manager.py#L347-L359)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `sync_birthdays_topic`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import sync_birthdays_topic

# Execute call
result = await sync_birthdays_topic()
```

---

### `birthday_sync_loop`
```python
async def birthday_sync_loop() -> None
```

- **Source Reference**: [`services/birthday_manager.py#L362-L371`](../../services/birthday_manager.py#L362-L371)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `birthday_sync_loop`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import birthday_sync_loop

# Execute call
result = await birthday_sync_loop()
```

---
