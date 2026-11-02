# Component Reference: `bot/templates/user/messages.py`
> **File Path**: [`bot/templates/user/messages.py`](../../bot/templates/user/messages.py)
> **Subsystem**: `User Message Formatter`

## 1. Purpose
Модуль стильного и информативного форматирования сообщений бота.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_format_remote_credentials`](#_format_remote_credentials) | Function | L18–L40 | `str` | Форматирует идентификатор конференции и пароль Zoom/Тел... |
| [`format_lesson_card`](#format_lesson_card) | Function | L43–L72 | `str` | Формирует подробную информационную карточку пары для Te... |
| [`format_minutes`](#format_minutes) | Function | L75–L93 | `str` | Преобразует общее количество минут в человекочитаемую с... |
| [`_parse_time_interval_minutes`](#_parse_time_interval_minutes) | Function | L96–L113 | `tuple[int, int] \| None` | Извлекает границы времени начала и конца пары в минутах... |
| [`_check_single_lesson_status`](#_check_single_lesson_status) | Function | L116–L139 | `tuple[bool, str]` | Проверяет статус конкретной пары относительно текущей м... |
| [`get_lesson_status_banner`](#get_lesson_status_banner) | Function | L142–L162 | `str` | Рассчитывает динамический баннер статуса пар для сегодн... |
| [`format_day_schedule`](#format_day_schedule) | Function | L165–L185 | `str` | Форматирует расписание на конкретный учебный день в ито... |
| [`format_week_lesson_loc`](#format_week_lesson_loc) | Function | L188–L203 | `str` | Формирует лаконичную строку локации для недельного дайд... |
| [`format_week_lesson_card`](#format_week_lesson_card) | Function | L206–L227 | `str` | Формирует компактную цитатную карточку пары для недельн... |
| [`format_week_day_block`](#format_week_day_block) | Function | L230–L249 | `str` | Формирует визуальный блок одного учебного дня для недел... |
| [`format_week_schedule`](#format_week_schedule) | Function | L252–L265 | `str` | Формирует полное недельное расписание с пн по сб единым... |
| [`format_reminder_text`](#format_reminder_text) | Function | L268–L280 | `str` | Формирует текст персонального напоминания за 10 минут д... |
| [`format_notice_settings_text`](#format_notice_settings_text) | Function | L283–L307 | `str` | Формирует информационный текст экрана управления личным... |

---

## 3. Comprehensive Function Specifications

### `_format_remote_credentials`
```python
def _format_remote_credentials(lesson: Lesson) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L18-L40`](../../bot/templates/user/messages.py#L18-L40)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Форматирует идентификатор конференции и пароль Zoom/Телемост в HTML.

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
from bot.templates.user.messages import _format_remote_credentials

# Execute call
result = _format_remote_credentials(lesson=...)
```

---

