# Component Reference: `bot/commands.py`
> **File Path**: [`bot/commands.py`](../../bot/commands.py)
> **Subsystem**: `Bot Menu Registry`

## 1. Purpose
Модуль регистрации интерактивного меню команд Telegram (bot.set_my_commands).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_default_user_commands`](#get_default_user_commands) | Function | L18–L36 | `list[BotCommand]` | Возвращает список общедоступных команд бота для студент... |
| [`get_admin_commands`](#get_admin_commands) | Function | L39–L56 | `list[BotCommand]` | Возвращает расширенный список команд управления для ста... |
| [`register_bot_commands`](#register_bot_commands) | Function | L59–L79 | `None` | Регистрирует меню команд в Telegram API для пользовател... |

---

## 3. Comprehensive Function Specifications

### `get_default_user_commands`
```python
def get_default_user_commands() -> list[BotCommand]
```

- **Source Reference**: [`bot/commands.py#L18-L36`](../../bot/commands.py#L18-L36)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[BotCommand]`

#### Overview & Architectural Purpose
Возвращает список общедоступных команд бота для студентов группы.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.commands import get_default_user_commands

# Execute call
result = get_default_user_commands()
```

---

### `get_admin_commands`
```python
def get_admin_commands() -> list[BotCommand]
```

- **Source Reference**: [`bot/commands.py#L39-L56`](../../bot/commands.py#L39-L56)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[BotCommand]`

#### Overview & Architectural Purpose
Возвращает расширенный список команд управления для старосты группы.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.commands import get_admin_commands

# Execute call
result = get_admin_commands()
```

---

### `register_bot_commands`
```python
async def register_bot_commands(bot: Bot) -> None
```

- **Source Reference**: [`bot/commands.py#L59-L79`](../../bot/commands.py#L59-L79)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Регистрирует меню команд в Telegram API для пользователей и старосты.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Bot` | Yes | Parameter `bot` of type `Bot`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.commands import register_bot_commands

# Execute call
result = await register_bot_commands(bot=...)
```

---
