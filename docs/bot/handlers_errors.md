# Module Specification: `bot/handlers/errors.py`
> **Path**: [`bot/handlers/errors.py`](file:///home/u/Рабочий стол/para/bot/handlers/errors.py)  
> **Subsystem**: `Global Error Trapper`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Глобальный обработчик необработанных исключений диспетчера aiogram. Перехватывает системные сбои в хэндлерах, гасит анимацию ожидания callback-кнопок и информирует пользователя о временной ошибке вместо зависания интерфейса.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`global_error_handler`](#global_error_handler) | Function | L18–L32 | `bool` | Перехватывает исключения хэндлеров, логирует и уведомляет по |

---

## 3. Exhaustive Function Specifications

### `global_error_handler`
- **Signature**: `async def global_error_handler(event: ErrorEvent) -> bool`
- **Source Reference**: [bot/handlers/errors.py#L18-L32](file:///home/u/Рабочий стол/para/bot/handlers/errors.py#L18-L32)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Перехватывает исключения хэндлеров, логирует и уведомляет пользователя.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `event` | `ErrorEvent` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.error(f"❌ Необработанная ошибка в хэндлере: {event.exception}")`
2. `update = event.update`
3. `if update.callback_query:`
4. `return True`

---
