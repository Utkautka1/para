# Module Specification: `api/grpc/servicers.py`
> **Path**: [`api/grpc/servicers.py`](file:///home/u/Рабочий стол/para/api/grpc/servicers.py)  
> **Subsystem**: `gRPC RPC Servicers`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Сервисеры gRPC (ScheduleService, ExamsService, TeachersService). Обрабатывают входящие RPC-вызовы от микросервисов бота и воркера, транслируя Protobuf-запросы во внутренние асинхронные парсеры с кэшированием.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_resolve_day`](#_resolve_day) | Function | L35–L39 | `date` | Парсит ISO дату или возвращает сегодняшнюю дату по МСК. |
| [`_resolve_monday`](#_resolve_monday) | Function | L42–L47 | `date` | Парсит дату понедельника или вычисляет текущий понедельник. |
| [`ScheduleServicer.GetDaySchedule`](#scheduleservicergetdayschedule) | Method | L53–L68 | `schedule_pb2.DayScheduleResponse` | Возвращает расписание занятий на день. |
| [`ScheduleServicer.GetWeekSchedule`](#scheduleservicergetweekschedule) | Method | L70–L85 | `schedule_pb2.WeekScheduleResponse` | Возвращает недельное расписание занятий. |
| [`ExamsServicer.GetExams`](#examsservicergetexams) | Method | L91–L105 | `exams_pb2.ExamsResponse` | Возвращает список контрольных мероприятий и экзаменов. |
| [`TeachersServicer.GetTeachers`](#teachersservicergetteachers) | Method | L111–L124 | `teachers_pb2.TeachersResponse` | Возвращает контакты преподавателей из справочника. |

---

## 3. Exhaustive Function Specifications

### `_resolve_day`
- **Signature**: `def _resolve_day(raw_date: str) -> date`
- **Source Reference**: [api/grpc/servicers.py#L35-L39](file:///home/u/Рабочий стол/para/api/grpc/servicers.py#L35-L39)
- **Async**: `No`
- **Return Type**: `date`

#### Purpose & Architectural Intent
Парсит ISO дату или возвращает сегодняшнюю дату по МСК.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw_date` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if raw_date:`
2. `return datetime.now(TIMEZONE).date()`

---

### `_resolve_monday`
- **Signature**: `def _resolve_monday(raw_monday: str) -> date`
- **Source Reference**: [api/grpc/servicers.py#L42-L47](file:///home/u/Рабочий стол/para/api/grpc/servicers.py#L42-L47)
- **Async**: `No`
- **Return Type**: `date`

#### Purpose & Architectural Intent
Парсит дату понедельника или вычисляет текущий понедельник.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw_monday` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if raw_monday:`
2. `today = datetime.now(TIMEZONE).date()`
3. `return today - timedelta(days=today.weekday())`

---

## Class: `ScheduleServicer`
Серверный обработчик gRPC-запросов расписания.

### `ScheduleServicer.GetDaySchedule`
- **Signature**: `async def GetDaySchedule( self, request: schedule_pb2.DayScheduleRequest, context: grpc.aio.ServicerContext, ) -> schedule_pb2.DayScheduleResponse`
- **Source Reference**: [api/grpc/servicers.py#L53-L68](file:///home/u/Рабочий стол/para/api/grpc/servicers.py#L53-L68)
- **Async**: `Yes`
- **Return Type**: `schedule_pb2.DayScheduleResponse`

#### Purpose & Architectural Intent
Возвращает расписание занятий на день. Использует кэш L1/L2 расписания и отдает типизированный Protobuf-ответ. Возвращает DayScheduleResponse со списком уроков.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `request` | `schedule_pb2.DayScheduleRequest` | Input parameter |
| `context` | `grpc.aio.ServicerContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.debug(f"gRPC GetDaySchedule: date='{request.target_date}', refresh={request.force`
2. `target = _resolve_day(request.target_date)`
3. `lessons = await get_schedule_for_date(target, force_refresh=request.force_refresh)`
4. `proto_lessons = [lesson_to_proto(item) for item in lessons]`
5. `return schedule_pb2.DayScheduleResponse(date=target.isoformat(), lessons=proto_lesson`

---

### `ScheduleServicer.GetWeekSchedule`
- **Signature**: `async def GetWeekSchedule( self, request: schedule_pb2.WeekScheduleRequest, context: grpc.aio.ServicerContext, ) -> schedule_pb2.WeekScheduleResponse`
- **Source Reference**: [api/grpc/servicers.py#L70-L85](file:///home/u/Рабочий стол/para/api/grpc/servicers.py#L70-L85)
- **Async**: `Yes`
- **Return Type**: `schedule_pb2.WeekScheduleResponse`

#### Purpose & Architectural Intent
Возвращает недельное расписание занятий. Парсит неделю и возвращает список дней от понедельника до субботы. Возвращает WeekScheduleResponse с вложенными днями и парами.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `request` | `schedule_pb2.WeekScheduleRequest` | Input parameter |
| `context` | `grpc.aio.ServicerContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.debug(f"gRPC GetWeekSchedule: monday='{request.monday}', refresh={request.force_r`
2. `mon = _resolve_monday(request.monday)`
3. `raw_days = await get_week_schedule(mon, force_refresh=request.force_refresh)`
4. `days_proto = week_days_to_proto(raw_days)`
5. `return schedule_pb2.WeekScheduleResponse(monday=mon.isoformat(), days=days_proto)`

---

## Class: `ExamsServicer`
Серверный обработчик gRPC-запросов экзаменов.

### `ExamsServicer.GetExams`
- **Signature**: `async def GetExams( self, request: exams_pb2.ExamsRequest, context: grpc.aio.ServicerContext, ) -> exams_pb2.ExamsResponse`
- **Source Reference**: [api/grpc/servicers.py#L91-L105](file:///home/u/Рабочий стол/para/api/grpc/servicers.py#L91-L105)
- **Async**: `Yes`
- **Return Type**: `exams_pb2.ExamsResponse`

#### Purpose & Architectural Intent
Возвращает список контрольных мероприятий и экзаменов. Вызывает парсер экзаменов с поддержкой принудительного обновления. Возвращает ExamsResponse с массивом ExamItemProto.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `request` | `exams_pb2.ExamsRequest` | Input parameter |
| `context` | `grpc.aio.ServicerContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.debug(f"gRPC GetExams: refresh={request.force_refresh}")`
2. `exams = await get_group_exams()`
3. `proto_exams = [exam_item_to_proto(item) for item in exams]`
4. `return exams_pb2.ExamsResponse(count=len(proto_exams), exams=proto_exams)`

---

## Class: `TeachersServicer`
Серверный обработчик gRPC-запросов преподавателей.

### `TeachersServicer.GetTeachers`
- **Signature**: `async def GetTeachers( self, request: teachers_pb2.TeachersRequest, context: grpc.aio.ServicerContext, ) -> teachers_pb2.TeachersResponse`
- **Source Reference**: [api/grpc/servicers.py#L111-L124](file:///home/u/Рабочий стол/para/api/grpc/servicers.py#L111-L124)
- **Async**: `Yes`
- **Return Type**: `teachers_pb2.TeachersResponse`

#### Purpose & Architectural Intent
Возвращает контакты преподавателей из справочника. Загружает файл преподавателей из Яндекс Диска через docx_parser. Возвращает TeachersResponse с отображением фамилий на ссылки.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `request` | `teachers_pb2.TeachersRequest` | Input parameter |
| `context` | `grpc.aio.ServicerContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.debug(f"gRPC GetTeachers: refresh={request.force_refresh}")`
2. `raw_map = await get_teacher_links(force_refresh=request.force_refresh)`
3. `return teachers_dict_to_proto(raw_map)`

---
