# Component Reference: `services/achievement_sync.py`
> **File Path**: [`services/achievement_sync.py`](../../services/achievement_sync.py)
> **Subsystem**: `Achievement Sync`

## 1. Purpose
Фоновая выдача ачивок по журналу посещаемости и рейтингу (крутится в worker).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_is_birthday_today`](#_is_birthday_today) | Function | L55–L58 | `bool` | Проверяет по календарю группы, что у студента сегодня (... |
| [`_delta_stats`](#_delta_stats) | Function | L61–L66 | `dict[str, StudentStat]` | Строит срезы журнала после точки отсчёта для всех студе... |
| [`_group_context`](#_group_context) | Function | L69–L81 | `tuple[dict[str, int], float]` | Считает места в рейтинге (без старосты) и пульс группы ... |
| [`compute_new_achievements`](#compute_new_achievements) | Function | L84–L96 | `set[str]` | Определяет ачивки, которые студент заработал, но ещё не... |
| [`_grant_to_student`](#_grant_to_student) | Function | L99–L118 | `int` | Сохраняет новые ачивки студента и отправляет сводку в Л... |
| [`sync_stat_achievements`](#sync_stat_achievements) | Function | L121–L142 | `int` | Один проход выдачи журнальных и мета-ачивок всей группе... |
| [`achievement_sync_loop`](#achievement_sync_loop) | Function | L145–L159 | `None` | Бесконечный цикл фоновой выдачи ачивок в worker. |

---

## 3. Comprehensive Function Specifications

### `_is_birthday_today`
```python
def _is_birthday_today(classmate: dict[str, Any] | None) -> bool
```

- **Source Reference**: [`services/achievement_sync.py#L55-L58`](../../services/achievement_sync.py#L55-L58)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет по календарю группы, что у студента сегодня (МСК) день рождения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `classmate` | `dict[str, Any] | None` | Yes | Parameter `classmate` of type `dict[str, Any] | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_sync import _is_birthday_today

# Execute call
result = _is_birthday_today(classmate=...)
```

---

### `_delta_stats`
```python
def _delta_stats(stats: dict[str, dict[str, Any]], baselines: dict[str, dict[str, Any]]) -> dict[str, StudentStat]
```

- **Source Reference**: [`services/achievement_sync.py#L61-L66`](../../services/achievement_sync.py#L61-L66)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, StudentStat]`

#### Overview & Architectural Purpose
Строит срезы журнала после точки отсчёта для всех студентов.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `stats` | `dict[str, dict[str, Any]]` | Yes | Parameter `stats` of type `dict[str, dict[str, Any]]`. |
| `baselines` | `dict[str, dict[str, Any]]` | Yes | Parameter `baselines` of type `dict[str, dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_sync import _delta_stats

# Execute call
result = _delta_stats(stats=..., baselines=...)
```

---

### `_group_context`
```python
def _group_context(board: list[StudentProfile], deltas: dict[str, StudentStat]) -> tuple[dict[str, int], float]
```

- **Source Reference**: [`services/achievement_sync.py#L69-L81`](../../services/achievement_sync.py#L69-L81)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[dict[str, int], float]`

#### Overview & Architectural Purpose
Считает места в рейтинге (без старосты) и пульс группы после точки отсчёта.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `board` | `list[StudentProfile]` | Yes | Parameter `board` of type `list[StudentProfile]`. |
| `deltas` | `dict[str, StudentStat]` | Yes | Parameter `deltas` of type `dict[str, StudentStat]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_sync import _group_context

# Execute call
result = _group_context(board=..., deltas=...)
```

---

### `compute_new_achievements`
```python
def compute_new_achievements( profile: StudentProfile, stat: StudentStat, places: dict[str, int], pulse: float ) -> set[str]
```

- **Source Reference**: [`services/achievement_sync.py#L84-L96`](../../services/achievement_sync.py#L84-L96)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `set[str]`

#### Overview & Architectural Purpose
Определяет ачивки, которые студент заработал, но ещё не получил.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `profile` | `StudentProfile` | Yes | Parameter `profile` of type `StudentProfile`. |
| `stat` | `StudentStat` | Yes | Parameter `stat` of type `StudentStat`. |
| `places` | `dict[str, int]` | Yes | Parameter `places` of type `dict[str, int]`. |
| `pulse` | `float` | Yes | Parameter `pulse` of type `float`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_sync import compute_new_achievements

# Execute call
result = compute_new_achievements(profile=..., stat=..., places=...)
```

---

### `_grant_to_student`
```python
async def _grant_to_student(bot: Any, fio: str, new_ids: set[str]) -> int
```

- **Source Reference**: [`services/achievement_sync.py#L99-L118`](../../services/achievement_sync.py#L99-L118)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Сохраняет новые ачивки студента и отправляет сводку в ЛС, если известен tg_id.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `new_ids` | `set[str]` | Yes | Parameter `new_ids` of type `set[str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_sync import _grant_to_student

# Execute call
result = await _grant_to_student(bot=..., fio=..., new_ids=...)
```

---

### `sync_stat_achievements`
```python
async def sync_stat_achievements(bot: Any) -> int
```

- **Source Reference**: [`services/achievement_sync.py#L121-L142`](../../services/achievement_sync.py#L121-L142)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Один проход выдачи журнальных и мета-ачивок всей группе.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_sync import sync_stat_achievements

# Execute call
result = await sync_stat_achievements(bot=...)
```

---

### `achievement_sync_loop`
```python
async def achievement_sync_loop(bot: Any) -> None
```

- **Source Reference**: [`services/achievement_sync.py#L145-L159`](../../services/achievement_sync.py#L145-L159)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Бесконечный цикл фоновой выдачи ачивок в worker.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.achievement_sync import achievement_sync_loop

# Execute call
result = await achievement_sync_loop(bot=...)
```

---
