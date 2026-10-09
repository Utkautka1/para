# Module Specification: `api/router/exams.py`
> **Path**: [`api/router/exams.py`](file:///home/u/Рабочий стол/para/api/router/exams.py)  
> **Subsystem**: `Exams API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер экзаменов — GET /exams, GET /exams/upcoming, POST /exams/refresh. Возвращает контрольные мероприятия (зачёты, экзамены, курсовые) с привязкой к неделям семестра.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`list_exams`](#list_exams) | Function | L23–L26 | `ExamsResponse` | Полный список аттестаций и экзаменов группы. |
| [`_resolve_current_week`](#_resolve_current_week) | Function | L29–L34 | `int` | Определяет номер текущей учебной недели семестра. |
| [`upcoming_exams`](#upcoming_exams) | Function | L38–L47 | `UpcomingExamsResponse` | Ближайшие предстоящие экзамены и зачёты. |
| [`refresh_exams`](#refresh_exams) | Function | L51–L55 | `ExamsRefreshResponse` | Принудительное обновление расписания экзаменов (Admin only). |

---

## 3. Exhaustive Function Specifications

### `list_exams`
- **Signature**: `async def list_exams() -> ExamsResponse`
- **Source Reference**: [api/router/exams.py#L23-L26](file:///home/u/Рабочий стол/para/api/router/exams.py#L23-L26)
- **Async**: `Yes`
- **Return Type**: `ExamsResponse`

#### Purpose & Architectural Intent
Полный список аттестаций и экзаменов группы.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `exams = await get_group_exams()`
2. `return ExamsResponse(count=len(exams), exams=exams)`

---

### `_resolve_current_week`
- **Signature**: `async def _resolve_current_week() -> int`
- **Source Reference**: [api/router/exams.py#L29-L34](file:///home/u/Рабочий стол/para/api/router/exams.py#L29-L34)
- **Async**: `Yes`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Определяет номер текущей учебной недели семестра.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `data = await fetch_schedule_data(force_refresh=False)`
2. `sem_start = data.get("config", {}).get("semesterStart", "2026-09-01") if data else "2`
3. `today = datetime.now(TIMEZONE).date()`
4. `return calculate_week_number(today, sem_start)`

---

### `upcoming_exams`
- **Signature**: `async def upcoming_exams( weeks_ahead: int = Query(default=4, ge=1, le=20, description="Горизонт планирования (недель)"), ) -> UpcomingExamsResponse`
- **Source Reference**: [api/router/exams.py#L38-L47](file:///home/u/Рабочий стол/para/api/router/exams.py#L38-L47)
- **Async**: `Yes`
- **Return Type**: `UpcomingExamsResponse`

#### Purpose & Architectural Intent
Ближайшие предстоящие экзамены и зачёты.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `weeks_ahead` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `cur_week = await _resolve_current_week()`
2. `exams = await get_group_exams()`
3. `filtered: list[ExamItem] = [`
4. `return UpcomingExamsResponse(current_week=cur_week, count=len(filtered), upcoming_exa`

---

### `refresh_exams`
- **Signature**: `async def refresh_exams() -> ExamsRefreshResponse`
- **Source Reference**: [api/router/exams.py#L51-L55](file:///home/u/Рабочий стол/para/api/router/exams.py#L51-L55)
- **Async**: `Yes`
- **Return Type**: `ExamsRefreshResponse`

#### Purpose & Architectural Intent
Принудительное обновление расписания экзаменов (Admin only).

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `await fetch_schedule_data(force_refresh=True)`
2. `exams = await get_group_exams()`
3. `return ExamsRefreshResponse(status="ok", updated_count=len(exams))`

---
