# Module Specification: `api/router/schedule.py`
> **Path**: [`api/router/schedule.py`](file:///home/u/Рабочий стол/para/api/router/schedule.py)  
> **Subsystem**: `Schedule API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер расписания — GET /schedule (day, today, tomorrow, week, current, refresh). Предоставляет чистые данные расписания занятий группы 1-КПД-3 с валидацией прав тестера или API-ключа.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_current_monday`](#_current_monday) | Function | L28–L31 | `date` | Вычисляет понедельник текущей недели. |
| [`schedule_day`](#schedule_day) | Function | L35–L42 | `DayScheduleResponse` | Расписание на конкретный учебный день. |
| [`schedule_today`](#schedule_today) | Function | L46–L50 | `DayScheduleResponse` | Расписание занятий на сегодня. |
| [`schedule_tomorrow`](#schedule_tomorrow) | Function | L54–L58 | `DayScheduleResponse` | Расписание занятий на завтра. |
| [`schedule_week`](#schedule_week) | Function | L62–L70 | `WeekScheduleResponse` | Расписание занятий на целую неделю (пн—сб). |
| [`_find_current_and_next`](#_find_current_and_next) | Function | L73–L84 | `tuple[Lesson | None, Lesson | None]` | Находит текущую и ближайшую следующую пару по текущему време |
| [`schedule_current`](#schedule_current) | Function | L88–L97 | `CurrentLessonResponse` | Информация о текущем и следующем занятии прямо сейчас. |
| [`schedule_refresh`](#schedule_refresh) | Function | L101–L105 | `ScheduleRefreshResponse` | Принудительная очистка кэша расписания (Admin only). |

---

## 3. Exhaustive Function Specifications

### `_current_monday`
- **Signature**: `def _current_monday() -> date`
- **Source Reference**: [api/router/schedule.py#L28-L31](file:///home/u/Рабочий стол/para/api/router/schedule.py#L28-L31)
- **Async**: `No`
- **Return Type**: `date`

#### Purpose & Architectural Intent
Вычисляет понедельник текущей недели.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `today = datetime.now(TIMEZONE).date()`
2. `return today - timedelta(days=today.weekday())`

---

### `schedule_day`
- **Signature**: `async def schedule_day( target_date: date | None = Query(default=None, description="YYYY-MM-DD, по умолчанию сегодня"), force_refresh: bool = Query(default=False), ) -> DayScheduleResponse`
- **Source Reference**: [api/router/schedule.py#L35-L42](file:///home/u/Рабочий стол/para/api/router/schedule.py#L35-L42)
- **Async**: `Yes`
- **Return Type**: `DayScheduleResponse`

#### Purpose & Architectural Intent
Расписание на конкретный учебный день.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date | None` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `day = target_date or datetime.now(TIMEZONE).date()`
2. `lessons = await get_schedule_for_date(day, force_refresh=force_refresh)`
3. `return DayScheduleResponse(date=day, lessons=lessons)`

---

### `schedule_today`
- **Signature**: `async def schedule_today(force_refresh: bool = Query(default=False)) -> DayScheduleResponse`
- **Source Reference**: [api/router/schedule.py#L46-L50](file:///home/u/Рабочий стол/para/api/router/schedule.py#L46-L50)
- **Async**: `Yes`
- **Return Type**: `DayScheduleResponse`

#### Purpose & Architectural Intent
Расписание занятий на сегодня.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `today = datetime.now(TIMEZONE).date()`
2. `lessons = await get_schedule_for_date(today, force_refresh=force_refresh)`
3. `return DayScheduleResponse(date=today, lessons=lessons)`

---

### `schedule_tomorrow`
- **Signature**: `async def schedule_tomorrow(force_refresh: bool = Query(default=False)) -> DayScheduleResponse`
- **Source Reference**: [api/router/schedule.py#L54-L58](file:///home/u/Рабочий стол/para/api/router/schedule.py#L54-L58)
- **Async**: `Yes`
- **Return Type**: `DayScheduleResponse`

#### Purpose & Architectural Intent
Расписание занятий на завтра.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `tomorrow = datetime.now(TIMEZONE).date() + timedelta(days=1)`
2. `lessons = await get_schedule_for_date(tomorrow, force_refresh=force_refresh)`
3. `return DayScheduleResponse(date=tomorrow, lessons=lessons)`

---

### `schedule_week`
- **Signature**: `async def schedule_week( monday: date | None = Query(default=None, description="Понедельник недели (YYYY-MM-DD)"), force_refresh: bool = Query(default=False), ) -> WeekScheduleResponse`
- **Source Reference**: [api/router/schedule.py#L62-L70](file:///home/u/Рабочий стол/para/api/router/schedule.py#L62-L70)
- **Async**: `Yes`
- **Return Type**: `WeekScheduleResponse`

#### Purpose & Architectural Intent
Расписание занятий на целую неделю (пн—сб).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `monday` | `date | None` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `mon = monday or _current_monday()`
2. `raw = await get_week_schedule(mon, force_refresh=force_refresh)`
3. `days = [WeekDayItem(date=d, lessons=ls) for d, ls in raw]`
4. `return WeekScheduleResponse(monday=mon, days=days)`

---

### `_find_current_and_next`
- **Signature**: `def _find_current_and_next(lessons: list[Lesson], now_time: str) -> tuple[Lesson | None, Lesson | None]`
- **Source Reference**: [api/router/schedule.py#L73-L84](file:///home/u/Рабочий стол/para/api/router/schedule.py#L73-L84)
- **Async**: `No`
- **Return Type**: `tuple[Lesson | None, Lesson | None]`

#### Purpose & Architectural Intent
Находит текущую и ближайшую следующую пару по текущему времени.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Input parameter |
| `now_time` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `curr, nxt = None, None`
2. `for l in sorted(lessons, key=lambda x: x.period):`
3. `return curr, nxt`

---

### `schedule_current`
- **Signature**: `async def schedule_current() -> CurrentLessonResponse`
- **Source Reference**: [api/router/schedule.py#L88-L97](file:///home/u/Рабочий стол/para/api/router/schedule.py#L88-L97)
- **Async**: `Yes`
- **Return Type**: `CurrentLessonResponse`

#### Purpose & Architectural Intent
Информация о текущем и следующем занятии прямо сейчас.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `now_dt = datetime.now(TIMEZONE)`
2. `lessons = await get_schedule_for_date(now_dt.date())`
3. `curr, nxt = _find_current_and_next(lessons, now_dt.strftime("%H:%M"))`
4. `return CurrentLessonResponse(`

---

### `schedule_refresh`
- **Signature**: `async def schedule_refresh() -> ScheduleRefreshResponse`
- **Source Reference**: [api/router/schedule.py#L101-L105](file:///home/u/Рабочий стол/para/api/router/schedule.py#L101-L105)
- **Async**: `Yes`
- **Return Type**: `ScheduleRefreshResponse`

#### Purpose & Architectural Intent
Принудительная очистка кэша расписания (Admin only).

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `deleted = await cache_flush(pattern="sched:*")`
2. `now_str = datetime.now(TIMEZONE).isoformat()`
3. `return ScheduleRefreshResponse(status="ok", flushed_keys=deleted, timestamp=now_str)`

---
