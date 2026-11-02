# Component Reference: `bot/templates/user/keyboards.py`
> **File Path**: [`bot/templates/user/keyboards.py`](../../bot/templates/user/keyboards.py)
> **Subsystem**: `User Inline Keyboards`

## 1. Purpose
Модуль аккуратных Inline-клавиатур навигации.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`format_lesson_button_text`](#format_lesson_button_text) | Function | L14–L26 | `str` | Формирует лаконичный текст кнопки подключения к дистанц... |
| [`chunk_link_buttons`](#chunk_link_buttons) | Function | L29–L46 | `list[list[InlineKeyboardButton]]` | Разбивает кнопки ссылок на дистанционные занятия по 2 ш... |
| [`_build_admin_nav_rows`](#_build_admin_nav_rows) | Function | L49–L68 | `list[list[InlineKeyboardButton]]` | Формирует дополнительные служебные кнопки старосты и ад... |
| [`_build_calendar_rows`](#_build_calendar_rows) | Function | L71–L90 | `list[list[InlineKeyboardButton]]` | Формирует базовые ряды кнопок календаря (сегодня, завтр... |
| [`_build_nav_rows`](#_build_nav_rows) | Function | L93–L106 | `list[list[InlineKeyboardButton]]` | Формирует основные кнопки навигации по календарю и пере... |
| [`get_schedule_inline_kb`](#get_schedule_inline_kb) | Function | L109–L120 | `InlineKeyboardMarkup` | Генерирует полную навигационную клавиатуру для экрана р... |
| [`get_tester_cabinet_kb`](#get_tester_cabinet_kb) | Function | L123–L141 | `InlineKeyboardMarkup` | Формирует инлайн-клавиатуру персонального кабинета тест... |
| [`get_topic_inline_kb`](#get_topic_inline_kb) | Function | L144–L159 | `InlineKeyboardMarkup \| None` | Генерирует лаконичную клавиатуру со ссылками на пары дл... |
| [`get_notice_settings_kb`](#get_notice_settings_kb) | Function | L162–L179 | `InlineKeyboardMarkup` | Генерирует интерактивную клавиатуру управления уведомле... |

---

## 3. Comprehensive Function Specifications

### `format_lesson_button_text`
```python
def format_lesson_button_text(lesson: Lesson) -> str
```

- **Source Reference**: [`bot/templates/user/keyboards.py#L14-L26`](../../bot/templates/user/keyboards.py#L14-L26)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует лаконичный текст кнопки подключения к дистанционной паре.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.keyboards import format_lesson_button_text

# Execute call
result = format_lesson_button_text(lesson=...)
```

---

### `chunk_link_buttons`
```python
def chunk_link_buttons(lessons: list[Lesson]) -> list[list[InlineKeyboardButton]]
```

- **Source Reference**: [`bot/templates/user/keyboards.py#L29-L46`](../../bot/templates/user/keyboards.py#L29-L46)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[list[InlineKeyboardButton]]`

#### Overview & Architectural Purpose
Разбивает кнопки ссылок на дистанционные занятия по 2 штуки в ряд.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.keyboards import chunk_link_buttons

# Execute call
result = chunk_link_buttons(lessons=...)
```

---

### `_build_admin_nav_rows`
```python
def _build_admin_nav_rows(is_admin: bool, is_attendance_admin: bool) -> list[list[InlineKeyboardButton]]
```

- **Source Reference**: [`bot/templates/user/keyboards.py#L49-L68`](../../bot/templates/user/keyboards.py#L49-L68)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[list[InlineKeyboardButton]]`

#### Overview & Architectural Purpose
Формирует дополнительные служебные кнопки старосты и администратора.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `is_admin` | `bool` | Yes | Parameter `is_admin` of type `bool`. |
| `is_attendance_admin` | `bool` | Yes | Parameter `is_attendance_admin` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.keyboards import _build_admin_nav_rows

# Execute call
result = _build_admin_nav_rows(is_admin=..., is_attendance_admin=...)
```

---

### `_build_calendar_rows`
```python
def _build_calendar_rows(week_offset: int, is_subscribed: bool) -> list[list[InlineKeyboardButton]]
```

- **Source Reference**: [`bot/templates/user/keyboards.py#L71-L90`](../../bot/templates/user/keyboards.py#L71-L90)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[list[InlineKeyboardButton]]`

#### Overview & Architectural Purpose
Формирует базовые ряды кнопок календаря (сегодня, завтра, смена недели, пуши).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `week_offset` | `int` | Yes | Parameter `week_offset` of type `int`. |
| `is_subscribed` | `bool` | Yes | Parameter `is_subscribed` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.keyboards import _build_calendar_rows

# Execute call
result = _build_calendar_rows(week_offset=..., is_subscribed=...)
```

---

### `_build_nav_rows`
```python
def _build_nav_rows( week_offset: int, is_admin: bool = False, is_subscribed: bool = True, is_attendance_admin: bool = False, is_tester: bool = False, ) -> list[list[InlineKeyboardButton]]
```

- **Source Reference**: [`bot/templates/user/keyboards.py#L93-L106`](../../bot/templates/user/keyboards.py#L93-L106)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[list[InlineKeyboardButton]]`

#### Overview & Architectural Purpose
Формирует основные кнопки навигации по календарю и переключатели настроек.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `week_offset` | `int` | Yes | Parameter `week_offset` of type `int`. |
| `is_admin` | `bool` | Yes | Parameter `is_admin` of type `bool`. |
| `is_subscribed` | `bool` | Yes | Parameter `is_subscribed` of type `bool`. |
| `is_attendance_admin` | `bool` | Yes | Parameter `is_attendance_admin` of type `bool`. |
| `is_tester` | `bool` | Yes | Parameter `is_tester` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.keyboards import _build_nav_rows

# Execute call
result = _build_nav_rows(week_offset=..., is_admin=..., is_subscribed=...)
```

---

### `get_schedule_inline_kb`
```python
def get_schedule_inline_kb( lessons: list[Lesson] | None = None, week_offset: int = 0, is_admin: bool = False, is_subscribed: bool = True, is_attendance_admin: bool = False, is_tester: bool = False, ) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/user/keyboards.py#L109-L120`](../../bot/templates/user/keyboards.py#L109-L120)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует полную навигационную клавиатуру для экрана расписания в ЛС.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list[Lesson] | None` | Yes | Parameter `lessons` of type `list[Lesson] | None`. |
| `week_offset` | `int` | Yes | Parameter `week_offset` of type `int`. |
| `is_admin` | `bool` | Yes | Parameter `is_admin` of type `bool`. |
| `is_subscribed` | `bool` | Yes | Parameter `is_subscribed` of type `bool`. |
| `is_attendance_admin` | `bool` | Yes | Parameter `is_attendance_admin` of type `bool`. |
| `is_tester` | `bool` | Yes | Parameter `is_tester` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.keyboards import get_schedule_inline_kb

# Execute call
result = get_schedule_inline_kb(lessons=..., week_offset=..., is_admin=...)
```

---

### `get_tester_cabinet_kb`
```python
def get_tester_cabinet_kb(login_url: str | None = None) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/user/keyboards.py#L123-L141`](../../bot/templates/user/keyboards.py#L123-L141)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Формирует инлайн-клавиатуру персонального кабинета тестера API.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `login_url` | `str | None` | Yes | Parameter `login_url` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.keyboards import get_tester_cabinet_kb

# Execute call
result = get_tester_cabinet_kb(login_url=...)
```

---

### `get_topic_inline_kb`
```python
def get_topic_inline_kb(lessons: list[Lesson] | None = None) -> InlineKeyboardMarkup | None
```

- **Source Reference**: [`bot/templates/user/keyboards.py#L144-L159`](../../bot/templates/user/keyboards.py#L144-L159)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup | None`

#### Overview & Architectural Purpose
Генерирует лаконичную клавиатуру со ссылками на пары для топика группы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list[Lesson] | None` | Yes | Parameter `lessons` of type `list[Lesson] | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.keyboards import get_topic_inline_kb

# Execute call
result = get_topic_inline_kb(lessons=...)
```

---

### `get_notice_settings_kb`
```python
def get_notice_settings_kb(is_subscribed: bool) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/user/keyboards.py#L162-L179`](../../bot/templates/user/keyboards.py#L162-L179)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует интерактивную клавиатуру управления уведомлениями для /notice.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `is_subscribed` | `bool` | Yes | Parameter `is_subscribed` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.keyboards import get_notice_settings_kb

# Execute call
result = get_notice_settings_kb(is_subscribed=...)
```

---
