# Module Specification: `bot.py`
> **Path**: [`bot.py`](file:///home/u/Рабочий стол/para/bot.py)  
> **Subsystem**: `Telegram Gateway`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Главный модуль запуска Telegram-бота расписания КТМУ. Инициализирует роутеры хэндлеров, подключение к Redis и запускает процесс получения обновлений (polling) от Telegram. Все фоновые задачи синхронизации вынесены в para-worker, а решение домашних заданий — в para-solver.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`register_all_routers`](#register_all_routers) | Function | L20–L43 | `None` | Регистрирует все хэндлеры и роутеры в диспетчере aiogram. |
| [`shutdown_bot`](#shutdown_bot) | Function | L46–L54 | `None` | Корректно закрывает сессию бота, HTTP-клиент API и подключен |
| [`setup_all_middlewares`](#setup_all_middlewares) | Function | L58–L64 | `None` | Регистрирует глобальные middleware для отказоустойчивости бо |
| [`main`](#main) | Function | L67–L82 | `None` | Основная асинхронная функция инициализации и запуска бота. |

---

## 3. Exhaustive Function Specifications

### `register_all_routers`
- **Signature**: `def register_all_routers() -> None`
- **Source Reference**: [bot.py#L20-L43](file:///home/u/Рабочий стол/para/bot.py#L20-L43)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Регистрирует все хэндлеры и роутеры в диспетчере aiogram.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `from bot.handlers.admin.attendance import router as attendance_router`
2. `from bot.handlers.admin.mute import router as mute_router`
3. `from bot.handlers.admin.panel import router as admin_router`
4. `from bot.handlers.admin.ping_all import router as ping_all_router`
5. `from bot.handlers.admin.testers import router as testers_router`
6. `from bot.handlers.errors import router as error_router`

---

### `shutdown_bot`
- **Signature**: `async def shutdown_bot() -> None`
- **Source Reference**: [bot.py#L46-L54](file:///home/u/Рабочий стол/para/bot.py#L46-L54)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Корректно закрывает сессию бота, HTTP-клиент API и подключение к Redis.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `log.info("Остановка бота: закрытие сессий...")`
2. `await close_api_client()`
3. `if dp.storage:`
4. `await close_redis()`
5. `await bot.session.close()`
6. `log.info("Сессии Telegram, API, Storage и Redis закрыты. Бот остановлен.")`

---

### `setup_all_middlewares`
- **Signature**: `def setup_all_middlewares() -> None`
- **Source Reference**: [bot.py#L58-L64](file:///home/u/Рабочий стол/para/bot.py#L58-L64)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Регистрирует глобальные middleware для отказоустойчивости бота.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `from bot.middlewares.retry import RetryAfterMiddleware`
2. `from bot.middlewares.throttling import CallbackThrottleMiddleware`
3. `dp.message.middleware(RetryAfterMiddleware())`
4. `dp.callback_query.middleware(RetryAfterMiddleware())`
5. `dp.callback_query.middleware(CallbackThrottleMiddleware())`

---

### `main`
- **Signature**: `async def main() -> None`
- **Source Reference**: [bot.py#L67-L82](file:///home/u/Рабочий стол/para/bot.py#L67-L82)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Основная асинхронная функция инициализации и запуска бота.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `from bot.commands import register_bot_commands`
2. `log.info("=" * 60)`
3. `log.info("ЗАПУСК Персонального Telegram Бота КТМУ (para-bot)")`
4. `log.info("=" * 60)`
5. `register_all_routers()`
6. `setup_all_middlewares()`

---
