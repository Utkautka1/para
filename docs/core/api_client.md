# Module Specification: `core/api_client.py`
> **Path**: [`core/api_client.py`](file:///home/u/Рабочий стол/para/core/api_client.py)  
> **Subsystem**: `Internal RPC Client`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Клиент для обращения к сервису para-api по протоколу gRPC (с HTTP fallback). Используется ботом, воркером и решателем ДЗ. Переиспользует постоянный асинхронный gRPC-канал через HTTP/2 multiplexing для максимальной производительности.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_get_client`](#_get_client) | Function | L43–L54 | `httpx.AsyncClient` | Возвращает или создает персистентный HTTP-клиент к para-api. |
| [`_get_grpc_channel`](#_get_grpc_channel) | Function | L57–L70 | `grpc.aio.Channel` | Возвращает или создает персистентный асинхронный gRPC канал  |
| [`close_api_client`](#close_api_client) | Function | L73–L81 | `None` | Закрывает HTTP-клиент и gRPC канал при остановке сервиса. |
| [`_api_get`](#_api_get) | Function | L84–L97 | `dict[str, Any]` | Выполняет GET-запрос к para-api с retry при временном сбое. |
| [`_fetch_day_schedule_grpc`](#_fetch_day_schedule_grpc) | Function | L100–L109 | `dict[str, Any]` | Вызывает gRPC метод ScheduleService.GetDaySchedule. |
| [`fetch_day_schedule`](#fetch_day_schedule) | Function | L112–L121 | `dict[str, Any]` | Запрашивает расписание на день через gRPC с fallback на HTTP |
| [`_fetch_week_schedule_grpc`](#_fetch_week_schedule_grpc) | Function | L124–L133 | `dict[str, Any]` | Вызывает gRPC метод ScheduleService.GetWeekSchedule. |
| [`fetch_week_schedule`](#fetch_week_schedule) | Function | L136–L145 | `dict[str, Any]` | Запрашивает расписание на неделю через gRPC с fallback на HT |
| [`_fetch_exams_grpc`](#_fetch_exams_grpc) | Function | L148–L154 | `dict[str, Any]` | Вызывает gRPC метод ExamsService.GetExams. |
| [`fetch_exams`](#fetch_exams) | Function | L157–L163 | `dict[str, Any]` | Запрашивает список экзаменов через gRPC с fallback на HTTP. |
| [`_fetch_teachers_grpc`](#_fetch_teachers_grpc) | Function | L166–L172 | `dict[str, Any]` | Вызывает gRPC метод TeachersService.GetTeachers. |
| [`fetch_teachers`](#fetch_teachers) | Function | L175–L181 | `dict[str, Any]` | Запрашивает контакты преподавателей через gRPC с fallback на |
| [`get_api_schedule_for_date`](#get_api_schedule_for_date) | Function | L184–L187 | `list[Lesson]` | Запрашивает расписание на день и десериализует в модели Less |
| [`get_api_week_schedule`](#get_api_week_schedule) | Function | L190–L198 | `list[tuple[date, list[Lesson]]]` | Запрашивает расписание на неделю и возвращает пары (дата, ур |
| [`get_api_exams`](#get_api_exams) | Function | L201–L204 | `list[ExamItem]` | Запрашивает список экзаменов и десериализует в модели ExamIt |
| [`get_api_teachers`](#get_api_teachers) | Function | L207–L210 | `dict[str, Any]` | Запрашивает контакты преподавателей (словарь фамилия -> конт |

---

## 3. Exhaustive Function Specifications

### `_get_client`
- **Signature**: `def _get_client() -> httpx.AsyncClient`
- **Source Reference**: [core/api_client.py#L43-L54](file:///home/u/Рабочий стол/para/core/api_client.py#L43-L54)
- **Async**: `No`
- **Return Type**: `httpx.AsyncClient`

#### Purpose & Architectural Intent
Возвращает или создает персистентный HTTP-клиент к para-api.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _CLIENT`
2. `if _CLIENT is None or _CLIENT.is_closed:`
3. `return _CLIENT`

---

### `_get_grpc_channel`
- **Signature**: `def _get_grpc_channel() -> grpc.aio.Channel`
- **Source Reference**: [core/api_client.py#L57-L70](file:///home/u/Рабочий стол/para/core/api_client.py#L57-L70)
- **Async**: `No`
- **Return Type**: `grpc.aio.Channel`

#### Purpose & Architectural Intent
Возвращает или создает персистентный асинхронный gRPC канал с keepalive.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _CHANNEL`
2. `if _CHANNEL is None:`
3. `return _CHANNEL`

---

### `close_api_client`
- **Signature**: `async def close_api_client() -> None`
- **Source Reference**: [core/api_client.py#L73-L81](file:///home/u/Рабочий стол/para/core/api_client.py#L73-L81)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Закрывает HTTP-клиент и gRPC канал при остановке сервиса.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _CLIENT, _CHANNEL`
2. `if _CLIENT and not _CLIENT.is_closed:`
3. `if _CHANNEL:`

---

### `_api_get`
- **Signature**: `async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L84-L97](file:///home/u/Рабочий стол/para/core/api_client.py#L84-L97)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Выполняет GET-запрос к para-api с retry при временном сбое.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `path` | `str` | Input parameter |
| `params` | `dict[str, Any] | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `for attempt in range(2):`

---

### `_fetch_day_schedule_grpc`
- **Signature**: `async def _fetch_day_schedule_grpc(target_date: date | None, force_refresh: bool) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L100-L109](file:///home/u/Рабочий стол/para/core/api_client.py#L100-L109)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Вызывает gRPC метод ScheduleService.GetDaySchedule.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date | None` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `stub = schedule_pb2_grpc.ScheduleServiceStub(_get_grpc_channel())`
2. `req = schedule_pb2.DayScheduleRequest(`
3. `resp = await stub.GetDaySchedule(req, timeout=30.0)`
4. `lessons = [proto_to_lesson(item).model_dump() for item in resp.lessons]`
5. `return {"date": resp.date, "lessons": lessons}`

---

### `fetch_day_schedule`
- **Signature**: `async def fetch_day_schedule(target_date: date | None = None, force_refresh: bool = False) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L112-L121](file:///home/u/Рабочий стол/para/core/api_client.py#L112-L121)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Запрашивает расписание на день через gRPC с fallback на HTTP.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date | None` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_fetch_week_schedule_grpc`
- **Signature**: `async def _fetch_week_schedule_grpc(monday: date | None, force_refresh: bool) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L124-L133](file:///home/u/Рабочий стол/para/core/api_client.py#L124-L133)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Вызывает gRPC метод ScheduleService.GetWeekSchedule.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `monday` | `date | None` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `stub = schedule_pb2_grpc.ScheduleServiceStub(_get_grpc_channel())`
2. `req = schedule_pb2.WeekScheduleRequest(`
3. `resp = await stub.GetWeekSchedule(req, timeout=30.0)`
4. `days = [{"date": d.date, "lessons": [proto_to_lesson(item).model_dump() for item in d`
5. `return {"monday": resp.monday, "days": days}`

---

### `fetch_week_schedule`
- **Signature**: `async def fetch_week_schedule(monday: date | None = None, force_refresh: bool = False) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L136-L145](file:///home/u/Рабочий стол/para/core/api_client.py#L136-L145)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Запрашивает расписание на неделю через gRPC с fallback на HTTP.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `monday` | `date | None` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_fetch_exams_grpc`
- **Signature**: `async def _fetch_exams_grpc(force_refresh: bool) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L148-L154](file:///home/u/Рабочий стол/para/core/api_client.py#L148-L154)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Вызывает gRPC метод ExamsService.GetExams.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `stub = exams_pb2_grpc.ExamsServiceStub(_get_grpc_channel())`
2. `req = exams_pb2.ExamsRequest(force_refresh=force_refresh)`
3. `resp = await stub.GetExams(req, timeout=30.0)`
4. `exams = [proto_to_exam_item(item).model_dump() for item in resp.exams]`
5. `return {"count": resp.count, "exams": exams}`

---

### `fetch_exams`
- **Signature**: `async def fetch_exams(force_refresh: bool = False) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L157-L163](file:///home/u/Рабочий стол/para/core/api_client.py#L157-L163)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Запрашивает список экзаменов через gRPC с fallback на HTTP.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_fetch_teachers_grpc`
- **Signature**: `async def _fetch_teachers_grpc(force_refresh: bool) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L166-L172](file:///home/u/Рабочий стол/para/core/api_client.py#L166-L172)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Вызывает gRPC метод TeachersService.GetTeachers.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `stub = teachers_pb2_grpc.TeachersServiceStub(_get_grpc_channel())`
2. `req = teachers_pb2.TeachersRequest(force_refresh=force_refresh)`
3. `resp = await stub.GetTeachers(req, timeout=30.0)`
4. `teachers = {k: {"full_name": v.full_name, "link_info": v.link_info} for k, v in resp.`
5. `return {"count": resp.count, "teachers": teachers}`

---

### `fetch_teachers`
- **Signature**: `async def fetch_teachers(force_refresh: bool = False) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L175-L181](file:///home/u/Рабочий стол/para/core/api_client.py#L175-L181)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Запрашивает контакты преподавателей через gRPC с fallback на HTTP.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `get_api_schedule_for_date`
- **Signature**: `async def get_api_schedule_for_date(target_date: date | None = None, force_refresh: bool = False) -> list[Lesson]`
- **Source Reference**: [core/api_client.py#L184-L187](file:///home/u/Рабочий стол/para/core/api_client.py#L184-L187)
- **Async**: `Yes`
- **Return Type**: `list[Lesson]`

#### Purpose & Architectural Intent
Запрашивает расписание на день и десериализует в модели Lesson.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date | None` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = await fetch_day_schedule(target_date=target_date, force_refresh=force_refresh)`
2. `return [Lesson(**item) for item in data.get("lessons", [])]`

---

### `get_api_week_schedule`
- **Signature**: `async def get_api_week_schedule(monday: date | None = None, force_refresh: bool = False) -> list[tuple[date, list[Lesson]]]`
- **Source Reference**: [core/api_client.py#L190-L198](file:///home/u/Рабочий стол/para/core/api_client.py#L190-L198)
- **Async**: `Yes`
- **Return Type**: `list[tuple[date, list[Lesson]]]`

#### Purpose & Architectural Intent
Запрашивает расписание на неделю и возвращает пары (дата, уроки).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `monday` | `date | None` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = await fetch_week_schedule(monday=monday, force_refresh=force_refresh)`
2. `result: list[tuple[date, list[Lesson]]] = []`
3. `for day in data.get("days", []):`
4. `return result`

---

### `get_api_exams`
- **Signature**: `async def get_api_exams(force_refresh: bool = False) -> list[ExamItem]`
- **Source Reference**: [core/api_client.py#L201-L204](file:///home/u/Рабочий стол/para/core/api_client.py#L201-L204)
- **Async**: `Yes`
- **Return Type**: `list[ExamItem]`

#### Purpose & Architectural Intent
Запрашивает список экзаменов и десериализует в модели ExamItem.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = await fetch_exams(force_refresh=force_refresh)`
2. `return [ExamItem(**item) for item in data.get("exams", [])]`

---

### `get_api_teachers`
- **Signature**: `async def get_api_teachers(force_refresh: bool = False) -> dict[str, Any]`
- **Source Reference**: [core/api_client.py#L207-L210](file:///home/u/Рабочий стол/para/core/api_client.py#L207-L210)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Запрашивает контакты преподавателей (словарь фамилия -> контакты).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = await fetch_teachers(force_refresh=force_refresh)`
2. `return data.get("teachers", {})`

---
