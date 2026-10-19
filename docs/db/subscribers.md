# Component Reference: `db/subscribers.py`
> **File Path**: [`db/subscribers.py`](../../db/subscribers.py)
> **Subsystem**: `Subscriber Store`
> **Architecture Layer**: `Enterprise Microservice Subsystem`
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`
> **Persistence Backend**: `Redis 7 Persistent Store`
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `db/subscribers.py` module implements core operational logic for the `Subscriber Store` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

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
| [`_query_sqlite_subscribers`](#_query_sqlite_subscribers) | Function | L18–L30 | `set[int] | None` | Executes core domain logic for `_query_sqlite_subscribe... |
| [`_update_sqlite_subscriber`](#_update_sqlite_subscriber) | Function | L33–L49 | `None` | Executes core domain logic for `_update_sqlite_subscrib... |
| [`load_subscribers`](#load_subscribers) | Function | L52–L58 | `set[int]` | Executes core domain logic for `load_subscribers`. |
| [`save_subscribers`](#save_subscribers) | Function | L61–L68 | `bool` | Saves serialized entity data to storage for `save_subsc... |
| [`add_subscriber`](#add_subscriber) | Function | L71–L80 | `bool` | Executes core domain logic for `add_subscriber`. |
| [`remove_subscriber`](#remove_subscriber) | Function | L83–L92 | `bool` | Executes core domain logic for `remove_subscriber`. |
| [`is_subscribed`](#is_subscribed) | Function | L95–L97 | `bool` | Executes core domain logic for `is_subscribed`. |
| [`toggle_subscriber`](#toggle_subscriber) | Function | L100–L109 | `bool` | Executes core domain logic for `toggle_subscriber`. |

---

## 3. Comprehensive Function Specifications

### `_query_sqlite_subscribers`
```python
def _query_sqlite_subscribers() -> set[int] | None
```

- **Source Reference**: [`db/subscribers.py#L18-L30`](../../db/subscribers.py#L18-L30)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `set[int] | None`

#### Overview & Architectural Purpose
Executes core domain logic for `_query_sqlite_subscribers`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from db.subscribers import _query_sqlite_subscribers

# Execute call
result = _query_sqlite_subscribers()
```

---

### `_update_sqlite_subscriber`
```python
def _update_sqlite_subscriber(chat_id: int, is_active: bool) -> None
```

- **Source Reference**: [`db/subscribers.py#L33-L49`](../../db/subscribers.py#L33-L49)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_update_sqlite_subscriber`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `is_active` | `bool` | Yes | Parameter `is_active` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from db.subscribers import _update_sqlite_subscriber

# Execute call
result = _update_sqlite_subscriber(chat_id=..., is_active=...)
```

---

### `load_subscribers`
```python
def load_subscribers() -> set[int]
```

- **Source Reference**: [`db/subscribers.py#L52-L58`](../../db/subscribers.py#L52-L58)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `set[int]`

#### Overview & Architectural Purpose
Executes core domain logic for `load_subscribers`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from db.subscribers import load_subscribers

# Execute call
result = load_subscribers()
```

---

### `save_subscribers`
```python
def save_subscribers(subs: set[int]) -> bool
```

- **Source Reference**: [`db/subscribers.py#L61-L68`](../../db/subscribers.py#L61-L68)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Saves serialized entity data to storage for `save_subscribers`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `subs` | `set[int]` | Yes | Parameter `subs` of type `set[int]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from db.subscribers import save_subscribers

# Execute call
result = save_subscribers(subs=...)
```

---

### `add_subscriber`
```python
def add_subscriber(chat_id: int) -> bool
```

- **Source Reference**: [`db/subscribers.py#L71-L80`](../../db/subscribers.py#L71-L80)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `add_subscriber`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from db.subscribers import add_subscriber

# Execute call
result = add_subscriber(chat_id=...)
```

---

### `remove_subscriber`
```python
def remove_subscriber(chat_id: int) -> bool
```

- **Source Reference**: [`db/subscribers.py#L83-L92`](../../db/subscribers.py#L83-L92)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `remove_subscriber`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from db.subscribers import remove_subscriber

# Execute call
result = remove_subscriber(chat_id=...)
```

---

### `is_subscribed`
```python
def is_subscribed(chat_id: int) -> bool
```

- **Source Reference**: [`db/subscribers.py#L95-L97`](../../db/subscribers.py#L95-L97)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `is_subscribed`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from db.subscribers import is_subscribed

# Execute call
result = is_subscribed(chat_id=...)
```

---

### `toggle_subscriber`
```python
def toggle_subscriber(chat_id: int) -> bool
```

- **Source Reference**: [`db/subscribers.py#L100-L109`](../../db/subscribers.py#L100-L109)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `toggle_subscriber`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from db.subscribers import toggle_subscriber

# Execute call
result = toggle_subscriber(chat_id=...)
```

---
