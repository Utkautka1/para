# Module Specification: `bot/handlers/admin/attendance.py`
> **Path**: [`bot/handlers/admin/attendance.py`](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py)  
> **Subsystem**: `Headman Attendance Polling`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Хэндлеры управления процессом отметки посещаемости. Обрабатывает команду /attendance и все инлайн-кнопки (att:*) исключительно для старосты (ALLOWED_USER_ID) и замстаросты (DEPUTY_USER_ID).

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_async_commit_and_update`](#_async_commit_and_update) | Function | L45–L60 | `None` | Фоновая асинхронная запись в Яндекс Таблицу с обновлением ст |
| [`_instant_topic_sync`](#_instant_topic_sync) | Function | L63–L72 | `None` | Мгновенно применяет оптимистичные отметки и обновляет топик  |
| [`get_partner_admin_id`](#get_partner_admin_id) | Function | L75–L83 | `int | None` | Возвращает Telegram ID второго администратора (староста/замс |
| [`notify_partner_about_attendance`](#notify_partner_about_attendance) | Function | L86–L103 | `None` | Отправляет полный отчёт об отметке пары второму администрато |
| [`finish_and_notify`](#finish_and_notify) | Function | L106–L121 | `None` | Мгновенно отображает сводку старосте и запускает параллельну |
| [`show_attendance_menu`](#show_attendance_menu) | Function | L126–L136 | `None` | Открывает меню выбора даты для отметки посещаемости. |
| [`cb_select_day`](#cb_select_day) | Function | L140–L150 | `None` | Выводит список пар на выбранную дату. |
| [`parse_start_callback`](#parse_start_callback) | Function | L153–L159 | `Any` | Извлекает целевую дату и номер пары из callback данных. |
| [`get_initiator_title`](#get_initiator_title) | Function | L162–L165 | `str` | Возвращает читаемый статус инициатора опроса (Староста / Зам |
| [`check_session_ownership`](#check_session_ownership) | Function | L168–L177 | `bool` | Проверяет принадлежность активной сессии текущему старосте. |
| [`cb_start_attendance`](#cb_start_attendance) | Function | L181–L205 | `None` | Инициализирует сессию отметки и выводит первого студента. |
| [`cb_mark_student`](#cb_mark_student) | Function | L209–L226 | `None` | Фиксирует отметку и переключает на следующего студента. |
| [`cb_step_back`](#cb_step_back) | Function | L230–L244 | `None` | Возвращает к предыдущему студенту для исправления отметки. |
| [`cb_all_present`](#cb_all_present) | Function | L248–L258 | `None` | Проставляет 'П' всем оставшимся студентам и завершает опрос. |
| [`notify_partner_about_cancellation`](#notify_partner_about_cancellation) | Function | L261–L278 | `None` | Оповещает второго администратора об отмене проведения пары. |
| [`cb_cancel_lesson`](#cb_cancel_lesson) | Function | L282–L291 | `None` | Отменяет опрос для указанной пары и уведомляет напарника. |
| [`cb_abort_survey`](#cb_abort_survey) | Function | L295–L305 | `None` | Прерывает активный опрос старостой. |
| [`cb_close_menu`](#cb_close_menu) | Function | L309–L313 | `None` | Удаляет меню выбора пары. |

---

## 3. Exhaustive Function Specifications

### `_async_commit_and_update`
- **Signature**: `async def _async_commit_and_update( message: Message | None, session, stats: dict[str, int] ) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L45-L60](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L45-L60)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Фоновая асинхронная запись в Яндекс Таблицу с обновлением статуса.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message | None` | Input parameter |
| `session` | `Any` | Input parameter |
| `stats` | `dict[str, int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `success = await commit_session_to_table(session)`
2. `if not message:`
3. `badge = (`
4. `try:`

---

### `_instant_topic_sync`
- **Signature**: `async def _instant_topic_sync(session) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L63-L72](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L63-L72)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Мгновенно применяет оптимистичные отметки и обновляет топик в Telegram.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `get_partner_admin_id`
- **Signature**: `def get_partner_admin_id(current_user_id: int) -> int | None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L75-L83](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L75-L83)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Возвращает Telegram ID второго администратора (староста/замстаросты).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `current_user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `from config import ALLOWED_USER_ID, DEPUTY_USER_ID`
2. `if current_user_id == ALLOWED_USER_ID:`
3. `if current_user_id == DEPUTY_USER_ID:`
4. `return None`

---

### `notify_partner_about_attendance`
- **Signature**: `async def notify_partner_about_attendance( session, stats: dict[str, int], user_full_name: str | None = None ) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L86-L103](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L86-L103)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет полный отчёт об отметке пары второму администратору в ЛС.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `Any` | Input parameter |
| `stats` | `dict[str, int]` | Input parameter |
| `user_full_name` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `partner_id = get_partner_admin_id(session.initiator_id)`
2. `if not partner_id:`
3. `title = get_initiator_title(session.initiator_id)`
4. `if user_full_name:`
5. `text = format_partner_attendance_report(session, stats, title)`
6. `try:`

---

