# Module Specification: `api/router/birthdays.py`
> **Path**: [`api/router/birthdays.py`](file:///home/u/Рабочий стол/para/api/router/birthdays.py)  
> **Subsystem**: `Birthdays API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер дней рождения — GET /birthdays, upcoming, today. Предоставляет календарь и расчёт дней до дня рождения одногруппников.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_map_calculated_to_dto`](#_map_calculated_to_dto) | Function | L25–L35 | `BirthdayItem` | Формирует объект BirthdayItem из рассчитанного словаря. |
| [`get_birthdays_calendar`](#get_birthdays_calendar) | Function | L39–L46 | `BirthdaysCalendarResponse` | Полный календарь дней рождения всех одногруппников. |
| [`get_upcoming_birthdays`](#get_upcoming_birthdays) | Function | L50–L60 | `UpcomingBirthdaysResponse` | Ближайшие дни рождения на N дней вперёд. |
| [`get_today_birthdays`](#get_today_birthdays) | Function | L64–L71 | `TodayBirthdaysResponse` | Список студентов, празднующих день рождения сегодня. |

---

## 3. Exhaustive Function Specifications

### `_map_calculated_to_dto`
- **Signature**: `def _map_calculated_to_dto(c: dict) -> BirthdayItem`
- **Source Reference**: [api/router/birthdays.py#L25-L35](file:///home/u/Рабочий стол/para/api/router/birthdays.py#L25-L35)
- **Async**: `No`
- **Return Type**: `BirthdayItem`

#### Purpose & Architectural Intent
Формирует объект BirthdayItem из рассчитанного словаря.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `c` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `b_date = f"{c.get('day', 1):02d}.{c.get('month', 1):02d}"`
2. `return BirthdayItem(`

---

### `get_birthdays_calendar`
- **Signature**: `async def get_birthdays_calendar() -> BirthdaysCalendarResponse`
- **Source Reference**: [api/router/birthdays.py#L39-L46](file:///home/u/Рабочий стол/para/api/router/birthdays.py#L39-L46)
- **Async**: `Yes`
- **Return Type**: `BirthdaysCalendarResponse`

#### Purpose & Architectural Intent
Полный календарь дней рождения всех одногруппников.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `registry = load_classmates_registry()`
2. `today = datetime.now(TIMEZONE).date()`
3. `calculated = [calculate_days_and_age(s, today) for s in registry]`
4. `calculated.sort(key=lambda x: x["days_until"])`
5. `items = [_map_calculated_to_dto(c) for c in calculated]`
6. `return BirthdaysCalendarResponse(count=len(items), birthdays=items)`

---

### `get_upcoming_birthdays`
- **Signature**: `async def get_upcoming_birthdays( days: int = Query(default=30, ge=1, le=365, description="Горизонт поиска (дней)"), ) -> UpcomingBirthdaysResponse`
- **Source Reference**: [api/router/birthdays.py#L50-L60](file:///home/u/Рабочий стол/para/api/router/birthdays.py#L50-L60)
- **Async**: `Yes`
- **Return Type**: `UpcomingBirthdaysResponse`

#### Purpose & Architectural Intent
Ближайшие дни рождения на N дней вперёд.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `days` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `registry = load_classmates_registry()`
2. `today = datetime.now(TIMEZONE).date()`
3. `calculated = [calculate_days_and_age(s, today) for s in registry]`
4. `filtered = [c for c in calculated if 0 <= c["days_until"] <= days]`
5. `filtered.sort(key=lambda x: x["days_until"])`
6. `items = [_map_calculated_to_dto(c) for c in filtered]`

---

### `get_today_birthdays`
- **Signature**: `async def get_today_birthdays() -> TodayBirthdaysResponse`
- **Source Reference**: [api/router/birthdays.py#L64-L71](file:///home/u/Рабочий стол/para/api/router/birthdays.py#L64-L71)
- **Async**: `Yes`
- **Return Type**: `TodayBirthdaysResponse`

#### Purpose & Architectural Intent
Список студентов, празднующих день рождения сегодня.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `registry = load_classmates_registry()`
2. `today = datetime.now(TIMEZONE).date()`
3. `calculated = [calculate_days_and_age(s, today) for s in registry]`
4. `today_items = [c for c in calculated if c["is_today"]]`
5. `items = [_map_calculated_to_dto(c) for c in today_items]`
6. `return TodayBirthdaysResponse(count=len(items), celebrants=items)`

---
