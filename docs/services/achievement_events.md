# Component Reference: `services/achievement_events.py`
> **File Path**: [`services/achievement_events.py`](../../services/achievement_events.py)
> **Subsystem**: `Achievement Events`

## 1. Purpose
Выдача событийных ачивок: связывает действия в боте, чате и Mini App со счётчиками.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_now`](#_now) | Function | L62–L64 | `datetime` | Текущее московское время — во всех описаниях ачивок вре... |
| [`is_group_member`](#is_group_member) | Function | L67–L69 | `bool` | Проверяет, что пользователь — одногруппник (или старост... |
| [`_award_all`](#_award_all) | Function | L72–L75 | `None` | Выдаёт набор ачивок по одной (каждая сама проверяет, не... |
| [`bump_counter`](#bump_counter) | Function | L78–L91 | `int` | Увеличивает счётчик студента и выдаёт ачивки за пройден... |
| [`on_interaction`](#on_interaction) | Function | L94–L99 | `None` | Любое действие одногруппника в ЛС бота: «Тапер», «Юбиля... |
| [`on_schedule_view`](#on_schedule_view) | Function | L102–L106 | `None` | Просмотр расписания: время суток, кнопка и пары показан... |
| [`on_refresh_click`](#on_refresh_click) | Function | L109–L116 | `None` | Кнопка «Обновить»: «F5 Мастер» и «Нетерпеливый» (3 нажа... |
| [`on_attendance_view`](#on_attendance_view) | Function | L119–L124 | `None` | Личная посещаемость: «Самоконтроль» и «Аналитик» (5 раз... |
| [`on_homework_task`](#on_homework_task) | Function | L127–L144 | `None` | Задание в топике ДЗ: разовые ачивки, счётчики заданий, ... |
| [`mark_ping_all`](#mark_ping_all) | Function | L147–L149 | `None` | Открывает 15-минутное окно «Общего сбора» после /all ст... |
| [`_has_birthday_today`](#_has_birthday_today) | Function | L152–L157 | `bool` | Проверяет, есть ли сегодня именинник среди одногруппник... |
| [`_chat_reply_achievement`](#_chat_reply_achievement) | Function | L160–L171 | `str \| None` | Классифицирует реплай в чате: старосте → «Связь со стар... |
| [`_award_chat_specials`](#_award_chat_specials) | Function | L174–L180 | `None` | Разовые ачивки чата: поздравление именинника и реакция ... |
| [`on_group_message`](#on_group_message) | Function | L183–L201 | `None` | Сообщение в чате группы: счётчики сообщений, стикеров и... |
| [`on_profile_view`](#on_profile_view) | Function | L204–L220 | `bool` | Просмотр чужого профиля в Mini App: «Солидарность» за 5... |

---

## 3. Comprehensive Function Specifications

### `_now`
```python
def _now() -> datetime
```

- **Source Reference**: [`services/achievement_events.py#L62-L64`](../../services/achievement_events.py#L62-L64)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `datetime`

#### Overview & Architectural Purpose
Текущее московское время — во всех описаниях ачивок время московское.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import _now

# Execute call
result = _now()
```

---

### `is_group_member`
```python
def is_group_member(user_id: int) -> bool
```

- **Source Reference**: [`services/achievement_events.py#L67-L69`](../../services/achievement_events.py#L67-L69)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, что пользователь — одногруппник (или староста).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import is_group_member

# Execute call
result = is_group_member(user_id=...)
```

---

### `_award_all`
```python
async def _award_all(uid: int, ids: set[str], bot: Any, name: str | None) -> None
```

- **Source Reference**: [`services/achievement_events.py#L72-L75`](../../services/achievement_events.py#L72-L75)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Выдаёт набор ачивок по одной (каждая сама проверяет, не открыта ли уже).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `ids` | `set[str]` | Yes | Parameter `ids` of type `set[str]`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `name` | `str | None` | Yes | Parameter `name` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import _award_all

# Execute call
result = await _award_all(uid=..., ids=..., bot=...)
```

---

### `bump_counter`
```python
async def bump_counter(uid: int, key: str, bot: Any, name: str | None) -> int
```

- **Source Reference**: [`services/achievement_events.py#L78-L91`](../../services/achievement_events.py#L78-L91)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Увеличивает счётчик студента и выдаёт ачивки за пройденные пороги.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `name` | `str | None` | Yes | Parameter `name` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import bump_counter

# Execute call
result = await bump_counter(uid=..., key=..., bot=...)
```

---

### `on_interaction`
```python
async def on_interaction(user: User, bot: Any) -> None
```

- **Source Reference**: [`services/achievement_events.py#L94-L99`](../../services/achievement_events.py#L94-L99)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Любое действие одногруппника в ЛС бота: «Тапер», «Юбиляр», «На связи».

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user` | `User` | Yes | Parameter `user` of type `User`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import on_interaction

# Execute call
result = await on_interaction(user=..., bot=...)
```

---

