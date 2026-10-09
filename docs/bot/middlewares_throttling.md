# Module Specification: `bot/middlewares/throttling.py`
> **Path**: [`bot/middlewares/throttling.py`](file:///home/u/Рабочий стол/para/bot/middlewares/throttling.py)  
> **Subsystem**: `Throttling Middleware`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Middleware для защиты от частого нажатия инлайн-кнопок (Debounce / Throttling). Предотвращает лавины параллельных обработчиков при повторных кликах нетерпеливых пользователей по инлайн-кнопкам расписания и админки.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_determine_cooldown`](#_determine_cooldown) | Function | L25–L31 | `float` | Определяет необходимый интервал кулдауна по префиксу callbac |
| [`CallbackThrottleMiddleware.__init__`](#callbackthrottlemiddleware__init__) | Method | L37–L39 | `None` | Method |
| [`CallbackThrottleMiddleware._cleanup_old_entries`](#callbackthrottlemiddleware_cleanup_old_entries) | Method | L41–L47 | `None` | Очищает устаревшие записи, предотвращая утечку памяти. |
| [`CallbackThrottleMiddleware._handle_callback_throttle`](#callbackthrottlemiddleware_handle_callback_throttle) | Method | L49–L66 | `bool` | Проверяет кулдаун клика. Возвращает True, если клик разрешён |
| [`CallbackThrottleMiddleware.__call__`](#callbackthrottlemiddleware__call__) | Method | L68–L77 | `Any` | Перехватывает CallbackQuery и отсекает спам-клики. |

---

## 3. Exhaustive Function Specifications

### `_determine_cooldown`
- **Signature**: `def _determine_cooldown(cb_data: str) -> float`
- **Source Reference**: [bot/middlewares/throttling.py#L25-L31](file:///home/u/Рабочий стол/para/bot/middlewares/throttling.py#L25-L31)
- **Async**: `No`
- **Return Type**: `float`

#### Purpose & Architectural Intent
Определяет необходимый интервал кулдауна по префиксу callback_data.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cb_data` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if cb_data in ("sched:refresh", "admin:sync"):`
2. `if cb_data.startswith("sched:"):`
3. `return DEFAULT_COOLDOWN`

---

## Class: `CallbackThrottleMiddleware`
Предотвращает спам-клики по инлайн-кнопкам бота.

### `CallbackThrottleMiddleware.__init__`
- **Signature**: `def __init__(self) -> None`
- **Source Reference**: [bot/middlewares/throttling.py#L37-L39](file:///home/u/Рабочий стол/para/bot/middlewares/throttling.py#L37-L39)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Executes internal domain logic according to service invariants.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `self._last_clicks: dict[str, float] = {}`

---

### `CallbackThrottleMiddleware._cleanup_old_entries`
- **Signature**: `def _cleanup_old_entries(self, now: float) -> None`
- **Source Reference**: [bot/middlewares/throttling.py#L41-L47](file:///home/u/Рабочий стол/para/bot/middlewares/throttling.py#L41-L47)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Очищает устаревшие записи, предотвращая утечку памяти.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `now` | `float` | Input parameter |

#### Step-by-Step Logic Execution
1. `if len(self._last_clicks) > 1000:`

---

### `CallbackThrottleMiddleware._handle_callback_throttle`
- **Signature**: `async def _handle_callback_throttle( self, event: CallbackQuery, now: float ) -> bool`
- **Source Reference**: [bot/middlewares/throttling.py#L49-L66](file:///home/u/Рабочий стол/para/bot/middlewares/throttling.py#L49-L66)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет кулдаун клика. Возвращает True, если клик разрешён.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `event` | `CallbackQuery` | Input parameter |
| `now` | `float` | Input parameter |

#### Step-by-Step Logic Execution
1. `uid = event.from_user.id if event.from_user else 0`
2. `cb_data = event.data or ""`
3. `key = f"{uid}:{cb_data}"`
4. `cooldown = _determine_cooldown(cb_data)`
5. `last_time = self._last_clicks.get(key, 0.0)`
6. `if now - last_time < cooldown:`

---

### `CallbackThrottleMiddleware.__call__`
- **Signature**: `async def __call__( self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any], ) -> Any`
- **Source Reference**: [bot/middlewares/throttling.py#L68-L77](file:///home/u/Рабочий стол/para/bot/middlewares/throttling.py#L68-L77)
- **Async**: `Yes`
- **Return Type**: `Any`

#### Purpose & Architectural Intent
Перехватывает CallbackQuery и отсекает спам-клики.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `handler` | `Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]` | Input parameter |
| `event` | `TelegramObject` | Input parameter |
| `data` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `if isinstance(event, CallbackQuery) and not await self._handle_callback_throttle(even`
2. `return await handler(event, data)`

---
