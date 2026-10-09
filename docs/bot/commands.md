# Module Specification: `bot/commands.py`
> **Path**: [`bot/commands.py`](file:///home/u/Рабочий стол/para/bot/commands.py)  
> **Subsystem**: `Bot Menu Registry`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль регистрации интерактивного меню команд Telegram (bot.set_my_commands). Настраивает видимость команд через BotCommandScope: - BotCommandScopeDefault: базовые команды для всех студентов группы - BotCommandScopeChat: расширенные команды управления для старосты (ALLOWED_USER_ID)

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_default_user_commands`](#get_default_user_commands) | Function | L18–L25 | `list[BotCommand]` | Возвращает список общедоступных команд для студентов группы. |
| [`get_admin_commands`](#get_admin_commands) | Function | L28–L37 | `list[BotCommand]` | Возвращает расширенный список команд для старосты группы. |
| [`register_bot_commands`](#register_bot_commands) | Function | L40–L47 | `None` | Регистрирует меню команд в Telegram API для пользователей и  |

---

## 3. Exhaustive Function Specifications

### `get_default_user_commands`
- **Signature**: `def get_default_user_commands() -> list[BotCommand]`
- **Source Reference**: [bot/commands.py#L18-L25](file:///home/u/Рабочий стол/para/bot/commands.py#L18-L25)
- **Async**: `No`
- **Return Type**: `list[BotCommand]`

#### Purpose & Architectural Intent
Возвращает список общедоступных команд для студентов группы.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return [`

---

### `get_admin_commands`
- **Signature**: `def get_admin_commands() -> list[BotCommand]`
- **Source Reference**: [bot/commands.py#L28-L37](file:///home/u/Рабочий стол/para/bot/commands.py#L28-L37)
- **Async**: `No`
- **Return Type**: `list[BotCommand]`

#### Purpose & Architectural Intent
Возвращает расширенный список команд для старосты группы.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return [`

---

### `register_bot_commands`
- **Signature**: `async def register_bot_commands(bot: Bot) -> None`
- **Source Reference**: [bot/commands.py#L40-L47](file:///home/u/Рабочий стол/para/bot/commands.py#L40-L47)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Регистрирует меню команд в Telegram API для пользователей и администратора.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `bot` | `Bot` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---
