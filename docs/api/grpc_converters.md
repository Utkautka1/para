# Component Reference: `api/grpc/converters.py`
> **File Path**: [`api/grpc/converters.py`](../../api/grpc/converters.py)
> **Subsystem**: `Protobuf Converters`

## 1. Purpose
Конвертеры между доменными Pydantic-моделями и Protobuf-сообщениями.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`lesson_to_proto`](#lesson_to_proto) | Function | L17–L39 | `LessonProto` | Конвертирует Pydantic-модель Lesson в Protobuf-сообщени... |
| [`proto_to_lesson`](#proto_to_lesson) | Function | L42–L64 | `Lesson` | Конвертирует Protobuf-сообщение LessonProto в модель Le... |
| [`week_days_to_proto`](#week_days_to_proto) | Function | L67–L81 | `list[WeekDayProto]` | Конвертирует список кортежей (дата, пары) в список сооб... |
| [`exam_item_to_proto`](#exam_item_to_proto) | Function | L84–L105 | `ExamItemProto` | Конвертирует ExamItem в Protobuf-сообщение ExamItemProt... |
| [`proto_to_exam_item`](#proto_to_exam_item) | Function | L108–L130 | `ExamItem` | Конвертирует ExamItemProto в доменную Pydantic-модель E... |
| [`teachers_dict_to_proto`](#teachers_dict_to_proto) | Function | L133–L149 | `TeachersResponse` | Конвертирует словарь преподавателей в Protobuf-ответ Te... |

---

## 3. Comprehensive Function Specifications

### `lesson_to_proto`
```python
def lesson_to_proto(lesson: Lesson) -> LessonProto
```

- **Source Reference**: [`api/grpc/converters.py#L17-L39`](../../api/grpc/converters.py#L17-L39)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `LessonProto`

#### Overview & Architectural Purpose
Конвертирует Pydantic-модель Lesson в Protobuf-сообщение LessonProto.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.converters import lesson_to_proto

# Execute call
result = lesson_to_proto(lesson=...)
```

---

### `proto_to_lesson`
```python
def proto_to_lesson(proto: LessonProto) -> Lesson
```

- **Source Reference**: [`api/grpc/converters.py#L42-L64`](../../api/grpc/converters.py#L42-L64)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Lesson`

#### Overview & Architectural Purpose
Конвертирует Protobuf-сообщение LessonProto в модель Lesson.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `proto` | `LessonProto` | Yes | Parameter `proto` of type `LessonProto`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.converters import proto_to_lesson

# Execute call
result = proto_to_lesson(proto=...)
```

---

### `week_days_to_proto`
```python
def week_days_to_proto(raw_days: list[tuple[date, list[Lesson]]]) -> list[WeekDayProto]
```

- **Source Reference**: [`api/grpc/converters.py#L67-L81`](../../api/grpc/converters.py#L67-L81)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[WeekDayProto]`

#### Overview & Architectural Purpose
Конвертирует список кортежей (дата, пары) в список сообщений WeekDayProto.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw_days` | `list[tuple[date, list[Lesson]]]` | Yes | Parameter `raw_days` of type `list[tuple[date, list[Lesson]]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.converters import week_days_to_proto

# Execute call
result = week_days_to_proto(raw_days=...)
```

---

### `exam_item_to_proto`
```python
def exam_item_to_proto(exam: ExamItem) -> ExamItemProto
```

- **Source Reference**: [`api/grpc/converters.py#L84-L105`](../../api/grpc/converters.py#L84-L105)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `ExamItemProto`

#### Overview & Architectural Purpose
Конвертирует ExamItem в Protobuf-сообщение ExamItemProto.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `exam` | `ExamItem` | Yes | Parameter `exam` of type `ExamItem`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.converters import exam_item_to_proto

# Execute call
result = exam_item_to_proto(exam=...)
```

---

### `proto_to_exam_item`
```python
def proto_to_exam_item(proto: ExamItemProto) -> ExamItem
```

- **Source Reference**: [`api/grpc/converters.py#L108-L130`](../../api/grpc/converters.py#L108-L130)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `ExamItem`

#### Overview & Architectural Purpose
Конвертирует ExamItemProto в доменную Pydantic-модель ExamItem.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `proto` | `ExamItemProto` | Yes | Parameter `proto` of type `ExamItemProto`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.converters import proto_to_exam_item

# Execute call
result = proto_to_exam_item(proto=...)
```

---

### `teachers_dict_to_proto`
```python
def teachers_dict_to_proto(raw: dict[str, dict[str, Any]]) -> TeachersResponse
```

- **Source Reference**: [`api/grpc/converters.py#L133-L149`](../../api/grpc/converters.py#L133-L149)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `TeachersResponse`

#### Overview & Architectural Purpose
Конвертирует словарь преподавателей в Protobuf-ответ TeachersResponse.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw` | `dict[str, dict[str, Any]]` | Yes | Parameter `raw` of type `dict[str, dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.converters import teachers_dict_to_proto

# Execute call
result = teachers_dict_to_proto(raw=...)
```

---
