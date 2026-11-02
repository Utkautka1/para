# Component Reference: `bot/handlers/admin/panel.py`
> **File Path**: [`bot/handlers/admin/panel.py`](../../bot/handlers/admin/panel.py)
> **Subsystem**: `Admin Control Panel`

## 1. Purpose
Хэндлеры управления панелью администратора (только для ALLOWED_USER_ID).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_ack_admin_callback`](#_ack_admin_callback) | Function | L51–L67 | `None` | Мгновенно подтверждает callback в админ-панели с обрабо... |
| [`_safe_edit_admin_message`](#_safe_edit_admin_message) | Function | L70–L92 | `None` | Безопасно обновляет сообщение админки, перехватывая 'no... |
| [`format_admin_panel_text`](#format_admin_panel_text) | Function | L95–L114 | `str` | Формирует приветственный HTML-текст главной панели упра... |
| [`cb_admin_menu`](#cb_admin_menu) | Function | L119–L137 | `None` | Отображает главную панель управления старосты с инлайн-... |
| [`cb_admin_sync`](#cb_admin_sync) | Function | L141–L160 | `None` | Принудительно скачивает расписание КТМУ и таблицу препо... |
| [`_get_redis_memory_stat`](#_get_redis_memory_stat) | Function | L163–L181 | `str` | Безопасно извлекает объем используемой оперативной памя... |
| [`_collect_health_summary`](#_collect_health_summary) | Function | L184–L211 | `str` | Собирает диагностические метрики всех компонентов и сер... |
| [`cb_admin_status`](#cb_admin_status) | Function | L215–L227 | `None` | Отображает подробный дашборд состояния компонентов и се... |
| [`cb_admin_force_topic`](#cb_admin_force_topic) | Function | L231–L245 | `None` | Принудительно публикует или обновляет сообщение расписа... |
| [`cb_admin_recreate_topic`](#cb_admin_recreate_topic) | Function | L249–L264 | `None` | Удаляет старое сообщение топика и создает новое с фикса... |
| [`cb_admin_force_exam`](#cb_admin_force_exam) | Function | L268–L283 | `None` | Принудительно обновляет сообщение сессии и экзаменов в ... |
| [`cb_admin_recreate_exam`](#cb_admin_recreate_exam) | Function | L287–L302 | `None` | Удаляет закрепленное сообщение экзаменов и создает ново... |
| [`cb_admin_force_att_topic`](#cb_admin_force_att_topic) | Function | L306–L321 | `None` | Принудительно обновляет сводный реестр посещаемости в т... |
| [`cb_admin_recreate_att_topic`](#cb_admin_recreate_att_topic) | Function | L325–L340 | `None` | Удаляет старое сообщение реестра и создает новое в топи... |
| [`_build_custom_teachers_view`](#_build_custom_teachers_view) | Function | L343–L367 | `tuple[str, list]` | Формирует текст списка кастомных преподавателей и ряды ... |
| [`cb_admin_list_custom`](#cb_admin_list_custom) | Function | L371–L387 | `None` | Отображает список кастомных преподавателей с кнопками д... |
| [`cb_admin_delete_teacher`](#cb_admin_delete_teacher) | Function | L391–L406 | `None` | Удаляет запись преподавателя из пользовательского реест... |
| [`cb_admin_edit_teacher`](#cb_admin_edit_teacher) | Function | L410–L435 | `None` | Запускает сценарий FSM для редактирования ссылки встреч... |
| [`cb_admin_start_add_teacher`](#cb_admin_start_add_teacher) | Function | L439–L459 | `None` | Инициирует пошаговый диалог FSM для добавления нового п... |
| [`msg_admin_got_teacher_name`](#msg_admin_got_teacher_name) | Function | L463–L482 | `None` | Принимает ФИО преподавателя и переключает FSM на ожидан... |
| [`msg_admin_got_teacher_link`](#msg_admin_got_teacher_link) | Function | L486–L511 | `None` | Сохраняет преподавателя в пользовательский реестр и сбр... |
| [`_build_unbound_students_kb`](#_build_unbound_students_kb) | Function | L514–L534 | `InlineKeyboardMarkup` | Формирует клавиатуру со списком студентов группы для пр... |
| [`cb_admin_list_students_for_binding`](#cb_admin_list_students_for_binding) | Function | L538–L565 | `None` | Отображает интерактивный список студентов группы для пр... |
| [`cb_admin_select_student`](#cb_admin_select_student) | Function | L569–L591 | `None` | Запрашивает числовой Telegram ID для выбранного из реес... |
| [`msg_admin_got_student_id`](#msg_admin_got_student_id) | Function | L595–L621 | `None` | Фиксирует Telegram ID студента в реестре одногруппников... |

---

## 3. Comprehensive Function Specifications

## Class Model: `AddTeacherState`

Класс `AddTeacherState`.

## Class Model: `BindStudentState`

Класс `BindStudentState`.

### `_ack_admin_callback`
```python
async def _ack_admin_callback(callback: CallbackQuery, text: str | None = None) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L51-L67`](../../bot/handlers/admin/panel.py#L51-L67)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Мгновенно подтверждает callback в админ-панели с обработкой устаревания.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `text` | `str | None` | Yes | Parameter `text` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _ack_admin_callback

# Execute call
result = await _ack_admin_callback(callback=..., text=...)
```

