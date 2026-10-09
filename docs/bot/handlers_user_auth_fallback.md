# Module Specification: `bot/handlers/user/auth_fallback.py`
> **Path**: [`bot/handlers/user/auth_fallback.py`](file:///home/u/Рабочий стол/para/bot/handlers/user/auth_fallback.py)  
> **Subsystem**: `Fallback Auth Flow`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Хэндлер обработки сообщений от неавторизованных пользователей. Срабатывает, если Telegram ID отправителя не совпадает с ALLOWED_USER_ID.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`unauth_fallback`](#unauth_fallback) | Function | L20–L33 | `None` | Информирует посторонних пользователей об ограничении доступа |

---

## 3. Exhaustive Function Specifications

### `unauth_fallback`
- **Signature**: `async def unauth_fallback(message: Message) -> None`
- **Source Reference**: [bot/handlers/user/auth_fallback.py#L20-L33](file:///home/u/Рабочий стол/para/bot/handlers/user/auth_fallback.py#L20-L33)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Информирует посторонних пользователей об ограничении доступа в ЛС.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `user = message.from_user`
2. `if not user or is_authorized_user(user) or await is_tester_allowed(user.id):`
3. `uid = user.id`
4. `uname = f"@{user.username}" if user.username else "нет username"`
5. `log.warning(f"⛔ Доступ ограничен: id={uid}, username={uname}")`
6. `await message.answer(`

---
