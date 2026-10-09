# Module Specification: `bot/handlers/user/attendance.py`
> **Path**: [`bot/handlers/user/attendance.py`](file:///home/u/Рабочий стол/para/bot/handlers/user/attendance.py)  
> **Subsystem**: `User Attendance Flow`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Хэндлеры просмотра персональной посещаемости студента (/my_attendance). Позволяет студентам группы 1-КПД-3: 1. Узнать свои суммарные отметки П/О/У/Н за всё время в ЛС бота 2. Видеть детальную помесячную разбивку (Сентябрь, Октябрь, ...) 3. Отслеживать персональный процент посещаемости пар 4. Обновлять сводку в топике по кнопке att_topic:refresh

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_calculate_attendance_percent`](#_calculate_attendance_percent) | Function | L33–L39 | `str` | Вычисляет процент посещения с учетом уважительных причин (У) |
| [`_format_personal_month_breakdown`](#_format_personal_month_breakdown) | Function | L42–L53 | `str` | Формирует компактный блок помесячной посещаемости. |
| [`format_personal_attendance_card`](#format_personal_attendance_card) | Function | L56–L79 | `str` | Формирует HTML-карточку персональной посещаемости студента. |
| [`get_personal_attendance_kb`](#get_personal_attendance_kb) | Function | L82–L86 | `InlineKeyboardMarkup` | Возвращает клавиатуру персонального экрана посещаемости. |
| [`_resolve_student_fio`](#_resolve_student_fio) | Function | L89–L97 | `str | None` | Определяет ФИО авторизованного студента по реестру одногрупп |
| [`cmd_my_attendance`](#cmd_my_attendance) | Function | L101–L120 | `None` | Отображает персональную карточку посещаемости студента. |
| [`cb_my_attendance_refresh`](#cb_my_attendance_refresh) | Function | L124–L139 | `None` | Обновляет персональную карточку посещаемости студента в ЛС. |
| [`cb_att_topic_refresh`](#cb_att_topic_refresh) | Function | L143–L148 | `None` | Обрабатывает нажатие 'Обновить сводку' прямо из топика Посещ |

---

## 3. Exhaustive Function Specifications

### `_calculate_attendance_percent`
- **Signature**: `def _calculate_attendance_percent(p: int, o: int, u: int, total: int) -> str`
- **Source Reference**: [bot/handlers/user/attendance.py#L33-L39](file:///home/u/Рабочий стол/para/bot/handlers/user/attendance.py#L33-L39)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Вычисляет процент посещения с учетом уважительных причин (У).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `p` | `int` | Input parameter |
| `o` | `int` | Input parameter |
| `u` | `int` | Input parameter |
| `total` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if total <= 0:`
2. `valid_classes = p + o + u`
3. `pct = (valid_classes / total) * 100.0`
4. `return f"{pct:.1f}%"`

---

### `_format_personal_month_breakdown`
- **Signature**: `def _format_personal_month_breakdown(months: dict[str, dict[str, int]]) -> str`
- **Source Reference**: [bot/handlers/user/attendance.py#L42-L53](file:///home/u/Рабочий стол/para/bot/handlers/user/attendance.py#L42-L53)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует компактный блок помесячной посещаемости.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `months` | `dict[str, dict[str, int]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not months:`
2. `lines = []`
3. `for m_name, counts in sorted(months.items()):`
4. `return "\n".join(lines)`

---

### `format_personal_attendance_card`
- **Signature**: `def format_personal_attendance_card(fio: str, student_data: dict[str, Any]) -> str`
- **Source Reference**: [bot/handlers/user/attendance.py#L56-L79](file:///home/u/Рабочий стол/para/bot/handlers/user/attendance.py#L56-L79)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует HTML-карточку персональной посещаемости студента.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `fio` | `str` | Input parameter |
| `student_data` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `tot = student_data.get("total", {})`
2. `p = tot.get("П", 0)`
3. `o = tot.get("О", 0)`
4. `u = tot.get("У", 0)`
5. `n = tot.get("Н", 0)`
6. `total_classes = p + o + u + n`

---

### `get_personal_attendance_kb`
- **Signature**: `def get_personal_attendance_kb() -> InlineKeyboardMarkup`
- **Source Reference**: [bot/handlers/user/attendance.py#L82-L86](file:///home/u/Рабочий стол/para/bot/handlers/user/attendance.py#L82-L86)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Возвращает клавиатуру персонального экрана посещаемости.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return InlineKeyboardMarkup(inline_keyboard=[[`

---

### `_resolve_student_fio`
- **Signature**: `def _resolve_student_fio(user, student: dict[str, Any] | None = None) -> str | None`
- **Source Reference**: [bot/handlers/user/attendance.py#L89-L97](file:///home/u/Рабочий стол/para/bot/handlers/user/attendance.py#L89-L97)
- **Async**: `No`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Определяет ФИО авторизованного студента по реестру одногруппников.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user` | `Any` | Input parameter |
| `student` | `dict[str, Any] | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if student and student.get("full_name"):`
2. `uid = user.id if user else 0`
3. `st = find_classmate_by_tg_id(uid)`
4. `if st and st.get("full_name"):`
5. `return user.full_name if user else None`

---

### `cmd_my_attendance`
- **Signature**: `async def cmd_my_attendance(message: Message) -> None`
- **Source Reference**: [bot/handlers/user/attendance.py#L101-L120](file:///home/u/Рабочий стол/para/bot/handlers/user/attendance.py#L101-L120)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отображает персональную карточку посещаемости студента.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if message.chat.type != "private":`
2. `is_auth, _, student = process_user_auth(message.from_user)`
3. `if not is_auth:`
4. `fio = _resolve_student_fio(message.from_user, student)`
5. `stats = await fetch_all_time_attendance(force_refresh=False)`
6. `data = find_student_attendance(stats, fio) if fio else None`

---

### `cb_my_attendance_refresh`
- **Signature**: `async def cb_my_attendance_refresh(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/attendance.py#L124-L139](file:///home/u/Рабочий стол/para/bot/handlers/user/attendance.py#L124-L139)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Обновляет персональную карточку посещаемости студента в ЛС.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `await callback.answer("⏳ Обновляю данные из журнала...")`
2. `fio = _resolve_student_fio(callback.from_user)`
3. `stats = await fetch_all_time_attendance(force_refresh=True)`
4. `data = find_student_attendance(stats, fio) if fio else None`
5. `if not data:`
6. `text = format_personal_attendance_card(data.get("fio", fio), data)`

---

### `cb_att_topic_refresh`
- **Signature**: `async def cb_att_topic_refresh(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/attendance.py#L143-L148](file:///home/u/Рабочий стол/para/bot/handlers/user/attendance.py#L143-L148)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Обрабатывает нажатие 'Обновить сводку' прямо из топика Посещаемость.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `await callback.answer("⏳ Загружаю свежие данные из Яндекс Документов...", show_alert=`
2. `success = await sync_attendance_topic_message(force_refresh=True)`
3. `ans = "✅ Сводка посещаемости успешно обновлена!" if success else "⚠️ Ошибка синхрониз`
4. `await callback.answer(ans, show_alert=True)`

---
