# Component Reference: `api/router/teachers.py`
> **File Path**: [`api/router/teachers.py`](../../api/router/teachers.py)
> **Subsystem**: `Teachers API`

## 1. Purpose
Роутер преподавателей — GET /teachers, search, custom, refresh.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`list_teachers`](#list_teachers) | Function | L28–L41 | `TeachersResponse` | Возвращает полный реестр преподавателей и их ссылок вид... |
| [`search_teachers`](#search_teachers) | Function | L45–L65 | `TeacherSearchResponse` | Выполняет регистронезависимый поиск преподавателей по ф... |
| [`get_teacher`](#get_teacher) | Function | L69–L86 | `TeacherSingleResponse` | Возвращает контактную карточку преподавателя по его фам... |
| [`add_custom_teacher`](#add_custom_teacher) | Function | L90–L104 | `TeacherSingleResponse` | Добавляет или обновляет персональную ссылку преподавате... |
| [`remove_custom_teacher`](#remove_custom_teacher) | Function | L108–L120 | `TeacherDeleteResponse` | Удаляет пользовательское переопределение преподавателя ... |
| [`refresh_teachers`](#refresh_teachers) | Function | L124–L136 | `TeachersRefreshResponse` | Выполняет принудительную перепроверку документа на Янде... |

---

## 3. Comprehensive Function Specifications

### `list_teachers`
```python
async def list_teachers(force_refresh: bool = Query(default=False)) -> TeachersResponse
```

- **Source Reference**: [`api/router/teachers.py#L28-L41`](../../api/router/teachers.py#L28-L41)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TeachersResponse`

#### Overview & Architectural Purpose
Возвращает полный реестр преподавателей и их ссылок видеосвязи.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.teachers import list_teachers

# Execute call
result = await list_teachers(force_refresh=...)
```

---

### `search_teachers`
```python
async def search_teachers( q: str = Query(..., min_length=2, description="Search query substring"), ) -> TeacherSearchResponse
```

- **Source Reference**: [`api/router/teachers.py#L45-L65`](../../api/router/teachers.py#L45-L65)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TeacherSearchResponse`

#### Overview & Architectural Purpose
Выполняет регистронезависимый поиск преподавателей по фрагменту ФИО.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `q` | `str` | Yes | Parameter `q` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.teachers import search_teachers

# Execute call
result = await search_teachers(q=...)
```

---

### `get_teacher`
```python
async def get_teacher(last_name: str) -> TeacherSingleResponse
```

- **Source Reference**: [`api/router/teachers.py#L69-L86`](../../api/router/teachers.py#L69-L86)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TeacherSingleResponse`

#### Overview & Architectural Purpose
Возвращает контактную карточку преподавателя по его фамилии.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `last_name` | `str` | Yes | Parameter `last_name` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.teachers import get_teacher

# Execute call
result = await get_teacher(last_name=...)
```

---

### `add_custom_teacher`
```python
async def add_custom_teacher(payload: CustomTeacherCreateRequest) -> TeacherSingleResponse
```

- **Source Reference**: [`api/router/teachers.py#L90-L104`](../../api/router/teachers.py#L90-L104)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TeacherSingleResponse`

#### Overview & Architectural Purpose
Добавляет или обновляет персональную ссылку преподавателя (Admin only).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `payload` | `CustomTeacherCreateRequest` | Yes | Parameter `payload` of type `CustomTeacherCreateRequest`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.teachers import add_custom_teacher

# Execute call
result = await add_custom_teacher(payload=...)
```

---

### `remove_custom_teacher`
```python
async def remove_custom_teacher(last_name: str) -> TeacherDeleteResponse
```

- **Source Reference**: [`api/router/teachers.py#L108-L120`](../../api/router/teachers.py#L108-L120)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TeacherDeleteResponse`

#### Overview & Architectural Purpose
Удаляет пользовательское переопределение преподавателя (Admin only).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `last_name` | `str` | Yes | Parameter `last_name` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.teachers import remove_custom_teacher

# Execute call
result = await remove_custom_teacher(last_name=...)
```

---

### `refresh_teachers`
```python
async def refresh_teachers() -> TeachersRefreshResponse
```

- **Source Reference**: [`api/router/teachers.py#L124-L136`](../../api/router/teachers.py#L124-L136)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TeachersRefreshResponse`

#### Overview & Architectural Purpose
Выполняет принудительную перепроверку документа на Яндекс Диске (Admin only).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.teachers import refresh_teachers

# Execute call
result = await refresh_teachers()
```

---
