# Component Reference: `config.py`
> **File Path**: [`config.py`](../../config.py)
> **Subsystem**: `System Configuration`

## 1. Purpose
Централизованный модуль конфигурации распределенной системы Para.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_required_env`](#get_required_env) | Function | L40–L53 | `str` | Извлекает обязательную строковую переменную из окружени... |
| [`get_env`](#get_env) | Function | L56–L65 | `str` | Извлекает опциональную строковую переменную окружения с... |
| [`get_env_int`](#get_env_int) | Function | L68–L84 | `int` | Извлекает целочисленный параметр окружения с приведение... |
| [`get_env_int_list`](#get_env_int_list) | Function | L87–L99 | `tuple[int, ...]` | Парсит разделенный запятыми список целых чисел из перем... |
| [`get_env_float`](#get_env_float) | Function | L102–L116 | `float` | Извлекает параметр с плавающей точкой с приведением тип... |
| [`get_env_list`](#get_env_list) | Function | L119–L131 | `tuple[str, ...]` | Парсит разделенный запятыми список строк из переменной ... |
| [`get_env_bool`](#get_env_bool) | Function | L134–L146 | `bool` | Парсит булево значение из переменной окружения. |

---

## 3. Comprehensive Function Specifications

### `get_required_env`
```python
def get_required_env(key: str) -> str
```

- **Source Reference**: [`config.py#L40-L53`](../../config.py#L40-L53)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Извлекает обязательную строковую переменную из окружения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from config import get_required_env

# Execute call
result = get_required_env(key=...)
```

---

### `get_env`
```python
def get_env(key: str, default: str) -> str
```

- **Source Reference**: [`config.py#L56-L65`](../../config.py#L56-L65)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Извлекает опциональную строковую переменную окружения с фолбэком.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `default` | `str` | Yes | Parameter `default` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from config import get_env

# Execute call
result = get_env(key=..., default=...)
```

---

### `get_env_int`
```python
def get_env_int(key: str, default: int | None = None) -> int
```

- **Source Reference**: [`config.py#L68-L84`](../../config.py#L68-L84)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Извлекает целочисленный параметр окружения с приведением типа.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `default` | `int | None` | Yes | Parameter `default` of type `int | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from config import get_env_int

# Execute call
result = get_env_int(key=..., default=...)
```

---

### `get_env_int_list`
```python
def get_env_int_list(key: str, default: tuple[int, ...] = ()) -> tuple[int, ...]
```

- **Source Reference**: [`config.py#L87-L99`](../../config.py#L87-L99)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[int, ...]`

#### Overview & Architectural Purpose
Парсит разделенный запятыми список целых чисел из переменной окружения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `default` | `tuple[int, ...]` | Yes | Parameter `default` of type `tuple[int, ...]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from config import get_env_int_list

# Execute call
result = get_env_int_list(key=..., default=...)
```

---

### `get_env_float`
```python
def get_env_float(key: str, default: float | None = None) -> float
```

- **Source Reference**: [`config.py#L102-L116`](../../config.py#L102-L116)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `float`

#### Overview & Architectural Purpose
Извлекает параметр с плавающей точкой с приведением типа.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `default` | `float | None` | Yes | Parameter `default` of type `float | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from config import get_env_float

# Execute call
result = get_env_float(key=..., default=...)
```

---

### `get_env_list`
```python
def get_env_list(key: str, default: tuple[str, ...] = ()) -> tuple[str, ...]
```

- **Source Reference**: [`config.py#L119-L131`](../../config.py#L119-L131)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, ...]`

#### Overview & Architectural Purpose
Парсит разделенный запятыми список строк из переменной окружения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `default` | `tuple[str, ...]` | Yes | Parameter `default` of type `tuple[str, ...]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from config import get_env_list

# Execute call
result = get_env_list(key=..., default=...)
```

---

### `get_env_bool`
```python
def get_env_bool(key: str, default: bool = False) -> bool
```

- **Source Reference**: [`config.py#L134-L146`](../../config.py#L134-L146)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Парсит булево значение из переменной окружения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `default` | `bool` | Yes | Parameter `default` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from config import get_env_bool

# Execute call
result = get_env_bool(key=..., default=...)
```

---