### `finish_and_notify`
- **Signature**: `async def finish_and_notify(cb: CallbackQuery, session) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L106-L121](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L106-L121)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Мгновенно отображает сводку старосте и запускает параллельную синхронизацию.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |
| `session` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `stats = calculate_summary_stats(session.marks)`
2. `text_saving = (`
3. `if cb.message:`
4. `asyncio.create_task(_instant_topic_sync(session))`
5. `asyncio.create_task(_async_commit_and_update(cb.message, session, stats))`
6. `asyncio.create_task(notify_partner_about_attendance(session, stats, cb.from_user.full`

---

### `show_attendance_menu`
- **Signature**: `async def show_attendance_menu(event: Message | CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L126-L136](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L126-L136)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Открывает меню выбора даты для отметки посещаемости.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `event` | `Message | CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `from bot.templates.admin.attendance import get_days_select_kb`
2. `text = "📋 <b>Отметка посещаемости</b>\n\nВыберите учебный день для отметки пар:"`
3. `kb = get_days_select_kb()`
4. `if isinstance(event, CallbackQuery):`

---

### `cb_select_day`
- **Signature**: `async def cb_select_day(cb: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L140-L150](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L140-L150)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Выводит список пар на выбранную дату.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `from datetime import date`
2. `day_str = cb.data.split(":")[2]`
3. `target_date = date.fromisoformat(day_str)`
4. `lessons = await get_api_schedule_for_date(target_date)`
5. `kb = get_lesson_select_kb(lessons, target_date)`
6. `text = f"📋 <b>Дата: {target_date.strftime('%d.%m.%Y')}</b>\nВыберите пару для отметки`

---

### `parse_start_callback`
- **Signature**: `def parse_start_callback(data: str)`
- **Source Reference**: [bot/handlers/admin/attendance.py#L153-L159](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L153-L159)
- **Async**: `No`
- **Return Type**: `Any`

#### Purpose & Architectural Intent
Извлекает целевую дату и номер пары из callback данных.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `data` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `from datetime import date`
2. `parts = data.split(":")`
3. `if len(parts) == 4:`
4. `return datetime.now(TIMEZONE).date(), int(parts[2])`

---

### `get_initiator_title`
- **Signature**: `def get_initiator_title(initiator_id: int) -> str`
- **Source Reference**: [bot/handlers/admin/attendance.py#L162-L165](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L162-L165)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Возвращает читаемый статус инициатора опроса (Староста / Замстаросты).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `initiator_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `from config import ALLOWED_USER_ID`
2. `return "Староста" if initiator_id == ALLOWED_USER_ID else "Замстаросты"`

---

### `check_session_ownership`
- **Signature**: `async def check_session_ownership(cb: CallbackQuery, session) -> bool`
- **Source Reference**: [bot/handlers/admin/attendance.py#L168-L177](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L168-L177)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет принадлежность активной сессии текущему старосте.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |
| `session` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not session:`
2. `if session.initiator_id != cb.from_user.id:`
3. `return True`

---

### `cb_start_attendance`
- **Signature**: `async def cb_start_attendance(cb: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L181-L205](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L181-L205)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Инициализирует сессию отметки и выводит первого студента.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `active = await get_active_session()`
2. `if active and active.initiator_id != cb.from_user.id:`
3. `await cb.answer()`
4. `target_date, lesson_num = parse_start_callback(cb.data)`
5. `lessons = await get_api_schedule_for_date(target_date)`
6. `matched = [les for les in lessons if getattr(les, "number", getattr(les, "period", -1`

---

### `cb_mark_student`
- **Signature**: `async def cb_mark_student(cb: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L209-L226](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L209-L226)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Фиксирует отметку и переключает на следующего студента.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `if not await check_session_ownership(cb, session):`
3. `mark = cb.data.split(":")[2]`
4. `session = await record_student_mark(mark)`
5. `if not session:`
6. `await cb.answer()`

---

### `cb_step_back`
- **Signature**: `async def cb_step_back(cb: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L230-L244](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L230-L244)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Возвращает к предыдущему студенту для исправления отметки.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `if not await check_session_ownership(cb, session):`
3. `session = await step_back()`
4. `if not session:`
5. `can_back = session.current_idx > 0`
6. `text = format_student_card(session)`

---

### `cb_all_present`
- **Signature**: `async def cb_all_present(cb: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L248-L258](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L248-L258)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Проставляет 'П' всем оставшимся студентам и завершает опрос.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `if not await check_session_ownership(cb, session):`
3. `session = await mark_all_remaining_present()`
4. `if not session:`
5. `await cb.answer()`
6. `await finish_and_notify(cb, session)`

---

### `notify_partner_about_cancellation`
- **Signature**: `async def notify_partner_about_cancellation( lesson_num: int | str, user_id: int, user_full_name: str | None = None ) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L261-L278](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L261-L278)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Оповещает второго администратора об отмене проведения пары.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson_num` | `int | str` | Input parameter |
| `user_id` | `int` | Input parameter |
| `user_full_name` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `partner_id = get_partner_admin_id(user_id)`
2. `if not partner_id:`
3. `title = get_initiator_title(user_id)`
4. `if user_full_name:`
5. `text = format_partner_cancel_report(lesson_num, title)`
6. `try:`

---

### `cb_cancel_lesson`
- **Signature**: `async def cb_cancel_lesson(cb: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L282-L291](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L282-L291)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отменяет опрос для указанной пары и уведомляет напарника.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `lesson_num = cb.data.split(":")[2]`
2. `await clear_session()`
3. `if cb.message:`
4. `asyncio.create_task(`
5. `await cb.answer()`

---

### `cb_abort_survey`
- **Signature**: `async def cb_abort_survey(cb: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L295-L305](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L295-L305)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Прерывает активный опрос старостой.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `if session and session.initiator_id != cb.from_user.id:`
3. `await clear_session()`
4. `if cb.message:`
5. `await cb.answer()`

---

### `cb_close_menu`
- **Signature**: `async def cb_close_menu(cb: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/attendance.py#L309-L313](file:///home/u/Рабочий стол/para/bot/handlers/admin/attendance.py#L309-L313)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет меню выбора пары.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `if cb.message:`
2. `await cb.answer()`

---
