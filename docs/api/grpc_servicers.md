# Component Reference: `api/grpc/servicers.py`
> **File Path**: [`api/grpc/servicers.py`](../../api/grpc/servicers.py)
> **Subsystem**: `gRPC RPC Servicers`

## 1. Purpose
Сервисеры gRPC (ScheduleService, ExamsService, TeachersService).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_resolve_day`](#_resolve_day) | Function | L35–L46 | `date` | Парсит ISO дату или возвращает сегодняшнюю дату по часо... |
| [`_resolve_monday`](#_resolve_monday) | Function | L49–L61 | `date` | Парсит дату понедельника или вычисляет дату понедельник... |
| [`ScheduleServicer.GetDaySchedule`](#scheduleservicergetdayschedule) | Method | L67–L87 | `schedule_pb2.DayScheduleResponse` | Возвращает расписание занятий группы на целевой день в ... |
| [`ScheduleServicer.GetWeekSchedule`](#scheduleservicergetweekschedule) | Method | L89–L108 | `schedule_pb2.WeekScheduleResponse` | Возвращает недельное расписание занятий академической г... |
| [`ExamsServicer.GetExams`](#examsservicergetexams) | Method | L114–L132 | `exams_pb2.ExamsResponse` | Возвращает список контрольных мероприятий и экзаменов с... |
| [`TeachersServicer.GetTeachers`](#teachersservicergetteachers) | Method | L138–L154 | `teachers_pb2.TeachersResponse` | Возвращает справочник контактов и видеоконференций преп... |

---

## 3. Comprehensive Function Specifications

### `_resolve_day`
```python
def _resolve_day(raw_date: str) -> date
```

- **Source Reference**: [`api/grpc/servicers.py#L35-L46`](../../api/grpc/servicers.py#L35-L46)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `date`

#### Overview & Architectural Purpose
Парсит ISO дату или возвращает сегодняшнюю дату по часовому поясу МСК.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw_date` | `str` | Yes | Parameter `raw_date` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.servicers import _resolve_day

# Execute call
result = _resolve_day(raw_date=...)
```

---

### `_resolve_monday`
```python
def _resolve_monday(raw_monday: str) -> date
```

- **Source Reference**: [`api/grpc/servicers.py#L49-L61`](../../api/grpc/servicers.py#L49-L61)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `date`

#### Overview & Architectural Purpose
Парсит дату понедельника или вычисляет дату понедельника текущей недели.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw_monday` | `str` | Yes | Parameter `raw_monday` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.servicers import _resolve_monday

# Execute call
result = _resolve_monday(raw_monday=...)
```

---

## Class Model: `ScheduleServicer`

Серверный обработчик gRPC-запросов расписания.

### `ScheduleServicer.GetDaySchedule`
```python
async def GetDaySchedule( self, request: schedule_pb2.DayScheduleRequest, context: grpc.aio.ServicerContext, ) -> schedule_pb2.DayScheduleResponse
```

- **Source Reference**: [`api/grpc/servicers.py#L67-L87`](../../api/grpc/servicers.py#L67-L87)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `schedule_pb2.DayScheduleResponse`

#### Overview & Architectural Purpose
Возвращает расписание занятий группы на целевой день в формате Protobuf.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request` | `schedule_pb2.DayScheduleRequest` | Yes | Parameter `request` of type `schedule_pb2.DayScheduleRequest`. |
| `context` | `grpc.aio.ServicerContext` | Yes | Parameter `context` of type `grpc.aio.ServicerContext`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.servicers import GetDaySchedule

# Execute call
result = await GetDaySchedule(request=..., context=...)
```

---

### `ScheduleServicer.GetWeekSchedule`
```python
async def GetWeekSchedule( self, request: schedule_pb2.WeekScheduleRequest, context: grpc.aio.ServicerContext, ) -> schedule_pb2.WeekScheduleResponse
```

- **Source Reference**: [`api/grpc/servicers.py#L89-L108`](../../api/grpc/servicers.py#L89-L108)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `schedule_pb2.WeekScheduleResponse`

#### Overview & Architectural Purpose
Возвращает недельное расписание занятий академической группы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request` | `schedule_pb2.WeekScheduleRequest` | Yes | Parameter `request` of type `schedule_pb2.WeekScheduleRequest`. |
| `context` | `grpc.aio.ServicerContext` | Yes | Parameter `context` of type `grpc.aio.ServicerContext`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.servicers import GetWeekSchedule

# Execute call
result = await GetWeekSchedule(request=..., context=...)
```

---

## Class Model: `ExamsServicer`

Серверный обработчик gRPC-запросов экзаменов.

### `ExamsServicer.GetExams`
```python
async def GetExams( self, request: exams_pb2.ExamsRequest, context: grpc.aio.ServicerContext, ) -> exams_pb2.ExamsResponse
```

- **Source Reference**: [`api/grpc/servicers.py#L114-L132`](../../api/grpc/servicers.py#L114-L132)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `exams_pb2.ExamsResponse`

#### Overview & Architectural Purpose
Возвращает список контрольных мероприятий и экзаменов сессии.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request` | `exams_pb2.ExamsRequest` | Yes | Parameter `request` of type `exams_pb2.ExamsRequest`. |
| `context` | `grpc.aio.ServicerContext` | Yes | Parameter `context` of type `grpc.aio.ServicerContext`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.servicers import GetExams

# Execute call
result = await GetExams(request=..., context=...)
```

---

## Class Model: `TeachersServicer`

Серверный обработчик gRPC-запросов преподавателей.

### `TeachersServicer.GetTeachers`
```python
async def GetTeachers( self, request: teachers_pb2.TeachersRequest, context: grpc.aio.ServicerContext, ) -> teachers_pb2.TeachersResponse
```

- **Source Reference**: [`api/grpc/servicers.py#L138-L154`](../../api/grpc/servicers.py#L138-L154)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `teachers_pb2.TeachersResponse`

#### Overview & Architectural Purpose
Возвращает справочник контактов и видеоконференций преподавателей.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request` | `teachers_pb2.TeachersRequest` | Yes | Parameter `request` of type `teachers_pb2.TeachersRequest`. |
| `context` | `grpc.aio.ServicerContext` | Yes | Parameter `context` of type `grpc.aio.ServicerContext`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.servicers import GetTeachers

# Execute call
result = await GetTeachers(request=..., context=...)
```

---
