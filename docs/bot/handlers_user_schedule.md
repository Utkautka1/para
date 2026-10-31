# Component Reference: `bot/handlers/user/schedule.py`
> **File Path**: [`bot/handlers/user/schedule.py`](../../bot/handlers/user/schedule.py)
> **Subsystem**: `User Schedule Flow`
> **Architecture Layer**: `Enterprise Microservice Subsystem`
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`
> **Persistence Backend**: `Redis 7 Persistent Store`
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `bot/handlers/user/schedule.py` module implements core operational logic for the `User Schedule Flow` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

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
| [`get_day_schedule_cached`](#get_day_schedule_cached) | Function | L51–L66 | `tuple[str, list[Lesson]]` | Retrieves and resolves domain data for `get_day_schedul... |
| [`_ack_callback`](#_ack_callback) | Function | L69–L77 | `None` | Executes core domain logic for `_ack_callback`. |
| [`edit_or_answer`](#edit_or_answer) | Function | L80–L97 | `None` | Executes core domain logic for `edit_or_answer`. |
| [`_greet_new_student`](#_greet_new_student) | Function | L100–L118 | `None` | Executes core domain logic for `_greet_new_student`. |
| [`_show_access_denied`](#_show_access_denied) | Function | L121–L138 | `None` | Executes core domain logic for `_show_access_denied`. |
| [`_show_tester_cabinet`](#_show_tester_cabinet) | Function | L141–L165 | `None` | Executes core domain logic for `_show_tester_cabinet`. |
| [`_send_today_schedule`](#_send_today_schedule) | Function | L168–L189 | `list[Lesson]` | Executes core domain logic for `_send_today_schedule`. |
| [`_award_today_view`](#_award_today_view) | Function | L192–L199 | `None` | Executes core domain logic for `_award_today_view`. |
| [`_handle_unauthorized_user`](#_handle_unauthorized_user) | Function | L202–L210 | `bool` | Executes core domain logic for `_handle_unauthorized_us... |
| [`cmd_start`](#cmd_start) | Function | L215–L228 | `None` | Processes inbound Telegram slash command for `cmd_start... |
| [`cmd_my_api_key`](#cmd_my_api_key) | Function | L233–L248 | `None` | Processes inbound Telegram slash command for `cmd_my_ap... |
| [`cb_show_tester_key`](#cb_show_tester_key) | Function | L252–L265 | `None` | Handles Telegram inline callback query events for `cb_s... |
| [`_trigger_notify_achievements`](#_trigger_notify_achievements) | Function | L268–L275 | `None` | Executes core domain logic for `_trigger_notify_achieve... |
| [`_update_schedule_inline_markup`](#_update_schedule_inline_markup) | Function | L278–L293 | `None` | Executes core domain logic for `_update_schedule_inline... |
| [`cb_toggle_notify`](#cb_toggle_notify) | Function | L297–L306 | `None` | Handles Telegram inline callback query events for `cb_t... |
| [`cmd_notice`](#cmd_notice) | Function | L310–L328 | `None` | Processes inbound Telegram slash command for `cmd_notic... |
| [`cb_notice_toggle`](#cb_notice_toggle) | Function | L332–L352 | `None` | Handles Telegram inline callback query events for `cb_n... |
| [`cb_today`](#cb_today) | Function | L356–L372 | `None` | Handles Telegram inline callback query events for `cb_t... |
| [`cb_tomorrow`](#cb_tomorrow) | Function | L376–L392 | `None` | Handles Telegram inline callback query events for `cb_t... |
| [`cb_week`](#cb_week) | Function | L396–L421 | `None` | Handles Telegram inline callback query events for `cb_w... |
| [`_get_next_week_monday`](#_get_next_week_monday) | Function | L424–L427 | `date` | Executes core domain logic for `_get_next_week_monday`. |
| [`cb_week_next`](#cb_week_next) | Function | L431–L447 | `None` | Handles Telegram inline callback query events for `cb_w... |
| [`_safe_fetch_lessons_for_refresh`](#_safe_fetch_lessons_for_refresh) | Function | L450–L456 | `list[Lesson]` | Executes core domain logic for `_safe_fetch_lessons_for... |
| [`_refresh_and_format_schedule`](#_refresh_and_format_schedule) | Function | L459–L469 | `tuple[str, list[Lesson], int]` | Executes core domain logic for `_refresh_and_format_sch... |
| [`cb_refresh`](#cb_refresh) | Function | L473–L484 | `None` | Handles Telegram inline callback query events for `cb_r... |
| [`format_help_text`](#format_help_text) | Function | L487–L510 | `str` | Formats message payload and presentation markup for `fo... |
| [`cmd_help`](#cmd_help) | Function | L514–L535 | `None` | Processes inbound Telegram slash command for `cmd_help`... |
| [`handle_user_text_message`](#handle_user_text_message) | Function | L539–L555 | `None` | Executes core domain logic for `handle_user_text_messag... |

---

## 3. Comprehensive Function Specifications

### `get_day_schedule_cached`
```python
async def get_day_schedule_cached(target_date: date) -> tuple[str, list[Lesson]]
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L51-L66`](../../bot/handlers/user/schedule.py#L51-L66)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[str, list[Lesson]]`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_day_schedule_cached`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import get_day_schedule_cached

# Execute call
result = await get_day_schedule_cached(target_date=...)
```

---

### `_ack_callback`
```python
async def _ack_callback(callback: CallbackQuery, text: str | None = None) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L69-L77`](../../bot/handlers/user/schedule.py#L69-L77)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_ack_callback`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `text` | `str | None` | Yes | Parameter `text` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _ack_callback

# Execute call
result = await _ack_callback(callback=..., text=...)
```

---

### `edit_or_answer`
```python
async def edit_or_answer( callback: CallbackQuery, text: str, lessons: list[Lesson] | None = None, week_offset: int = 0 ) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L80-L97`](../../bot/handlers/user/schedule.py#L80-L97)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `edit_or_answer`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `lessons` | `list[Lesson] | None` | Yes | Parameter `lessons` of type `list[Lesson] | None`. |
| `week_offset` | `int` | Yes | Parameter `week_offset` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import edit_or_answer

# Execute call
result = await edit_or_answer(callback=..., text=..., lessons=...)
```

---

### `_greet_new_student`
```python
async def _greet_new_student(message: Message, student: dict) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L100-L118`](../../bot/handlers/user/schedule.py#L100-L118)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_greet_new_student`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `student` | `dict` | Yes | Parameter `student` of type `dict`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _greet_new_student

# Execute call
result = await _greet_new_student(message=..., student=...)
```

---

### `_show_access_denied`
```python
async def _show_access_denied(message: Message, uid: int) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L121-L138`](../../bot/handlers/user/schedule.py#L121-L138)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_show_access_denied`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _show_access_denied

# Execute call
result = await _show_access_denied(message=..., uid=...)
```

---

### `_show_tester_cabinet`
```python
async def _show_tester_cabinet(message: Message, uid: int) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L141-L165`](../../bot/handlers/user/schedule.py#L141-L165)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_show_tester_cabinet`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _show_tester_cabinet

# Execute call
result = await _show_tester_cabinet(message=..., uid=...)
```

---

### `_send_today_schedule`
```python
async def _send_today_schedule(message: Message, uid: int, is_tester: bool) -> list[Lesson]
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L168-L189`](../../bot/handlers/user/schedule.py#L168-L189)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[Lesson]`

#### Overview & Architectural Purpose
Executes core domain logic for `_send_today_schedule`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `is_tester` | `bool` | Yes | Parameter `is_tester` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _send_today_schedule

# Execute call
result = await _send_today_schedule(message=..., uid=..., is_tester=...)
```

---

### `_award_today_view`
```python
def _award_today_view(message: Message, lessons: list[Lesson]) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L192-L199`](../../bot/handlers/user/schedule.py#L192-L199)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_award_today_view`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _award_today_view

# Execute call
result = _award_today_view(message=..., lessons=...)
```

---

### `_handle_unauthorized_user`
```python
async def _handle_unauthorized_user(message: Message, is_auth: bool, is_tester: bool, uid: int) -> bool
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L202-L210`](../../bot/handlers/user/schedule.py#L202-L210)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_handle_unauthorized_user`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `is_auth` | `bool` | Yes | Parameter `is_auth` of type `bool`. |
| `is_tester` | `bool` | Yes | Parameter `is_tester` of type `bool`. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _handle_unauthorized_user

# Execute call
result = await _handle_unauthorized_user(message=..., is_auth=..., is_tester=...)
```

---

### `cmd_start`
```python
async def cmd_start(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L215-L228`](../../bot/handlers/user/schedule.py#L215-L228)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Processes inbound Telegram slash command for `cmd_start`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cmd_start

# Execute call
result = await cmd_start(message=...)
```

---

### `cmd_my_api_key`
```python
async def cmd_my_api_key(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L233-L248`](../../bot/handlers/user/schedule.py#L233-L248)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Processes inbound Telegram slash command for `cmd_my_api_key`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cmd_my_api_key

# Execute call
result = await cmd_my_api_key(message=...)
```

---

### `cb_show_tester_key`
```python
async def cb_show_tester_key(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L252-L265`](../../bot/handlers/user/schedule.py#L252-L265)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_show_tester_key`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cb_show_tester_key

# Execute call
result = await cb_show_tester_key(callback=...)
```

---

### `_trigger_notify_achievements`
```python
def _trigger_notify_achievements(uid: int, bot: Any, new_sub: bool, full_name: str | None) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L268-L275`](../../bot/handlers/user/schedule.py#L268-L275)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_trigger_notify_achievements`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `new_sub` | `bool` | Yes | Parameter `new_sub` of type `bool`. |
| `full_name` | `str | None` | Yes | Parameter `full_name` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _trigger_notify_achievements

# Execute call
result = _trigger_notify_achievements(uid=..., bot=..., new_sub=...)
```

---

### `_update_schedule_inline_markup`
```python
async def _update_schedule_inline_markup(callback: CallbackQuery, uid: int, new_sub: bool) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L278-L293`](../../bot/handlers/user/schedule.py#L278-L293)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_update_schedule_inline_markup`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `new_sub` | `bool` | Yes | Parameter `new_sub` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _update_schedule_inline_markup

# Execute call
result = await _update_schedule_inline_markup(callback=..., uid=..., new_sub=...)
```

---

### `cb_toggle_notify`
```python
async def cb_toggle_notify(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L297-L306`](../../bot/handlers/user/schedule.py#L297-L306)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_toggle_notify`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cb_toggle_notify

# Execute call
result = await cb_toggle_notify(callback=...)
```

---

### `cmd_notice`
```python
async def cmd_notice(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L310-L328`](../../bot/handlers/user/schedule.py#L310-L328)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Processes inbound Telegram slash command for `cmd_notice`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cmd_notice

# Execute call
result = await cmd_notice(message=...)
```

---

### `cb_notice_toggle`
```python
async def cb_notice_toggle(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L332-L352`](../../bot/handlers/user/schedule.py#L332-L352)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_notice_toggle`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cb_notice_toggle

# Execute call
result = await cb_notice_toggle(callback=...)
```

---

### `cb_today`
```python
async def cb_today(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L356-L372`](../../bot/handlers/user/schedule.py#L356-L372)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_today`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cb_today

# Execute call
result = await cb_today(callback=...)
```

---

### `cb_tomorrow`
```python
async def cb_tomorrow(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L376-L392`](../../bot/handlers/user/schedule.py#L376-L392)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_tomorrow`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cb_tomorrow

# Execute call
result = await cb_tomorrow(callback=...)
```

---

### `cb_week`
```python
async def cb_week(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L396-L421`](../../bot/handlers/user/schedule.py#L396-L421)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_week`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cb_week

# Execute call
result = await cb_week(callback=...)
```

---

### `_get_next_week_monday`
```python
def _get_next_week_monday() -> date
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L424-L427`](../../bot/handlers/user/schedule.py#L424-L427)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `date`

#### Overview & Architectural Purpose
Executes core domain logic for `_get_next_week_monday`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _get_next_week_monday

# Execute call
result = _get_next_week_monday()
```

---

### `cb_week_next`
```python
async def cb_week_next(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L431-L447`](../../bot/handlers/user/schedule.py#L431-L447)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_week_next`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cb_week_next

# Execute call
result = await cb_week_next(callback=...)
```

---

### `_safe_fetch_lessons_for_refresh`
```python
async def _safe_fetch_lessons_for_refresh(now: date) -> list[Lesson]
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L450-L456`](../../bot/handlers/user/schedule.py#L450-L456)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[Lesson]`

#### Overview & Architectural Purpose
Executes core domain logic for `_safe_fetch_lessons_for_refresh`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now` | `date` | Yes | Parameter `now` of type `date`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _safe_fetch_lessons_for_refresh

# Execute call
result = await _safe_fetch_lessons_for_refresh(now=...)
```

---

### `_refresh_and_format_schedule`
```python
async def _refresh_and_format_schedule(now: date) -> tuple[str, list[Lesson], int]
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L459-L469`](../../bot/handlers/user/schedule.py#L459-L469)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[str, list[Lesson], int]`

#### Overview & Architectural Purpose
Executes core domain logic for `_refresh_and_format_schedule`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now` | `date` | Yes | Parameter `now` of type `date`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _refresh_and_format_schedule

# Execute call
result = await _refresh_and_format_schedule(now=...)
```

---

### `cb_refresh`
```python
async def cb_refresh(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L473-L484`](../../bot/handlers/user/schedule.py#L473-L484)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_refresh`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cb_refresh

# Execute call
result = await cb_refresh(callback=...)
```

---

### `format_help_text`
```python
def format_help_text(is_admin: bool) -> str
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L487-L510`](../../bot/handlers/user/schedule.py#L487-L510)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_help_text`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `is_admin` | `bool` | Yes | Parameter `is_admin` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import format_help_text

# Execute call
result = format_help_text(is_admin=...)
```

---

### `cmd_help`
```python
async def cmd_help(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L514-L535`](../../bot/handlers/user/schedule.py#L514-L535)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Processes inbound Telegram slash command for `cmd_help`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cmd_help

# Execute call
result = await cmd_help(message=...)
```

---

### `handle_user_text_message`
```python
async def handle_user_text_message(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L539-L555`](../../bot/handlers/user/schedule.py#L539-L555)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `handle_user_text_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import handle_user_text_message

# Execute call
result = await handle_user_text_message(message=...)
```

---
