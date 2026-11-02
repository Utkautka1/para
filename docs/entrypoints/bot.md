# Component Reference: `bot.py`
> **File Path**: [`bot.py`](../../bot.py)
> **Subsystem**: `Telegram Gateway`
> **Architecture Layer**: `Event Gateway & Bot Dispatcher`
> **Concurrency Model**: `Long-Polling Aiogram 3.4 Worker Mesh`
> **Persistence Backend**: `RedisStorage FSM State Engine`
> **Service Level Objective**: `Sub-100ms Telegram Message Ingress`

## 1. Purpose
Главный модуль запуска Telegram-бота расписания КТМУ.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_register_admin_routers`](#_register_admin_routers) | Function | L21–L43 | `None` | Регистрирует административные роутеры в диспетчере aiog... |
| [`_register_user_routers`](#_register_user_routers) | Function | L46–L70 | `None` | Регистрирует пользовательские роутеры в диспетчере aiog... |
| [`register_all_routers`](#register_all_routers) | Function | L73–L87 | `None` | Регистрирует все группы роутеров и обработчик ошибок в ... |
| [`shutdown_bot`](#shutdown_bot) | Function | L90–L109 | `None` | Корректно закрывает сессию бота, HTTP-клиент API и подк... |
| [`setup_all_middlewares`](#setup_all_middlewares) | Function | L112–L135 | `None` | Регистрирует глобальные middleware для отказоустойчивос... |
| [`_init_bot_subsystems`](#_init_bot_subsystems) | Function | L138–L157 | `None` | Инициализирует роутеры, middleware и соединения (модель... |
| [`main`](#main) | Function | L160–L180 | `None` | Основная асинхронная функция запуска long polling Teleg... |

---

## 3. Comprehensive Function Specifications

### `_register_admin_routers`
```python
def _register_admin_routers() -> None
```

- **Source Reference**: [`bot.py#L21-L43`](../../bot.py#L21-L43)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Регистрирует административные роутеры в диспетчере aiogram.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot import _register_admin_routers

# Execute call
result = _register_admin_routers()
```

---

### `_register_user_routers`
```python
def _register_user_routers() -> None
```

- **Source Reference**: [`bot.py#L46-L70`](../../bot.py#L46-L70)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Регистрирует пользовательские роутеры в диспетчере aiogram.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot import _register_user_routers

# Execute call
result = _register_user_routers()
```

---

### `register_all_routers`
```python
def register_all_routers() -> None
```

- **Source Reference**: [`bot.py#L73-L87`](../../bot.py#L73-L87)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Регистрирует все группы роутеров и обработчик ошибок в диспетчере.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot import register_all_routers

# Execute call
result = register_all_routers()
```

---

### `shutdown_bot`
```python
async def shutdown_bot() -> None
```

- **Source Reference**: [`bot.py#L90-L109`](../../bot.py#L90-L109)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Корректно закрывает сессию бота, HTTP-клиент API и подключение к Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot import shutdown_bot

# Execute call
result = await shutdown_bot()
```

---

### `setup_all_middlewares`
```python
def setup_all_middlewares() -> None
```

- **Source Reference**: [`bot.py#L112-L135`](../../bot.py#L112-L135)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Регистрирует глобальные middleware для отказоустойчивости бота.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot import setup_all_middlewares

# Execute call
result = setup_all_middlewares()
```

---

### `_init_bot_subsystems`
```python
async def _init_bot_subsystems() -> None
```

- **Source Reference**: [`bot.py#L138-L157`](../../bot.py#L138-L157)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Инициализирует роутеры, middleware и соединения (модель STT живёт в сервисе stt).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot import _init_bot_subsystems

# Execute call
result = await _init_bot_subsystems()
```

---

### `main`
```python
async def main() -> None
```

- **Source Reference**: [`bot.py#L160-L180`](../../bot.py#L160-L180)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Основная асинхронная функция запуска long polling Telegram-бота.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot import main

# Execute call
result = await main()
```

---
