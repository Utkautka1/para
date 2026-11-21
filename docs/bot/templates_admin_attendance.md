# Component Reference: `bot/templates/admin/attendance.py`
> **File Path**: [`bot/templates/admin/attendance.py`](../../bot/templates/admin/attendance.py)
> **Subsystem**: `Attendance Keyboards`

## 1. Purpose
Шаблоны сообщений и клавиатур для модуля отметки посещаемости.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_lesson_confirm_kb`](#get_lesson_confirm_kb) | Function | L21–L38 | `InlineKeyboardMarkup` | Генерирует инлайн-клавиатуру подтверждения проведения п... |
| [`get_student_poll_kb`](#get_student_poll_kb) | Function | L41–L69 | `InlineKeyboardMarkup` | Генерирует инлайн-клавиатуру выставления статуса студен... |
| [`format_confirm_text`](#format_confirm_text) | Function | L72–L86 | `str` | Формирует текст диалога подтверждения факта проведения ... |
| [`format_student_card`](#format_student_card) | Function | L89–L108 | `str` | Формирует текст карточки текущего студента с прогресс-и... |
| [`_format_absent_students`](#_format_absent_students) | Function | L111–L129 | `str` | Формирует список отсутствовавших и опоздавших студентов... |
| [`format_summary_text`](#format_summary_text) | Function | L132–L151 | `str` | Формирует итоговый текстовый отчет после успешной фикса... |
| [`format_partner_attendance_report`](#format_partner_attendance_report) | Function | L154–L171 | `str` | Формирует уведомление о сохранении посещаемости для вто... |
| [`format_partner_cancel_report`](#format_partner_cancel_report) | Function | L174–L188 | `str` | Формирует уведомление об отмене занятия для второго адм... |
| [`get_days_select_kb`](#get_days_select_kb) | Function | L191–L214 | `InlineKeyboardMarkup` | Генерирует клавиатуру выбора учебного дня за последнюю ... |
| [`get_lesson_select_kb`](#get_lesson_select_kb) | Function | L217–L248 | `InlineKeyboardMarkup` | Генерирует кнопки выбора пар для конкретного учебного д... |
| [`get_lesson_mode_kb`](#get_lesson_mode_kb) | Function | L251–L262 | `InlineKeyboardMarkup` | Генерирует выбор режима отметки пары: опрос всей группы... |
| [`get_single_student_select_kb`](#get_single_student_select_kb) | Function | L265–L280 | `InlineKeyboardMarkup` | Генерирует список студентов по два в ряд для точечной о... |
| [`get_student_mark_choice_kb`](#get_student_mark_choice_kb) | Function | L283–L298 | `InlineKeyboardMarkup` | Генерирует кнопки выбора статуса посещаемости для одног... |
| [`get_single_mark_confirmed_kb`](#get_single_mark_confirmed_kb) | Function | L301–L312 | `InlineKeyboardMarkup` | Генерирует кнопки после успешного обновления отметки ст... |
| [`format_single_student_card`](#format_single_student_card) | Function | L315–L324 | `str` | Формирует карточку студента для выбора нового статуса п... |
| [`format_single_update_confirm`](#format_single_update_confirm) | Function | L327–L336 | `str` | Формирует сообщение подтверждения изменения отметки сту... |
| [`format_partner_single_report`](#format_partner_single_report) | Function | L339–L350 | `str` | Формирует отчет напарнику о точечном изменении отметки ... |

---

## 3. Comprehensive Function Specifications

### `get_lesson_confirm_kb`
```python
def get_lesson_confirm_kb(lesson_num: int) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L21-L38`](../../bot/templates/admin/attendance.py#L21-L38)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует инлайн-клавиатуру подтверждения проведения пары.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import get_lesson_confirm_kb

# Execute call
result = get_lesson_confirm_kb(lesson_num=...)
```

---

