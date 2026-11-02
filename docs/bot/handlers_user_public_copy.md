# Component Reference: `bot/handlers/user/public_copy.py`
> **File Path**: [`bot/handlers/user/public_copy.py`](../../bot/handlers/user/public_copy.py)
> **Subsystem**: `Public Sharing Flow`

## 1. Purpose
Отдельный публичный роутер для копирования Zoom-реквизитов участниками топика.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`cb_public_copy_value`](#cb_public_copy_value) | Function | L19–L33 | `None` | Отображает всплывающее окно с реквизитами конференции Z... |

---

## 3. Comprehensive Function Specifications

### `cb_public_copy_value`
```python
async def cb_public_copy_value(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/user/public_copy.py#L19-L33`](../../bot/handlers/user/public_copy.py#L19-L33)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает всплывающее окно с реквизитами конференции Zoom для копирования.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.public_copy import cb_public_copy_value

# Execute call
result = await cb_public_copy_value(callback=...)
```

---
