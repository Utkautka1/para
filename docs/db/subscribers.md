# Component Reference: `db/subscribers.py`
> **File Path**: [`db/subscribers.py`](../../db/subscribers.py)
> **Subsystem**: `Subscriber Store`

## 1. Purpose
Модуль персистентного хранения подписчиков бота с поддержкой SQLite (WAL) и JSON-фолбэка.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_query_sqlite_subscribers`](#_query_sqlite_subscribers) | Function | L18–L30 | `set[int] \| None` | Извлекает активных подписчиков из базы данных SQLite. |
| [`_update_sqlite_subscriber`](#_update_sqlite_subscriber) | Function | L33–L49 | `None` | Атомарно обновляет статус подписчика в SQLite. |
| [`load_subscribers`](#load_subscribers) | Function | L52–L58 | `set[int]` | Загружает множество идентификаторов подписчиков из SQLi... |
| [`save_subscribers`](#save_subscribers) | Function | L61–L68 | `bool` | Сохраняет актуальное множество подписчиков в JSON-файл ... |
| [`add_subscriber`](#add_subscriber) | Function | L71–L80 | `bool` | Добавляет новый идентификатор чата в список активных по... |
| [`remove_subscriber`](#remove_subscriber) | Function | L83–L92 | `bool` | Удаляет идентификатор чата из списка получателей рассыл... |
| [`is_subscribed`](#is_subscribed) | Function | L95–L97 | `bool` | Проверяет, подписан ли пользователь на персональные уве... |
| [`toggle_subscriber`](#toggle_subscriber) | Function | L100–L109 | `bool` | Переключает статус подписки пользователя на противополо... |

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
Извлекает активных подписчиков из базы данных SQLite.

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
Атомарно обновляет статус подписчика в SQLite.

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
Загружает множество идентификаторов подписчиков из SQLite с фолбэком на JSON.

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
Сохраняет актуальное множество подписчиков в JSON-файл и SQLite.

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
Добавляет новый идентификатор чата в список активных подписчиков.

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
Удаляет идентификатор чата из списка получателей рассылки.

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
Проверяет, подписан ли пользователь на персональные уведомления в ЛС.

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
Переключает статус подписки пользователя на противоположный (Toggle).

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
