# Module Specification: `bot/templates/admin/attendance.py`
> **Path**: [`bot/templates/admin/attendance.py`](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py)  
> **Subsystem**: `Attendance Keyboards`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Шаблоны сообщений и клавиатур для модуля отметки посещаемости. Содержит: - Инлайн-клавиатуры для подтверждения пары, выбора статуса (П, О, У, Н) - Кнопки быстрого завершения ('Все остальные П') и шага назад - Форматирование карточек студентов и итоговой сводки

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_lesson_confirm_kb`](#get_lesson_confirm_kb) | Function | L16–L24 | `InlineKeyboardMarkup` | Клавиатура подтверждения факта проведения пары. |
| [`get_student_poll_kb`](#get_student_poll_kb) | Function | L27–L47 | `InlineKeyboardMarkup` | Генерирует 4 инлайн-кнопки статусов и кнопки навигации. |
| [`format_confirm_text`](#format_confirm_text) | Function | L50–L56 | `str` | Формирует текст запроса подтверждения проведения пары. |
| [`format_student_card`](#format_student_card) | Function | L59–L69 | `str` | Формирует текст карточки текущего студента с прогресс-баром. |
| [`format_summary_text`](#format_summary_text) | Function | L72–L88 | `str` | Формирует финальный отчёт после сохранения посещаемости. |
| [`format_partner_attendance_report`](#format_partner_attendance_report) | Function | L91–L105 | `str` | Формирует полный отчёт посещаемости для второго администрато |
| [`format_partner_cancel_report`](#format_partner_cancel_report) | Function | L108–L116 | `str` | Формирует уведомление об отмене пары для второго администрат |
| [`get_days_select_kb`](#get_days_select_kb) | Function | L119–L135 | `InlineKeyboardMarkup` | Генерирует инлайн-кнопки выбора учебных дней для отметки пос |
| [`get_lesson_select_kb`](#get_lesson_select_kb) | Function | L138–L159 | `InlineKeyboardMarkup` | Формирует список пар на выбор для указанной даты. |

---

## 3. Exhaustive Function Specifications

### `get_lesson_confirm_kb`
- **Signature**: `def get_lesson_confirm_kb(lesson_num: int) -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/admin/attendance.py#L16-L24](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py#L16-L24)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Клавиатура подтверждения факта проведения пары.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson_num` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `kb = [`
2. `return InlineKeyboardMarkup(inline_keyboard=kb)`

---

### `get_student_poll_kb`
- **Signature**: `def get_student_poll_kb(can_back: bool) -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/admin/attendance.py#L27-L47](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py#L27-L47)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Генерирует 4 инлайн-кнопки статусов и кнопки навигации.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `can_back` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `kb = [`
2. `nav_row = []`
3. `if can_back:`
4. `nav_row.append(InlineKeyboardButton(text="❌ Отменить", callback_data="att:abort"))`
5. `kb.append(nav_row)`
6. `return InlineKeyboardMarkup(inline_keyboard=kb)`

---

### `format_confirm_text`
- **Signature**: `def format_confirm_text(lesson_num: int, title: str, teacher: str) -> str`
- **Source Reference**: [bot/templates/admin/attendance.py#L50-L56](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py#L50-L56)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует текст запроса подтверждения проведения пары.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson_num` | `int` | Input parameter |
| `title` | `str` | Input parameter |
| `teacher` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `return (`

---

### `format_student_card`
- **Signature**: `def format_student_card(session: AttendanceSession) -> str`
- **Source Reference**: [bot/templates/admin/attendance.py#L59-L69](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py#L59-L69)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует текст карточки текущего студента с прогресс-баром.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `AttendanceSession` | Input parameter |

#### Step-by-Step Logic Execution
1. `total = len(session.students)`
2. `idx = session.current_idx + 1`
3. `_, fio = session.students[session.current_idx]`
4. `return (`

---

### `format_summary_text`
- **Signature**: `def format_summary_text(session: AttendanceSession, stats: dict[str, int]) -> str`
- **Source Reference**: [bot/templates/admin/attendance.py#L72-L88](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py#L72-L88)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует финальный отчёт после сохранения посещаемости.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `AttendanceSession` | Input parameter |
| `stats` | `dict[str, int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `absent_names: list[str] = []`
2. `for row_idx, fio in session.students:`
3. `absent_str = "\n\nОтсутствующие / Опоздавшие:\n• " + "\n• ".join(absent_names) if abs`
4. `return (`

---

### `format_partner_attendance_report`
- **Signature**: `def format_partner_attendance_report( session: AttendanceSession, stats: dict[str, int], initiator_title: str ) -> str`
- **Source Reference**: [bot/templates/admin/attendance.py#L91-L105](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py#L91-L105)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует полный отчёт посещаемости для второго администратора. Показывает, кто провел отметку, предмет, баланс присутствующих и список отсутствующих.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `AttendanceSession` | Input parameter |
| `stats` | `dict[str, int]` | Input parameter |
| `initiator_title` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `base_summary = format_summary_text(session, stats)`
2. `return (`

---

### `format_partner_cancel_report`
- **Signature**: `def format_partner_cancel_report(lesson_num: int | str, initiator_title: str) -> str`
- **Source Reference**: [bot/templates/admin/attendance.py#L108-L116](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py#L108-L116)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует уведомление об отмене пары для второго администратора.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson_num` | `int | str` | Input parameter |
| `initiator_title` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `return (`

---

### `get_days_select_kb`
- **Signature**: `def get_days_select_kb() -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/admin/attendance.py#L119-L135](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py#L119-L135)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Генерирует инлайн-кнопки выбора учебных дней для отметки посещаемости.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `from datetime import datetime, timedelta`
2. `from config import TIMEZONE`
3. `today = datetime.now(TIMEZONE).date()`
4. `weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]`
5. `kb = []`
6. `for offset in range(7):`

---

### `get_lesson_select_kb`
- **Signature**: `def get_lesson_select_kb(lessons: list, chosen_date=None) -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/admin/attendance.py#L138-L159](file:///home/u/Рабочий стол/para/bot/templates/admin/attendance.py#L138-L159)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Формирует список пар на выбор для указанной даты.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lessons` | `list` | Input parameter |
| `chosen_date` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `from datetime import datetime`
2. `from config import TIMEZONE`
3. `d_obj = chosen_date or datetime.now(TIMEZONE).date()`
4. `d_str = d_obj.isoformat()`
5. `kb, seen = [], set()`
6. `for les in lessons:`

---
