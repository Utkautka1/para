# Component Reference: `bot/handlers/user/schedule.py`
> **File Path**: [`bot/handlers/user/schedule.py`](../../bot/handlers/user/schedule.py)
> **Subsystem**: `User Schedule Flow`

## 1. Purpose
Хэндлеры команд и Inline-кнопок пользователя.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_day_schedule_cached`](#get_day_schedule_cached) | Function | L52–L67 | `tuple[str, list[Lesson]]` | Возвращает форматированный текст расписания и список па... |
| [`_ack_callback`](#_ack_callback) | Function | L70–L78 | `None` | Мгновенно подтверждает callback-запрос от инлайн-кнопок... |
| [`edit_or_answer`](#edit_or_answer) | Function | L81–L98 | `None` | Безопасно обновляет содержимое текущего сообщения распи... |
| [`_greet_new_student`](#_greet_new_student) | Function | L101–L119 | `None` | Отправляет персональное приветственное сообщение новому... |
| [`_show_access_denied`](#_show_access_denied) | Function | L122–L139 | `None` | Информирует неавторизованного пользователя об отказе в ... |
| [`_show_tester_cabinet`](#_show_tester_cabinet) | Function | L142–L166 | `None` | Отправляет экран личного кабинета авторизованного тести... |
| [`_send_today_schedule`](#_send_today_schedule) | Function | L169–L190 | `list[Lesson]` | Отправляет пользователю карточку расписания на сегодня ... |
| [`_award_today_view`](#_award_today_view) | Function | L193–L199 | `None` | Запускает в фоне выдачу ачивок за /start и /today (прив... |
| [`_handle_unauthorized_user`](#_handle_unauthorized_user) | Function | L202–L210 | `bool` | Обрабатывает отказ в доступе или показ кабинета тестера... |
| [`cmd_start`](#cmd_start) | Function | L215–L228 | `None` | Авторизует пользователя, проверяет права тестера и отпр... |
| [`cmd_my_api_key`](#cmd_my_api_key) | Function | L233–L248 | `None` | Показывает персональный API-ключ и кнопки запуска Swagg... |
| [`cb_show_tester_key`](#cb_show_tester_key) | Function | L252–L265 | `None` | Отправляет всплывающее уведомление с персональным ключо... |
| [`_trigger_notify_achievements`](#_trigger_notify_achievements) | Function | L268–L274 | `None` | Асинхронно разблокирует достижения при смене статуса на... |
| [`_update_schedule_inline_markup`](#_update_schedule_inline_markup) | Function | L277–L292 | `None` | Обновляет инлайн-клавиатуру в сообщении расписания посл... |
| [`cb_toggle_notify`](#cb_toggle_notify) | Function | L296–L305 | `None` | Переключает статус подписки на 10-минутные напоминания ... |
| [`cmd_notice`](#cmd_notice) | Function | L309–L327 | `None` | Отображает экран настроек персональных уведомлений о па... |
| [`cb_notice_toggle`](#cb_notice_toggle) | Function | L331–L351 | `None` | Переключает статус подписки в меню /notice с обновление... |
| [`cb_today`](#cb_today) | Function | L355–L371 | `None` | Заменяет сообщение на расписание на сегодня с Redis-кэш... |
| [`cb_tomorrow`](#cb_tomorrow) | Function | L375–L391 | `None` | Заменяет сообщение на расписание на завтра с Redis-кэши... |
| [`cb_week`](#cb_week) | Function | L395–L420 | `None` | Заменяет сообщение на расписание на текущую неделю с Re... |
| [`_get_next_week_monday`](#_get_next_week_monday) | Function | L423–L426 | `date` | Вычисляет дату понедельника следующей недели. |
| [`cb_week_next`](#cb_week_next) | Function | L430–L446 | `None` | Заменяет сообщение на расписание на следующую неделю с ... |
| [`_safe_fetch_lessons_for_refresh`](#_safe_fetch_lessons_for_refresh) | Function | L449–L455 | `list[Lesson]` | Запрашивает расписание из API с fallback на кэш при сбо... |
| [`_refresh_and_format_schedule`](#_refresh_and_format_schedule) | Function | L458–L468 | `tuple[str, list[Lesson], int]` | Сбрасывает UI-кэш представлений и загружает свежее расп... |
| [`cb_refresh`](#cb_refresh) | Function | L472–L483 | `None` | Сразу показывает расписание из кэша и просит worker ска... |
| [`format_help_text`](#format_help_text) | Function | L486–L509 | `str` | Формирует справочное сообщение со списком команд бота. |
| [`cmd_help`](#cmd_help) | Function | L513–L531 | `None` | Выводит список доступных команд для авторизованного пол... |
| [`handle_user_text_message`](#handle_user_text_message) | Function | L535–L551 | `None` | Отвечает на произвольный текст авторизованного пользова... |

---

## 3. Comprehensive Function Specifications

### `get_day_schedule_cached`
```python
async def get_day_schedule_cached(target_date: date) -> tuple[str, list[Lesson]]
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L52-L67`](../../bot/handlers/user/schedule.py#L52-L67)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[str, list[Lesson]]`