---

### `_safe_edit_admin_message`
```python
async def _safe_edit_admin_message( message: Message | None, text: str, reply_markup: InlineKeyboardMarkup | None = None ) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L70-L92`](../../bot/handlers/admin/panel.py#L70-L92)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Безопасно обновляет сообщение админки, перехватывая 'not modified'.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message | None` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `reply_markup` | `InlineKeyboardMarkup | None` | Yes | Parameter `reply_markup` of type `InlineKeyboardMarkup | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _safe_edit_admin_message

# Execute call
result = await _safe_edit_admin_message(message=..., text=..., reply_markup=...)
```

---

### `format_admin_panel_text`
```python
def format_admin_panel_text(status_note: str = "") -> str
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L95-L114`](../../bot/handlers/admin/panel.py#L95-L114)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует приветственный HTML-текст главной панели управления администратора.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `status_note` | `str` | Yes | Parameter `status_note` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import format_admin_panel_text

# Execute call
result = format_admin_panel_text(status_note=...)
```

---

### `cb_admin_menu`
```python
async def cb_admin_menu(event: Message | CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L119-L137`](../../bot/handlers/admin/panel.py#L119-L137)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает главную панель управления старосты с инлайн-кнопками.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `event` | `Message | CallbackQuery` | Yes | Parameter `event` of type `Message | CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_menu

# Execute call
result = await cb_admin_menu(event=...)
```

---

### `cb_admin_sync`
```python
async def cb_admin_sync(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L141-L160`](../../bot/handlers/admin/panel.py#L141-L160)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Принудительно скачивает расписание КТМУ и таблицу преподавателей.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_sync

# Execute call
result = await cb_admin_sync(callback=...)
```

---

### `_get_redis_memory_stat`
```python
async def _get_redis_memory_stat() -> str
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L163-L181`](../../bot/handlers/admin/panel.py#L163-L181)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Безопасно извлекает объем используемой оперативной памяти Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _get_redis_memory_stat

# Execute call
result = await _get_redis_memory_stat()
```

---

### `_collect_health_summary`
```python
async def _collect_health_summary() -> str
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L184-L211`](../../bot/handlers/admin/panel.py#L184-L211)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Собирает диагностические метрики всех компонентов и сервисов системы.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _collect_health_summary

# Execute call
result = await _collect_health_summary()
```

---

### `cb_admin_status`
```python
async def cb_admin_status(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L215-L227`](../../bot/handlers/admin/panel.py#L215-L227)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает подробный дашборд состояния компонентов и сервисов бота.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_status

# Execute call
result = await cb_admin_status(callback=...)
```

---

### `cb_admin_force_topic`
```python
async def cb_admin_force_topic(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L231-L245`](../../bot/handlers/admin/panel.py#L231-L245)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Принудительно публикует или обновляет сообщение расписания в топике.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_force_topic

# Execute call
result = await cb_admin_force_topic(callback=...)
```

---

### `cb_admin_recreate_topic`
```python
async def cb_admin_recreate_topic(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L249-L264`](../../bot/handlers/admin/panel.py#L249-L264)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет старое сообщение топика и создает новое с фиксацией message_id.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_recreate_topic

# Execute call
result = await cb_admin_recreate_topic(callback=...)
```

---

### `cb_admin_force_exam`
```python
async def cb_admin_force_exam(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L268-L283`](../../bot/handlers/admin/panel.py#L268-L283)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Принудительно обновляет сообщение сессии и экзаменов в топике.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_force_exam

# Execute call
result = await cb_admin_force_exam(callback=...)
```

---

### `cb_admin_recreate_exam`
```python
async def cb_admin_recreate_exam(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L287-L302`](../../bot/handlers/admin/panel.py#L287-L302)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет закрепленное сообщение экзаменов и создает новое в топике.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_recreate_exam

# Execute call
result = await cb_admin_recreate_exam(callback=...)
```

---

### `cb_admin_force_att_topic`
```python
async def cb_admin_force_att_topic(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L306-L321`](../../bot/handlers/admin/panel.py#L306-L321)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Принудительно обновляет сводный реестр посещаемости в топике Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_force_att_topic

# Execute call
result = await cb_admin_force_att_topic(callback=...)
```

---

### `cb_admin_recreate_att_topic`
```python
async def cb_admin_recreate_att_topic(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L325-L340`](../../bot/handlers/admin/panel.py#L325-L340)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет старое сообщение реестра и создает новое в топике посещаемости.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_recreate_att_topic

# Execute call
result = await cb_admin_recreate_att_topic(callback=...)
```

---

### `_build_custom_teachers_view`
```python
def _build_custom_teachers_view(custom: dict) -> tuple[str, list]
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L343-L367`](../../bot/handlers/admin/panel.py#L343-L367)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, list]`

#### Overview & Architectural Purpose
Формирует текст списка кастомных преподавателей и ряды кнопок управления.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `custom` | `dict` | Yes | Parameter `custom` of type `dict`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _build_custom_teachers_view

# Execute call
result = _build_custom_teachers_view(custom=...)
```

---

### `cb_admin_list_custom`
```python
async def cb_admin_list_custom(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L371-L387`](../../bot/handlers/admin/panel.py#L371-L387)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает список кастомных преподавателей с кнопками добавления и удаления.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_list_custom

# Execute call
result = await cb_admin_list_custom(callback=...)
```

---

### `cb_admin_delete_teacher`
```python
async def cb_admin_delete_teacher(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L391-L406`](../../bot/handlers/admin/panel.py#L391-L406)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет запись преподавателя из пользовательского реестра и обновляет меню.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_delete_teacher

# Execute call
result = await cb_admin_delete_teacher(callback=...)
```

---

### `cb_admin_edit_teacher`
```python
async def cb_admin_edit_teacher(callback: CallbackQuery, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L410-L435`](../../bot/handlers/admin/panel.py#L410-L435)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Запускает сценарий FSM для редактирования ссылки встречи преподавателя.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_edit_teacher

# Execute call
result = await cb_admin_edit_teacher(callback=..., state=...)
```

---

### `cb_admin_start_add_teacher`
```python
async def cb_admin_start_add_teacher(callback: CallbackQuery, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L439-L459`](../../bot/handlers/admin/panel.py#L439-L459)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Инициирует пошаговый диалог FSM для добавления нового преподавателя.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_start_add_teacher

# Execute call
result = await cb_admin_start_add_teacher(callback=..., state=...)
```

---

### `msg_admin_got_teacher_name`
```python
async def msg_admin_got_teacher_name(message: Message, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L463-L482`](../../bot/handlers/admin/panel.py#L463-L482)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Принимает ФИО преподавателя и переключает FSM на ожидание ссылки подключения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import msg_admin_got_teacher_name

# Execute call
result = await msg_admin_got_teacher_name(message=..., state=...)
```

---

### `msg_admin_got_teacher_link`
```python
async def msg_admin_got_teacher_link(message: Message, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L486-L511`](../../bot/handlers/admin/panel.py#L486-L511)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сохраняет преподавателя в пользовательский реестр и сбрасывает стейт FSM.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import msg_admin_got_teacher_link

# Execute call
result = await msg_admin_got_teacher_link(message=..., state=...)
```

---

### `_build_unbound_students_kb`
```python
def _build_unbound_students_kb() -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L514-L534`](../../bot/handlers/admin/panel.py#L514-L534)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Формирует клавиатуру со списком студентов группы для привязки Telegram ID.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import _build_unbound_students_kb

# Execute call
result = _build_unbound_students_kb()
```

---

### `cb_admin_list_students_for_binding`
```python
async def cb_admin_list_students_for_binding(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L538-L565`](../../bot/handlers/admin/panel.py#L538-L565)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает интерактивный список студентов группы для привязки Telegram ID.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_list_students_for_binding

# Execute call
result = await cb_admin_list_students_for_binding(callback=...)
```

---

### `cb_admin_select_student`
```python
async def cb_admin_select_student(callback: CallbackQuery, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L569-L591`](../../bot/handlers/admin/panel.py#L569-L591)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Запрашивает числовой Telegram ID для выбранного из реестра студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import cb_admin_select_student

# Execute call
result = await cb_admin_select_student(callback=..., state=...)
```

---

### `msg_admin_got_student_id`
```python
async def msg_admin_got_student_id(message: Message, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/panel.py#L595-L621`](../../bot/handlers/admin/panel.py#L595-L621)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Фиксирует Telegram ID студента в реестре одногруппников и сбрасывает FSM.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.panel import msg_admin_got_student_id

# Execute call
result = await msg_admin_got_student_id(message=..., state=...)
```

---
