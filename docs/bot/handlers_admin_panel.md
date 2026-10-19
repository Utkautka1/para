# Component Reference: `bot/handlers/admin/panel.py`
> **File Path**: [`bot/handlers/admin/panel.py`](../../bot/handlers/admin/panel.py)  
> **Subsystem**: `Admin Control Panel`  
> **Architecture Layer**: `Enterprise Microservice Subsystem`  
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`  
> **Persistence Backend**: `Redis 7 Persistent Store`  
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `bot/handlers/admin/panel.py` module implements core operational logic for the `Admin Control Panel` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

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
| [`_ack_admin_callback`](#_ack_admin_callback) | Function | L39–L55 | `None` | Executes core domain logic for `_ack_admin_callback`. |
| [`_safe_edit_admin_message`](#_safe_edit_admin_message) | Function | L58–L80 | `None` | Executes core domain logic for `_safe_edit_admin_messag... |
| [`format_admin_panel_text`](#format_admin_panel_text) | Function | L83–L102 | `str` | Formats message payload and presentation markup for `fo... |
| [`cb_admin_menu`](#cb_admin_menu) | Function | L107–L125 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_sync`](#cb_admin_sync) | Function | L129–L148 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`_get_redis_memory_stat`](#_get_redis_memory_stat) | Function | L151–L171 | `str` | Executes core domain logic for `_get_redis_memory_stat`... |
| [`_collect_health_summary`](#_collect_health_summary) | Function | L174–L206 | `str` | Executes core domain logic for `_collect_health_summary... |
| [`cb_admin_status`](#cb_admin_status) | Function | L210–L222 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_force_topic`](#cb_admin_force_topic) | Function | L226–L240 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_recreate_topic`](#cb_admin_recreate_topic) | Function | L244–L260 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_force_exam`](#cb_admin_force_exam) | Function | L264–L280 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_recreate_exam`](#cb_admin_recreate_exam) | Function | L284–L300 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_force_att_topic`](#cb_admin_force_att_topic) | Function | L304–L320 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_recreate_att_topic`](#cb_admin_recreate_att_topic) | Function | L324–L340 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`_build_custom_teachers_view`](#_build_custom_teachers_view) | Function | L343–L367 | `tuple[str, list]` | Executes core domain logic for `_build_custom_teachers_... |
| [`cb_admin_list_custom`](#cb_admin_list_custom) | Function | L371–L387 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_delete_teacher`](#cb_admin_delete_teacher) | Function | L391–L408 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_edit_teacher`](#cb_admin_edit_teacher) | Function | L412–L437 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_start_add_teacher`](#cb_admin_start_add_teacher) | Function | L441–L461 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`msg_admin_got_teacher_name`](#msg_admin_got_teacher_name) | Function | L465–L484 | `None` | Executes core domain logic for `msg_admin_got_teacher_n... |
| [`msg_admin_got_teacher_link`](#msg_admin_got_teacher_link) | Function | L488–L513 | `None` | Executes core domain logic for `msg_admin_got_teacher_l... |
| [`_build_unbound_students_kb`](#_build_unbound_students_kb) | Function | L516–L538 | `InlineKeyboardMarkup` | Executes core domain logic for `_build_unbound_students... |
| [`cb_admin_list_students_for_binding`](#cb_admin_list_students_for_binding) | Function | L542–L571 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`cb_admin_select_student`](#cb_admin_select_student) | Function | L575–L599 | `None` | Handles Telegram inline callback query events for `cb_a... |
| [`msg_admin_got_student_id`](#msg_admin_got_student_id) | Function | L603–L629 | `None` | Executes core domain logic for `msg_admin_got_student_i... |

---

## 3. Comprehensive Function Specifications

## Class Model: `AddTeacherState`

Encapsulates domain entities and data transfer logic for `AddTeacherState`.

## Class Model: `BindStudentState`

Encapsulates domain entities and data transfer logic for `BindStudentState`.

### `_ack_admin_callback`
```python
async def _ack_admin_callback(callback: CallbackQuery, text: str | None = None) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L39-L55`](../../bot/handlers/admin/panel.py#L39-L55)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_ack_admin_callback`.

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
from bot.handlers.admin.panel import _ack_admin_callback

# Execute call
result = await _ack_admin_callback(callback=..., text=...)
```

---

### `_safe_edit_admin_message`
```python
async def _safe_edit_admin_message( message: Message | None, text: str, reply_markup: InlineKeyboardMarkup | None = None ) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L58-L80`](../../bot/handlers/admin/panel.py#L58-L80)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_safe_edit_admin_message`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message | None` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `reply_markup` | `InlineKeyboardMarkup | None` | Yes | Parameter `reply_markup` of type `InlineKeyboardMarkup | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _safe_edit_admin_message

# Execute call
result = await _safe_edit_admin_message(message=..., text=..., reply_markup=...)
```

---

### `format_admin_panel_text`
```python
def format_admin_panel_text(status_note: str = "") -> str
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L83-L102`](../../bot/handlers/admin/panel.py#L83-L102)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Formats message payload and presentation markup for `format_admin_panel_text`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `status_note` | `str` | Yes | Parameter `status_note` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import format_admin_panel_text

# Execute call
result = format_admin_panel_text(status_note=...)
```

---

### `cb_admin_menu`
```python
async def cb_admin_menu(event: Message | CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L107-L125`](../../bot/handlers/admin/panel.py#L107-L125)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_menu`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `event` | `Message | CallbackQuery` | Yes | Parameter `event` of type `Message | CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_menu

# Execute call
result = await cb_admin_menu(event=...)
```

---

### `cb_admin_sync`
```python
async def cb_admin_sync(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L129-L148`](../../bot/handlers/admin/panel.py#L129-L148)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_sync`.

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
from bot.handlers.admin.panel import cb_admin_sync

# Execute call
result = await cb_admin_sync(callback=...)
```

---

### `_get_redis_memory_stat`
```python
async def _get_redis_memory_stat() -> str
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L151-L171`](../../bot/handlers/admin/panel.py#L151-L171)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Executes core domain logic for `_get_redis_memory_stat`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _get_redis_memory_stat

# Execute call
result = await _get_redis_memory_stat()
```

---

### `_collect_health_summary`
```python
async def _collect_health_summary() -> str
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L174-L206`](../../bot/handlers/admin/panel.py#L174-L206)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Executes core domain logic for `_collect_health_summary`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _collect_health_summary

# Execute call
result = await _collect_health_summary()
```

---

### `cb_admin_status`
```python
async def cb_admin_status(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L210-L222`](../../bot/handlers/admin/panel.py#L210-L222)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_status`.

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
from bot.handlers.admin.panel import cb_admin_status

# Execute call
result = await cb_admin_status(callback=...)
```

---

### `cb_admin_force_topic`
```python
async def cb_admin_force_topic(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L226-L240`](../../bot/handlers/admin/panel.py#L226-L240)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_force_topic`.

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
from bot.handlers.admin.panel import cb_admin_force_topic

# Execute call
result = await cb_admin_force_topic(callback=...)
```

---

### `cb_admin_recreate_topic`
```python
async def cb_admin_recreate_topic(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L244-L260`](../../bot/handlers/admin/panel.py#L244-L260)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_recreate_topic`.

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
from bot.handlers.admin.panel import cb_admin_recreate_topic

# Execute call
result = await cb_admin_recreate_topic(callback=...)
```

---

### `cb_admin_force_exam`
```python
async def cb_admin_force_exam(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L264-L280`](../../bot/handlers/admin/panel.py#L264-L280)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_force_exam`.

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
from bot.handlers.admin.panel import cb_admin_force_exam

# Execute call
result = await cb_admin_force_exam(callback=...)
```

---

### `cb_admin_recreate_exam`
```python
async def cb_admin_recreate_exam(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L284-L300`](../../bot/handlers/admin/panel.py#L284-L300)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_recreate_exam`.

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
from bot.handlers.admin.panel import cb_admin_recreate_exam

# Execute call
result = await cb_admin_recreate_exam(callback=...)
```

---

### `cb_admin_force_att_topic`
```python
async def cb_admin_force_att_topic(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L304-L320`](../../bot/handlers/admin/panel.py#L304-L320)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_force_att_topic`.

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
from bot.handlers.admin.panel import cb_admin_force_att_topic

# Execute call
result = await cb_admin_force_att_topic(callback=...)
```

---

### `cb_admin_recreate_att_topic`
```python
async def cb_admin_recreate_att_topic(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L324-L340`](../../bot/handlers/admin/panel.py#L324-L340)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_recreate_att_topic`.

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
from bot.handlers.admin.panel import cb_admin_recreate_att_topic

# Execute call
result = await cb_admin_recreate_att_topic(callback=...)
```

---

### `_build_custom_teachers_view`
```python
def _build_custom_teachers_view(custom: dict) -> tuple[str, list]
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L343-L367`](../../bot/handlers/admin/panel.py#L343-L367)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, list]`

#### Overview & Architectural Purpose
Executes core domain logic for `_build_custom_teachers_view`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `custom` | `dict` | Yes | Parameter `custom` of type `dict`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _build_custom_teachers_view

# Execute call
result = _build_custom_teachers_view(custom=...)
```

---

### `cb_admin_list_custom`
```python
async def cb_admin_list_custom(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L371-L387`](../../bot/handlers/admin/panel.py#L371-L387)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_list_custom`.

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
from bot.handlers.admin.panel import cb_admin_list_custom

# Execute call
result = await cb_admin_list_custom(callback=...)
```

---

### `cb_admin_delete_teacher`
```python
async def cb_admin_delete_teacher(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L391-L408`](../../bot/handlers/admin/panel.py#L391-L408)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_delete_teacher`.

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
from bot.handlers.admin.panel import cb_admin_delete_teacher

# Execute call
result = await cb_admin_delete_teacher(callback=...)
```

---

### `cb_admin_edit_teacher`
```python
async def cb_admin_edit_teacher(callback: CallbackQuery, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L412-L437`](../../bot/handlers/admin/panel.py#L412-L437)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_edit_teacher`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_edit_teacher

# Execute call
result = await cb_admin_edit_teacher(callback=..., state=...)
```

---

### `cb_admin_start_add_teacher`
```python
async def cb_admin_start_add_teacher(callback: CallbackQuery, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L441-L461`](../../bot/handlers/admin/panel.py#L441-L461)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_start_add_teacher`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_start_add_teacher

# Execute call
result = await cb_admin_start_add_teacher(callback=..., state=...)
```

---

### `msg_admin_got_teacher_name`
```python
async def msg_admin_got_teacher_name(message: Message, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L465-L484`](../../bot/handlers/admin/panel.py#L465-L484)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `msg_admin_got_teacher_name`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import msg_admin_got_teacher_name

# Execute call
result = await msg_admin_got_teacher_name(message=..., state=...)
```

---

### `msg_admin_got_teacher_link`
```python
async def msg_admin_got_teacher_link(message: Message, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L488-L513`](../../bot/handlers/admin/panel.py#L488-L513)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `msg_admin_got_teacher_link`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import msg_admin_got_teacher_link

# Execute call
result = await msg_admin_got_teacher_link(message=..., state=...)
```

---

### `_build_unbound_students_kb`
```python
def _build_unbound_students_kb() -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L516-L538`](../../bot/handlers/admin/panel.py#L516-L538)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Executes core domain logic for `_build_unbound_students_kb`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _build_unbound_students_kb

# Execute call
result = _build_unbound_students_kb()
```

---

### `cb_admin_list_students_for_binding`
```python
async def cb_admin_list_students_for_binding(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L542-L571`](../../bot/handlers/admin/panel.py#L542-L571)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_list_students_for_binding`.

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
from bot.handlers.admin.panel import cb_admin_list_students_for_binding

# Execute call
result = await cb_admin_list_students_for_binding(callback=...)
```

---

### `cb_admin_select_student`
```python
async def cb_admin_select_student(callback: CallbackQuery, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L575-L599`](../../bot/handlers/admin/panel.py#L575-L599)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Handles Telegram inline callback query events for `cb_admin_select_student`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_select_student

# Execute call
result = await cb_admin_select_student(callback=..., state=...)
```

---

### `msg_admin_got_student_id`
```python
async def msg_admin_got_student_id(message: Message, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L603-L629`](../../bot/handlers/admin/panel.py#L603-L629)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `msg_admin_got_student_id`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import msg_admin_got_student_id

# Execute call
result = await msg_admin_got_student_id(message=..., state=...)
```

---
