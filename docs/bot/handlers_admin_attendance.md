# Component Reference: `bot/handlers/admin/attendance.py`
> **File Path**: [`bot/handlers/admin/attendance.py`](../../bot/handlers/admin/attendance.py)
> **Subsystem**: `Headman Attendance Polling`

## 1. Purpose
Хэндлеры управления процессом отметки посещаемости.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_async_commit_and_update`](#_async_commit_and_update) | Function | L59–L81 | `None` | Выполняет фоновую фиксацию посещаемости в Яндекс Таблиц... |
| [`_instant_topic_sync`](#_instant_topic_sync) | Function | L84–L99 | `None` | Мгновенно обновляет топик посещаемости в Telegram через... |
| [`get_partner_admin_id`](#get_partner_admin_id) | Function | L102–L118 | `int \| None` | Определяет Telegram ID напарника по модерации (староста... |
| [`notify_partner_about_attendance`](#notify_partner_about_attendance) | Function | L121–L144 | `None` | Отправляет полный отчет о завершении отметки пары второ... |
| [`finish_and_notify`](#finish_and_notify) | Function | L147–L170 | `None` | Мгновенно выводит сводку старосте и запускает асинхронн... |
| [`show_attendance_menu`](#show_attendance_menu) | Function | L175–L192 | `None` | Отображает интерактивное меню выбора учебного дня для о... |
| [`cb_select_day`](#cb_select_day) | Function | L196–L214 | `None` | Формирует и отображает кнопки доступных пар на выбранну... |
| [`parse_start_callback`](#parse_start_callback) | Function | L217–L231 | `Any` | Парсит целевую дату и номер пары из строки callback_dat... |
| [`get_initiator_title`](#get_initiator_title) | Function | L234–L244 | `str` | Возвращает русскоязычное наименование роли старосты по ... |
| [`check_session_ownership`](#check_session_ownership) | Function | L247–L266 | `bool` | Проверяет, принадлежит ли активная сессия опроса текуще... |
| [`_resolve_lesson_title_for_start`](#_resolve_lesson_title_for_start) | Function | L269–L282 | `str` | Определяет наименование дисциплины по номеру пары из ра... |
| [`_ensure_session_available`](#_ensure_session_available) | Function | L285–L301 | `bool` | Проверяет доступность запуска нового опроса посещаемост... |
| [`_init_session_safe`](#_init_session_safe) | Function | L304–L326 | `Any` | Безопасно создает сессию посещаемости с обработкой ошиб... |
| [`notify_partner_about_single_update`](#notify_partner_about_single_update) | Function | L329–L350 | `None` | Отправляет уведомление второму администратору о точечно... |
| [`_commit_single_attendance_background`](#_commit_single_attendance_background) | Function | L353–L375 | `None` | Выполняет фоновую фиксацию одиночной отметки в Яндекс Т... |
| [`cb_lesson_mode`](#cb_lesson_mode) | Function | L379–L397 | `None` | Отображает выбор режима отметки пары: опрос всей группы... |
| [`cb_single_student_menu`](#cb_single_student_menu) | Function | L401–L420 | `None` | Отображает список студентов по два в ряд для точечной о... |
| [`cb_pick_student`](#cb_pick_student) | Function | L424–L443 | `None` | Отображает карточку студента с кнопками установки новой... |
| [`_build_single_session`](#_build_single_session) | Function | L446–L463 | `AttendanceSession` | Создает объект AttendanceSession с отметкой для одного ... |
| [`cb_set_single_mark`](#cb_set_single_mark) | Function | L467–L492 | `None` | Устанавливает новую отметку выбранному студенту и запус... |
| [`cb_start_attendance`](#cb_start_attendance) | Function | L496–L518 | `None` | Инициализирует интерактивную сессию опроса посещаемости... |
| [`cb_mark_student`](#cb_mark_student) | Function | L522–L546 | `None` | Фиксирует статус студента и переходит к следующему шагу... |
| [`cb_step_back`](#cb_step_back) | Function | L550–L573 | `None` | Возвращает старосту к предыдущему студенту для исправле... |
| [`cb_all_present`](#cb_all_present) | Function | L577–L597 | `None` | Проставляет статус 'П' (Присутствует) всем оставшимся с... |
| [`notify_partner_about_cancellation`](#notify_partner_about_cancellation) | Function | L600–L624 | `None` | Оповещает второго администратора об отмене проведения п... |
| [`cb_cancel_lesson`](#cb_cancel_lesson) | Function | L628–L644 | `None` | Отменяет опрос для указанной пары и уведомляет напарник... |
| [`cb_abort_survey`](#cb_abort_survey) | Function | L648–L668 | `None` | Прерывает активный опрос посещаемости по запросу его ин... |
| [`cb_close_menu`](#cb_close_menu) | Function | L672–L685 | `None` | Удаляет сообщение с интерактивным меню посещаемости из ... |

---

## 3. Comprehensive Function Specifications

### `_async_commit_and_update`
```python
async def _async_commit_and_update(message: Message | None, session, stats: dict[str, int]) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L59-L81`](../../bot/handlers/admin/attendance.py#L59-L81)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Выполняет фоновую фиксацию посещаемости в Яндекс Таблицу с обновлением сообщения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message | None` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `session` | `Any` | Yes | Active domain session instance containing current student index and marks. |
| `stats` | `dict[str, int]` | Yes | Parameter `stats` of type `dict[str, int]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import _async_commit_and_update

# Execute call
result = await _async_commit_and_update(message=..., session=..., stats=...)
```

