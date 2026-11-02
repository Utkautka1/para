# Component Reference: `bot/middlewares/throttling.py`
> **File Path**: [`bot/middlewares/throttling.py`](../../bot/middlewares/throttling.py)
> **Subsystem**: `Throttling Middleware`

## 1. Purpose
Middleware для защиты от частого нажатия инлайн-кнопок (Debounce / Throttling).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_determine_cooldown`](#_determine_cooldown) | Function | L30–L46 | `float` | Определяет необходимый интервал кулдауна по префиксу ca... |
| [`CallbackThrottleMiddleware.__init__`](#callbackthrottlemiddleware__init__) | Method | L52–L60 | `None` | Инициализирует локальное состояние трекинга времени кли... |
| [`CallbackThrottleMiddleware._cleanup_old_entries`](#callbackthrottlemiddleware_cleanup_old_entries) | Method | L62–L74 | `None` | Очищает устаревшие записи, предотвращая утечку оператив... |
| [`CallbackThrottleMiddleware._handle_callback_throttle`](#callbackthrottlemiddleware_handle_callback_throttle) | Method | L76–L100 | `bool` | Проверяет интервал времени между кликами и отправляет в... |
| [`CallbackThrottleMiddleware.__call__`](#callbackthrottlemiddleware__call__) | Method | L102–L120 | `Any` | Перехватывает входящие события и отсекает частые нажати... |

---

## 3. Comprehensive Function Specifications

### `_determine_cooldown`
```python
def _determine_cooldown(cb_data: str) -> float
```

- **Source Reference**: [`bot/middlewares/throttling.py#L30-L46`](../../bot/middlewares/throttling.py#L30-L46)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `float`

#### Overview & Architectural Purpose
Определяет необходимый интервал кулдауна по префиксу callback_data.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cb_data` | `str` | Yes | Parameter `cb_data` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.middlewares.throttling import _determine_cooldown

# Execute call
result = _determine_cooldown(cb_data=...)
```

---

## Class Model: `CallbackThrottleMiddleware`

Предотвращает спам-клики по инлайн-кнопкам бота.

### `CallbackThrottleMiddleware.__init__`
```python
def __init__(self) -> None
```

- **Source Reference**: [`bot/middlewares/throttling.py#L52-L60`](../../bot/middlewares/throttling.py#L52-L60)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Инициализирует локальное состояние трекинга времени кликов.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.middlewares.throttling import __init__

# Execute call
result = __init__()
```

---

### `CallbackThrottleMiddleware._cleanup_old_entries`
```python
def _cleanup_old_entries(self, now: float) -> None
```

- **Source Reference**: [`bot/middlewares/throttling.py#L62-L74`](../../bot/middlewares/throttling.py#L62-L74)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Очищает устаревшие записи, предотвращая утечку оперативной памяти.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now` | `float` | Yes | Parameter `now` of type `float`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.middlewares.throttling import _cleanup_old_entries

# Execute call
result = _cleanup_old_entries(now=...)
```

---

### `CallbackThrottleMiddleware._handle_callback_throttle`
```python
async def _handle_callback_throttle(self, event: CallbackQuery, now: float) -> bool
```

- **Source Reference**: [`bot/middlewares/throttling.py#L76-L100`](../../bot/middlewares/throttling.py#L76-L100)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет интервал времени между кликами и отправляет всплывающее предупреждение.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `event` | `CallbackQuery` | Yes | Parameter `event` of type `CallbackQuery`. |
| `now` | `float` | Yes | Parameter `now` of type `float`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.middlewares.throttling import _handle_callback_throttle

# Execute call
result = await _handle_callback_throttle(event=..., now=...)
```

---

### `CallbackThrottleMiddleware.__call__`
```python
async def __call__( self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any], ) -> Any
```

- **Source Reference**: [`bot/middlewares/throttling.py#L102-L120`](../../bot/middlewares/throttling.py#L102-L120)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Перехватывает входящие события и отсекает частые нажатия инлайн-кнопок.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `handler` | `Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]` | Yes | Parameter `handler` of type `Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]`. |
| `event` | `TelegramObject` | Yes | Parameter `event` of type `TelegramObject`. |
| `data` | `dict[str, Any]` | Yes | Parameter `data` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.middlewares.throttling import __call__

# Execute call
result = await __call__(handler=..., event=..., data=...)
```

---
