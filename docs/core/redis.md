# Component Reference: `core/redis.py`
> **File Path**: [`core/redis.py`](../../core/redis.py)
> **Subsystem**: `Redis Engine`

## 1. Purpose
Модуль инициализации и подключения к Redis.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_redis_pool`](#get_redis_pool) | Function | L18–L39 | `ConnectionPool` | Возвращает синглтон пула сетевых соединений к Redis с л... |
| [`init_redis`](#init_redis) | Function | L42–L61 | `Redis \| None` | Инициализирует асинхронное подключение к серверу Redis ... |
| [`get_redis`](#get_redis) | Function | L64–L75 | `Redis \| None` | Предоставляет активный синглтон клиента Redis с ленивой... |
| [`close_redis`](#close_redis) | Function | L78–L94 | `None` | Корректно закрывает активный клиент и освобождает пул с... |

---

## 3. Comprehensive Function Specifications

### `get_redis_pool`
```python
def get_redis_pool() -> ConnectionPool
```

- **Source Reference**: [`core/redis.py#L18-L39`](../../core/redis.py#L18-L39)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `ConnectionPool`

#### Overview & Architectural Purpose
Возвращает синглтон пула сетевых соединений к Redis с лимитом сокетов.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis import get_redis_pool

# Execute call
result = get_redis_pool()
```

---

### `init_redis`
```python
async def init_redis() -> Redis | None
```

- **Source Reference**: [`core/redis.py#L42-L61`](../../core/redis.py#L42-L61)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Redis | None`

#### Overview & Architectural Purpose
Инициализирует асинхронное подключение к серверу Redis через пул.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis import init_redis

# Execute call
result = await init_redis()
```

---

### `get_redis`
```python
async def get_redis() -> Redis | None
```

- **Source Reference**: [`core/redis.py#L64-L75`](../../core/redis.py#L64-L75)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Redis | None`

#### Overview & Architectural Purpose
Предоставляет активный синглтон клиента Redis с ленивой инициализацией.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis import get_redis

# Execute call
result = await get_redis()
```

---

### `close_redis`
```python
async def close_redis() -> None
```

- **Source Reference**: [`core/redis.py#L78-L94`](../../core/redis.py#L78-L94)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Корректно закрывает активный клиент и освобождает пул сокетов Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis import close_redis

# Execute call
result = await close_redis()
```

---
