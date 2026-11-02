# Component Reference: `services/user_cache.py`
> **File Path**: [`services/user_cache.py`](../../services/user_cache.py)
> **Subsystem**: `Student Identity Cache`

## 1. Purpose
Сервис постоянного кэширования пользователей Telegram (username -> user_id).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`clear_user_cache_memory`](#clear_user_cache_memory) | Function | L21–L33 | `None` | Сбрасывает оперативный in-memory буфер сопоставлений юз... |
| [`load_user_cache`](#load_user_cache) | Function | L36–L55 | `dict[str, int]` | Загружает словарь сопоставлений username -> user_id с п... |
| [`save_user_cache`](#save_user_cache) | Function | L58–L74 | `None` | Атомарно сохраняет словарь сопоставлений пользователей ... |
| [`get_cached_user_id`](#get_cached_user_id) | Function | L77–L87 | `int \| None` | Возвращает цифровой Telegram user_id по текстовому юзер... |
| [`add_user_to_cache`](#add_user_to_cache) | Function | L90–L106 | `None` | Добавляет связку юзернейма и ID пользователя в персисте... |

---

## 3. Comprehensive Function Specifications

### `clear_user_cache_memory`
```python
def clear_user_cache_memory() -> None
```

- **Source Reference**: [`services/user_cache.py#L21-L33`](../../services/user_cache.py#L21-L33)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сбрасывает оперативный in-memory буфер сопоставлений юзернеймов и ID.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.user_cache import clear_user_cache_memory

# Execute call
result = clear_user_cache_memory()
```

---

### `load_user_cache`
```python
def load_user_cache() -> dict[str, int]
```

- **Source Reference**: [`services/user_cache.py#L36-L55`](../../services/user_cache.py#L36-L55)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, int]`

#### Overview & Architectural Purpose
Загружает словарь сопоставлений username -> user_id с проверкой mtime файла.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.user_cache import load_user_cache

# Execute call
result = load_user_cache()
```

---

### `save_user_cache`
```python
def save_user_cache(cache: dict[str, int]) -> None
```

- **Source Reference**: [`services/user_cache.py#L58-L74`](../../services/user_cache.py#L58-L74)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Атомарно сохраняет словарь сопоставлений пользователей на диск и в память.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cache` | `dict[str, int]` | Yes | Parameter `cache` of type `dict[str, int]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.user_cache import save_user_cache

# Execute call
result = save_user_cache(cache=...)
```

---

### `get_cached_user_id`
```python
def get_cached_user_id(username: str) -> int | None
```

- **Source Reference**: [`services/user_cache.py#L77-L87`](../../services/user_cache.py#L77-L87)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Возвращает цифровой Telegram user_id по текстовому юзернейму.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `username` | `str` | Yes | Parameter `username` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.user_cache import get_cached_user_id

# Execute call
result = get_cached_user_id(username=...)
```

---

### `add_user_to_cache`
```python
def add_user_to_cache(username: str, user_id: int) -> None
```

- **Source Reference**: [`services/user_cache.py#L90-L106`](../../services/user_cache.py#L90-L106)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет связку юзернейма и ID пользователя в персистентный кэш.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `username` | `str` | Yes | Parameter `username` of type `str`. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.user_cache import add_user_to_cache

# Execute call
result = add_user_to_cache(username=..., user_id=...)
```

---