#### Overview & Architectural Purpose
Возвращает форматированный текст расписания и список пар с кэшированием в Redis на 180с.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import get_day_schedule_cached

# Execute call
result = await get_day_schedule_cached(target_date=...)
```

---

### `_ack_callback`
```python
async def _ack_callback(callback: CallbackQuery, text: str | None = None) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L70-L78`](../../bot/handlers/user/schedule.py#L70-L78)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Мгновенно подтверждает callback-запрос от инлайн-кнопок Telegram.

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
from bot.handlers.user.schedule import _ack_callback

# Execute call
result = await _ack_callback(callback=..., text=...)
```

---

### `edit_or_answer`
```python
async def edit_or_answer( callback: CallbackQuery, text: str, lessons: list[Lesson] | None = None, week_offset: int = 0 ) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L81-L98`](../../bot/handlers/user/schedule.py#L81-L98)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Безопасно обновляет содержимое текущего сообщения расписания в чате.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `lessons` | `list[Lesson] | None` | Yes | Parameter `lessons` of type `list[Lesson] | None`. |
| `week_offset` | `int` | Yes | Parameter `week_offset` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import edit_or_answer

# Execute call
result = await edit_or_answer(callback=..., text=..., lessons=...)
```

---

### `_greet_new_student`
```python
async def _greet_new_student(message: Message, student: dict) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L101-L119`](../../bot/handlers/user/schedule.py#L101-L119)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет персональное приветственное сообщение новому студенту группы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `student` | `dict` | Yes | Parameter `student` of type `dict`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _greet_new_student

# Execute call
result = await _greet_new_student(message=..., student=...)
```

---

### `_show_access_denied`
```python
async def _show_access_denied(message: Message, uid: int) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L122-L139`](../../bot/handlers/user/schedule.py#L122-L139)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Информирует неавторизованного пользователя об отказе в доступе к боту.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _show_access_denied

# Execute call
result = await _show_access_denied(message=..., uid=...)
```

---

### `_show_tester_cabinet`
```python
async def _show_tester_cabinet(message: Message, uid: int) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L142-L166`](../../bot/handlers/user/schedule.py#L142-L166)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет экран личного кабинета авторизованного тестировщика API.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _show_tester_cabinet

# Execute call
result = await _show_tester_cabinet(message=..., uid=...)
```

---

### `_send_today_schedule`
```python
async def _send_today_schedule(message: Message, uid: int, is_tester: bool) -> list[Lesson]
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L169-L190`](../../bot/handlers/user/schedule.py#L169-L190)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[Lesson]`

#### Overview & Architectural Purpose
Отправляет пользователю карточку расписания на сегодня с клавиатурой.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `is_tester` | `bool` | Yes | Parameter `is_tester` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _send_today_schedule

# Execute call
result = await _send_today_schedule(message=..., uid=..., is_tester=...)
```

---

### `_award_today_view`
```python
def _award_today_view(message: Message, lessons: list[Lesson]) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L193-L199`](../../bot/handlers/user/schedule.py#L193-L199)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Запускает в фоне выдачу ачивок за /start и /today (приветствие + время просмотра).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _award_today_view

# Execute call
result = _award_today_view(message=..., lessons=...)
```

---

### `_handle_unauthorized_user`
```python
async def _handle_unauthorized_user(message: Message, is_auth: bool, is_tester: bool, uid: int) -> bool
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L202-L210`](../../bot/handlers/user/schedule.py#L202-L210)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Обрабатывает отказ в доступе или показ кабинета тестера для неавторизованных студентов.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `is_auth` | `bool` | Yes | Parameter `is_auth` of type `bool`. |
| `is_tester` | `bool` | Yes | Parameter `is_tester` of type `bool`. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _handle_unauthorized_user

# Execute call
result = await _handle_unauthorized_user(message=..., is_auth=..., is_tester=...)
```

---

### `cmd_start`
```python
async def cmd_start(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L215-L228`](../../bot/handlers/user/schedule.py#L215-L228)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Авторизует пользователя, проверяет права тестера и отправляет меню расписания.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cmd_start

# Execute call
result = await cmd_start(message=...)
```

---

### `cmd_my_api_key`
```python
async def cmd_my_api_key(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L233-L248`](../../bot/handlers/user/schedule.py#L233-L248)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Показывает персональный API-ключ и кнопки запуска Swagger UI.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cmd_my_api_key

# Execute call
result = await cmd_my_api_key(message=...)
```

---

### `cb_show_tester_key`
```python
async def cb_show_tester_key(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L252-L265`](../../bot/handlers/user/schedule.py#L252-L265)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет всплывающее уведомление с персональным ключом тестера.

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
from bot.handlers.user.schedule import cb_show_tester_key

# Execute call
result = await cb_show_tester_key(callback=...)
```

---

### `_trigger_notify_achievements`
```python
def _trigger_notify_achievements(uid: int, bot: Any, new_sub: bool, full_name: str | None) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L268-L274`](../../bot/handlers/user/schedule.py#L268-L274)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Асинхронно разблокирует достижения при смене статуса напоминаний о парах.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `new_sub` | `bool` | Yes | Parameter `new_sub` of type `bool`. |
| `full_name` | `str | None` | Yes | Parameter `full_name` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _trigger_notify_achievements

# Execute call
result = _trigger_notify_achievements(uid=..., bot=..., new_sub=...)
```

---

### `_update_schedule_inline_markup`
```python
async def _update_schedule_inline_markup(callback: CallbackQuery, uid: int, new_sub: bool) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L277-L292`](../../bot/handlers/user/schedule.py#L277-L292)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Обновляет инлайн-клавиатуру в сообщении расписания после переключения напоминаний.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `new_sub` | `bool` | Yes | Parameter `new_sub` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _update_schedule_inline_markup

# Execute call
result = await _update_schedule_inline_markup(callback=..., uid=..., new_sub=...)
```

---

### `cb_toggle_notify`
```python
async def cb_toggle_notify(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L296-L305`](../../bot/handlers/user/schedule.py#L296-L305)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Переключает статус подписки на 10-минутные напоминания о парах в ЛС.

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
from bot.handlers.user.schedule import cb_toggle_notify

# Execute call
result = await cb_toggle_notify(callback=...)
```

---

### `cmd_notice`
```python
async def cmd_notice(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L309-L327`](../../bot/handlers/user/schedule.py#L309-L327)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает экран настроек персональных уведомлений о парах /notice.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cmd_notice

# Execute call
result = await cmd_notice(message=...)
```

---

### `cb_notice_toggle`
```python
async def cb_notice_toggle(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L331-L351`](../../bot/handlers/user/schedule.py#L331-L351)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Переключает статус подписки в меню /notice с обновлением экрана.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cb_notice_toggle

# Execute call
result = await cb_notice_toggle(callback=...)
```

---

### `cb_today`
```python
async def cb_today(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L355-L371`](../../bot/handlers/user/schedule.py#L355-L371)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Заменяет сообщение на расписание на сегодня с Redis-кэшированием.

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
from bot.handlers.user.schedule import cb_today

# Execute call
result = await cb_today(callback=...)
```

---

### `cb_tomorrow`
```python
async def cb_tomorrow(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L375-L391`](../../bot/handlers/user/schedule.py#L375-L391)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Заменяет сообщение на расписание на завтра с Redis-кэшированием.

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
from bot.handlers.user.schedule import cb_tomorrow

# Execute call
result = await cb_tomorrow(callback=...)
```

---

### `cb_week`
```python
async def cb_week(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L395-L420`](../../bot/handlers/user/schedule.py#L395-L420)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Заменяет сообщение на расписание на текущую неделю с Redis-кэшированием.

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
from bot.handlers.user.schedule import cb_week

# Execute call
result = await cb_week(callback=...)
```

---

### `_get_next_week_monday`
```python
def _get_next_week_monday() -> date
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L423-L426`](../../bot/handlers/user/schedule.py#L423-L426)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `date`

#### Overview & Architectural Purpose
Вычисляет дату понедельника следующей недели.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _get_next_week_monday

# Execute call
result = _get_next_week_monday()
```

---

### `cb_week_next`
```python
async def cb_week_next(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L430-L446`](../../bot/handlers/user/schedule.py#L430-L446)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Заменяет сообщение на расписание на следующую неделю с Redis-кэшированием.

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
from bot.handlers.user.schedule import cb_week_next

# Execute call
result = await cb_week_next(callback=...)
```

---

### `_safe_fetch_lessons_for_refresh`
```python
async def _safe_fetch_lessons_for_refresh(now: date) -> list[Lesson]
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L449-L455`](../../bot/handlers/user/schedule.py#L449-L455)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[Lesson]`

#### Overview & Architectural Purpose
Запрашивает расписание из API с fallback на кэш при сбое сети.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now` | `date` | Yes | Parameter `now` of type `date`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _safe_fetch_lessons_for_refresh

# Execute call
result = await _safe_fetch_lessons_for_refresh(now=...)
```

---

### `_refresh_and_format_schedule`
```python
async def _refresh_and_format_schedule(now: date) -> tuple[str, list[Lesson], int]
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L458-L468`](../../bot/handlers/user/schedule.py#L458-L468)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[str, list[Lesson], int]`

#### Overview & Architectural Purpose
Сбрасывает UI-кэш представлений и загружает свежее расписание из API.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now` | `date` | Yes | Parameter `now` of type `date`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import _refresh_and_format_schedule

# Execute call
result = await _refresh_and_format_schedule(now=...)
```

---

### `cb_refresh`
```python
async def cb_refresh(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L472-L483`](../../bot/handlers/user/schedule.py#L472-L483)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сразу показывает расписание из кэша и просит worker скачать свежую версию КТМУ в фоне.

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
from bot.handlers.user.schedule import cb_refresh

# Execute call
result = await cb_refresh(callback=...)
```

---

### `format_help_text`
```python
def format_help_text(is_admin: bool) -> str
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L486-L509`](../../bot/handlers/user/schedule.py#L486-L509)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует справочное сообщение со списком команд бота.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `is_admin` | `bool` | Yes | Parameter `is_admin` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import format_help_text

# Execute call
result = format_help_text(is_admin=...)
```

---

### `cmd_help`
```python
async def cmd_help(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L513-L531`](../../bot/handlers/user/schedule.py#L513-L531)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Выводит список доступных команд для авторизованного пользователя.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import cmd_help

# Execute call
result = await cmd_help(message=...)
```

---

### `handle_user_text_message`
```python
async def handle_user_text_message(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/schedule.py#L535-L551`](../../bot/handlers/user/schedule.py#L535-L551)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отвечает на произвольный текст авторизованного пользователя расписанием.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.schedule import handle_user_text_message

# Execute call
result = await handle_user_text_message(message=...)
```

---
