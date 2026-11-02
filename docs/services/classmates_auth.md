# Component Reference: `services/classmates_auth.py`
> **File Path**: [`services/classmates_auth.py`](../../services/classmates_auth.py)
> **Subsystem**: `RBAC Security`

## 1. Purpose
Сервис аутентификации и разовой регистрации одногруппников группы 1-КПД-3.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`clear_registry_cache`](#clear_registry_cache) | Function | L32–L43 | `None` | Сбрасывает оперативный кэш реестра одногруппников в пам... |
| [`load_classmates_registry`](#load_classmates_registry) | Function | L46–L64 | `list[dict[str, Any]]` | Загружает актуальный список студентов группы с кэширова... |
| [`find_classmate_by_tg_id`](#find_classmate_by_tg_id) | Function | L67–L80 | `dict[str, Any] \| None` | Ищет студента в реестре группы по сохраненному числовом... |
| [`find_classmate_by_fio`](#find_classmate_by_fio) | Function | L83–L99 | `dict[str, Any] \| None` | Ищет студента в реестре группы по ФИО из журнала посеща... |
| [`_find_student_by_fullname`](#_find_student_by_fullname) | Function | L102–L113 | `dict[str, Any] \| None` | Ищет запись студента в реестре по нормализованному ФИО. |
| [`_bind_in_registry`](#_bind_in_registry) | Function | L116–L133 | `dict[str, Any] \| None` | Привязывает tg_id к студенту прямо в файле реестра (син... |
| [`bind_student_tg_id`](#bind_student_tg_id) | Function | L136–L155 | `dict[str, Any] \| None` | Привязывает Telegram ID к студенту по полному ФИО (для ... |
| [`is_authorized_user`](#is_authorized_user) | Function | L158–L171 | `bool` | Проверяет наличие прав доступа к функционалу бота у вхо... |
| [`process_user_auth`](#process_user_auth) | Function | L174–L190 | `tuple[bool, bool, dict[str, Any] \| None]` | Выполняет комплексную проверку статуса авторизации вход... |

---

## 3. Comprehensive Function Specifications

### `clear_registry_cache`
```python
def clear_registry_cache() -> None
```

- **Source Reference**: [`services/classmates_auth.py#L32-L43`](../../services/classmates_auth.py#L32-L43)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сбрасывает оперативный кэш реестра одногруппников в памяти.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.classmates_auth import clear_registry_cache

# Execute call
result = clear_registry_cache()
```

---

### `load_classmates_registry`
```python
def load_classmates_registry(force_reload: bool = False) -> list[dict[str, Any]]
```

- **Source Reference**: [`services/classmates_auth.py#L46-L64`](../../services/classmates_auth.py#L46-L64)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[dict[str, Any]]`

#### Overview & Architectural Purpose
Загружает актуальный список студентов группы с кэшированием в RAM по mtime.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_reload` | `bool` | Yes | Parameter `force_reload` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.classmates_auth import load_classmates_registry

# Execute call
result = load_classmates_registry(force_reload=...)
```

---

### `find_classmate_by_tg_id`
```python
def find_classmate_by_tg_id(user_id: int) -> dict[str, Any] | None
```

- **Source Reference**: [`services/classmates_auth.py#L67-L80`](../../services/classmates_auth.py#L67-L80)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any] | None`

#### Overview & Architectural Purpose
Ищет студента в реестре группы по сохраненному числовому Telegram ID.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.classmates_auth import find_classmate_by_tg_id

# Execute call
result = find_classmate_by_tg_id(user_id=...)
```

---

### `find_classmate_by_fio`
```python
def find_classmate_by_fio(fio: str) -> dict[str, Any] | None
```

- **Source Reference**: [`services/classmates_auth.py#L83-L99`](../../services/classmates_auth.py#L83-L99)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any] | None`

#### Overview & Architectural Purpose
Ищет студента в реестре группы по ФИО из журнала посещаемости.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.classmates_auth import find_classmate_by_fio

# Execute call
result = find_classmate_by_fio(fio=...)
```

---

### `_find_student_by_fullname`
```python
def _find_student_by_fullname(registry: list[dict[str, Any]], target_clean: str) -> dict[str, Any] | None
```

- **Source Reference**: [`services/classmates_auth.py#L102-L113`](../../services/classmates_auth.py#L102-L113)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any] | None`

#### Overview & Architectural Purpose
Ищет запись студента в реестре по нормализованному ФИО.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `registry` | `list[dict[str, Any]]` | Yes | Parameter `registry` of type `list[dict[str, Any]]`. |
| `target_clean` | `str` | Yes | Parameter `target_clean` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.classmates_auth import _find_student_by_fullname

# Execute call
result = _find_student_by_fullname(registry=..., target_clean=...)
```

---

### `_bind_in_registry`
```python
def _bind_in_registry(full_name: str, tg_id: int) -> dict[str, Any] | None
```

- **Source Reference**: [`services/classmates_auth.py#L116-L133`](../../services/classmates_auth.py#L116-L133)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any] | None`

#### Overview & Architectural Purpose
Привязывает tg_id к студенту прямо в файле реестра (синхронно, для to_thread).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `full_name` | `str` | Yes | Parameter `full_name` of type `str`. |
| `tg_id` | `int` | Yes | Telegram user identifier for identity verification. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.classmates_auth import _bind_in_registry

# Execute call
result = _bind_in_registry(full_name=..., tg_id=...)
```

---

### `bind_student_tg_id`
```python
async def bind_student_tg_id(full_name: str, tg_id: int) -> dict[str, Any] | None
```

- **Source Reference**: [`services/classmates_auth.py#L136-L155`](../../services/classmates_auth.py#L136-L155)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, Any] | None`

#### Overview & Architectural Purpose
Привязывает Telegram ID к студенту по полному ФИО (для пользователей без @username).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `full_name` | `str` | Yes | Parameter `full_name` of type `str`. |
| `tg_id` | `int` | Yes | Telegram user identifier for identity verification. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.classmates_auth import bind_student_tg_id

# Execute call
result = await bind_student_tg_id(full_name=..., tg_id=...)
```

---

### `is_authorized_user`
```python
def is_authorized_user(user: User | None) -> bool
```

- **Source Reference**: [`services/classmates_auth.py#L158-L171`](../../services/classmates_auth.py#L158-L171)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет наличие прав доступа к функционалу бота у входящего пользователя.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user` | `User | None` | Yes | Parameter `user` of type `User | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.classmates_auth import is_authorized_user

# Execute call
result = is_authorized_user(user=...)
```

---

### `process_user_auth`
```python
def process_user_auth(user: User | None) -> tuple[bool, bool, dict[str, Any] | None]
```

- **Source Reference**: [`services/classmates_auth.py#L174-L190`](../../services/classmates_auth.py#L174-L190)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[bool, bool, dict[str, Any] | None]`

#### Overview & Architectural Purpose
Выполняет комплексную проверку статуса авторизации входящего пользователя.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user` | `User | None` | Yes | Parameter `user` of type `User | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.classmates_auth import process_user_auth

# Execute call
result = process_user_auth(user=...)
```

---
