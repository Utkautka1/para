# Component Reference: `api/router/classmates.py`
> **File Path**: [`api/router/classmates.py`](../../api/router/classmates.py)
> **Subsystem**: `Classmates API`

## 1. Purpose
Роутер одногруппников — GET /classmates (список и карточка студента).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_to_classmate_item`](#_to_classmate_item) | Function | L22–L40 | `ClassmateItem` | Конвертирует сырой словарь студента из JSON в Pydantic ... |
| [`list_classmates`](#list_classmates) | Function | L44–L57 | `ClassmatesListResponse` | Возвращает полный реестр одногруппников группы 1-КПД-3. |
| [`_find_student_in_registry`](#_find_student_in_registry) | Function | L60–L74 | `dict \| None` | Ищет запись студента по порядковому номеру или по Teleg... |
| [`get_classmate_detail`](#get_classmate_detail) | Function | L78–L102 | `ClassmateDetailResponse` | Возвращает детальную карточку студента по его порядково... |

---

## 3. Comprehensive Function Specifications

### `_to_classmate_item`
```python
def _to_classmate_item(raw: dict) -> ClassmateItem
```

- **Source Reference**: [`api/router/classmates.py#L22-L40`](../../api/router/classmates.py#L22-L40)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `ClassmateItem`

#### Overview & Architectural Purpose
Конвертирует сырой словарь студента из JSON в Pydantic модель ClassmateItem.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw` | `dict` | Yes | Parameter `raw` of type `dict`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.classmates import _to_classmate_item

# Execute call
result = _to_classmate_item(raw=...)
```

---

### `list_classmates`
```python
async def list_classmates() -> ClassmatesListResponse
```

- **Source Reference**: [`api/router/classmates.py#L44-L57`](../../api/router/classmates.py#L44-L57)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `ClassmatesListResponse`

#### Overview & Architectural Purpose
Возвращает полный реестр одногруппников группы 1-КПД-3.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.classmates import list_classmates

# Execute call
result = await list_classmates()
```

---

### `_find_student_in_registry`
```python
def _find_student_in_registry(registry: list[dict], identifier: int) -> dict | None
```

- **Source Reference**: [`api/router/classmates.py#L60-L74`](../../api/router/classmates.py#L60-L74)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict | None`

#### Overview & Architectural Purpose
Ищет запись студента по порядковому номеру или по Telegram ID.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `registry` | `list[dict]` | Yes | Parameter `registry` of type `list[dict]`. |
| `identifier` | `int` | Yes | Parameter `identifier` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.classmates import _find_student_in_registry

# Execute call
result = _find_student_in_registry(registry=..., identifier=...)
```

---

### `get_classmate_detail`
```python
async def get_classmate_detail(student_id: int) -> ClassmateDetailResponse
```

- **Source Reference**: [`api/router/classmates.py#L78-L102`](../../api/router/classmates.py#L78-L102)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `ClassmateDetailResponse`

#### Overview & Architectural Purpose
Возвращает детальную карточку студента по его порядковому ID или Telegram ID.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | `int` | Yes | Parameter `student_id` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.classmates import get_classmate_detail

# Execute call
result = await get_classmate_detail(student_id=...)
```

---
