# Module Specification: `services/custom_teachers.py`
> **Path**: [`services/custom_teachers.py`](file:///home/u/Рабочий стол/para/services/custom_teachers.py)  
> **Subsystem**: `Faculty Registry`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль локального хранения персональных контактов преподавателей.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`load_custom_teachers`](#load_custom_teachers) | Function | L12–L18 | `dict[str, TeacherData]` | Загружает кастомные контакты преподавателей из JSON. |
| [`save_custom_teacher`](#save_custom_teacher) | Function | L21–L34 | `None` | Сохраняет или обновляет кастомного преподавателя. |
| [`delete_custom_teacher`](#delete_custom_teacher) | Function | L37–L46 | `None` | Удаляет преподавателя по его ключу-фамилии из JSON. |

---

## 3. Exhaustive Function Specifications

### `load_custom_teachers`
- **Signature**: `def load_custom_teachers() -> dict[str, TeacherData]`
- **Source Reference**: [services/custom_teachers.py#L12-L18](file:///home/u/Рабочий стол/para/services/custom_teachers.py#L12-L18)
- **Async**: `No`
- **Return Type**: `dict[str, TeacherData]`

#### Purpose & Architectural Intent
Загружает кастомные контакты преподавателей из JSON. :return: Словарь преподавателей

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return sync_load_json(CUSTOM_TEACHERS_FILE, default={})`

---

### `save_custom_teacher`
- **Signature**: `def save_custom_teacher(last_name: str, full_name: str, link_info: str) -> None`
- **Source Reference**: [services/custom_teachers.py#L21-L34](file:///home/u/Рабочий стол/para/services/custom_teachers.py#L21-L34)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет или обновляет кастомного преподавателя. :param last_name: Фамилия ключа :param full_name: Полное имя :param link_info: Данные ссылки

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `last_name` | `str` | Input parameter |
| `full_name` | `str` | Input parameter |
| `link_info` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = load_custom_teachers()`
2. `data[last_name.lower()] = {`
3. `sync_atomic_save_json(CUSTOM_TEACHERS_FILE, data)`

---

### `delete_custom_teacher`
- **Signature**: `def delete_custom_teacher(last_name: str) -> None`
- **Source Reference**: [services/custom_teachers.py#L37-L46](file:///home/u/Рабочий стол/para/services/custom_teachers.py#L37-L46)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет преподавателя по его ключу-фамилии из JSON. :param last_name: Фамилия (ключ)

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `last_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = load_custom_teachers()`
2. `if last_name.lower() in data:`

---
