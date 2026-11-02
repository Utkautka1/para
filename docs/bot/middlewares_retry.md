# Component Reference: `bot/middlewares/retry.py`
> **File Path**: [`bot/middlewares/retry.py`](../../bot/middlewares/retry.py)
> **Subsystem**: `Network Retry Middleware`

## 1. Purpose
Middleware для прозрачной обработки Telegram flood control (429 RetryAfter).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`RetryAfterMiddleware.__call__`](#retryaftermiddleware__call__) | Method | L24–L48 | `Any` | Исполняет хэндлер с автоматическим повтором при Telegra... |

---

## 3. Comprehensive Function Specifications

## Class Model: `RetryAfterMiddleware`

Перехватывает TelegramRetryAfter и повторяет запрос после паузы.

### `RetryAfterMiddleware.__call__`
```python
async def __call__( self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any], ) -> Any
```

- **Source Reference**: [`bot/middlewares/retry.py#L24-L48`](../../bot/middlewares/retry.py#L24-L48)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Исполняет хэндлер с автоматическим повтором при TelegramRetryAfter.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `handler` | `Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]` | Yes | Parameter `handler` of type `Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]`. |
| `event` | `TelegramObject` | Yes | Parameter `event` of type `TelegramObject`. |
| `data` | `dict[str, Any]` | Yes | Parameter `data` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from bot.middlewares.retry import __call__

# Execute call
result = await __call__(handler=..., event=..., data=...)
```

---
