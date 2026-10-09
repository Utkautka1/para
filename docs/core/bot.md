# Module Specification: `core/bot.py`
> **Path**: [`core/bot.py`](file:///home/u/Рабочий стол/para/core/bot.py)  
> **Subsystem**: `Bot Instance Singleton`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Инициализация aiogram Bot и Dispatcher. Создает синглтоны bot и dp с HTML форматированием и отключенным предпросмотром ссылок (link preview) по умолчанию.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`create_bot_session`](#create_bot_session) | Function | L18–L23 | `AiohttpSession` | Создает сессию aiohttp с пулом соединений (limit=50) и SOCKS |
| [`create_fsm_storage`](#create_fsm_storage) | Function | L26–L41 | `Any` | Создает персистентное Redis-хранилище FSM с fallback на Memo |

---

## 3. Exhaustive Function Specifications

### `create_bot_session`
- **Signature**: `def create_bot_session() -> AiohttpSession`
- **Source Reference**: [core/bot.py#L18-L23](file:///home/u/Рабочий стол/para/core/bot.py#L18-L23)
- **Async**: `No`
- **Return Type**: `AiohttpSession`

#### Purpose & Architectural Intent
Создает сессию aiohttp с пулом соединений (limit=50) и SOCKS5 прокси.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `if PROXY_URL:`
2. `return AiohttpSession(limit=50, timeout=15.0)`

---

### `create_fsm_storage`
- **Signature**: `def create_fsm_storage()`
- **Source Reference**: [core/bot.py#L26-L41](file:///home/u/Рабочий стол/para/core/bot.py#L26-L41)
- **Async**: `No`
- **Return Type**: `Any`

#### Purpose & Architectural Intent
Создает персистентное Redis-хранилище FSM с fallback на MemoryStorage.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `try:`

---
