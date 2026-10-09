# Module Specification: `bot/middlewares/retry.py`
> **Path**: [`bot/middlewares/retry.py`](file:///home/u/Рабочий стол/para/bot/middlewares/retry.py)  
> **Subsystem**: `Network Retry Middleware`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Middleware для прозрачной обработки Telegram flood control (429 RetryAfter). При получении исключения TelegramRetryAfter приостанавливает выполнение на указанный интервал retry_after и повторяет вызов хэндлера.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`RetryAfterMiddleware.__call__`](#retryaftermiddleware__call__) | Method | L24–L39 | `Any` | Исполняет хэндлер с retry при временном flood control. |

---

## 3. Exhaustive Function Specifications

## Class: `RetryAfterMiddleware`
Перехватывает TelegramRetryAfter и повторяет запрос после паузы.

### `RetryAfterMiddleware.__call__`
- **Signature**: `async def __call__( self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any], ) -> Any`
- **Source Reference**: [bot/middlewares/retry.py#L24-L39](file:///home/u/Рабочий стол/para/bot/middlewares/retry.py#L24-L39)
- **Async**: `Yes`
- **Return Type**: `Any`

#### Purpose & Architectural Intent
Исполняет хэндлер с retry при временном flood control.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `handler` | `Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]` | Input parameter |
| `event` | `TelegramObject` | Input parameter |
| `data` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `for attempt in range(2):`
2. `return await handler(event, data)`

---
