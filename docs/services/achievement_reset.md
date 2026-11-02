# Component Reference: `services/achievement_reset.py`
> **File Path**: [`services/achievement_reset.py`](../../services/achievement_reset.py)
> **Subsystem**: `Achievement Reset`

## 1. Purpose
Разовый сброс ачивок группы с новой точкой отсчёта журнала.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_backup_database`](#_backup_database) | Function | L28–L39 | `str \| None` | Сохраняет копию SQLite перед удалением ачивок. |
| [`reset_achievements`](#reset_achievements) | Function | L42–L68 | `bool` | Обнуляет ачивки и счётчики группы и ставит точку отсчёт... |
| [`_run`](#_run) | Function | L71–L79 | `bool` | Поднимает Redis, выполняет сброс и закрывает соединения... |
| [`main`](#main) | Function | L82–L91 | `int` | Требует явный --confirm: команда необратимо удаляет ачи... |

---

## 3. Comprehensive Function Specifications

### `_backup_database`
```python
async def _backup_database() -> str | None
```

- **Source Reference**: [`services/achievement_reset.py#L28-L39`](../../services/achievement_reset.py#L28-L39)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Сохраняет копию SQLite перед удалением ачивок.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_reset import _backup_database

# Execute call
result = await _backup_database()
```

---

### `reset_achievements`
```python
async def reset_achievements() -> bool
```

- **Source Reference**: [`services/achievement_reset.py#L42-L68`](../../services/achievement_reset.py#L42-L68)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Обнуляет ачивки и счётчики группы и ставит точку отсчёта по текущему журналу.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_reset import reset_achievements

# Execute call
result = await reset_achievements()
```

---

### `_run`
```python
async def _run() -> bool
```

- **Source Reference**: [`services/achievement_reset.py#L71-L79`](../../services/achievement_reset.py#L71-L79)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Поднимает Redis, выполняет сброс и закрывает соединения короткого процесса.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.achievement_reset import _run

# Execute call
result = await _run()
```

---

### `main`
```python
def main(argv: list[str]) -> int
```

- **Source Reference**: [`services/achievement_reset.py#L82-L91`](../../services/achievement_reset.py#L82-L91)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Требует явный --confirm: команда необратимо удаляет ачивки всей группы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `argv` | `list[str]` | Yes | Parameter `argv` of type `list[str]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_reset import main

# Execute call
result = main(argv=...)
```

---