---

### `_instant_topic_sync`
```python
async def _instant_topic_sync(session) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L84-L99`](../../bot/handlers/admin/attendance.py#L84-L99)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Мгновенно обновляет топик посещаемости в Telegram через оптимистичные метки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `Any` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import _instant_topic_sync

# Execute call
result = await _instant_topic_sync(session=...)
```

---

### `get_partner_admin_id`
```python
def get_partner_admin_id(current_user_id: int) -> int | None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L102-L118`](../../bot/handlers/admin/attendance.py#L102-L118)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Определяет Telegram ID напарника по модерации (староста <-> замстаросты).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `current_user_id` | `int` | Yes | Parameter `current_user_id` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import get_partner_admin_id

# Execute call
result = get_partner_admin_id(current_user_id=...)
```

---

### `notify_partner_about_attendance`
```python
async def notify_partner_about_attendance(session, stats: dict[str, int], user_full_name: str | None = None) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L121-L144`](../../bot/handlers/admin/attendance.py#L121-L144)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет полный отчет о завершении отметки пары второму администратору в ЛС.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `Any` | Yes | Active domain session instance containing current student index and marks. |
| `stats` | `dict[str, int]` | Yes | Parameter `stats` of type `dict[str, int]`. |
| `user_full_name` | `str | None` | Yes | Parameter `user_full_name` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import notify_partner_about_attendance

# Execute call
result = await notify_partner_about_attendance(session=..., stats=..., user_full_name=...)
```

---

### `finish_and_notify`
```python
async def finish_and_notify(cb: CallbackQuery, session) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L147-L170`](../../bot/handlers/admin/attendance.py#L147-L170)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Мгновенно выводит сводку старосте и запускает асинхронные задачи сохранения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |
| `session` | `Any` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import finish_and_notify

# Execute call
result = await finish_and_notify(cb=..., session=...)
```

---

### `show_attendance_menu`
```python
async def show_attendance_menu(event: Message | CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L175-L192`](../../bot/handlers/admin/attendance.py#L175-L192)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает интерактивное меню выбора учебного дня для отметки пар.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `event` | `Message | CallbackQuery` | Yes | Parameter `event` of type `Message | CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import show_attendance_menu

# Execute call
result = await show_attendance_menu(event=...)
```

---

### `cb_select_day`
```python
async def cb_select_day(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L196-L214`](../../bot/handlers/admin/attendance.py#L196-L214)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Формирует и отображает кнопки доступных пар на выбранную старостой дату.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_select_day

# Execute call
result = await cb_select_day(cb=...)
```

---

### `parse_start_callback`
```python
def parse_start_callback(data: str)
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L217-L231`](../../bot/handlers/admin/attendance.py#L217-L231)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Парсит целевую дату и номер пары из строки callback_data.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `data` | `str` | Yes | Parameter `data` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import parse_start_callback

# Execute call
result = parse_start_callback(data=...)
```

---

### `get_initiator_title`
```python
def get_initiator_title(initiator_id: int) -> str
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L234-L244`](../../bot/handlers/admin/attendance.py#L234-L244)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает русскоязычное наименование роли старосты по его Telegram ID.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `initiator_id` | `int` | Yes | Parameter `initiator_id` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import get_initiator_title

# Execute call
result = get_initiator_title(initiator_id=...)
```

---

### `check_session_ownership`
```python
async def check_session_ownership(cb: CallbackQuery, session) -> bool
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L247-L266`](../../bot/handlers/admin/attendance.py#L247-L266)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, принадлежит ли активная сессия опроса текущему пользователю.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |
| `session` | `Any` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import check_session_ownership

# Execute call
result = await check_session_ownership(cb=..., session=...)
```

---

### `_resolve_lesson_title_for_start`
```python
async def _resolve_lesson_title_for_start(target_date, lesson_num: int) -> str
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L269-L282`](../../bot/handlers/admin/attendance.py#L269-L282)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Определяет наименование дисциплины по номеру пары из расписания на дату.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `Any` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import _resolve_lesson_title_for_start

# Execute call
result = await _resolve_lesson_title_for_start(target_date=..., lesson_num=...)
```

---

### `_ensure_session_available`
```python
async def _ensure_session_available(cb: CallbackQuery) -> bool
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L285-L301`](../../bot/handlers/admin/attendance.py#L285-L301)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет доступность запуска нового опроса посещаемости.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import _ensure_session_available

# Execute call
result = await _ensure_session_available(cb=...)
```

---

### `_init_session_safe`
```python
async def _init_session_safe(cb: CallbackQuery, target_date, lesson_num: int, title: str)
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L304-L326`](../../bot/handlers/admin/attendance.py#L304-L326)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Безопасно создает сессию посещаемости с обработкой ошибок API/таблицы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |
| `target_date` | `Any` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `title` | `str` | Yes | Parameter `title` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import _init_session_safe

# Execute call
result = await _init_session_safe(cb=..., target_date=..., lesson_num=...)
```

---

### `notify_partner_about_single_update`
```python
async def notify_partner_about_single_update( session: AttendanceSession, fio: str, mark: str, user_id: int, user_full_name: str | None = None ) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L329-L350`](../../bot/handlers/admin/attendance.py#L329-L350)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет уведомление второму администратору о точечном изменении отметки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `mark` | `str` | Yes | Attendance evaluation symbol assigned to the student. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `user_full_name` | `str | None` | Yes | Parameter `user_full_name` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import notify_partner_about_single_update

# Execute call
result = await notify_partner_about_single_update(session=..., fio=..., mark=...)
```

---

### `_commit_single_attendance_background`
```python
async def _commit_single_attendance_background( session: AttendanceSession, message: Message | None, fio: str, mark: str ) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L353-L375`](../../bot/handlers/admin/attendance.py#L353-L375)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Выполняет фоновую фиксацию одиночной отметки в Яндекс Таблицу.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |
| `message` | `Message | None` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `mark` | `str` | Yes | Attendance evaluation symbol assigned to the student. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import _commit_single_attendance_background

# Execute call
result = await _commit_single_attendance_background(session=..., message=..., fio=...)
```

---

### `cb_lesson_mode`
```python
async def cb_lesson_mode(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L379-L397`](../../bot/handlers/admin/attendance.py#L379-L397)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает выбор режима отметки пары: опрос всей группы или один студент.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_lesson_mode

# Execute call
result = await cb_lesson_mode(cb=...)
```

---

### `cb_single_student_menu`
```python
async def cb_single_student_menu(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L401-L420`](../../bot/handlers/admin/attendance.py#L401-L420)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает список студентов по два в ряд для точечной отметки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_single_student_menu

# Execute call
result = await cb_single_student_menu(cb=...)
```

---

### `cb_pick_student`
```python
async def cb_pick_student(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L424-L443`](../../bot/handlers/admin/attendance.py#L424-L443)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает карточку студента с кнопками установки новой отметки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_pick_student

# Execute call
result = await cb_pick_student(cb=...)
```

---

### `_build_single_session`
```python
def _build_single_session( d_str: str, lesson_num: int, title: str, students: list, row_idx: int, mark: str, user_id: int ) -> AttendanceSession
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L446-L463`](../../bot/handlers/admin/attendance.py#L446-L463)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `AttendanceSession`

#### Overview & Architectural Purpose
Создает объект AttendanceSession с отметкой для одного студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `d_str` | `str` | Yes | Parameter `d_str` of type `str`. |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `students` | `list` | Yes | Parameter `students` of type `list`. |
| `row_idx` | `int` | Yes | Parameter `row_idx` of type `int`. |
| `mark` | `str` | Yes | Attendance evaluation symbol assigned to the student. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import _build_single_session

# Execute call
result = _build_single_session(d_str=..., lesson_num=..., title=...)
```

---

### `cb_set_single_mark`
```python
async def cb_set_single_mark(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L467-L492`](../../bot/handlers/admin/attendance.py#L467-L492)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Устанавливает новую отметку выбранному студенту и запускает сохранение.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_set_single_mark

# Execute call
result = await cb_set_single_mark(cb=...)
```

---

### `cb_start_attendance`
```python
async def cb_start_attendance(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L496-L518`](../../bot/handlers/admin/attendance.py#L496-L518)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Инициализирует интерактивную сессию опроса посещаемости и открывает карточку.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_start_attendance

# Execute call
result = await cb_start_attendance(cb=...)
```

---

### `cb_mark_student`
```python
async def cb_mark_student(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L522-L546`](../../bot/handlers/admin/attendance.py#L522-L546)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Фиксирует статус студента и переходит к следующему шагу опроса.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_mark_student

# Execute call
result = await cb_mark_student(cb=...)
```

---

### `cb_step_back`
```python
async def cb_step_back(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L550-L573`](../../bot/handlers/admin/attendance.py#L550-L573)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Возвращает старосту к предыдущему студенту для исправления отметки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_step_back

# Execute call
result = await cb_step_back(cb=...)
```

---

### `cb_all_present`
```python
async def cb_all_present(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L577-L597`](../../bot/handlers/admin/attendance.py#L577-L597)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Проставляет статус 'П' (Присутствует) всем оставшимся студентам группы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_all_present

# Execute call
result = await cb_all_present(cb=...)
```

---

### `notify_partner_about_cancellation`
```python
async def notify_partner_about_cancellation( lesson_num: int | str, user_id: int, user_full_name: str | None = None ) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L600-L624`](../../bot/handlers/admin/attendance.py#L600-L624)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Оповещает второго администратора об отмене проведения пары.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson_num` | `int | str` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `user_full_name` | `str | None` | Yes | Parameter `user_full_name` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import notify_partner_about_cancellation

# Execute call
result = await notify_partner_about_cancellation(lesson_num=..., user_id=..., user_full_name=...)
```

---

### `cb_cancel_lesson`
```python
async def cb_cancel_lesson(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L628-L644`](../../bot/handlers/admin/attendance.py#L628-L644)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отменяет опрос для указанной пары и уведомляет напарника старосты.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_cancel_lesson

# Execute call
result = await cb_cancel_lesson(cb=...)
```

---

### `cb_abort_survey`
```python
async def cb_abort_survey(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L648-L668`](../../bot/handlers/admin/attendance.py#L648-L668)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Прерывает активный опрос посещаемости по запросу его инициатора.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_abort_survey

# Execute call
result = await cb_abort_survey(cb=...)
```

---

### `cb_close_menu`
```python
async def cb_close_menu(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L672-L685`](../../bot/handlers/admin/attendance.py#L672-L685)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет сообщение с интерактивным меню посещаемости из чата.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `CallbackQuery` | Yes | Parameter `cb` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.attendance import cb_close_menu

# Execute call
result = await cb_close_menu(cb=...)
```

---
