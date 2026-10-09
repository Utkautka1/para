# Module Specification: `services/user_cache.py`
> **Path**: [`services/user_cache.py`](file:///home/u/Рабочий стол/para/services/user_cache.py)  
> **Subsystem**: `Student Identity Cache`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Сервис постоянного кэширования пользователей Telegram (username -> user_id). Сохраняет соответствия юзернеймов и цифровых Telegram ID на диск (data/user_cache.json), чтобы при перезапуске бота кэш не сбрасывался.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`clear_user_cache_memory`](#clear_user_cache_memory) | Function | L21–L26 | `None` | Сбрасывает оперативный кэш пользователей. |
| [`load_user_cache`](#load_user_cache) | Function | L29–L41 | `dict[str, int]` | Загружает кэш пользователей с in-memory буферизацией по mtim |
| [`save_user_cache`](#save_user_cache) | Function | L44–L53 | `None` | Атомарно сохраняет словарь кэша пользователей на диск и в па |
| [`get_cached_user_id`](#get_cached_user_id) | Function | L56–L59 | `int | None` | Возвращает Telegram ID из постоянного кэша по юзернейму. |
| [`add_user_to_cache`](#add_user_to_cache) | Function | L62–L71 | `None` | Добавляет пользователя в постоянный кэш и сохраняет на диск. |

---

## 3. Exhaustive Function Specifications

### `clear_user_cache_memory`
- **Signature**: `def clear_user_cache_memory() -> None`
- **Source Reference**: [services/user_cache.py#L21-L26](file:///home/u/Рабочий стол/para/services/user_cache.py#L21-L26)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сбрасывает оперативный кэш пользователей.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _USER_CACHE, _USER_CACHE_MTIME, _USER_CACHE_PATH`
2. `_USER_CACHE = None`
3. `_USER_CACHE_MTIME = 0.0`
4. `_USER_CACHE_PATH = None`

---

### `load_user_cache`
- **Signature**: `def load_user_cache() -> dict[str, int]`
- **Source Reference**: [services/user_cache.py#L29-L41](file:///home/u/Рабочий стол/para/services/user_cache.py#L29-L41)
- **Async**: `No`
- **Return Type**: `dict[str, int]`

#### Purpose & Architectural Intent
Загружает кэш пользователей с in-memory буферизацией по mtime.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _USER_CACHE, _USER_CACHE_MTIME, _USER_CACHE_PATH`
2. `try:`
3. `if _USER_CACHE is not None and _USER_CACHE_PATH == CACHE_FILE_PATH and current_mtime `
4. `_USER_CACHE = sync_load_json(CACHE_FILE_PATH, default={})`
5. `_USER_CACHE_MTIME = current_mtime`
6. `_USER_CACHE_PATH = CACHE_FILE_PATH`

---

### `save_user_cache`
- **Signature**: `def save_user_cache(cache: dict[str, int]) -> None`
- **Source Reference**: [services/user_cache.py#L44-L53](file:///home/u/Рабочий стол/para/services/user_cache.py#L44-L53)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Атомарно сохраняет словарь кэша пользователей на диск и в память.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cache` | `dict[str, int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _USER_CACHE, _USER_CACHE_MTIME, _USER_CACHE_PATH`
2. `_USER_CACHE = cache`
3. `sync_atomic_save_json(CACHE_FILE_PATH, cache)`
4. `_USER_CACHE_PATH = CACHE_FILE_PATH`
5. `try:`

---

### `get_cached_user_id`
- **Signature**: `def get_cached_user_id(username: str) -> int | None`
- **Source Reference**: [services/user_cache.py#L56-L59](file:///home/u/Рабочий стол/para/services/user_cache.py#L56-L59)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Возвращает Telegram ID из постоянного кэша по юзернейму.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `username` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `clean = username.lstrip("@").lower()`
2. `return load_user_cache().get(clean)`

---

### `add_user_to_cache`
- **Signature**: `def add_user_to_cache(username: str, user_id: int) -> None`
- **Source Reference**: [services/user_cache.py#L62-L71](file:///home/u/Рабочий стол/para/services/user_cache.py#L62-L71)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Добавляет пользователя в постоянный кэш и сохраняет на диск.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `username` | `str` | Input parameter |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not username:`
2. `clean = username.lstrip("@").lower()`
3. `cache = load_user_cache()`
4. `if cache.get(clean) != user_id:`

---
