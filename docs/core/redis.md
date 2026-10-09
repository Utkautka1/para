# Module Specification: `core/redis.py`
> **Path**: [`core/redis.py`](file:///home/u/Рабочий стол/para/core/redis.py)  
> **Subsystem**: `Redis Engine`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль инициализации и подключения к Redis. Предоставляет синглтон клиента Redis для асинхронного кэширования.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_redis_pool`](#get_redis_pool) | Function | L18–L31 | `ConnectionPool` | Создает или возвращает синглтон пула соединений к Redis с ли |
| [`init_redis`](#init_redis) | Function | L34–L50 | `Redis | None` | Инициализирует подключение к Redis через пул соединений. |
| [`get_redis`](#get_redis) | Function | L53–L62 | `Redis | None` | Возвращает синглтон клиента Redis, подключаясь при необходим |
| [`close_redis`](#close_redis) | Function | L65–L74 | `None` | Освобождает клиент и пул соединений с Redis при завершении с |

---

## 3. Exhaustive Function Specifications

### `get_redis_pool`
- **Signature**: `def get_redis_pool() -> ConnectionPool`
- **Source Reference**: [core/redis.py#L18-L31](file:///home/u/Рабочий стол/para/core/redis.py#L18-L31)
- **Async**: `No`
- **Return Type**: `ConnectionPool`

#### Purpose & Architectural Intent
Создает или возвращает синглтон пула соединений к Redis с лимитом сокетов.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _pool`
2. `if _pool is None:`
3. `return _pool`

---

### `init_redis`
- **Signature**: `async def init_redis() -> Redis | None`
- **Source Reference**: [core/redis.py#L34-L50](file:///home/u/Рабочий стол/para/core/redis.py#L34-L50)
- **Async**: `Yes`
- **Return Type**: `Redis | None`

#### Purpose & Architectural Intent
Инициализирует подключение к Redis через пул соединений. :return: Объект Redis или None при сбое сети

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global redis_client`
2. `if redis_client is None:`
3. `return redis_client`

---

### `get_redis`
- **Signature**: `async def get_redis() -> Redis | None`
- **Source Reference**: [core/redis.py#L53-L62](file:///home/u/Рабочий стол/para/core/redis.py#L53-L62)
- **Async**: `Yes`
- **Return Type**: `Redis | None`

#### Purpose & Architectural Intent
Возвращает синглтон клиента Redis, подключаясь при необходимости. Позволяет безопасно получать активное соединение из любых модулей без риска захвата неинициализированной ссылки во время импорта.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `if redis_client is None:`
2. `return redis_client`

---

### `close_redis`
- **Signature**: `async def close_redis() -> None`
- **Source Reference**: [core/redis.py#L65-L74](file:///home/u/Рабочий стол/para/core/redis.py#L65-L74)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Освобождает клиент и пул соединений с Redis при завершении сервиса.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global redis_client, _pool`
2. `if redis_client:`
3. `if _pool:`
4. `log.info("Соединение и пул соединений с Redis успешно закрыты")`

---
