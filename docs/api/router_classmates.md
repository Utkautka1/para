# Module Specification: `api/router/classmates.py`
> **Path**: [`api/router/classmates.py`](file:///home/u/Рабочий стол/para/api/router/classmates.py)  
> **Subsystem**: `Classmates API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер одногруппников — GET /classmates (список и карточка студента).

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_to_classmate_item`](#_to_classmate_item) | Function | L22–L31 | `ClassmateItem` | Конвертирует словарь студента в Pydantic модель. |
| [`list_classmates`](#list_classmates) | Function | L35–L39 | `ClassmatesListResponse` | Полный реестр студентов учебной группы 1-КПД-3. |
| [`_find_student_in_registry`](#_find_student_in_registry) | Function | L42–L47 | `dict | None` | Ищет студента по порядковому номеру в журнале либо Telegram  |
| [`get_classmate_detail`](#get_classmate_detail) | Function | L51–L65 | `ClassmateDetailResponse` | Детальная информация о студенте по порядковому ID или Telegr |

---

## 3. Exhaustive Function Specifications

### `_to_classmate_item`
- **Signature**: `def _to_classmate_item(raw: dict) -> ClassmateItem`
- **Source Reference**: [api/router/classmates.py#L22-L31](file:///home/u/Рабочий стол/para/api/router/classmates.py#L22-L31)
- **Async**: `No`
- **Return Type**: `ClassmateItem`

#### Purpose & Architectural Intent
Конвертирует словарь студента в Pydantic модель.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `b_day = f"{raw.get('day', 1):02d}.{raw.get('month', 1):02d}.{raw.get('year', 2005)}"`
2. `return ClassmateItem(`

---

### `list_classmates`
- **Signature**: `async def list_classmates() -> ClassmatesListResponse`
- **Source Reference**: [api/router/classmates.py#L35-L39](file:///home/u/Рабочий стол/para/api/router/classmates.py#L35-L39)
- **Async**: `Yes`
- **Return Type**: `ClassmatesListResponse`

#### Purpose & Architectural Intent
Полный реестр студентов учебной группы 1-КПД-3.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `registry = load_classmates_registry()`
2. `items = [_to_classmate_item(r) for r in registry]`
3. `return ClassmatesListResponse(count=len(items), classmates=items)`

---

### `_find_student_in_registry`
- **Signature**: `def _find_student_in_registry(registry: list[dict], identifier: int) -> dict | None`
- **Source Reference**: [api/router/classmates.py#L42-L47](file:///home/u/Рабочий стол/para/api/router/classmates.py#L42-L47)
- **Async**: `No`
- **Return Type**: `dict | None`

#### Purpose & Architectural Intent
Ищет студента по порядковому номеру в журнале либо Telegram ID.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `registry` | `list[dict]` | Input parameter |
| `identifier` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `for s in registry:`
2. `return None`

---

### `get_classmate_detail`
- **Signature**: `async def get_classmate_detail(student_id: int) -> ClassmateDetailResponse`
- **Source Reference**: [api/router/classmates.py#L51-L65](file:///home/u/Рабочий стол/para/api/router/classmates.py#L51-L65)
- **Async**: `Yes`
- **Return Type**: `ClassmateDetailResponse`

#### Purpose & Architectural Intent
Детальная информация о студенте по порядковому ID или Telegram ID.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `student_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `registry = load_classmates_registry()`
2. `student = _find_student_in_registry(registry, student_id)`
3. `if not student:`
4. `today = datetime.now(TIMEZONE).date()`
5. `calc = calculate_days_and_age(student, today)`
6. `item = _to_classmate_item(student)`

---
