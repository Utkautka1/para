# Module Specification: `services/models.py`
> **Path**: [`services/models.py`](file:///home/u/Рабочий стол/para/services/models.py)  
> **Subsystem**: `Domain Models`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Общие Pydantic-модели данных, используемые всеми сервисами. Вынесены из парсеров, чтобы бот мог десериализовать JSON из API без импорта тяжёлых модулей парсинга (httpx, docx, etc).

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`Lesson.number`](#lessonnumber) | Method | L29–L31 | `int` | Номер пары от 1 до 6 (period + 1). |

---

## 3. Exhaustive Function Specifications

## Class: `Lesson`
Модель данных одного занятия в расписании.

### `Lesson.number`
- **Signature**: `def number(self) -> int`
- **Source Reference**: [services/models.py#L29-L31](file:///home/u/Рабочий стол/para/services/models.py#L29-L31)
- **Async**: `No`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Номер пары от 1 до 6 (period + 1).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `return self.period + 1`

---

## Class: `ExamItem`
Модель контрольного мероприятия/экзамена.
