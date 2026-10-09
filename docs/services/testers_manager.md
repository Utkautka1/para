# Module Specification: `services/testers_manager.py`
> **Path**: [`services/testers_manager.py`](file:///home/u/Рабочий стол/para/services/testers_manager.py)  
> **Subsystem**: `Testing Whitelist`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Менеджер белого списка тестировщиков и персональных API-ключей para-api. Хранит ID тестеров в Redis и генерирует уникальные API-ключи для каждого тестера для персонального аудита запросов в логах системы.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`generate_or_get_tester_key`](#generate_or_get_tester_key) | Function | L26–L40 | `str | None` | Генерирует или возвращает существующий персональный API-ключ |
| [`get_tester_by_key`](#get_tester_by_key) | Function | L43–L54 | `int | None` | Возвращает Telegram ID тестера по переданному персональному  |
| [`add_tester`](#add_tester) | Function | L57–L65 | `bool` | Добавляет ID в белый список и сразу генерирует персональный  |
| [`remove_tester`](#remove_tester) | Function | L68–L82 | `bool` | Удаляет тестера и аннулирует его персональный API-ключ. |
| [`is_tester_allowed`](#is_tester_allowed) | Function | L85–L92 | `bool` | Проверяет доступ пользователя к тестированию Swagger UI. |
| [`get_all_testers`](#get_all_testers) | Function | L95–L104 | `list[int]` | Возвращает отсортированный список всех авторизованных тестер |

---

## 3. Exhaustive Function Specifications

### `generate_or_get_tester_key`
- **Signature**: `async def generate_or_get_tester_key(user_id: int) -> str | None`
- **Source Reference**: [services/testers_manager.py#L26-L40](file:///home/u/Рабочий стол/para/services/testers_manager.py#L26-L40)
- **Async**: `Yes`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Генерирует или возвращает существующий персональный API-ключ тестера.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `r = await get_redis()`
2. `if not r:`
3. `existing = await r.get(f"{REDIS_TESTER_UID_TO_KEY_PREFIX}{user_id}")`
4. `if existing:`
5. `new_key = f"{API_TESTER_KEY_PREFIX}{secrets.token_hex(16)}"`
6. `async with r.pipeline(transaction=True) as pipe:`

---

### `get_tester_by_key`
- **Signature**: `async def get_tester_by_key(api_key: str) -> int | None`
- **Source Reference**: [services/testers_manager.py#L43-L54](file:///home/u/Рабочий стол/para/services/testers_manager.py#L43-L54)
- **Async**: `Yes`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Возвращает Telegram ID тестера по переданному персональному API-ключу.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `api_key` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not api_key or not api_key.startswith(API_TESTER_KEY_PREFIX):`
2. `r = await get_redis()`
3. `if not r:`
4. `uid_raw = await r.get(f"{REDIS_TESTER_KEY_TO_UID_PREFIX}{api_key}")`
5. `if not uid_raw:`
6. `uid_str = uid_raw.decode() if isinstance(uid_raw, bytes) else str(uid_raw)`

---

### `add_tester`
- **Signature**: `async def add_tester(user_id: int) -> bool`
- **Source Reference**: [services/testers_manager.py#L57-L65](file:///home/u/Рабочий стол/para/services/testers_manager.py#L57-L65)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Добавляет ID в белый список и сразу генерирует персональный API-ключ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `r = await get_redis()`
2. `if not r:`
3. `await r.sadd(REDIS_TESTERS_KEY, str(user_id))`
4. `await generate_or_get_tester_key(user_id)`
5. `log.info(f"✅ Пользователь {user_id} добавлен в тестеры API с персональным ключом")`
6. `return True`

---

### `remove_tester`
- **Signature**: `async def remove_tester(user_id: int) -> bool`
- **Source Reference**: [services/testers_manager.py#L68-L82](file:///home/u/Рабочий стол/para/services/testers_manager.py#L68-L82)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Удаляет тестера и аннулирует его персональный API-ключ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if user_id in ADMIN_TESTERS:`
2. `r = await get_redis()`
3. `if not r:`
4. `key = await r.get(f"{REDIS_TESTER_UID_TO_KEY_PREFIX}{user_id}")`
5. `if key:`
6. `await r.srem(REDIS_TESTERS_KEY, str(user_id))`

---

### `is_tester_allowed`
- **Signature**: `async def is_tester_allowed(user_id: int) -> bool`
- **Source Reference**: [services/testers_manager.py#L85-L92](file:///home/u/Рабочий стол/para/services/testers_manager.py#L85-L92)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет доступ пользователя к тестированию Swagger UI.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if user_id in ADMIN_TESTERS:`
2. `r = await get_redis()`
3. `if not r:`
4. `return bool(await r.sismember(REDIS_TESTERS_KEY, str(user_id)))`

---

### `get_all_testers`
- **Signature**: `async def get_all_testers() -> list[int]`
- **Source Reference**: [services/testers_manager.py#L95-L104](file:///home/u/Рабочий стол/para/services/testers_manager.py#L95-L104)
- **Async**: `Yes`
- **Return Type**: `list[int]`

#### Purpose & Architectural Intent
Возвращает отсортированный список всех авторизованных тестеров.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `testers: set[int] = set(ADMIN_TESTERS)`
2. `r = await get_redis()`
3. `if r:`
4. `return sorted(testers)`

---
