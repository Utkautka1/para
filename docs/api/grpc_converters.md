# Module Specification: `api/grpc/converters.py`
> **Path**: [`api/grpc/converters.py`](file:///home/u/Рабочий стол/para/api/grpc/converters.py)  
> **Subsystem**: `Protobuf Converters`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Конвертеры между доменными Pydantic-моделями и Protobuf-сообщениями. Обеспечивают строгую валидацию и чистую трансляцию данных без дублирования логики сериализации между REST и gRPC.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`lesson_to_proto`](#lesson_to_proto) | Function | L16–L32 | `LessonProto` | Конвертирует Pydantic-модель Lesson в Protobuf-сообщение Les |
| [`proto_to_lesson`](#proto_to_lesson) | Function | L35–L51 | `Lesson` | Конвертирует Protobuf-сообщение LessonProto в модель Lesson. |
| [`week_days_to_proto`](#week_days_to_proto) | Function | L54–L60 | `list[WeekDayProto]` | Конвертирует список кортежей (дата, пары) в список WeekDayPr |
| [`exam_item_to_proto`](#exam_item_to_proto) | Function | L63–L74 | `ExamItemProto` | Конвертирует ExamItem в Protobuf-сообщение ExamItemProto. |
| [`proto_to_exam_item`](#proto_to_exam_item) | Function | L77–L88 | `ExamItem` | Конвертирует ExamItemProto в Pydantic-модель ExamItem. |
| [`teachers_dict_to_proto`](#teachers_dict_to_proto) | Function | L91–L99 | `TeachersResponse` | Конвертирует словарь преподавателей в TeachersResponse. |

---

## 3. Exhaustive Function Specifications

### `lesson_to_proto`
- **Signature**: `def lesson_to_proto(lesson: Lesson) -> LessonProto`
- **Source Reference**: [api/grpc/converters.py#L16-L32](file:///home/u/Рабочий стол/para/api/grpc/converters.py#L16-L32)
- **Async**: `No`
- **Return Type**: `LessonProto`

#### Purpose & Architectural Intent
Конвертирует Pydantic-модель Lesson в Protobuf-сообщение LessonProto.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |

#### Step-by-Step Logic Execution
1. `return LessonProto(`

---

### `proto_to_lesson`
- **Signature**: `def proto_to_lesson(proto: LessonProto) -> Lesson`
- **Source Reference**: [api/grpc/converters.py#L35-L51](file:///home/u/Рабочий стол/para/api/grpc/converters.py#L35-L51)
- **Async**: `No`
- **Return Type**: `Lesson`

#### Purpose & Architectural Intent
Конвертирует Protobuf-сообщение LessonProto в модель Lesson.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `proto` | `LessonProto` | Input parameter |

#### Step-by-Step Logic Execution
1. `return Lesson(`

---

### `week_days_to_proto`
- **Signature**: `def week_days_to_proto(raw_days: list[tuple[date, list[Lesson]]]) -> list[WeekDayProto]`
- **Source Reference**: [api/grpc/converters.py#L54-L60](file:///home/u/Рабочий стол/para/api/grpc/converters.py#L54-L60)
- **Async**: `No`
- **Return Type**: `list[WeekDayProto]`

#### Purpose & Architectural Intent
Конвертирует список кортежей (дата, пары) в список WeekDayProto.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw_days` | `list[tuple[date, list[Lesson]]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `result: list[WeekDayProto] = []`
2. `for day_date, lessons in raw_days:`
3. `return result`

---

### `exam_item_to_proto`
- **Signature**: `def exam_item_to_proto(exam: ExamItem) -> ExamItemProto`
- **Source Reference**: [api/grpc/converters.py#L63-L74](file:///home/u/Рабочий стол/para/api/grpc/converters.py#L63-L74)
- **Async**: `No`
- **Return Type**: `ExamItemProto`

#### Purpose & Architectural Intent
Конвертирует ExamItem в Protobuf-сообщение ExamItemProto.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `exam` | `ExamItem` | Input parameter |

#### Step-by-Step Logic Execution
1. `return ExamItemProto(`

---

### `proto_to_exam_item`
- **Signature**: `def proto_to_exam_item(proto: ExamItemProto) -> ExamItem`
- **Source Reference**: [api/grpc/converters.py#L77-L88](file:///home/u/Рабочий стол/para/api/grpc/converters.py#L77-L88)
- **Async**: `No`
- **Return Type**: `ExamItem`

#### Purpose & Architectural Intent
Конвертирует ExamItemProto в Pydantic-модель ExamItem.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `proto` | `ExamItemProto` | Input parameter |

#### Step-by-Step Logic Execution
1. `return ExamItem(`

---

### `teachers_dict_to_proto`
- **Signature**: `def teachers_dict_to_proto(raw: dict[str, dict]) -> TeachersResponse`
- **Source Reference**: [api/grpc/converters.py#L91-L99](file:///home/u/Рабочий стол/para/api/grpc/converters.py#L91-L99)
- **Async**: `No`
- **Return Type**: `TeachersResponse`

#### Purpose & Architectural Intent
Конвертирует словарь преподавателей в TeachersResponse.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw` | `dict[str, dict]` | Input parameter |

#### Step-by-Step Logic Execution
1. `teachers_map: dict[str, TeacherItemProto] = {}`
2. `for name, data in raw.items():`
3. `return TeachersResponse(count=len(teachers_map), teachers=teachers_map)`

---
