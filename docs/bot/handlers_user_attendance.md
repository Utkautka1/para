# Component Reference: `bot/handlers/user/attendance.py`
> **File Path**: [`bot/handlers/user/attendance.py`](../../bot/handlers/user/attendance.py)
> **Subsystem**: `User Attendance Flow`

## 1. Purpose
Хэндлеры просмотра персональной посещаемости студента (/my_attendance).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_calculate_attendance_percent`](#_calculate_attendance_percent) | Function | L38–L54 | `str` | Вычисляет процент посещаемости студента с учетом уважит... |
| [`_format_personal_month_breakdown`](#_format_personal_month_breakdown) | Function | L57–L78 | `str` | Формирует текстовый блок детальной помесячной статистик... |
| [`_format_card_header_and_summary`](#_format_card_header_and_summary) | Function | L81–L91 | `str` | Формирует шапку и сводный блок отметок персональной кар... |
| [`format_personal_attendance_card`](#format_personal_attendance_card) | Function | L94–L106 | `str` | Формирует персональную HTML-карточку посещаемости конкр... |
| [`get_personal_attendance_kb`](#get_personal_attendance_kb) | Function | L109–L121 | `InlineKeyboardMarkup` | Возвращает инлайн-клавиатуру персонального экрана посещ... |
| [`_resolve_student_fio`](#_resolve_student_fio) | Function | L124–L142 | `str \| None` | Определяет официальное ФИО студента по реестру одногруп... |
| [`_respond_personal_attendance`](#_respond_personal_attendance) | Function | L145–L149 | `None` | Отправляет карточку посещаемости и фиксирует ачивку сам... |
| [`cmd_my_attendance`](#cmd_my_attendance) | Function | L153–L168 | `None` | Отображает персональную карточку посещаемости авторизов... |
| [`cb_my_attendance_refresh`](#cb_my_attendance_refresh) | Function | L172–L188 | `None` | Обновляет персональную карточку посещаемости студента в... |
| [`cb_att_topic_refresh`](#cb_att_topic_refresh) | Function | L192–L206 | `None` | Синхронизирует сводный реестр посещаемости по кнопке в ... |

---

## 3. Comprehensive Function Specifications

### `_calculate_attendance_percent`
```python
def _calculate_attendance_percent(p: int, o: int, u: int, total: int) -> str
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L38-L54`](../../bot/handlers/user/attendance.py#L38-L54)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Вычисляет процент посещаемости студента с учетом уважительных причин.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `p` | `int` | Yes | Parameter `p` of type `int`. |
| `o` | `int` | Yes | Parameter `o` of type `int`. |
| `u` | `int` | Yes | Parameter `u` of type `int`. |
| `total` | `int` | Yes | Parameter `total` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.attendance import _calculate_attendance_percent

# Execute call
result = _calculate_attendance_percent(p=..., o=..., u=...)
```

---

### `_format_personal_month_breakdown`
```python
def _format_personal_month_breakdown(months: dict[str, dict[str, int]]) -> str
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L57-L78`](../../bot/handlers/user/attendance.py#L57-L78)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует текстовый блок детальной помесячной статистики посещаемости.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `months` | `dict[str, dict[str, int]]` | Yes | Parameter `months` of type `dict[str, dict[str, int]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.attendance import _format_personal_month_breakdown

# Execute call
result = _format_personal_month_breakdown(months=...)
```

---

### `_format_card_header_and_summary`
```python
def _format_card_header_and_summary(fio: str, p: int, o: int, u: int, n: int) -> str
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L81-L91`](../../bot/handlers/user/attendance.py#L81-L91)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует шапку и сводный блок отметок персональной карточки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `p` | `int` | Yes | Parameter `p` of type `int`. |
| `o` | `int` | Yes | Parameter `o` of type `int`. |
| `u` | `int` | Yes | Parameter `u` of type `int`. |
| `n` | `int` | Yes | Parameter `n` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.attendance import _format_card_header_and_summary

# Execute call
result = _format_card_header_and_summary(fio=..., p=..., o=...)
```

---

### `format_personal_attendance_card`
```python
def format_personal_attendance_card(fio: str, student_data: dict[str, Any]) -> str
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L94-L106`](../../bot/handlers/user/attendance.py#L94-L106)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует персональную HTML-карточку посещаемости конкретного студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `student_data` | `dict[str, Any]` | Yes | Parameter `student_data` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.attendance import format_personal_attendance_card

# Execute call
result = format_personal_attendance_card(fio=..., student_data=...)
```

---

### `get_personal_attendance_kb`
```python
def get_personal_attendance_kb() -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L109-L121`](../../bot/handlers/user/attendance.py#L109-L121)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Возвращает инлайн-клавиатуру персонального экрана посещаемости студента.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.attendance import get_personal_attendance_kb

# Execute call
result = get_personal_attendance_kb()
```

---

### `_resolve_student_fio`
```python
def _resolve_student_fio(user, student: dict[str, Any] | None = None) -> str | None
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L124-L142`](../../bot/handlers/user/attendance.py#L124-L142)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Определяет официальное ФИО студента по реестру одногруппников группы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user` | `Any` | Yes | Parameter `user` of type `Any`. |
| `student` | `dict[str, Any] | None` | Yes | Parameter `student` of type `dict[str, Any] | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.attendance import _resolve_student_fio

# Execute call
result = _resolve_student_fio(user=..., student=...)
```

---

### `_respond_personal_attendance`
```python
async def _respond_personal_attendance(message: Message, fio: str, data: dict[str, Any]) -> None
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L145-L149`](../../bot/handlers/user/attendance.py#L145-L149)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет карточку посещаемости и фиксирует ачивку самопроверки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `data` | `dict[str, Any]` | Yes | Parameter `data` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.attendance import _respond_personal_attendance

# Execute call
result = await _respond_personal_attendance(message=..., fio=..., data=...)
```

---

### `cmd_my_attendance`
```python
async def cmd_my_attendance(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L153-L168`](../../bot/handlers/user/attendance.py#L153-L168)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает персональную карточку посещаемости авторизованного студента.

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
from bot.handlers.user.attendance import cmd_my_attendance

# Execute call
result = await cmd_my_attendance(message=...)
```

---

### `cb_my_attendance_refresh`
```python
async def cb_my_attendance_refresh(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L172-L188`](../../bot/handlers/user/attendance.py#L172-L188)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Обновляет персональную карточку посещаемости студента в ЛС по кнопке.

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
from bot.handlers.user.attendance import cb_my_attendance_refresh

# Execute call
result = await cb_my_attendance_refresh(callback=...)
```

---

### `cb_att_topic_refresh`
```python
async def cb_att_topic_refresh(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/attendance.py#L192-L206`](../../bot/handlers/user/attendance.py#L192-L206)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Синхронизирует сводный реестр посещаемости по кнопке в топике Telegram.

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
from bot.handlers.user.attendance import cb_att_topic_refresh

# Execute call
result = await cb_att_topic_refresh(callback=...)
```

---