### `format_lesson_card`
```python
def format_lesson_card(lesson: Lesson) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L43-L72`](../../bot/templates/user/messages.py#L43-L72)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует подробную информационную карточку пары для Telegram-сообщения.

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
from bot.templates.user.messages import format_lesson_card

# Execute call
result = format_lesson_card(lesson=...)
```

---

### `format_minutes`
```python
def format_minutes(total_minutes: int) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L75-L93`](../../bot/templates/user/messages.py#L75-L93)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Преобразует общее количество минут в человекочитаемую строку часов и минут.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `total_minutes` | `int` | Yes | Parameter `total_minutes` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.messages import format_minutes

# Execute call
result = format_minutes(total_minutes=...)
```

---

### `_parse_time_interval_minutes`
```python
def _parse_time_interval_minutes(time_str: str) -> tuple[int, int] | None
```

- **Source Reference**: [`bot/templates/user/messages.py#L96-L113`](../../bot/templates/user/messages.py#L96-L113)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[int, int] | None`

#### Overview & Architectural Purpose
Извлекает границы времени начала и конца пары в минутах от начала суток.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `time_str` | `str` | Yes | Parameter `time_str` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.messages import _parse_time_interval_minutes

# Execute call
result = _parse_time_interval_minutes(time_str=...)
```

---

### `_check_single_lesson_status`
```python
def _check_single_lesson_status(lesson: Lesson, n_min: int) -> tuple[bool, str]
```

- **Source Reference**: [`bot/templates/user/messages.py#L116-L139`](../../bot/templates/user/messages.py#L116-L139)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[bool, str]`

#### Overview & Architectural Purpose
Проверяет статус конкретной пары относительно текущей минуты суток.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson` | `Lesson` | Yes | Parameter `lesson` of type `Lesson`. |
| `n_min` | `int` | Yes | Parameter `n_min` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.messages import _check_single_lesson_status

# Execute call
result = _check_single_lesson_status(lesson=..., n_min=...)
```

---

### `get_lesson_status_banner`
```python
def get_lesson_status_banner(lessons: list[Lesson], target_date: date) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L142-L162`](../../bot/templates/user/messages.py#L142-L162)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Рассчитывает динамический баннер статуса пар для сегодняшнего дня.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.messages import get_lesson_status_banner

# Execute call
result = get_lesson_status_banner(lessons=..., target_date=...)
```

---

### `format_day_schedule`
```python
def format_day_schedule(target_date: date, lessons: list[Lesson]) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L165-L185`](../../bot/templates/user/messages.py#L165-L185)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Форматирует расписание на конкретный учебный день в итоговый HTML-блок.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.messages import format_day_schedule

# Execute call
result = format_day_schedule(target_date=..., lessons=...)
```

---

### `format_week_lesson_loc`
```python
def format_week_lesson_loc(lesson: Lesson) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L188-L203`](../../bot/templates/user/messages.py#L188-L203)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует лаконичную строку локации для недельного дайджеста расписания.

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
from bot.templates.user.messages import format_week_lesson_loc

# Execute call
result = format_week_lesson_loc(lesson=...)
```

---

### `format_week_lesson_card`
```python
def format_week_lesson_card(lesson: Lesson) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L206-L227`](../../bot/templates/user/messages.py#L206-L227)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует компактную цитатную карточку пары для недельного обзора.

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
from bot.templates.user.messages import format_week_lesson_card

# Execute call
result = format_week_lesson_card(lesson=...)
```

---

### `format_week_day_block`
```python
def format_week_day_block(day_date: date, lessons: list[Lesson]) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L230-L249`](../../bot/templates/user/messages.py#L230-L249)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует визуальный блок одного учебного дня для недельного дайджеста.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `day_date` | `date` | Yes | Parameter `day_date` of type `date`. |
| `lessons` | `list[Lesson]` | Yes | Parameter `lessons` of type `list[Lesson]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.messages import format_week_day_block

# Execute call
result = format_week_day_block(day_date=..., lessons=...)
```

---

### `format_week_schedule`
```python
def format_week_schedule(days_data: list[tuple[date, list[Lesson]]]) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L252-L265`](../../bot/templates/user/messages.py#L252-L265)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует полное недельное расписание с пн по сб единым сообщением.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `days_data` | `list[tuple[date, list[Lesson]]]` | Yes | Parameter `days_data` of type `list[tuple[date, list[Lesson]]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.messages import format_week_schedule

# Execute call
result = format_week_schedule(days_data=...)
```

---

### `format_reminder_text`
```python
def format_reminder_text(lesson: Lesson) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L268-L280`](../../bot/templates/user/messages.py#L268-L280)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует текст персонального напоминания за 10 минут до начала пары.

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
from bot.templates.user.messages import format_reminder_text

# Execute call
result = format_reminder_text(lesson=...)
```

---

### `format_notice_settings_text`
```python
def format_notice_settings_text(is_subscribed: bool) -> str
```

- **Source Reference**: [`bot/templates/user/messages.py#L283-L307`](../../bot/templates/user/messages.py#L283-L307)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует информационный текст экрана управления личными уведомлениями.

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
from bot.templates.user.messages import format_notice_settings_text

# Execute call
result = format_notice_settings_text(is_subscribed=...)
```

---
