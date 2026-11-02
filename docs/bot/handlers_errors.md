# Component Reference: `bot/handlers/errors.py`
> **File Path**: [`bot/handlers/errors.py`](../../bot/handlers/errors.py)
> **Subsystem**: `Global Error Trapper`

## 1. Purpose
Глобальный обработчик необработанных исключений диспетчера aiogram.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_notify_callback_error`](#_notify_callback_error) | Function | L22–L35 | `None` | Отправляет всплывающее alert-уведомление при сбое внутр... |
| [`_notify_message_error`](#_notify_message_error) | Function | L38–L51 | `None` | Отправляет текстовое сообщение пользователю при сбое вн... |
| [`_dispatch_error_alert`](#_dispatch_error_alert) | Function | L54–L66 | `None` | Асинхронно отправляет алерт о сбое хэндлера в Fatal топ... |
| [`_is_stale_callback`](#_is_stale_callback) | Function | L69–L76 | `bool` | Проверяет, что Telegram отверг ответ на устаревшее нажа... |
| [`global_error_handler`](#global_error_handler) | Function | L80–L102 | `bool` | Перехватывает любые непредвиденные исключения в жизненн... |

---

## 3. Comprehensive Function Specifications

### `_notify_callback_error`
```python
async def _notify_callback_error(cb) -> None
```

- **Source Reference**: [`bot/handlers/errors.py#L22-L35`](../../bot/handlers/errors.py#L22-L35)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет всплывающее alert-уведомление при сбое внутри CallbackQuery.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb` | `Any` | Yes | Parameter `cb` of type `Any`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.errors import _notify_callback_error

# Execute call
result = await _notify_callback_error(cb=...)
```

---

### `_notify_message_error`
```python
async def _notify_message_error(msg) -> None
```

- **Source Reference**: [`bot/handlers/errors.py#L38-L51`](../../bot/handlers/errors.py#L38-L51)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет текстовое сообщение пользователю при сбое внутри Message хэндлера.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg` | `Any` | Yes | Parameter `msg` of type `Any`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.errors import _notify_message_error

# Execute call
result = await _notify_message_error(msg=...)
```

---

### `_dispatch_error_alert`
```python
async def _dispatch_error_alert(exc: Exception) -> None
```

- **Source Reference**: [`bot/handlers/errors.py#L54-L66`](../../bot/handlers/errors.py#L54-L66)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Асинхронно отправляет алерт о сбое хэндлера в Fatal топик.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `exc` | `Exception` | Yes | Parameter `exc` of type `Exception`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.errors import _dispatch_error_alert

# Execute call
result = await _dispatch_error_alert(exc=...)
```

---

### `_is_stale_callback`
```python
def _is_stale_callback(exc: Exception) -> bool
```

- **Source Reference**: [`bot/handlers/errors.py#L69-L76`](../../bot/handlers/errors.py#L69-L76)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, что Telegram отверг ответ на устаревшее нажатие кнопки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `exc` | `Exception` | Yes | Parameter `exc` of type `Exception`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.errors import _is_stale_callback

# Execute call
result = _is_stale_callback(exc=...)
```

---

### `global_error_handler`
```python
async def global_error_handler(event: ErrorEvent) -> bool
```

- **Source Reference**: [`bot/handlers/errors.py#L80-L102`](../../bot/handlers/errors.py#L80-L102)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Перехватывает любые непредвиденные исключения в жизненном цикле aiogram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `event` | `ErrorEvent` | Yes | Parameter `event` of type `ErrorEvent`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.errors import global_error_handler

# Execute call
result = await global_error_handler(event=...)
```

---
