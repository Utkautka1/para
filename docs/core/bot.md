# Component Reference: `core/bot.py`
> **File Path**: [`core/bot.py`](../../core/bot.py)
> **Subsystem**: `Bot Instance Singleton`

## 1. Purpose
Инициализация aiogram Bot и Dispatcher.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`create_bot_session`](#create_bot_session) | Function | L19–L31 | `AiohttpSession` | Создает сессию сетевого взаимодействия aiohttp для Tele... |
| [`create_fsm_storage`](#create_fsm_storage) | Function | L34–L58 | `Any` | Создает постоянное хранилище состояний FSM диалогов на ... |

---

## 3. Comprehensive Function Specifications

### `create_bot_session`
```python
def create_bot_session() -> AiohttpSession
```

- **Source Reference**: [`core/bot.py#L19-L31`](../../core/bot.py#L19-L31)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `AiohttpSession`

#### Overview & Architectural Purpose
Создает сессию сетевого взаимодействия aiohttp для Telegram Bot API.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.bot import create_bot_session

# Execute call
result = create_bot_session()
```

---

### `create_fsm_storage`
```python
def create_fsm_storage()
```

- **Source Reference**: [`core/bot.py#L34-L58`](../../core/bot.py#L34-L58)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Создает постоянное хранилище состояний FSM диалогов на базе Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.bot import create_fsm_storage

# Execute call
result = create_fsm_storage()
```

---
