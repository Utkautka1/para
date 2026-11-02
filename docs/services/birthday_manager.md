# Component Reference: `services/birthday_manager.py`
> **File Path**: [`services/birthday_manager.py`](../../services/birthday_manager.py)
> **Subsystem**: `Student Lifecycle`

## 1. Purpose
Менеджер дней рождения группы 1-КПД-3.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_compute_next_birthday`](#_compute_next_birthday) | Function | L47–L68 | `tuple[int, bool, int]` | Рассчитывает количество дней до ближайшего дня рождения... |
| [`calculate_days_and_age`](#calculate_days_and_age) | Function | L71–L82 | `dict[str, Any]` | Вычисляет оставшиеся дни до дня рождения и возраст, исп... |
| [`format_person_tag`](#format_person_tag) | Function | L85–L101 | `str` | Формирует кликабельное имя человека для реестра Telegra... |
| [`format_days_left_badge`](#format_days_left_badge) | Function | L104–L124 | `str` | Формирует понятный бейдж оставшихся дней с правильным р... |
| [`format_today_block`](#format_today_block) | Function | L127–L142 | `list[str]` | Формирует праздничный блок в HTML-цитате для имениннико... |
| [`format_age_badge`](#format_age_badge) | Function | L145–L160 | `str` | Склоняет возраст человека по правилам русского языка (г... |
| [`format_upcoming_block`](#format_upcoming_block) | Function | L163–L186 | `list[str]` | Формирует блок ближайших именинников в цитате Telegram. |
| [`season_sort_key`](#season_sort_key) | Function | L189–L198 | `int` | Вычисляет целочисленный индекс сортировки даты внутри з... |
| [`format_season_block`](#format_season_block) | Function | L201–L220 | `list[str]` | Форматирует сезонный блок именинников (осень, зима, вес... |
| [`format_birthday_registry_text`](#format_birthday_registry_text) | Function | L223–L239 | `str` | Собирает полный итоговый текст закрепленного сообщения ... |
| [`pick_unique_wish`](#pick_unique_wish) | Function | L242–L263 | `str` | Выбирает случайное неповторяющееся поздравление для уча... |
| [`get_person_mention`](#get_person_mention) | Function | L266–L281 | `str` | Формирует кликабельное упоминание именинника для персон... |
| [`format_starosta_block`](#format_starosta_block) | Function | L284–L295 | `str` | Формирует цитату с напутственным словом старосты группы... |
| [`format_congrats_message`](#format_congrats_message) | Function | L298–L320 | `str` | Формирует праздничное персональное поздравление от имен... |
| [`_send_congrats_telegram`](#_send_congrats_telegram) | Function | L323–L338 | `None` | Отправляет поздравление в топик 'Важное' и сохраняет фл... |
| [`send_congrats_for_item`](#send_congrats_for_item) | Function | L341–L360 | `None` | Оркестрирует отправку персонального поздравления для им... |
| [`is_morning_congrats_time`](#is_morning_congrats_time) | Function | L363–L371 | `bool` | Проверяет наступление утреннего времени отправки поздра... |
| [`check_and_send_birthday_congratulations`](#check_and_send_birthday_congratulations) | Function | L374–L390 | `None` | Проверяет сегодняшних именинников и отправляет поздравл... |
| [`_edit_existing_birthday_message`](#_edit_existing_birthday_message) | Function | L393–L410 | `bool` | Редактирует существующее закрепленное сообщение реестра... |
| [`_create_new_birthday_message`](#_create_new_birthday_message) | Function | L413–L433 | `bool` | Публикует и закрепляет новое сообщение реестра дней рож... |
| [`update_birthday_pinned_message`](#update_birthday_pinned_message) | Function | L436–L449 | `bool` | Оркестрирует обновление или повторное создание закрепле... |
| [`sync_birthdays_topic`](#sync_birthdays_topic) | Function | L452–L471 | `bool` | Выполняет полный цикл синхронизации реестра дней рожден... |
| [`birthday_sync_loop`](#birthday_sync_loop) | Function | L474–L490 | `None` | Запускает бесконечный цикл фоновой синхронизации дней р... |

---

## 3. Comprehensive Function Specifications

### `_compute_next_birthday`
```python
def _compute_next_birthday(today: date, b_day: int, b_month: int) -> tuple[int, bool, int]
```

- **Source Reference**: [`services/birthday_manager.py#L47-L68`](../../services/birthday_manager.py#L47-L68)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[int, bool, int]`

#### Overview & Architectural Purpose
Рассчитывает количество дней до ближайшего дня рождения с учетом високосных лет.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `today` | `date` | Yes | Parameter `today` of type `date`. |
| `b_day` | `int` | Yes | Parameter `b_day` of type `int`. |
| `b_month` | `int` | Yes | Parameter `b_month` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import _compute_next_birthday

