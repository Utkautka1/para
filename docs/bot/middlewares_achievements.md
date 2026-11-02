# Component Reference: `bot/middlewares/achievements.py`
> **File Path**: [`bot/middlewares/achievements.py`](../../bot/middlewares/achievements.py)
> **Subsystem**: `Achievement Activity Middleware`

## 1. Purpose
Middleware учёта активности для накопительных ачивок.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_activity_for`](#_activity_for) | Function | L26–L40 | `Coroutine[Any, Any, None] \| None` | Выбирает, как учесть апдейт: действие в ЛС/кнопка или с... |
| [`AchievementActivityMiddleware.__call__`](#achievementactivitymiddleware__call__) | Method | L46–L56 | `Any` | Ставит учёт активности в фон и передаёт апдейт дальше б... |

---

## 3. Comprehensive Function Specifications

### `_activity_for`
```python
def _activity_for(event: TelegramObject) -> Coroutine[Any, Any, None] | None
```

- **Source Reference**: [`bot/middlewares/achievements.py#L26-L40`](../../bot/middlewares/achievements.py#L26-L40)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Coroutine[Any, Any, None] | None`

#### Overview & Architectural Purpose
Выбирает, как учесть апдейт: действие в ЛС/кнопка или сообщение в чате группы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `event` | `TelegramObject` | Yes | Parameter `event` of type `TelegramObject`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.middlewares.achievements import _activity_for

# Execute call
result = _activity_for(event=...)
```

---

## Class Model: `AchievementActivityMiddleware`

Считает действия одногруппников в боте и чате группы для ачивок.

### `AchievementActivityMiddleware.__call__`
```python
async def __call__( self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any], ) -> Any
```

- **Source Reference**: [`bot/middlewares/achievements.py#L46-L56`](../../bot/middlewares/achievements.py#L46-L56)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Ставит учёт активности в фон и передаёт апдейт дальше без задержки.

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
from bot.middlewares.achievements import __call__

# Execute call
result = await __call__(handler=..., event=..., data=...)
```

---
