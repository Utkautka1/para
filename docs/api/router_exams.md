# Component Reference: `api/router/exams.py`
> **File Path**: [`api/router/exams.py`](../../api/router/exams.py)
> **Subsystem**: `Exams API`

## 1. Purpose
Роутер экзаменов — GET /exams, GET /exams/upcoming, POST /exams/refresh.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`list_exams`](#list_exams) | Function | L23–L35 | `ExamsResponse` | Возвращает полный реестр экзаменов и зачётов текущего с... |
| [`_resolve_current_week`](#_resolve_current_week) | Function | L38–L52 | `int` | Вычисляет номер текущей учебной недели семестра. |
| [`upcoming_exams`](#upcoming_exams) | Function | L56–L72 | `UpcomingExamsResponse` | Возвращает список ближайших контрольных мероприятий на ... |
| [`refresh_exams`](#refresh_exams) | Function | L76–L89 | `ExamsRefreshResponse` | Выполняет принудительное обновление расписания экзамено... |

---

## 3. Comprehensive Function Specifications

### `list_exams`
```python
async def list_exams() -> ExamsResponse
```

- **Source Reference**: [`api/router/exams.py#L23-L35`](../../api/router/exams.py#L23-L35)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `ExamsResponse`

#### Overview & Architectural Purpose
Возвращает полный реестр экзаменов и зачётов текущего семестра.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.exams import list_exams

# Execute call
result = await list_exams()
```

---

### `_resolve_current_week`
```python
async def _resolve_current_week() -> int
```

- **Source Reference**: [`api/router/exams.py#L38-L52`](../../api/router/exams.py#L38-L52)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Вычисляет номер текущей учебной недели семестра.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.exams import _resolve_current_week

# Execute call
result = await _resolve_current_week()
```

---

### `upcoming_exams`
```python
async def upcoming_exams( weeks_ahead: int = Query(default=4, ge=1, le=20, description="Planning horizon (weeks)"), ) -> UpcomingExamsResponse
```

- **Source Reference**: [`api/router/exams.py#L56-L72`](../../api/router/exams.py#L56-L72)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `UpcomingExamsResponse`

#### Overview & Architectural Purpose
Возвращает список ближайших контрольных мероприятий на N недель вперёд.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `weeks_ahead` | `int` | Yes | Parameter `weeks_ahead` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.exams import upcoming_exams

# Execute call
result = await upcoming_exams(weeks_ahead=...)
```

---

### `refresh_exams`
```python
async def refresh_exams() -> ExamsRefreshResponse
```

- **Source Reference**: [`api/router/exams.py#L76-L89`](../../api/router/exams.py#L76-L89)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `ExamsRefreshResponse`

#### Overview & Architectural Purpose
Выполняет принудительное обновление расписания экзаменов из API колледжа.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.exams import refresh_exams

# Execute call
result = await refresh_exams()
```

---
