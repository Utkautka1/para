# Component Reference: `services/topic_updater.py`
> **File Path**: [`services/topic_updater.py`](../../services/topic_updater.py)
> **Subsystem**: `Live Schedule Topic`

## 1. Purpose
Модуль синхронизации и авто-обновления расписания в Telegram-топике группы.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`load_topic_state`](#load_topic_state) | Function | L42–L52 | `int \| None` | Загружает сохраненный ID главного сообщения расписания ... |
| [`save_topic_state`](#save_topic_state) | Function | L55–L69 | `None` | Атомарно сохраняет ID главного сообщения в файл состоян... |
| [`cleanup_expired_messages`](#cleanup_expired_messages) | Function | L72–L94 | `None` | Удаляет временные сервисные уведомления из топика с ист... |
| [`send_temp_topic_reminder`](#send_temp_topic_reminder) | Function | L97–L119 | `None` | Отправляет всплывающее уведомление за 10 минут до начал... |
| [`check_and_trigger_reminder`](#check_and_trigger_reminder) | Function | L122–L147 | `None` | Проверяет приближение времени начала пары и запускает о... |
| [`get_next_working_day`](#get_next_working_day) | Function | L150–L162 | `date` | Определяет дату следующего учебного дня с автоматически... |
| [`_should_switch_to_next_day`](#_should_switch_to_next_day) | Function | L165–L180 | `bool` | Проверяет, завершились ли все учебные пары сегодняшнего... |
| [`resolve_target_date`](#resolve_target_date) | Function | L183–L200 | `date \| None` | Рассчитывает целевую дату отображения расписания для за... |
| [`is_too_early_to_publish`](#is_too_early_to_publish) | Function | L203–L220 | `bool` | Проверяет, не наступило ли слишком раннее утреннее врем... |
| [`_edit_topic_message`](#_edit_topic_message) | Function | L223–L237 | `bool` | Редактирует текст и клавиатуру активного сообщения в то... |
| [`update_topic_message_payload`](#update_topic_message_payload) | Function | L240–L264 | `bool` | Атомарно отправляет новое или редактирует закрепленное ... |
| [`_topic_fingerprint`](#_topic_fingerprint) | Function | L267–L270 | `str` | Склеивает текст и сериализованную клавиатуру — по ним с... |
| [`_is_unchanged_since_last_send`](#_is_unchanged_since_last_send) | Function | L273–L283 | `bool` | Проверяет, что пост уже в этом состоянии и недавно подт... |
| [`_remember_sent`](#_remember_sent) | Function | L286–L290 | `None` | Запоминает состояние поста, подтверждённое Telegram (от... |
| [`_send_new_topic_message`](#_send_new_topic_message) | Function | L293–L314 | `bool` | Создает новое сообщение расписания в топике и закрепляе... |
| [`_pin_silently`](#_pin_silently) | Function | L317–L332 | `None` | Закрепляет сообщение в супергруппе без отправки системн... |
| [`_try_delete_old_topic_msg`](#_try_delete_old_topic_msg) | Function | L335–L350 | `None` | Пытается удалить старое призрачное сообщение из топика ... |
| [`recreate_topic_message`](#recreate_topic_message) | Function | L353–L370 | `bool` | Сбрасывает сохраненный ID сообщения и принудительно пер... |
| [`_recreate_after_edit_failure`](#_recreate_after_edit_failure) | Function | L373–L384 | `bool` | Сбрасывает ID закрепленного сообщения и пытается отправ... |
| [`_handle_edit_failure`](#_handle_edit_failure) | Function | L387–L409 | `bool` | Обрабатывает исключения редактирования сообщения Telegr... |
| [`should_skip_topic_update`](#should_skip_topic_update) | Function | L412–L429 | `bool` | Определяет необходимость отложить публикацию расписания... |
| [`process_today_reminders`](#process_today_reminders) | Function | L432–L442 | `None` | Запускает проверку и отправку персональных напоминаний ... |
| [`_prepare_target_schedule`](#_prepare_target_schedule) | Function | L445–L464 | `tuple[date \| None, list[Lesson] \| None]` | Вычисляет целевую дату и запрашивает список уроков для ... |
| [`_ensure_topic_main_msg_id`](#_ensure_topic_main_msg_id) | Function | L467–L476 | `None` | Загружает сохраненный ID сообщения из файла состояния п... |
| [`sync_topic_main_message`](#sync_topic_main_message) | Function | L479–L501 | `bool` | Атомарно синхронизирует главное закрепленное сообщение ... |
| [`notify_admin_about_api_down`](#notify_admin_about_api_down) | Function | L508–L529 | `None` | Отправляет экстренное оповещение старосте в ЛС при паде... |
| [`_track_api_failure`](#_track_api_failure) | Function | L532–L543 | `None` | Отслеживает длительность сбоя внешних API и отправляет ... |
| [`_reset_api_failure_tracker`](#_reset_api_failure_tracker) | Function | L546–L557 | `None` | Сбрасывает таймер и флаг аварийного оповещения при успе... |
| [`topic_sync_loop`](#topic_sync_loop) | Function | L560–L578 | `None` | Фоновый непрерывный рабочий цикл обновления расписания ... |

---

## 3. Comprehensive Function Specifications

### `load_topic_state`
```python
def load_topic_state() -> int | None
```

- **Source Reference**: [`services/topic_updater.py#L42-L52`](../../services/topic_updater.py#L42-L52)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Загружает сохраненный ID главного сообщения расписания из локального JSON.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import load_topic_state

# Execute call
result = load_topic_state()
```

---

### `save_topic_state`
```python
def save_topic_state(msg_id: int | None) -> None
```

- **Source Reference**: [`services/topic_updater.py#L55-L69`](../../services/topic_updater.py#L55-L69)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Атомарно сохраняет ID главного сообщения в файл состояния и Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg_id` | `int | None` | Yes | Parameter `msg_id` of type `int | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import save_topic_state

# Execute call
result = save_topic_state(msg_id=...)
```

---

### `cleanup_expired_messages`
```python
async def cleanup_expired_messages() -> None
```

- **Source Reference**: [`services/topic_updater.py#L72-L94`](../../services/topic_updater.py#L72-L94)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет временные сервисные уведомления из топика с истекшим сроком жизни.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import cleanup_expired_messages

# Execute call
result = await cleanup_expired_messages()
```

---

### `send_temp_topic_reminder`
```python
async def send_temp_topic_reminder(lesson: Lesson) -> None
```

- **Source Reference**: [`services/topic_updater.py#L97-L119`](../../services/topic_updater.py#L97-L119)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет всплывающее уведомление за 10 минут до начала пары с кнопками.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import send_temp_topic_reminder

# Execute call
result = await send_temp_topic_reminder(lesson=...)
```

---

### `check_and_trigger_reminder`
```python
async def check_and_trigger_reminder(lesson: Lesson, now_dt: datetime, today: date) -> None
```

- **Source Reference**: [`services/topic_updater.py#L122-L147`](../../services/topic_updater.py#L122-L147)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Проверяет приближение времени начала пары и запускает отправку напоминания.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import check_and_trigger_reminder

# Execute call
result = await check_and_trigger_reminder(lesson=..., now_dt=..., today=...)
```

---

### `get_next_working_day`
```python
def get_next_working_day(target_date: date) -> date
```

- **Source Reference**: [`services/topic_updater.py#L150-L162`](../../services/topic_updater.py#L150-L162)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `date`

#### Overview & Architectural Purpose
Определяет дату следующего учебного дня с автоматическим пропуском воскресенья.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import get_next_working_day

# Execute call
result = get_next_working_day(target_date=...)
```

---

### `_should_switch_to_next_day`
```python
def _should_switch_to_next_day(today_lessons: list[Lesson], today: date, now_dt: datetime) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L165-L180`](../../services/topic_updater.py#L165-L180)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, завершились ли все учебные пары сегодняшнего дня по времени звонков.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `today_lessons` | `list[Lesson]` | Yes | Parameter `today_lessons` of type `list[Lesson]`. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _should_switch_to_next_day

# Execute call
result = _should_switch_to_next_day(today_lessons=..., today=..., now_dt=...)
```

---

### `resolve_target_date`
```python
async def resolve_target_date(now_dt: datetime, ignore_restriction: bool) -> date | None
```

- **Source Reference**: [`services/topic_updater.py#L183-L200`](../../services/topic_updater.py#L183-L200)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `date | None`

#### Overview & Architectural Purpose
Рассчитывает целевую дату отображения расписания для закрепленного сообщения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `ignore_restriction` | `bool` | Yes | Parameter `ignore_restriction` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import resolve_target_date

# Execute call
result = await resolve_target_date(now_dt=..., ignore_restriction=...)
```

---

### `is_too_early_to_publish`
```python
def is_too_early_to_publish(lessons: list[Lesson], now_dt: datetime, today: date, ignore_restriction: bool) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L203-L220`](../../services/topic_updater.py#L203-L220)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, не наступило ли слишком раннее утреннее время до первой пары.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |
| `ignore_restriction` | `bool` | Yes | Parameter `ignore_restriction` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import is_too_early_to_publish

# Execute call
result = is_too_early_to_publish(lessons=..., now_dt=..., today=...)
```

---

### `_edit_topic_message`
```python
async def _edit_topic_message(text: str, kb: Any) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L223-L237`](../../services/topic_updater.py#L223-L237)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Редактирует текст и клавиатуру активного сообщения в топике Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _edit_topic_message

# Execute call
result = await _edit_topic_message(text=..., kb=...)
```

---

### `update_topic_message_payload`
```python
async def update_topic_message_payload(text: str, kb: Any, _retry: bool = False) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L240-L264`](../../services/topic_updater.py#L240-L264)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Атомарно отправляет новое или редактирует закрепленное сообщение в топике.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |
| `_retry` | `bool` | Yes | Parameter `_retry` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import update_topic_message_payload

# Execute call
result = await update_topic_message_payload(text=..., kb=..., _retry=...)
```

---

### `_topic_fingerprint`
```python
def _topic_fingerprint(text: str, kb: Any) -> str
```

- **Source Reference**: [`services/topic_updater.py#L267-L270`](../../services/topic_updater.py#L267-L270)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Склеивает текст и сериализованную клавиатуру — по ним сравниваем, изменился ли пост.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |

#### Concurrency & Side Effects
- Serializes entity state into JSON using Pydantic V2 engine.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _topic_fingerprint

# Execute call
result = _topic_fingerprint(text=..., kb=...)
```

---

### `_is_unchanged_since_last_send`
```python
def _is_unchanged_since_last_send(fingerprint: str) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L273-L283`](../../services/topic_updater.py#L273-L283)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, что пост уже в этом состоянии и недавно подтверждён Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fingerprint` | `str` | Yes | Parameter `fingerprint` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _is_unchanged_since_last_send

# Execute call
result = _is_unchanged_since_last_send(fingerprint=...)
```

---

### `_remember_sent`
```python
def _remember_sent(fingerprint: str) -> None
```

- **Source Reference**: [`services/topic_updater.py#L286-L290`](../../services/topic_updater.py#L286-L290)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Запоминает состояние поста, подтверждённое Telegram (отправка, правка или 'not modified').

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fingerprint` | `str` | Yes | Parameter `fingerprint` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _remember_sent

# Execute call
result = _remember_sent(fingerprint=...)
```

---

### `_send_new_topic_message`
```python
async def _send_new_topic_message(text: str, kb: Any) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L293-L314`](../../services/topic_updater.py#L293-L314)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Создает новое сообщение расписания в топике и закрепляет его без звука.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _send_new_topic_message

# Execute call
result = await _send_new_topic_message(text=..., kb=...)
```

---

### `_pin_silently`
```python
async def _pin_silently(chat_id: int, message_id: int) -> None
```

- **Source Reference**: [`services/topic_updater.py#L317-L332`](../../services/topic_updater.py#L317-L332)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Закрепляет сообщение в супергруппе без отправки системного пуш-уведомления.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `message_id` | `int` | Yes | Parameter `message_id` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import _pin_silently

# Execute call
result = await _pin_silently(chat_id=..., message_id=...)
```

---

### `_try_delete_old_topic_msg`
```python
async def _try_delete_old_topic_msg(old_id: int | None) -> None
```

- **Source Reference**: [`services/topic_updater.py#L335-L350`](../../services/topic_updater.py#L335-L350)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Пытается удалить старое призрачное сообщение из топика Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `old_id` | `int | None` | Yes | Parameter `old_id` of type `int | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import _try_delete_old_topic_msg

# Execute call
result = await _try_delete_old_topic_msg(old_id=...)
```

---

### `recreate_topic_message`
```python
async def recreate_topic_message() -> bool
```

- **Source Reference**: [`services/topic_updater.py#L353-L370`](../../services/topic_updater.py#L353-L370)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Сбрасывает сохраненный ID сообщения и принудительно пересоздает пост с нуля.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import recreate_topic_message

# Execute call
result = await recreate_topic_message()
```

---

### `_recreate_after_edit_failure`
```python
async def _recreate_after_edit_failure(text: str, kb: Any) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L373-L384`](../../services/topic_updater.py#L373-L384)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Сбрасывает ID закрепленного сообщения и пытается отправить новое.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _recreate_after_edit_failure

# Execute call
result = await _recreate_after_edit_failure(text=..., kb=...)
```

---

### `_handle_edit_failure`
```python
async def _handle_edit_failure( e: TelegramBadRequest, text: str, kb: Any, is_retry: bool, ) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L387-L409`](../../services/topic_updater.py#L387-L409)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Обрабатывает исключения редактирования сообщения Telegram API.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `e` | `TelegramBadRequest` | Yes | Parameter `e` of type `TelegramBadRequest`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `kb` | `Any` | Yes | Parameter `kb` of type `Any`. |
| `is_retry` | `bool` | Yes | Parameter `is_retry` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _handle_edit_failure

# Execute call
result = await _handle_edit_failure(e=..., text=..., kb=...)
```

---

### `should_skip_topic_update`
```python
def should_skip_topic_update( lessons: list[Lesson], now_dt: datetime, target_date: date, ignore_time_restriction: bool, ) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L412-L429`](../../services/topic_updater.py#L412-L429)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Определяет необходимость отложить публикацию расписания до утреннего окна.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `ignore_time_restriction` | `bool` | Yes | Parameter `ignore_time_restriction` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import should_skip_topic_update

# Execute call
result = should_skip_topic_update(lessons=..., now_dt=..., target_date=...)
```

---

### `process_today_reminders`
```python
async def process_today_reminders(lessons: list[Lesson], now_dt: datetime, target_date: date) -> None
```

- **Source Reference**: [`services/topic_updater.py#L432-L442`](../../services/topic_updater.py#L432-L442)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Запускает проверку и отправку персональных напоминаний о парах текущего дня.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import process_today_reminders

# Execute call
result = await process_today_reminders(lessons=..., now_dt=..., target_date=...)
```

---

### `_prepare_target_schedule`
```python
async def _prepare_target_schedule( ignore_restriction: bool, ) -> tuple[date | None, list[Lesson] | None]
```

- **Source Reference**: [`services/topic_updater.py#L445-L464`](../../services/topic_updater.py#L445-L464)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[date | None, list[Lesson] | None]`

#### Overview & Architectural Purpose
Вычисляет целевую дату и запрашивает список уроков для обновления топика.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `ignore_restriction` | `bool` | Yes | Parameter `ignore_restriction` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _prepare_target_schedule

# Execute call
result = await _prepare_target_schedule(ignore_restriction=...)
```

---

### `_ensure_topic_main_msg_id`
```python
def _ensure_topic_main_msg_id() -> None
```

- **Source Reference**: [`services/topic_updater.py#L467-L476`](../../services/topic_updater.py#L467-L476)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Загружает сохраненный ID сообщения из файла состояния при первом вызове.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _ensure_topic_main_msg_id

# Execute call
result = _ensure_topic_main_msg_id()
```

---

### `sync_topic_main_message`
```python
async def sync_topic_main_message(ignore_time_restriction: bool = False) -> bool
```

- **Source Reference**: [`services/topic_updater.py#L479-L501`](../../services/topic_updater.py#L479-L501)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Атомарно синхронизирует главное закрепленное сообщение расписания в топике.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `ignore_time_restriction` | `bool` | Yes | Parameter `ignore_time_restriction` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import sync_topic_main_message

# Execute call
result = await sync_topic_main_message(ignore_time_restriction=...)
```

---

### `notify_admin_about_api_down`
```python
async def notify_admin_about_api_down() -> None
```

- **Source Reference**: [`services/topic_updater.py#L508-L529`](../../services/topic_updater.py#L508-L529)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет экстренное оповещение старосте в ЛС при падении внешних API > 30 минут.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import notify_admin_about_api_down

# Execute call
result = await notify_admin_about_api_down()
```

---

### `_track_api_failure`
```python
async def _track_api_failure(now: datetime) -> None
```

- **Source Reference**: [`services/topic_updater.py#L532-L543`](../../services/topic_updater.py#L532-L543)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отслеживает длительность сбоя внешних API и отправляет алерт при превышении порога.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now` | `datetime` | Yes | Parameter `now` of type `datetime`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _track_api_failure

# Execute call
result = await _track_api_failure(now=...)
```

---

### `_reset_api_failure_tracker`
```python
def _reset_api_failure_tracker() -> None
```

- **Source Reference**: [`services/topic_updater.py#L546-L557`](../../services/topic_updater.py#L546-L557)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сбрасывает таймер и флаг аварийного оповещения при успешном ответе сервисов.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.topic_updater import _reset_api_failure_tracker

# Execute call
result = _reset_api_failure_tracker()
```

---

### `topic_sync_loop`
```python
async def topic_sync_loop() -> None
```

- **Source Reference**: [`services/topic_updater.py#L560-L578`](../../services/topic_updater.py#L560-L578)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Фоновый непрерывный рабочий цикл обновления расписания в топике группы.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.topic_updater import topic_sync_loop

# Execute call
result = await topic_sync_loop()
```

---