### `on_schedule_view`
```python
async def on_schedule_view(user: User | None, bot: Any, view: ScheduleView, lessons: list[Lesson]) -> None
```

- **Source Reference**: [`services/achievement_events.py#L102-L106`](../../services/achievement_events.py#L102-L106)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Просмотр расписания: время суток, кнопка и пары показанного дня.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user` | `User | None` | Yes | Parameter `user` of type `User | None`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `view` | `ScheduleView` | Yes | Parameter `view` of type `ScheduleView`. |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import on_schedule_view

# Execute call
result = await on_schedule_view(user=..., bot=..., view=...)
```

---

### `on_refresh_click`
```python
async def on_refresh_click(user: User | None, bot: Any) -> None
```

- **Source Reference**: [`services/achievement_events.py#L109-L116`](../../services/achievement_events.py#L109-L116)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Кнопка «Обновить»: «F5 Мастер» и «Нетерпеливый» (3 нажатия за минуту).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user` | `User | None` | Yes | Parameter `user` of type `User | None`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import on_refresh_click

# Execute call
result = await on_refresh_click(user=..., bot=...)
```

---

### `on_attendance_view`
```python
async def on_attendance_view(user: User | None, bot: Any) -> None
```

- **Source Reference**: [`services/achievement_events.py#L119-L124`](../../services/achievement_events.py#L119-L124)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Личная посещаемость: «Самоконтроль» и «Аналитик» (5 разных дней).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user` | `User | None` | Yes | Parameter `user` of type `User | None`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import on_attendance_view

# Execute call
result = await on_attendance_view(user=..., bot=...)
```

---

### `on_homework_task`
```python
async def on_homework_task(uid: int, name: str | None, bot: Any, task: HomeworkTask) -> None
```

- **Source Reference**: [`services/achievement_events.py#L127-L144`](../../services/achievement_events.py#L127-L144)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Задание в топике ДЗ: разовые ачивки, счётчики заданий, дней и форматов.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `name` | `str | None` | Yes | Parameter `name` of type `str | None`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `task` | `HomeworkTask` | Yes | Parameter `task` of type `HomeworkTask`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import on_homework_task

# Execute call
result = await on_homework_task(uid=..., name=..., bot=...)
```

---

### `mark_ping_all`
```python
async def mark_ping_all() -> None
```

- **Source Reference**: [`services/achievement_events.py#L147-L149`](../../services/achievement_events.py#L147-L149)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Открывает 15-минутное окно «Общего сбора» после /all старосты.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import mark_ping_all

# Execute call
result = await mark_ping_all()
```

---

### `_has_birthday_today`
```python
def _has_birthday_today(exclude_uid: int, today: date) -> bool
```

- **Source Reference**: [`services/achievement_events.py#L152-L157`](../../services/achievement_events.py#L152-L157)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, есть ли сегодня именинник среди одногруппников, кроме автора.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `exclude_uid` | `int` | Yes | Parameter `exclude_uid` of type `int`. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import _has_birthday_today

# Execute call
result = _has_birthday_today(exclude_uid=..., today=...)
```

---

### `_chat_reply_achievement`
```python
def _chat_reply_achievement(message: Message, uid: int) -> str | None
```

- **Source Reference**: [`services/achievement_events.py#L160-L171`](../../services/achievement_events.py#L160-L171)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Классифицирует реплай в чате: старосте → «Связь со старостой», одногруппнику → «Коллоквиум».

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
from services.achievement_events import _chat_reply_achievement

# Execute call
result = _chat_reply_achievement(message=..., uid=...)
```

---

### `_award_chat_specials`
```python
async def _award_chat_specials(message: Message, uid: int, bot: Any, name: str | None) -> None
```

- **Source Reference**: [`services/achievement_events.py#L174-L180`](../../services/achievement_events.py#L174-L180)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Разовые ачивки чата: поздравление именинника и реакция на /all.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `name` | `str | None` | Yes | Parameter `name` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import _award_chat_specials

# Execute call
result = await _award_chat_specials(message=..., uid=..., bot=...)
```

---

### `on_group_message`
```python
async def on_group_message(message: Message, bot: Any) -> None
```

- **Source Reference**: [`services/achievement_events.py#L183-L201`](../../services/achievement_events.py#L183-L201)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сообщение в чате группы: счётчики сообщений, стикеров и реплаев.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import on_group_message

# Execute call
result = await on_group_message(message=..., bot=...)
```

---

### `on_profile_view`
```python
async def on_profile_view(uid: int, viewed_fio: str) -> bool
```

- **Source Reference**: [`services/achievement_events.py#L204-L220`](../../services/achievement_events.py#L204-L220)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Просмотр чужого профиля в Mini App: «Солидарность» за 5 разных одногруппников.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `uid` | `int` | Yes | Parameter `uid` of type `int`. |
| `viewed_fio` | `str` | Yes | Parameter `viewed_fio` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_events import on_profile_view

# Execute call
result = await on_profile_view(uid=..., viewed_fio=...)
```

---
