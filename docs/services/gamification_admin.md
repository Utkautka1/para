# Component Reference: `services/gamification_admin.py`
> **File Path**: [`services/gamification_admin.py`](../../services/gamification_admin.py)
> **Subsystem**: `Gamification Admin Operations`

## 1. Purpose
Ручное управление геймификацией из админ-панели старосты.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`list_students`](#list_students) | Function | L51–L54 | `list[StudentProfile]` | Возвращает профили всех студентов журнала в алфавитном ... |
| [`_target_of`](#_target_of) | Function | L57–L62 | `StudentTarget` | Определяет ФИО-владельца и Telegram ID студента по реес... |
| [`get_student`](#get_student) | Function | L65–L72 | `StudentTarget \| None` | Находит студента по индексу в алфавитном списке. |
| [`get_bonuses`](#get_bonuses) | Function | L75–L79 | `tuple[int, int]` | Возвращает (бонус XP, бонус очков гильдии) студента. |
| [`_notify`](#_notify) | Function | L82–L85 | `None` | Сообщает студенту об изменении, если у него привязан Te... |
| [`format_bonus_notification`](#format_bonus_notification) | Function | L88–L91 | `str` | Текст уведомления студенту о ручном начислении или спис... |
| [`adjust_bonus`](#adjust_bonus) | Function | L94–L105 | `int` | Прибавляет к бонусу студента delta (отрицательная — спи... |
| [`bonus_for_total`](#bonus_for_total) | Function | L108–L118 | `int` | Считает бонус, при котором у студента будет ровно total... |
| [`set_total`](#set_total) | Function | L121–L135 | `int` | Выставляет студенту ровно total XP или очков гильдии и ... |
| [`reset_bonuses`](#reset_bonuses) | Function | L138–L144 | `None` | Обнуляет оба бонуса студента и уведомляет его. |
| [`toggle_achievement`](#toggle_achievement) | Function | L147–L165 | `bool` | Выдаёт ачивку, если её нет, или снимает, если есть, и у... |

---

## 3. Comprehensive Function Specifications

## Class Model: `StudentTarget`

Студент, которым управляет староста.

### `list_students`
```python
async def list_students() -> list[StudentProfile]
```

- **Source Reference**: [`services/gamification_admin.py#L51-L54`](../../services/gamification_admin.py#L51-L54)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[StudentProfile]`

#### Overview & Architectural Purpose
Возвращает профили всех студентов журнала в алфавитном порядке.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import list_students

# Execute call
result = await list_students()
```

---

### `_target_of`
```python
def _target_of(profile: StudentProfile) -> StudentTarget
```

- **Source Reference**: [`services/gamification_admin.py#L57-L62`](../../services/gamification_admin.py#L57-L62)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `StudentTarget`

#### Overview & Architectural Purpose
Определяет ФИО-владельца и Telegram ID студента по реестру одногруппников.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `profile` | `StudentProfile` | Yes | Parameter `profile` of type `StudentProfile`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import _target_of

# Execute call
result = _target_of(profile=...)
```

---

### `get_student`
```python
async def get_student(index: int) -> StudentTarget | None
```

- **Source Reference**: [`services/gamification_admin.py#L65-L72`](../../services/gamification_admin.py#L65-L72)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `StudentTarget | None`

#### Overview & Architectural Purpose
Находит студента по индексу в алфавитном списке.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `index` | `int` | Yes | Parameter `index` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import get_student

# Execute call
result = await get_student(index=...)
```

---

### `get_bonuses`
```python
async def get_bonuses(target: StudentTarget) -> tuple[int, int]
```

- **Source Reference**: [`services/gamification_admin.py#L75-L79`](../../services/gamification_admin.py#L75-L79)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[int, int]`

#### Overview & Architectural Purpose
Возвращает (бонус XP, бонус очков гильдии) студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target` | `StudentTarget` | Yes | Parameter `target` of type `StudentTarget`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import get_bonuses

# Execute call
result = await get_bonuses(target=...)
```

---

### `_notify`
```python
async def _notify(bot: Any, target: StudentTarget, text: str) -> None
```

- **Source Reference**: [`services/gamification_admin.py#L82-L85`](../../services/gamification_admin.py#L82-L85)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сообщает студенту об изменении, если у него привязан Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `target` | `StudentTarget` | Yes | Parameter `target` of type `StudentTarget`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import _notify

# Execute call
result = await _notify(bot=..., target=..., text=...)
```

---

### `format_bonus_notification`
```python
def format_bonus_notification(label: str, delta: int) -> str
```

- **Source Reference**: [`services/gamification_admin.py#L88-L91`](../../services/gamification_admin.py#L88-L91)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Текст уведомления студенту о ручном начислении или списании.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `label` | `str` | Yes | Parameter `label` of type `str`. |
| `delta` | `int` | Yes | Parameter `delta` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import format_bonus_notification

# Execute call
result = format_bonus_notification(label=..., delta=...)
```

---

### `adjust_bonus`
```python
async def adjust_bonus(bot: Any, target: StudentTarget, kind: str, delta: int) -> int
```

- **Source Reference**: [`services/gamification_admin.py#L94-L105`](../../services/gamification_admin.py#L94-L105)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Прибавляет к бонусу студента delta (отрицательная — списание) и уведомляет его.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `target` | `StudentTarget` | Yes | Parameter `target` of type `StudentTarget`. |
| `kind` | `str` | Yes | Parameter `kind` of type `str`. |
| `delta` | `int` | Yes | Parameter `delta` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import adjust_bonus

# Execute call
result = await adjust_bonus(bot=..., target=..., kind=...)
```

---

### `bonus_for_total`
```python
def bonus_for_total(target: StudentTarget, kind: str, total: int, bonuses: tuple[int, int]) -> int
```

- **Source Reference**: [`services/gamification_admin.py#L108-L118`](../../services/gamification_admin.py#L108-L118)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Считает бонус, при котором у студента будет ровно total XP или очков гильдии.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target` | `StudentTarget` | Yes | Parameter `target` of type `StudentTarget`. |
| `kind` | `str` | Yes | Parameter `kind` of type `str`. |
| `total` | `int` | Yes | Parameter `total` of type `int`. |
| `bonuses` | `tuple[int, int]` | Yes | Parameter `bonuses` of type `tuple[int, int]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import bonus_for_total

# Execute call
result = bonus_for_total(target=..., kind=..., total=...)
```

---

### `set_total`
```python
async def set_total(bot: Any, target: StudentTarget, kind: str, total: int) -> int
```

- **Source Reference**: [`services/gamification_admin.py#L121-L135`](../../services/gamification_admin.py#L121-L135)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Выставляет студенту ровно total XP или очков гильдии и уведомляет его.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `target` | `StudentTarget` | Yes | Parameter `target` of type `StudentTarget`. |
| `kind` | `str` | Yes | Parameter `kind` of type `str`. |
| `total` | `int` | Yes | Parameter `total` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import set_total

# Execute call
result = await set_total(bot=..., target=..., kind=...)
```

---

### `reset_bonuses`
```python
async def reset_bonuses(bot: Any, target: StudentTarget) -> None
```

- **Source Reference**: [`services/gamification_admin.py#L138-L144`](../../services/gamification_admin.py#L138-L144)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Обнуляет оба бонуса студента и уведомляет его.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `target` | `StudentTarget` | Yes | Parameter `target` of type `StudentTarget`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import reset_bonuses

# Execute call
result = await reset_bonuses(bot=..., target=...)
```

---

### `toggle_achievement`
```python
async def toggle_achievement(bot: Any, target: StudentTarget, achievement_id: str) -> bool
```

- **Source Reference**: [`services/gamification_admin.py#L147-L165`](../../services/gamification_admin.py#L147-L165)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Выдаёт ачивку, если её нет, или снимает, если есть, и уведомляет студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `target` | `StudentTarget` | Yes | Parameter `target` of type `StudentTarget`. |
| `achievement_id` | `str` | Yes | Unique identifier of academic milestone achievement. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification_admin import toggle_achievement

# Execute call
result = await toggle_achievement(bot=..., target=..., achievement_id=...)
```

---