### `get_student_poll_kb`
```python
def get_student_poll_kb(can_back: bool) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L41-L69`](../../bot/templates/admin/attendance.py#L41-L69)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует инлайн-клавиатуру выставления статуса студенту (П, О, У, Н).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `can_back` | `bool` | Yes | Parameter `can_back` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import get_student_poll_kb

# Execute call
result = get_student_poll_kb(can_back=...)
```

---

### `format_confirm_text`
```python
def format_confirm_text(lesson_num: int, title: str, teacher: str) -> str
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L72-L86`](../../bot/templates/admin/attendance.py#L72-L86)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует текст диалога подтверждения факта проведения занятия.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `teacher` | `str` | Yes | Parameter `teacher` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import format_confirm_text

# Execute call
result = format_confirm_text(lesson_num=..., title=..., teacher=...)
```

---

### `format_student_card`
```python
def format_student_card(session: AttendanceSession) -> str
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L89-L108`](../../bot/templates/admin/attendance.py#L89-L108)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует текст карточки текущего студента с прогресс-индикатором.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import format_student_card

# Execute call
result = format_student_card(session=...)
```

---

### `_format_absent_students`
```python
def _format_absent_students(session: AttendanceSession) -> str
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L111-L129`](../../bot/templates/admin/attendance.py#L111-L129)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует список отсутствовавших и опоздавших студентов с их отметками.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import _format_absent_students

# Execute call
result = _format_absent_students(session=...)
```

---

### `format_summary_text`
```python
def format_summary_text(session: AttendanceSession, stats: dict[str, int]) -> str
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L132-L151`](../../bot/templates/admin/attendance.py#L132-L151)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует итоговый текстовый отчет после успешной фиксации посещаемости.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |
| `stats` | `dict[str, int]` | Yes | Parameter `stats` of type `dict[str, int]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import format_summary_text

# Execute call
result = format_summary_text(session=..., stats=...)
```

---

### `format_partner_attendance_report`
```python
def format_partner_attendance_report(session: AttendanceSession, stats: dict[str, int], initiator_title: str) -> str
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L154-L171`](../../bot/templates/admin/attendance.py#L154-L171)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует уведомление о сохранении посещаемости для второго администратора.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `AttendanceSession` | Yes | Active domain session instance containing current student index and marks. |
| `stats` | `dict[str, int]` | Yes | Parameter `stats` of type `dict[str, int]`. |
| `initiator_title` | `str` | Yes | Parameter `initiator_title` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import format_partner_attendance_report

# Execute call
result = format_partner_attendance_report(session=..., stats=..., initiator_title=...)
```

---

### `format_partner_cancel_report`
```python
def format_partner_cancel_report(lesson_num: int | str, initiator_title: str) -> str
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L174-L188`](../../bot/templates/admin/attendance.py#L174-L188)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует уведомление об отмене занятия для второго администратора.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lesson_num` | `int | str` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `initiator_title` | `str` | Yes | Parameter `initiator_title` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import format_partner_cancel_report

# Execute call
result = format_partner_cancel_report(lesson_num=..., initiator_title=...)
```

---

### `get_days_select_kb`
```python
def get_days_select_kb() -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L191-L214`](../../bot/templates/admin/attendance.py#L191-L214)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует клавиатуру выбора учебного дня за последнюю неделю.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import get_days_select_kb

# Execute call
result = get_days_select_kb()
```

---

### `get_lesson_select_kb`
```python
def get_lesson_select_kb(lessons: list, chosen_date=None) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L217-L248`](../../bot/templates/admin/attendance.py#L217-L248)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует кнопки выбора пар для конкретного учебного дня.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lessons` | `list` | Yes | Parameter `lessons` of type `list`. |
| `chosen_date` | `Any` | Yes | Parameter `chosen_date` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import get_lesson_select_kb

# Execute call
result = get_lesson_select_kb(lessons=..., chosen_date=...)
```

---

### `get_lesson_mode_kb`
```python
def get_lesson_mode_kb(chosen_date: str, lesson_num: int) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L251-L262`](../../bot/templates/admin/attendance.py#L251-L262)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует выбор режима отметки пары: опрос всей группы или один студент.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chosen_date` | `str` | Yes | Parameter `chosen_date` of type `str`. |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import get_lesson_mode_kb

# Execute call
result = get_lesson_mode_kb(chosen_date=..., lesson_num=...)
```

---

### `get_single_student_select_kb`
```python
def get_single_student_select_kb( students: list[tuple[int, str]], saved_marks: dict[str, str], chosen_date: str, lesson_num: int, ) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L265-L280`](../../bot/templates/admin/attendance.py#L265-L280)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует список студентов по два в ряд для точечной отметки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `students` | `list[tuple[int, str]]` | Yes | Parameter `students` of type `list[tuple[int, str]]`. |
| `saved_marks` | `dict[str, str]` | Yes | Parameter `saved_marks` of type `dict[str, str]`. |
| `chosen_date` | `str` | Yes | Parameter `chosen_date` of type `str`. |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import get_single_student_select_kb

# Execute call
result = get_single_student_select_kb(students=..., saved_marks=..., chosen_date=...)
```

---

### `get_student_mark_choice_kb`
```python
def get_student_mark_choice_kb(chosen_date: str, lesson_num: int, row_idx: int) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L283-L298`](../../bot/templates/admin/attendance.py#L283-L298)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует кнопки выбора статуса посещаемости для одного студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chosen_date` | `str` | Yes | Parameter `chosen_date` of type `str`. |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `row_idx` | `int` | Yes | Parameter `row_idx` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import get_student_mark_choice_kb

# Execute call
result = get_student_mark_choice_kb(chosen_date=..., lesson_num=..., row_idx=...)
```

---

### `get_single_mark_confirmed_kb`
```python
def get_single_mark_confirmed_kb(chosen_date: str, lesson_num: int) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L301-L312`](../../bot/templates/admin/attendance.py#L301-L312)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует кнопки после успешного обновления отметки студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chosen_date` | `str` | Yes | Parameter `chosen_date` of type `str`. |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import get_single_mark_confirmed_kb

# Execute call
result = get_single_mark_confirmed_kb(chosen_date=..., lesson_num=...)
```

---

### `format_single_student_card`
```python
def format_single_student_card(fio: str, target_date: str, lesson_num: int, title: str, mark: str | None) -> str
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L315-L324`](../../bot/templates/admin/attendance.py#L315-L324)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует карточку студента для выбора нового статуса посещаемости.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `target_date` | `str` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `mark` | `str | None` | Yes | Attendance evaluation symbol assigned to the student. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import format_single_student_card

# Execute call
result = format_single_student_card(fio=..., target_date=..., lesson_num=...)
```

---

### `format_single_update_confirm`
```python
def format_single_update_confirm(fio: str, target_date: str, lesson_num: int, title: str, mark: str) -> str
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L327-L336`](../../bot/templates/admin/attendance.py#L327-L336)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует сообщение подтверждения изменения отметки студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `target_date` | `str` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `mark` | `str` | Yes | Attendance evaluation symbol assigned to the student. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import format_single_update_confirm

# Execute call
result = format_single_update_confirm(fio=..., target_date=..., lesson_num=...)
```

---

### `format_partner_single_report`
```python
def format_partner_single_report( fio: str, target_date: str, lesson_num: int, title: str, mark: str, initiator: str ) -> str
```

- **Source Reference**: [`bot/templates/admin/attendance.py#L339-L350`](../../bot/templates/admin/attendance.py#L339-L350)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует отчет напарнику о точечном изменении отметки студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `target_date` | `str` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `mark` | `str` | Yes | Attendance evaluation symbol assigned to the student. |
| `initiator` | `str` | Yes | Parameter `initiator` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.attendance import format_partner_single_report

# Execute call
result = format_partner_single_report(fio=..., target_date=..., lesson_num=...)
```

---
