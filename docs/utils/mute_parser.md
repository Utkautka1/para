# Component Reference: `utils/mute_parser.py`
> **File Path**: [`utils/mute_parser.py`](../../utils/mute_parser.py)
> **Subsystem**: `Ban Duration Parser`

## 1. Purpose
Утилита парсинга строк времени мута в секунды.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`parse_duration_to_seconds`](#parse_duration_to_seconds) | Function | L11–L25 | `int \| None` | Парсит текстовое выражение длительности ('5с', '10м', '... |

---

## 3. Comprehensive Function Specifications

### `parse_duration_to_seconds`
```python
def parse_duration_to_seconds(time_str: str) -> int | None
```

- **Source Reference**: [`utils/mute_parser.py#L11-L25`](../../utils/mute_parser.py#L11-L25)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Парсит текстовое выражение длительности ('5с', '10м', '2ч', '1д') в секунды.

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
from utils.mute_parser import parse_duration_to_seconds

# Execute call
result = parse_duration_to_seconds(time_str=...)
```

---
