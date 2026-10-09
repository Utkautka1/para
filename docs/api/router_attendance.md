# Module Specification: `api/router/attendance.py`
> **Path**: [`api/router/attendance.py`](file:///home/u/Рабочий стол/para/api/router/attendance.py)  
> **Subsystem**: `Attendance API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер посещаемости — GET /attendance/stats, student, session, mark, commit. Предоставляет аналитику пропусков и управление сессией отметки старосты.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_attendance_stats`](#get_attendance_stats) | Function | L38–L42 | `AttendanceStatsResponse` | Агрегированная сводка посещаемости группы за весь учебный го |
| [`get_student_attendance`](#get_student_attendance) | Function | L46–L56 | `StudentPersonalStatsResponse` | Персональная аналитика посещаемости по ФИО студента. |
| [`_build_session_response`](#_build_session_response) | Function | L59–L73 | `ActiveSessionResponse` | Собирает DTO активной сессии отметки пары. |
| [`get_current_session`](#get_current_session) | Function | L77–L80 | `ActiveSessionResponse` | Текущее состояние активного опроса пары старостой. |
| [`start_session`](#start_session) | Function | L84–L90 | `ActiveSessionResponse` | Инициализация новой сессии опроса посещаемости (Admin only). |
| [`mark_student`](#mark_student) | Function | L94–L99 | `ActiveSessionResponse` | Выставление статуса текущему студенту (П, О, У, Н) (Admin on |
| [`batch_present`](#batch_present) | Function | L103–L108 | `ActiveSessionResponse` | Массовая отметка всех оставшихся студентов как присутствующи |
| [`commit_session`](#commit_session) | Function | L112–L121 | `CommitAttendanceResponse` | Сохранение результатов сессии в онлайн-таблицу Яндекс Докуме |
| [`cancel_session`](#cancel_session) | Function | L125–L128 | `dict` | Сброс и отмена текущей незавершённой сессии (Admin only). |

---

## 3. Exhaustive Function Specifications

### `get_attendance_stats`
- **Signature**: `async def get_attendance_stats(force_refresh: bool = Query(default=False)) -> AttendanceStatsResponse`
- **Source Reference**: [api/router/attendance.py#L38-L42](file:///home/u/Рабочий стол/para/api/router/attendance.py#L38-L42)
- **Async**: `Yes`
- **Return Type**: `AttendanceStatsResponse`

#### Purpose & Architectural Intent
Агрегированная сводка посещаемости группы за весь учебный год.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = await fetch_all_time_attendance(force_refresh=force_refresh)`
2. `items = [StudentStatItem(fio=v["fio"], total=v["total"], months=v.get("months", {})) `
3. `return AttendanceStatsResponse(count=len(items), students=items)`

---

### `get_student_attendance`
- **Signature**: `async def get_student_attendance(fio: str) -> StudentPersonalStatsResponse`
- **Source Reference**: [api/router/attendance.py#L46-L56](file:///home/u/Рабочий стол/para/api/router/attendance.py#L46-L56)
- **Async**: `Yes`
- **Return Type**: `StudentPersonalStatsResponse`

#### Purpose & Architectural Intent
Персональная аналитика посещаемости по ФИО студента.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `fio` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = await fetch_all_time_attendance(force_refresh=False)`
2. `stat = find_student_attendance(data, fio)`
3. `if not stat:`
4. `tot = stat.get("total", {})`
5. `p, o, u, n = tot.get("П", 0), tot.get("О", 0), tot.get("У", 0), tot.get("Н", 0)`
6. `all_lessons = p + o + u + n`

---

### `_build_session_response`
- **Signature**: `def _build_session_response(s) -> ActiveSessionResponse`
- **Source Reference**: [api/router/attendance.py#L59-L73](file:///home/u/Рабочий стол/para/api/router/attendance.py#L59-L73)
- **Async**: `No`
- **Return Type**: `ActiveSessionResponse`

#### Purpose & Architectural Intent
Собирает DTO активной сессии отметки пары.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `s` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not s:`
2. `cur_name = s.students[s.current_idx][1] if s.current_idx < len(s.students) else None`
3. `return ActiveSessionResponse(`

---

### `get_current_session`
- **Signature**: `async def get_current_session() -> ActiveSessionResponse`
- **Source Reference**: [api/router/attendance.py#L77-L80](file:///home/u/Рабочий стол/para/api/router/attendance.py#L77-L80)
- **Async**: `Yes`
- **Return Type**: `ActiveSessionResponse`

#### Purpose & Architectural Intent
Текущее состояние активного опроса пары старостой.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `return _build_session_response(session)`

---

### `start_session`
- **Signature**: `async def start_session(payload: StartSessionRequest) -> ActiveSessionResponse`
- **Source Reference**: [api/router/attendance.py#L84-L90](file:///home/u/Рабочий стол/para/api/router/attendance.py#L84-L90)
- **Async**: `Yes`
- **Return Type**: `ActiveSessionResponse`

#### Purpose & Architectural Intent
Инициализация новой сессии опроса посещаемости (Admin only).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `payload` | `StartSessionRequest` | Input parameter |

#### Step-by-Step Logic Execution
1. `t_date = date.fromisoformat(payload.target_date)`
2. `session = await create_attendance_session(t_date, payload.lesson_num, payload.lesson_`
3. `if not session:`
4. `return _build_session_response(session)`

---

### `mark_student`
- **Signature**: `async def mark_student(payload: MarkStudentRequest) -> ActiveSessionResponse`
- **Source Reference**: [api/router/attendance.py#L94-L99](file:///home/u/Рабочий стол/para/api/router/attendance.py#L94-L99)
- **Async**: `Yes`
- **Return Type**: `ActiveSessionResponse`

#### Purpose & Architectural Intent
Выставление статуса текущему студенту (П, О, У, Н) (Admin only).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `payload` | `MarkStudentRequest` | Input parameter |

#### Step-by-Step Logic Execution
1. `session = await record_student_mark(payload.mark)`
2. `if not session:`
3. `return _build_session_response(session)`

---

### `batch_present`
- **Signature**: `async def batch_present() -> ActiveSessionResponse`
- **Source Reference**: [api/router/attendance.py#L103-L108](file:///home/u/Рабочий стол/para/api/router/attendance.py#L103-L108)
- **Async**: `Yes`
- **Return Type**: `ActiveSessionResponse`

#### Purpose & Architectural Intent
Массовая отметка всех оставшихся студентов как присутствующих (П) (Admin only).

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `session = await mark_all_remaining_present()`
2. `if not session:`
3. `return _build_session_response(session)`

---

### `commit_session`
- **Signature**: `async def commit_session() -> CommitAttendanceResponse`
- **Source Reference**: [api/router/attendance.py#L112-L121](file:///home/u/Рабочий стол/para/api/router/attendance.py#L112-L121)
- **Async**: `Yes`
- **Return Type**: `CommitAttendanceResponse`

#### Purpose & Architectural Intent
Сохранение результатов сессии в онлайн-таблицу Яндекс Документов (Admin only).

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `if not session:`
3. `count = len(session.marks)`
4. `ok = await commit_session_to_table(session)`
5. `if not ok:`
6. `return CommitAttendanceResponse(status="ok", message="Marks saved to Yandex Docs", ma`

---

### `cancel_session`
- **Signature**: `async def cancel_session() -> dict`
- **Source Reference**: [api/router/attendance.py#L125-L128](file:///home/u/Рабочий стол/para/api/router/attendance.py#L125-L128)
- **Async**: `Yes`
- **Return Type**: `dict`

#### Purpose & Architectural Intent
Сброс и отмена текущей незавершённой сессии (Admin only).

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `await clear_session()`
2. `return {"status": "ok", "message": "Attendance session cleared"}`

---
