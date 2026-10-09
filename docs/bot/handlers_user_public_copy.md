# Module Specification: `bot/handlers/user/public_copy.py`
> **Path**: [`bot/handlers/user/public_copy.py`](file:///home/u/Рабочий стол/para/bot/handlers/user/public_copy.py)  
> **Subsystem**: `Public Sharing Flow`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Отдельный публичный роутер для копирования Zoom-реквизитов участниками топика. Позволяет любому одногруппнику нажимать на кнопки скопировать ID/Код без прохождения закрытого AuthFilter.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`cb_public_copy_value`](#cb_public_copy_value) | Function | L19–L28 | `None` | Публичный обработчик копирования ID и паролей Zoom. |

---

## 3. Exhaustive Function Specifications

### `cb_public_copy_value`
- **Signature**: `async def cb_public_copy_value(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/public_copy.py#L19-L28](file:///home/u/Рабочий стол/para/bot/handlers/user/public_copy.py#L19-L28)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Публичный обработчик копирования ID и паролей Zoom. :param callback: CallbackQuery

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `val = callback.data.split("copy:", 1)[1]`
2. `user_id = callback.from_user.id if callback.from_user else 0`
3. `log.info(f"Публичный копир реквизитов вызван user_id={user_id}: {val}")`
4. `await callback.answer(f"Скопировано: {val}", show_alert=True)`

---
