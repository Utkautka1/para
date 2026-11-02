# Component Reference: `bot/handlers/admin/attendance.py`
> **File Path**: [`bot/handlers/admin/attendance.py`](../../bot/handlers/admin/attendance.py)
> **Subsystem**: `Headman Attendance Polling`

## 1. Purpose
Хэндлеры управления процессом отметки посещаемости.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_async_commit_and_update`](#_async_commit_and_update) | Function | L50–L72 | `None` | Выполняет фоновую фиксацию посещаемости в Яндекс Таблиц... |
| [`_instant_topic_sync`](#_instant_topic_sync) | Function | L75–L90 | `None` | Мгновенно обновляет топик посещаемости в Telegram через... |
| [`get_partner_admin_id`](#get_partner_admin_id) | Function | L93–L109 | `int \| None` | Определяет Telegram ID напарника по модерации (староста... |
| [`notify_partner_about_attendance`](#notify_partner_about_attendance) | Function | L112–L135 | `None` | Отправляет полный отчет о завершении отметки пары второ... |
| [`finish_and_notify`](#finish_and_notify) | Function | L138–L161 | `None` | Мгновенно выводит сводку старосте и запускает асинхронн... |
| [`show_attendance_menu`](#show_attendance_menu) | Function | L166–L183 | `None` | Отображает интерактивное меню выбора учебного дня для о... |
| [`cb_select_day`](#cb_select_day) | Function | L187–L205 | `None` | Формирует и отображает кнопки доступных пар на выбранну... |
| [`parse_start_callback`](#parse_start_callback) | Function | L208–L222 | `Any` | Парсит целевую дату и номер пары из строки callback_dat... |
| [`get_initiator_title`](#get_initiator_title) | Function | L225–L235 | `str` | Возвращает русскоязычное наименование роли старосты по ... |
| [`check_session_ownership`](#check_session_ownership) | Function | L238–L257 | `bool` | Проверяет, принадлежит ли активная сессия опроса текуще... |
| [`_resolve_lesson_title_for_start`](#_resolve_lesson_title_for_start) | Function | L260–L273 | `str` | Определяет наименование дисциплины по номеру пары из ра... |
| [`_ensure_session_available`](#_ensure_session_available) | Function | L276–L292 | `bool` | Проверяет доступность запуска нового опроса посещаемост... |
| [`_init_session_safe`](#_init_session_safe) | Function | L295–L317 | `Any` | Безопасно создает сессию посещаемости с обработкой ошиб... |
| [`cb_start_attendance`](#cb_start_attendance) | Function | L321–L343 | `None` | Инициализирует интерактивную сессию опроса посещаемости... |
| [`cb_mark_student`](#cb_mark_student) | Function | L347–L371 | `None` | Фиксирует статус студента и переходит к следующему шагу... |
| [`cb_step_back`](#cb_step_back) | Function | L375–L398 | `None` | Возвращает старосту к предыдущему студенту для исправле... |
| [`cb_all_present`](#cb_all_present) | Function | L402–L422 | `None` | Проставляет статус 'П' (Присутствует) всем оставшимся с... |
| [`notify_partner_about_cancellation`](#notify_partner_about_cancellation) | Function | L425–L449 | `None` | Оповещает второго администратора об отмене проведения п... |
| [`cb_cancel_lesson`](#cb_cancel_lesson) | Function | L453–L469 | `None` | Отменяет опрос для указанной пары и уведомляет напарник... |
| [`cb_abort_survey`](#cb_abort_survey) | Function | L473–L493 | `None` | Прерывает активный опрос посещаемости по запросу его ин... |
| [`cb_close_menu`](#cb_close_menu) | Function | L497–L510 | `None` | Удаляет сообщение с интерактивным меню посещаемости из ... |

---

## 3. Comprehensive Function Specifications

### `_async_commit_and_update`
```python
async def _async_commit_and_update(message: Message | None, session, stats: dict[str, int]) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L50-L72`](../../bot/handlers/admin/attendance.py#L50-L72)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L75-L90`](../../bot/handlers/admin/attendance.py#L75-L90)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L93-L109`](../../bot/handlers/admin/attendance.py#L93-L109)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L112-L135`](../../bot/handlers/admin/attendance.py#L112-L135)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L138-L161`](../../bot/handlers/admin/attendance.py#L138-L161)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L166-L183`](../../bot/handlers/admin/attendance.py#L166-L183)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L187-L205`](../../bot/handlers/admin/attendance.py#L187-L205)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L208-L222`](../../bot/handlers/admin/attendance.py#L208-L222)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L225-L235`](../../bot/handlers/admin/attendance.py#L225-L235)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L238-L257`](../../bot/handlers/admin/attendance.py#L238-L257)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L260-L273`](../../bot/handlers/admin/attendance.py#L260-L273)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L276-L292`](../../bot/handlers/admin/attendance.py#L276-L292)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L295-L317`](../../bot/handlers/admin/attendance.py#L295-L317)
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

### `cb_start_attendance`
```python
async def cb_start_attendance(cb: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/attendance.py#L321-L343`](../../bot/handlers/admin/attendance.py#L321-L343)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L347-L371`](../../bot/handlers/admin/attendance.py#L347-L371)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L375-L398`](../../bot/handlers/admin/attendance.py#L375-L398)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L402-L422`](../../bot/handlers/admin/attendance.py#L402-L422)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L425-L449`](../../bot/handlers/admin/attendance.py#L425-L449)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L453-L469`](../../bot/handlers/admin/attendance.py#L453-L469)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L473-L493`](../../bot/handlers/admin/attendance.py#L473-L493)
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

- **Source Reference**: [`bot/handlers/admin/attendance.py#L497-L510`](../../bot/handlers/admin/attendance.py#L497-L510)
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
