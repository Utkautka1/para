# Component Reference: `services/custom_teachers.py`
> **File Path**: [`services/custom_teachers.py`](../../services/custom_teachers.py)
> **Subsystem**: `Faculty Registry`

## 1. Purpose
Модуль локального хранения персональных контактов преподавателей.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`load_custom_teachers`](#load_custom_teachers) | Function | L12–L21 | `dict[str, TeacherData]` | Загружает переопределенные контакты и ссылки преподават... |
| [`save_custom_teacher`](#save_custom_teacher) | Function | L24–L35 | `None` | Атомарно сохраняет или обновляет контакты преподавателя... |
| [`delete_custom_teacher`](#delete_custom_teacher) | Function | L38–L50 | `None` | Удаляет переопределенные данные преподавателя по его фа... |

---

## 3. Comprehensive Function Specifications

### `load_custom_teachers`
```python
def load_custom_teachers() -> dict[str, TeacherData]
```

- **Source Reference**: [`services/custom_teachers.py#L12-L21`](../../services/custom_teachers.py#L12-L21)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, TeacherData]`

#### Overview & Architectural Purpose
Загружает переопределенные контакты и ссылки преподавателей из локального JSON.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.custom_teachers import load_custom_teachers

# Execute call
result = load_custom_teachers()
```

---

### `save_custom_teacher`
```python
def save_custom_teacher(last_name: str, full_name: str, link_info: str) -> None
```

- **Source Reference**: [`services/custom_teachers.py#L24-L35`](../../services/custom_teachers.py#L24-L35)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Атомарно сохраняет или обновляет контакты преподавателя в файле.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `last_name` | `str` | Yes | Parameter `last_name` of type `str`. |
| `full_name` | `str` | Yes | Parameter `full_name` of type `str`. |
| `link_info` | `str` | Yes | Parameter `link_info` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.custom_teachers import save_custom_teacher

# Execute call
result = save_custom_teacher(last_name=..., full_name=..., link_info=...)
```

---

### `delete_custom_teacher`
```python
def delete_custom_teacher(last_name: str) -> None
```

- **Source Reference**: [`services/custom_teachers.py#L38-L50`](../../services/custom_teachers.py#L38-L50)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет переопределенные данные преподавателя по его фамилии.

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
from services.custom_teachers import delete_custom_teacher

# Execute call
result = delete_custom_teacher(last_name=...)
```

---
