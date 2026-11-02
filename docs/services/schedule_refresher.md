# Component Reference: `services/schedule_refresher.py`
> **File Path**: [`services/schedule_refresher.py`](../../services/schedule_refresher.py)
> **Subsystem**: `KTMU Timetable Engine`
> **Architecture Layer**: `Upstream Ingress & Harvester`
> **Concurrency Model**: `AsyncIO Non-blocking Scraper`
> **Persistence Backend**: `L1 RAM In-Memory (<10µs) + L2 Redis Snapshots`
> **Service Level Objective**: `< 5ms Cached Response / 500ms Upstream Harvest`

## 1. Purpose
Фоновый загрузчик расписания КТМУ — единственный процесс, который качает API.

### Component Architecture & Data Flow
```mermaid
graph TD
    A[User Request] --> B[services.schedule_parser]
    B -->|L1 Hit <10µs| C[In-Memory RAM Cache]
    B -->|L2 Hit <2ms| D[(Redis Snapshot Cache)]
    B -->|L1/L2 Miss| E[KTMU Remote College Portal]
```

---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_refresh_if_due`](#_refresh_if_due) | Function | L23–L38 | `float` | Запускает загрузку, если подошёл срок по таймеру или её... |
| [`schedule_refresh_loop`](#schedule_refresh_loop) | Function | L41–L62 | `None` | Бесконечный цикл фонового обновления снапшота расписани... |

---

## 3. Comprehensive Function Specifications

### `_refresh_if_due`
```python
async def _refresh_if_due(next_due: float) -> float
```

- **Source Reference**: [`services/schedule_refresher.py#L23-L38`](../../services/schedule_refresher.py#L23-L38)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `float`

#### Overview & Architectural Purpose
Запускает загрузку, если подошёл срок по таймеру или её запросили вручную.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `next_due` | `float` | Yes | Parameter `next_due` of type `float`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.schedule_refresher import _refresh_if_due

# Execute call
result = await _refresh_if_due(next_due=...)
```

---

### `schedule_refresh_loop`
```python
async def schedule_refresh_loop() -> None
```

- **Source Reference**: [`services/schedule_refresher.py#L41-L62`](../../services/schedule_refresher.py#L41-L62)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Бесконечный цикл фонового обновления снапшота расписания в Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.schedule_refresher import schedule_refresh_loop

# Execute call
result = await schedule_refresh_loop()
```

---
