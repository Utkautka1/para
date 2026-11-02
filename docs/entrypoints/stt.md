# Component Reference: `stt.py`
> **File Path**: [`stt.py`](../../stt.py)
> **Subsystem**: `Speech-to-Text Queue Consumer`

## 1. Purpose
Точка входа микросервиса распознавания речи (para-stt).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_warmup_model`](#_warmup_model) | Function | L21–L33 | `None` | Загружает модель в память GPU до первого задания. |
| [`main`](#main) | Function | L36–L53 | `None` | Инициализирует Redis и модель, затем бесконечно обрабат... |

---

## 3. Comprehensive Function Specifications

### `_warmup_model`
```python
async def _warmup_model() -> None
```

- **Source Reference**: [`stt.py#L21-L33`](../../stt.py#L21-L33)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Загружает модель в память GPU до первого задания.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from stt import _warmup_model

# Execute call
result = await _warmup_model()
```

---

### `main`
```python
async def main() -> None
```

- **Source Reference**: [`stt.py#L36-L53`](../../stt.py#L36-L53)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Инициализирует Redis и модель, затем бесконечно обрабатывает очередь распознавания.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from stt import main

# Execute call
result = await main()
```

---