# Execute call
result = _compute_next_birthday(today=..., b_day=..., b_month=...)
```

---

### `calculate_days_and_age`
```python
def calculate_days_and_age(item: dict[str, Any], today: date) -> dict[str, Any]
```

- **Source Reference**: [`services/birthday_manager.py#L71-L82`](../../services/birthday_manager.py#L71-L82)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Вычисляет оставшиеся дни до дня рождения и возраст, исполняющийся в праздник.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import calculate_days_and_age

# Execute call
result = calculate_days_and_age(item=..., today=...)
```

---

### `format_person_tag`
```python
def format_person_tag(item: dict[str, Any]) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L85-L101`](../../services/birthday_manager.py#L85-L101)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует кликабельное имя человека для реестра Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_person_tag

# Execute call
result = format_person_tag(item=...)
```

---

### `format_days_left_badge`
```python
def format_days_left_badge(days: int) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L104-L124`](../../services/birthday_manager.py#L104-L124)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует понятный бейдж оставшихся дней с правильным русским склонением.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `days` | `int` | Yes | Parameter `days` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_days_left_badge

# Execute call
result = format_days_left_badge(days=...)
```

---

### `format_today_block`
```python
def format_today_block(today_items: list[dict[str, Any]]) -> list[str]
```

- **Source Reference**: [`services/birthday_manager.py#L127-L142`](../../services/birthday_manager.py#L127-L142)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[str]`

#### Overview & Architectural Purpose
Формирует праздничный блок в HTML-цитате для именинников сегодняшнего дня.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `today_items` | `list[dict[str, Any]]` | Yes | Parameter `today_items` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_today_block

# Execute call
result = format_today_block(today_items=...)
```

---

### `format_age_badge`
```python
def format_age_badge(age: int) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L145-L160`](../../services/birthday_manager.py#L145-L160)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Склоняет возраст человека по правилам русского языка (год / года / лет).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `age` | `int` | Yes | Parameter `age` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_age_badge

# Execute call
result = format_age_badge(age=...)
```

---

### `format_upcoming_block`
```python
def format_upcoming_block(items: list[dict[str, Any]]) -> list[str]
```

- **Source Reference**: [`services/birthday_manager.py#L163-L186`](../../services/birthday_manager.py#L163-L186)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[str]`

#### Overview & Architectural Purpose
Формирует блок ближайших именинников в цитате Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `items` | `list[dict[str, Any]]` | Yes | Parameter `items` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_upcoming_block

# Execute call
result = format_upcoming_block(items=...)
```

---

### `season_sort_key`
```python
def season_sort_key(item: dict[str, Any], months: list[int]) -> int
```

- **Source Reference**: [`services/birthday_manager.py#L189-L198`](../../services/birthday_manager.py#L189-L198)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Вычисляет целочисленный индекс сортировки даты внутри заданного сезона.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |
| `months` | `list[int]` | Yes | Parameter `months` of type `list[int]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import season_sort_key

# Execute call
result = season_sort_key(item=..., months=...)
```

---

### `format_season_block`
```python
def format_season_block(title: str, months: list[int], all_items: list[dict[str, Any]]) -> list[str]
```

- **Source Reference**: [`services/birthday_manager.py#L201-L220`](../../services/birthday_manager.py#L201-L220)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[str]`

#### Overview & Architectural Purpose
Форматирует сезонный блок именинников (осень, зима, весна, лето).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `months` | `list[int]` | Yes | Parameter `months` of type `list[int]`. |
| `all_items` | `list[dict[str, Any]]` | Yes | Parameter `all_items` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_season_block

# Execute call
result = format_season_block(title=..., months=..., all_items=...)
```

---

### `format_birthday_registry_text`
```python
def format_birthday_registry_text(items: list[dict[str, Any]]) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L223-L239`](../../services/birthday_manager.py#L223-L239)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Собирает полный итоговый текст закрепленного сообщения реестра дней рождения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `items` | `list[dict[str, Any]]` | Yes | Parameter `items` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_birthday_registry_text

# Execute call
result = format_birthday_registry_text(items=...)
```

---

### `pick_unique_wish`
```python
def pick_unique_wish(person_key: str, wishes: list[str], history_file: str = HISTORY_FILE) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L242-L263`](../../services/birthday_manager.py#L242-L263)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Выбирает случайное неповторяющееся поздравление для участника.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `person_key` | `str` | Yes | Parameter `person_key` of type `str`. |
| `wishes` | `list[str]` | Yes | Parameter `wishes` of type `list[str]`. |
| `history_file` | `str` | Yes | Parameter `history_file` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import pick_unique_wish

# Execute call
result = pick_unique_wish(person_key=..., wishes=..., history_file=...)
```

---

### `get_person_mention`
```python
def get_person_mention(item: dict[str, Any]) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L266-L281`](../../services/birthday_manager.py#L266-L281)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует кликабельное упоминание именинника для персонального поздравления.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import get_person_mention

# Execute call
result = get_person_mention(item=...)
```

---

### `format_starosta_block`
```python
def format_starosta_block(starosta_text: str | None) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L284-L295`](../../services/birthday_manager.py#L284-L295)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует цитату с напутственным словом старосты группы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `starosta_text` | `str | None` | Yes | Parameter `starosta_text` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_starosta_block

# Execute call
result = format_starosta_block(starosta_text=...)
```

---

### `format_congrats_message`
```python
def format_congrats_message(item: dict[str, Any], wish_text: str, starosta_text: str | None = None) -> str
```

- **Source Reference**: [`services/birthday_manager.py#L298-L320`](../../services/birthday_manager.py#L298-L320)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует праздничное персональное поздравление от имени группы и старосты.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |
| `wish_text` | `str` | Yes | Parameter `wish_text` of type `str`. |
| `starosta_text` | `str | None` | Yes | Parameter `starosta_text` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import format_congrats_message

# Execute call
result = format_congrats_message(item=..., wish_text=..., starosta_text=...)
```

---

### `_send_congrats_telegram`
```python
async def _send_congrats_telegram(text: str, person_key: str, key: str, state: dict[str, bool]) -> None
```

- **Source Reference**: [`services/birthday_manager.py#L323-L338`](../../services/birthday_manager.py#L323-L338)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет поздравление в топик 'Важное' и сохраняет флаг доставки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `person_key` | `str` | Yes | Parameter `person_key` of type `str`. |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `state` | `dict[str, bool]` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import _send_congrats_telegram

# Execute call
result = await _send_congrats_telegram(text=..., person_key=..., key=...)
```

---

### `send_congrats_for_item`
```python
async def send_congrats_for_item(item: dict[str, Any], today_str: str) -> None
```

- **Source Reference**: [`services/birthday_manager.py#L341-L360`](../../services/birthday_manager.py#L341-L360)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Оркестрирует отправку персонального поздравления для именинника.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Yes | Parameter `item` of type `dict[str, Any]`. |
| `today_str` | `str` | Yes | Parameter `today_str` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import send_congrats_for_item

# Execute call
result = await send_congrats_for_item(item=..., today_str=...)
```

---

### `is_morning_congrats_time`
```python
def is_morning_congrats_time(now_dt: datetime) -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L363-L371`](../../services/birthday_manager.py#L363-L371)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет наступление утреннего времени отправки поздравлений (07:00 МСК).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now_dt` | `datetime` | Yes | Current reference datetime anchored to Europe/Moscow timezone. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import is_morning_congrats_time

# Execute call
result = is_morning_congrats_time(now_dt=...)
```

---

### `check_and_send_birthday_congratulations`
```python
async def check_and_send_birthday_congratulations(items: list[dict[str, Any]], today: date) -> None
```

- **Source Reference**: [`services/birthday_manager.py#L374-L390`](../../services/birthday_manager.py#L374-L390)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Проверяет сегодняшних именинников и отправляет поздравления строго с 07:00.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `items` | `list[dict[str, Any]]` | Yes | Parameter `items` of type `list[dict[str, Any]]`. |
| `today` | `date` | Yes | Parameter `today` of type `date`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import check_and_send_birthday_congratulations

# Execute call
result = await check_and_send_birthday_congratulations(items=..., today=...)
```

---

### `_edit_existing_birthday_message`
```python
async def _edit_existing_birthday_message(msg_id: int, text: str) -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L393-L410`](../../services/birthday_manager.py#L393-L410)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Редактирует существующее закрепленное сообщение реестра дней рождения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg_id` | `int` | Yes | Parameter `msg_id` of type `int`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import _edit_existing_birthday_message

# Execute call
result = await _edit_existing_birthday_message(msg_id=..., text=...)
```

---

### `_create_new_birthday_message`
```python
async def _create_new_birthday_message(text: str) -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L413-L433`](../../services/birthday_manager.py#L413-L433)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Публикует и закрепляет новое сообщение реестра дней рождения в топике.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import _create_new_birthday_message

# Execute call
result = await _create_new_birthday_message(text=...)
```

---

### `update_birthday_pinned_message`
```python
async def update_birthday_pinned_message(text: str) -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L436-L449`](../../services/birthday_manager.py#L436-L449)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Оркестрирует обновление или повторное создание закрепленного сообщения реестра.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import update_birthday_pinned_message

# Execute call
result = await update_birthday_pinned_message(text=...)
```

---

### `sync_birthdays_topic`
```python
async def sync_birthdays_topic() -> bool
```

- **Source Reference**: [`services/birthday_manager.py#L452-L471`](../../services/birthday_manager.py#L452-L471)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Выполняет полный цикл синхронизации реестра дней рождения и отправки поздравлений.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.birthday_manager import sync_birthdays_topic

# Execute call
result = await sync_birthdays_topic()
```

---

### `birthday_sync_loop`
```python
async def birthday_sync_loop() -> None
```

- **Source Reference**: [`services/birthday_manager.py#L474-L490`](../../services/birthday_manager.py#L474-L490)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Запускает бесконечный цикл фоновой синхронизации дней рождения (каждые 30 минут).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.birthday_manager import birthday_sync_loop

# Execute call
result = await birthday_sync_loop()
```

---
