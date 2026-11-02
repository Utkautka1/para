# Component Reference: `core/redis_cache.py`
> **File Path**: [`core/redis_cache.py`](../../core/redis_cache.py)
> **Subsystem**: `Distributed L2 Cache`

## 1. Purpose
Сервис быстрых операций с кэшем Redis.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`cache_get`](#cache_get) | Function | L35–L54 | `str \| None` | Извлекает строковое значение из кэша Redis по ключу. |
| [`cache_set`](#cache_set) | Function | L57–L72 | `None` | Сохраняет строковое значение в Redis с настраиваемым вр... |
| [`cache_delete`](#cache_delete) | Function | L75–L93 | `bool` | Удаляет конкретный ключ из кэша Redis. |
| [`cache_flush`](#cache_flush) | Function | L96–L115 | `int` | Выполняет безопасную точечную очистку ключей по заданно... |
| [`is_message_processed`](#is_message_processed) | Function | L118–L129 | `bool` | Проверяет, было ли сообщение с домашним заданием уже ре... |
| [`mark_message_processed`](#mark_message_processed) | Function | L132–L142 | `None` | Помечает Telegram-сообщение как обработанное в Redis на... |
| [`_incr_window`](#_incr_window) | Function | L145–L166 | `int \| None` | Атомарно увеличивает счётчик фиксированного окна длиной... |
| [`incr_with_ttl`](#incr_with_ttl) | Function | L169–L178 | `int` | Увеличивает счётчик в Redis; TTL ставится на первом инк... |
| [`allow_request`](#allow_request) | Function | L181–L194 | `bool` | Проверяет и учитывает запрос в лимите limit штук за win... |
| [`check_user_rate_limit`](#check_user_rate_limit) | Function | L197–L208 | `bool` | Проверяет лимит заданий ДЗ пользователя из бота. |
| [`is_hash_processed`](#is_hash_processed) | Function | L211–L222 | `bool` | Проверяет, решалось ли идентичное задание за последние ... |
| [`mark_hash_processed`](#mark_hash_processed) | Function | L225–L235 | `None` | Сохраняет SHA256-хэш решенного задания в Redis на 24 ча... |
| [`save_schedule_snapshot`](#save_schedule_snapshot) | Function | L238–L265 | `None` | Транзакционно сохраняет срез расписания и его метаданны... |
| [`load_schedule_snapshot`](#load_schedule_snapshot) | Function | L268–L287 | `tuple[dict \| None, dict \| None]` | Считывает сохраненный срез расписания и метаданные из п... |
| [`load_schedule_meta`](#load_schedule_meta) | Function | L290–L304 | `dict \| None` | Читает только метаданные снапшота расписания (версия, в... |
| [`request_schedule_refresh`](#request_schedule_refresh) | Function | L307–L324 | `bool` | Ставит флаг «обновить расписание сейчас» для фонового з... |
| [`pop_schedule_refresh_request`](#pop_schedule_refresh_request) | Function | L327–L338 | `bool` | Атомарно забирает флаг внеочередного обновления расписа... |
| [`is_reminder_sent`](#is_reminder_sent) | Function | L341–L351 | `bool` | Проверяет, отправлялось ли уведомление с указанным ключ... |
| [`mark_reminder_sent`](#mark_reminder_sent) | Function | L354–L363 | `None` | Фиксирует факт отправки напоминания в Redis с суточным ... |
| [`get_topic_state_redis`](#get_topic_state_redis) | Function | L366–L376 | `int \| None` | Извлекает сохраненный Telegram ID главного сообщения то... |
| [`set_topic_state_redis`](#set_topic_state_redis) | Function | L379–L388 | `None` | Сохраняет Telegram ID главного сообщения топика без огр... |
| [`register_message_for_cleanup`](#register_message_for_cleanup) | Function | L391–L407 | `None` | Регистрирует временное служебное сообщение в ZSET для о... |
| [`get_expired_messages_for_cleanup`](#get_expired_messages_for_cleanup) | Function | L410–L430 | `list[tuple[int, int]]` | Извлекает и атомарно удаляет из ZSET все сообщения с ис... |
| [`redis_lock`](#redis_lock) | Function | L434–L458 | `AsyncGenerator[bool, None]` | Асинхронный контекстный менеджер распределенного замка ... |

---

## 3. Comprehensive Function Specifications

### `cache_get`
```python
async def cache_get(key: str) -> str | None
```

- **Source Reference**: [`core/redis_cache.py#L35-L54`](../../core/redis_cache.py#L35-L54)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Извлекает строковое значение из кэша Redis по ключу.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import cache_get

# Execute call
result = await cache_get(key=...)
```

---

### `cache_set`
```python
async def cache_set(key: str, value: str, ttl: int | None = REDIS_CACHE_TTL_SECONDS) -> None
```

- **Source Reference**: [`core/redis_cache.py#L57-L72`](../../core/redis_cache.py#L57-L72)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сохраняет строковое значение в Redis с настраиваемым временем жизни TTL.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `value` | `str` | Yes | Parameter `value` of type `str`. |
| `ttl` | `int | None` | Yes | Parameter `ttl` of type `int | None`. |

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import cache_set

# Execute call
result = await cache_set(key=..., value=..., ttl=...)
```

---

### `cache_delete`
```python
async def cache_delete(key: str) -> bool
```

- **Source Reference**: [`core/redis_cache.py#L75-L93`](../../core/redis_cache.py#L75-L93)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Удаляет конкретный ключ из кэша Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import cache_delete

# Execute call
result = await cache_delete(key=...)
```

---

### `cache_flush`
```python
async def cache_flush(pattern: str = "sched:*") -> int
```

- **Source Reference**: [`core/redis_cache.py#L96-L115`](../../core/redis_cache.py#L96-L115)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Выполняет безопасную точечную очистку ключей по заданному шаблону.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `pattern` | `str` | Yes | Parameter `pattern` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import cache_flush

# Execute call
result = await cache_flush(pattern=...)
```

---

### `is_message_processed`
```python
async def is_message_processed(message_id: int) -> bool
```

- **Source Reference**: [`core/redis_cache.py#L118-L129`](../../core/redis_cache.py#L118-L129)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, было ли сообщение с домашним заданием уже решено ранее.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message_id` | `int` | Yes | Parameter `message_id` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import is_message_processed

# Execute call
result = await is_message_processed(message_id=...)
```

---

### `mark_message_processed`
```python
async def mark_message_processed(message_id: int) -> None
```

- **Source Reference**: [`core/redis_cache.py#L132-L142`](../../core/redis_cache.py#L132-L142)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Помечает Telegram-сообщение как обработанное в Redis на HW_PROCESSED_TTL_SECONDS.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message_id` | `int` | Yes | Parameter `message_id` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import mark_message_processed

# Execute call
result = await mark_message_processed(message_id=...)
```

---

### `_incr_window`
```python
async def _incr_window(key: str, ttl: int) -> int | None
```

- **Source Reference**: [`core/redis_cache.py#L145-L166`](../../core/redis_cache.py#L145-L166)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Атомарно увеличивает счётчик фиксированного окна длиной ttl секунд.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `ttl` | `int` | Yes | Parameter `ttl` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import _incr_window

# Execute call
result = await _incr_window(key=..., ttl=...)
```

---

### `incr_with_ttl`
```python
async def incr_with_ttl(key: str, ttl: int) -> int
```

- **Source Reference**: [`core/redis_cache.py#L169-L178`](../../core/redis_cache.py#L169-L178)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Увеличивает счётчик в Redis; TTL ставится на первом инкременте окна.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `ttl` | `int` | Yes | Parameter `ttl` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import incr_with_ttl

# Execute call
result = await incr_with_ttl(key=..., ttl=...)
```

---

### `allow_request`
```python
async def allow_request(key: str, limit: int, window_seconds: int) -> bool
```

- **Source Reference**: [`core/redis_cache.py#L181-L194`](../../core/redis_cache.py#L181-L194)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет и учитывает запрос в лимите limit штук за window_seconds.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `limit` | `int` | Yes | Maximum number of records or results to retrieve. |
| `window_seconds` | `int` | Yes | Parameter `window_seconds` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import allow_request

# Execute call
result = await allow_request(key=..., limit=..., window_seconds=...)
```

---

### `check_user_rate_limit`
```python
async def check_user_rate_limit(user_id: int) -> bool
```

- **Source Reference**: [`core/redis_cache.py#L197-L208`](../../core/redis_cache.py#L197-L208)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет лимит заданий ДЗ пользователя из бота.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import check_user_rate_limit

# Execute call
result = await check_user_rate_limit(user_id=...)
```

---

### `is_hash_processed`
```python
async def is_hash_processed(content_hash: str) -> bool
```

- **Source Reference**: [`core/redis_cache.py#L211-L222`](../../core/redis_cache.py#L211-L222)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, решалось ли идентичное задание за последние 24 часа по SHA256-хэшу.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `content_hash` | `str` | Yes | Parameter `content_hash` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import is_hash_processed

# Execute call
result = await is_hash_processed(content_hash=...)
```

---

### `mark_hash_processed`
```python
async def mark_hash_processed(content_hash: str) -> None
```

- **Source Reference**: [`core/redis_cache.py#L225-L235`](../../core/redis_cache.py#L225-L235)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сохраняет SHA256-хэш решенного задания в Redis на 24 часа.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `content_hash` | `str` | Yes | Parameter `content_hash` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import mark_hash_processed

# Execute call
result = await mark_hash_processed(content_hash=...)
```

---

### `save_schedule_snapshot`
```python
async def save_schedule_snapshot(snapshot: dict, meta: dict, ttl: int = 86400) -> None
```

- **Source Reference**: [`core/redis_cache.py#L238-L265`](../../core/redis_cache.py#L238-L265)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Транзакционно сохраняет срез расписания и его метаданные через Redis Pipeline.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `snapshot` | `dict` | Yes | Parameter `snapshot` of type `dict`. |
| `meta` | `dict` | Yes | Parameter `meta` of type `dict`. |
| `ttl` | `int` | Yes | Parameter `ttl` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import save_schedule_snapshot

# Execute call
result = await save_schedule_snapshot(snapshot=..., meta=..., ttl=...)
```

---

### `load_schedule_snapshot`
```python
async def load_schedule_snapshot() -> tuple[dict | None, dict | None]
```

- **Source Reference**: [`core/redis_cache.py#L268-L287`](../../core/redis_cache.py#L268-L287)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[dict | None, dict | None]`

#### Overview & Architectural Purpose
Считывает сохраненный срез расписания и метаданные из постоянного кэша Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import load_schedule_snapshot

# Execute call
result = await load_schedule_snapshot()
```

---

### `load_schedule_meta`
```python
async def load_schedule_meta() -> dict | None
```

- **Source Reference**: [`core/redis_cache.py#L290-L304`](../../core/redis_cache.py#L290-L304)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict | None`

#### Overview & Architectural Purpose
Читает только метаданные снапшота расписания (версия, время загрузки).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import load_schedule_meta

# Execute call
result = await load_schedule_meta()
```

---

### `request_schedule_refresh`
```python
async def request_schedule_refresh() -> bool
```

- **Source Reference**: [`core/redis_cache.py#L307-L324`](../../core/redis_cache.py#L307-L324)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Ставит флаг «обновить расписание сейчас» для фонового загрузчика в worker.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import request_schedule_refresh

# Execute call
result = await request_schedule_refresh()
```

---

### `pop_schedule_refresh_request`
```python
async def pop_schedule_refresh_request() -> bool
```

- **Source Reference**: [`core/redis_cache.py#L327-L338`](../../core/redis_cache.py#L327-L338)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Атомарно забирает флаг внеочередного обновления расписания (GETDEL).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import pop_schedule_refresh_request

# Execute call
result = await pop_schedule_refresh_request()
```

---

### `is_reminder_sent`
```python
async def is_reminder_sent(rem_key: str) -> bool
```

- **Source Reference**: [`core/redis_cache.py#L341-L351`](../../core/redis_cache.py#L341-L351)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, отправлялось ли уведомление с указанным ключом в течение суток.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `rem_key` | `str` | Yes | Parameter `rem_key` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import is_reminder_sent

# Execute call
result = await is_reminder_sent(rem_key=...)
```

---

### `mark_reminder_sent`
```python
async def mark_reminder_sent(rem_key: str, ttl: int = 86400) -> None
```

- **Source Reference**: [`core/redis_cache.py#L354-L363`](../../core/redis_cache.py#L354-L363)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Фиксирует факт отправки напоминания в Redis с суточным временем жизни.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `rem_key` | `str` | Yes | Parameter `rem_key` of type `str`. |
| `ttl` | `int` | Yes | Parameter `ttl` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import mark_reminder_sent

# Execute call
result = await mark_reminder_sent(rem_key=..., ttl=...)
```

---

### `get_topic_state_redis`
```python
async def get_topic_state_redis(key: str = "topic:main_msg_id") -> int | None
```

- **Source Reference**: [`core/redis_cache.py#L366-L376`](../../core/redis_cache.py#L366-L376)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Извлекает сохраненный Telegram ID главного сообщения топика из Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import get_topic_state_redis

# Execute call
result = await get_topic_state_redis(key=...)
```

---

### `set_topic_state_redis`
```python
async def set_topic_state_redis(val: int, key: str = "topic:main_msg_id") -> None
```

- **Source Reference**: [`core/redis_cache.py#L379-L388`](../../core/redis_cache.py#L379-L388)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сохраняет Telegram ID главного сообщения топика без ограничения по сроку жизни.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `val` | `int` | Yes | Parameter `val` of type `int`. |
| `key` | `str` | Yes | Parameter `key` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.redis_cache import set_topic_state_redis

# Execute call
result = await set_topic_state_redis(val=..., key=...)
```

---

### `register_message_for_cleanup`
```python
async def register_message_for_cleanup(chat_id: int, msg_id: int, delay_sec: int = 900) -> None
```

- **Source Reference**: [`core/redis_cache.py#L391-L407`](../../core/redis_cache.py#L391-L407)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Регистрирует временное служебное сообщение в ZSET для отложенного удаления.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `msg_id` | `int` | Yes | Parameter `msg_id` of type `int`. |
| `delay_sec` | `int` | Yes | Parameter `delay_sec` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import register_message_for_cleanup

# Execute call
result = await register_message_for_cleanup(chat_id=..., msg_id=..., delay_sec=...)
```

---

### `get_expired_messages_for_cleanup`
```python
async def get_expired_messages_for_cleanup() -> list[tuple[int, int]]
```

- **Source Reference**: [`core/redis_cache.py#L410-L430`](../../core/redis_cache.py#L410-L430)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[tuple[int, int]]`

#### Overview & Architectural Purpose
Извлекает и атомарно удаляет из ZSET все сообщения с истекшим сроком жизни.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import get_expired_messages_for_cleanup

# Execute call
result = await get_expired_messages_for_cleanup()
```

---

### `redis_lock`
```python
async def redis_lock(key: str, ttl: int = 20) -> AsyncGenerator[bool, None]
```

- **Source Reference**: [`core/redis_cache.py#L434-L458`](../../core/redis_cache.py#L434-L458)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AsyncGenerator[bool, None]`

#### Overview & Architectural Purpose
Асинхронный контекстный менеджер распределенного замка с Lua-освобождением.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str` | Yes | Parameter `key` of type `str`. |
| `ttl` | `int` | Yes | Parameter `ttl` of type `int`. |

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.redis_cache import redis_lock

# Execute call
result = await redis_lock(key=..., ttl=...)
```

---
