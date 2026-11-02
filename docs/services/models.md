# Component Reference: `services/models.py`
> **File Path**: [`services/models.py`](../../services/models.py)
> **Subsystem**: `Domain Models`

## 1. Purpose
Общие Pydantic-модели данных, используемые всеми сервисами.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`Lesson.number`](#lessonnumber) | Method | L44–L53 | `int` | Преобразует нулевой индекс периода в академический номе... |

---

## 3. Comprehensive Function Specifications

## Class Model: `Lesson`

Модель данных одного учебного занятия в расписании.

### `Lesson.number`
```python
def number(self) -> int
```

- **Source Reference**: [`services/models.py#L44-L53`](../../services/models.py#L44-L53)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Преобразует нулевой индекс периода в академический номер пары.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.models import number

# Execute call
result = number()
```

---

## Class Model: `ExamItem`

Модель контрольного мероприятия, зачета или экзаменационной сессии.
