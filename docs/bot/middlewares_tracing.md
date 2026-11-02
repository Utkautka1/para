# Component Reference: `bot/middlewares/tracing.py`
> **File Path**: [`bot/middlewares/tracing.py`](../../bot/middlewares/tracing.py)
> **Subsystem**: `Telemetry Tracing Middleware`

## 1. Purpose
Middleware распределенного трейсинга OpenTelemetry для входящих событий Telegram.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_extract_callback_attrs`](#_extract_callback_attrs) | Function | L21–L35 | `tuple[str, dict[str, Any]]` | Формирует имя спана и словарь телеметрии для нажатия ин... |
| [`_extract_message_attrs`](#_extract_message_attrs) | Function | L38–L52 | `tuple[str, dict[str, Any]]` | Формирует имя спана и словарь телеметрии для входящего ... |
| [`TracingMiddleware.__call__`](#tracingmiddleware__call__) | Method | L58–L73 | `Any` | Перехватывает событие Telegram и оборачивает вызов хэнд... |

---

## 3. Comprehensive Function Specifications

### `_extract_callback_attrs`
```python
def _extract_callback_attrs(query: CallbackQuery) -> tuple[str, dict[str, Any]]
```

- **Source Reference**: [`bot/middlewares/tracing.py#L21-L35`](../../bot/middlewares/tracing.py#L21-L35)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, dict[str, Any]]`

#### Overview & Architectural Purpose
Формирует имя спана и словарь телеметрии для нажатия инлайн-кнопки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | `CallbackQuery` | Yes | Parameter `query` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.middlewares.tracing import _extract_callback_attrs

# Execute call
result = _extract_callback_attrs(query=...)
```

---

### `_extract_message_attrs`
```python
def _extract_message_attrs(message: Message) -> tuple[str, dict[str, Any]]
```

- **Source Reference**: [`bot/middlewares/tracing.py#L38-L52`](../../bot/middlewares/tracing.py#L38-L52)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, dict[str, Any]]`

#### Overview & Architectural Purpose
Формирует имя спана и словарь телеметрии для входящего сообщения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.middlewares.tracing import _extract_message_attrs

# Execute call
result = _extract_message_attrs(message=...)
```

---

## Class Model: `TracingMiddleware`

Сквозной трейсинг событий бота: создает родительский спан и передает trace_id.

### `TracingMiddleware.__call__`
```python
async def __call__( self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any], ) -> Any
```

- **Source Reference**: [`bot/middlewares/tracing.py#L58-L73`](../../bot/middlewares/tracing.py#L58-L73)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Перехватывает событие Telegram и оборачивает вызов хэндлера в спан.

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
from bot.middlewares.tracing import __call__

# Execute call
result = await __call__(handler=..., event=..., data=...)
```

---
