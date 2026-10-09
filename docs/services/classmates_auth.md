# Module Specification: `services/classmates_auth.py`
> **Path**: [`services/classmates_auth.py`](file:///home/u/Рабочий стол/para/services/classmates_auth.py)  
> **Subsystem**: `RBAC Security`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Сервис аутентификации и разовой регистрации одногруппников группы 1-КПД-3. Отвечает за: 1. Проверку принадлежности пользователя к группе (ALLOWED_USER_ID или реестр). 2. Разовую фиксацию цифрового Telegram ID при первом нажатии /start в ЛС бота. 3. Сохранение привязки в data/birthdays.json и постоянный кэш user_cache. 4. Защиту от несанкционированного доступа посторонних пользователей.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`clear_registry_cache`](#clear_registry_cache) | Function | L28–L32 | `None` | Сбрасывает кэш реестра одногруппников в оперативной памяти. |
| [`load_classmates_registry`](#load_classmates_registry) | Function | L35–L50 | `list[dict[str, Any]]` | Загружает актуальный список студентов с in-memory кэшировани |
| [`find_classmate_by_tg_id`](#find_classmate_by_tg_id) | Function | L53–L64 | `dict[str, Any] | None` | Ищет студента в реестре по его сохраненному Telegram ID. |
| [`find_unregistered_by_username`](#find_unregistered_by_username) | Function | L67–L80 | `dict[str, Any] | None` | Ищет студента по юзернейму, у которого еще не зафиксирован t |
| [`update_classmate_tg_id`](#update_classmate_tg_id) | Function | L83–L105 | `dict[str, Any] | None` | Атомарно фиксирует Telegram ID студента в birthdays.json и к |
| [`bind_student_tg_id`](#bind_student_tg_id) | Function | L108–L125 | `dict[str, Any] | None` | Привязывает Telegram ID к студенту по ФИО для студентов без  |
| [`is_authorized_user`](#is_authorized_user) | Function | L128–L139 | `bool` | Проверяет, авторизован ли пользователь (Администратор или ст |
| [`process_user_auth`](#process_user_auth) | Function | L142–L156 | `tuple[bool, bool, dict[str, Any] | None]` | Основная логика аутентификации пользователя при входе в бота |

---

## 3. Exhaustive Function Specifications

### `clear_registry_cache`
- **Signature**: `def clear_registry_cache() -> None`
- **Source Reference**: [services/classmates_auth.py#L28-L32](file:///home/u/Рабочий стол/para/services/classmates_auth.py#L28-L32)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сбрасывает кэш реестра одногруппников в оперативной памяти.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _REGISTRY_CACHE, _REGISTRY_MTIME`
2. `_REGISTRY_CACHE = None`
3. `_REGISTRY_MTIME = 0.0`

---

### `load_classmates_registry`
- **Signature**: `def load_classmates_registry(force_reload: bool = False) -> list[dict[str, Any]]`
- **Source Reference**: [services/classmates_auth.py#L35-L50](file:///home/u/Рабочий стол/para/services/classmates_auth.py#L35-L50)
- **Async**: `No`
- **Return Type**: `list[dict[str, Any]]`

#### Purpose & Architectural Intent
Загружает актуальный список студентов с in-memory кэшированием по mtime. Исключает дисковый I/O на каждый callback, возвращая срез из RAM.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_reload` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _REGISTRY_CACHE, _REGISTRY_MTIME`
2. `try:`
3. `if not force_reload and _REGISTRY_CACHE is not None and current_mtime == _REGISTRY_MT`
4. `_REGISTRY_CACHE = sync_load_json(BIRTHDAYS_FILE_PATH, default=[])`
5. `_REGISTRY_MTIME = current_mtime`
6. `return _REGISTRY_CACHE`

---

### `find_classmate_by_tg_id`
- **Signature**: `def find_classmate_by_tg_id(user_id: int) -> dict[str, Any] | None`
- **Source Reference**: [services/classmates_auth.py#L53-L64](file:///home/u/Рабочий стол/para/services/classmates_auth.py#L53-L64)
- **Async**: `No`
- **Return Type**: `dict[str, Any] | None`

#### Purpose & Architectural Intent
Ищет студента в реестре по его сохраненному Telegram ID. :param user_id: Числовой ID пользователя в Telegram :return: Словарь с данными студента или None

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `registry = load_classmates_registry()`
2. `for student in registry:`
3. `return None`

---

### `find_unregistered_by_username`
- **Signature**: `def find_unregistered_by_username(username: str) -> dict[str, Any] | None`
- **Source Reference**: [services/classmates_auth.py#L67-L80](file:///home/u/Рабочий стол/para/services/classmates_auth.py#L67-L80)
- **Async**: `No`
- **Return Type**: `dict[str, Any] | None`

#### Purpose & Architectural Intent
Ищет студента по юзернейму, у которого еще не зафиксирован tg_id (None). :param username: Юзернейм пользователя без префикса @ :return: Словарь с данными студента или None

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `username` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `clean = username.lstrip("@").lower()`
2. `registry = load_classmates_registry()`
3. `for student in registry:`
4. `return None`

---

### `update_classmate_tg_id`
- **Signature**: `def update_classmate_tg_id(clean_username: str, tg_id: int) -> dict[str, Any] | None`
- **Source Reference**: [services/classmates_auth.py#L83-L105](file:///home/u/Рабочий стол/para/services/classmates_auth.py#L83-L105)
- **Async**: `No`
- **Return Type**: `dict[str, Any] | None`

#### Purpose & Architectural Intent
Атомарно фиксирует Telegram ID студента в birthdays.json и кэше. Выполняется разово при первой авторизации по совпадению юзернейма.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `clean_username` | `str` | Input parameter |
| `tg_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `registry = load_classmates_registry()`
2. `updated_student = None`
3. `for student in registry:`
4. `if updated_student:`
5. `return updated_student`

---

### `bind_student_tg_id`
- **Signature**: `def bind_student_tg_id(full_name: str, tg_id: int) -> dict[str, Any] | None`
- **Source Reference**: [services/classmates_auth.py#L108-L125](file:///home/u/Рабочий стол/para/services/classmates_auth.py#L108-L125)
- **Async**: `No`
- **Return Type**: `dict[str, Any] | None`

#### Purpose & Architectural Intent
Привязывает Telegram ID к студенту по ФИО для студентов без username.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `full_name` | `str` | Input parameter |
| `tg_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `registry = load_classmates_registry()`
2. `target_clean = full_name.strip().lower()`
3. `updated = None`
4. `for student in registry:`
5. `if updated:`
6. `return updated`

---

### `is_authorized_user`
- **Signature**: `def is_authorized_user(user: User | None) -> bool`
- **Source Reference**: [services/classmates_auth.py#L128-L139](file:///home/u/Рабочий стол/para/services/classmates_auth.py#L128-L139)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, авторизован ли пользователь (Администратор или студент с ID). :param user: Экземпляр aiogram User :return: True, если доступ разрешен

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user` | `User | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not user:`
2. `if user.id == ALLOWED_USER_ID:`
3. `return find_classmate_by_tg_id(user.id) is not None`

---

### `process_user_auth`
- **Signature**: `def process_user_auth(user: User | None) -> tuple[bool, bool, dict[str, Any] | None]`
- **Source Reference**: [services/classmates_auth.py#L142-L156](file:///home/u/Рабочий стол/para/services/classmates_auth.py#L142-L156)
- **Async**: `No`
- **Return Type**: `tuple[bool, bool, dict[str, Any] | None]`

#### Purpose & Architectural Intent
Основная логика аутентификации пользователя при входе в бота. Политикой Варианта А разрешен доступ только проверенным студентам с подтвержденным tg_id или главному администратору.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user` | `User | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not user:`
2. `if user.id == ALLOWED_USER_ID:`
3. `existing = find_classmate_by_tg_id(user.id)`
4. `if existing:`
5. `return False, False, None`

---
