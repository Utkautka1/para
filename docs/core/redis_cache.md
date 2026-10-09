# Module Specification: `core/redis_cache.py`
> **Path**: [`core/redis_cache.py`](file:///home/u/Рабочий стол/para/core/redis_cache.py)  
> **Subsystem**: `Distributed L2 Cache`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Сервис быстрых операций с кэшем Redis. Отвечает за сохранение и извлечение кэшированных данных кнопок бота.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`cache_get`](#cache_get) | Function | L28–L44 | `str | None` | Извлекает строковое значение из Redis по ключу. |
| [`cache_set`](#cache_set) | Function | L47–L64 | `None` | Сохраняет строковое значение в Redis с опциональным TTL (сек |
| [`cache_flush`](#cache_flush) | Function | L67–L87 | `int` | Безопасно удаляет из Redis только ключи расписания. |
| [`is_message_processed`](#is_message_processed) | Function | L90–L99 | `bool` | Проверяет, было ли сообщение с ДЗ уже решено и отправлено ра |
| [`mark_message_processed`](#mark_message_processed) | Function | L102–L109 | `None` | Отмечает сообщение с ДЗ как обработанное на 30 дней в Redis. |
| [`check_user_rate_limit`](#check_user_rate_limit) | Function | L112–L132 | `bool` | Проверяет лимит запросов пользователя (максимум 3 запроса в  |
| [`is_hash_processed`](#is_hash_processed) | Function | L135–L144 | `bool` | Проверяет, отправлялось ли аналогичное задание (хэш текста/к |
| [`mark_hash_processed`](#mark_hash_processed) | Function | L147–L154 | `None` | Сохраняет хэш выполненного задания на 24 часа. |
| [`push_hw_task`](#push_hw_task) | Function | L157–L174 | `bool` | Помещает задачу на решение ДЗ в конец очереди Redis. |
| [`pop_hw_task`](#pop_hw_task) | Function | L177–L189 | `dict | None` | Атомарно перемещает задачу из очереди в processing и возвращ |
| [`ack_hw_task`](#ack_hw_task) | Function | L192–L201 | `None` | Удаляет завершенную задачу из processing очереди после успеш |
| [`recover_stale_hw_tasks`](#recover_stale_hw_tasks) | Function | L204–L216 | `int` | Возвращает зависшие задачи из processing обратно в очередь п |
| [`clear_hw_queue`](#clear_hw_queue) | Function | L219–L229 | `int` | Очищает основную и processing очереди задач ДЗ в Redis. |
| [`save_schedule_snapshot`](#save_schedule_snapshot) | Function | L232–L245 | `None` | Сохраняет отфильтрованный срез расписания группы и метаданны |
| [`load_schedule_snapshot`](#load_schedule_snapshot) | Function | L248–L260 | `tuple[dict | None, dict | None]` | Загружает сохраненный срез расписания и метаданные из Redis. |
| [`is_reminder_sent`](#is_reminder_sent) | Function | L263–L266 | `bool` | Проверяет, было ли уже отправлено напоминание с данным ключо |
| [`mark_reminder_sent`](#mark_reminder_sent) | Function | L269–L271 | `None` | Отмечает напоминание как отправленное в Redis с суточным TTL |
| [`get_topic_state_redis`](#get_topic_state_redis) | Function | L274–L277 | `int | None` | Извлекает сохраненный ID сообщения топика из Redis. |
| [`set_topic_state_redis`](#set_topic_state_redis) | Function | L280–L282 | `None` | Сохраняет ID главного сообщения топика в Redis без экспираци |
| [`register_message_for_cleanup`](#register_message_for_cleanup) | Function | L285–L294 | `None` | Регистрирует сообщение в ZSET для гарантированного удаления  |
| [`get_expired_messages_for_cleanup`](#get_expired_messages_for_cleanup) | Function | L297–L310 | `list[tuple[int, int]]` | Извлекает и удаляет из ZSET сообщения, чей срок хранения ист |
| [`redis_lock`](#redis_lock) | Function | L323–L345 | `AsyncGenerator[bool, None]` | Атомарный распределенный лок Redis с валидацией токена владе |
| [`nack_hw_task`](#nack_hw_task) | Function | L348–L363 | `bool` | Возвращает упавшую задачу в очередь или отправляет в DLQ. |

---

## 3. Exhaustive Function Specifications

### `cache_get`
- **Signature**: `async def cache_get(key: str) -> str | None`
- **Source Reference**: [core/redis_cache.py#L28-L44](file:///home/u/Рабочий стол/para/core/redis_cache.py#L28-L44)
- **Async**: `Yes`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Извлекает строковое значение из Redis по ключу. :param key: Ключ записи :return: Строка или None

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `key` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`
2. `return None`

---

### `cache_set`
- **Signature**: `async def cache_set(key: str, value: str, ttl: int | None = REDIS_CACHE_TTL_SECONDS) -> None`
- **Source Reference**: [core/redis_cache.py#L47-L64](file:///home/u/Рабочий стол/para/core/redis_cache.py#L47-L64)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет строковое значение в Redis с опциональным TTL (сек). :param key: Ключ записи :param value: Сохраняемая строка :param ttl: Время жизни в секундах (None / 0 для бессрочного)

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `key` | `str` | Input parameter |
| `value` | `str` | Input parameter |
| `ttl` | `int | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `cache_flush`
- **Signature**: `async def cache_flush(pattern: str = "sched:*") -> int`
- **Source Reference**: [core/redis_cache.py#L67-L87](file:///home/u/Рабочий стол/para/core/redis_cache.py#L67-L87)
- **Async**: `Yes`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Безопасно удаляет из Redis только ключи расписания. Используем scan_iter вместо flushdb, чтобы не затереть хэши решённых ДЗ и антиспам счётчики пользователей. :param pattern: Паттерн удаляемых ключей :return: Количество удалённых ключей

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `pattern` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `deleted = 0`
2. `try:`
3. `return deleted`

---

### `is_message_processed`
- **Signature**: `async def is_message_processed(message_id: int) -> bool`
- **Source Reference**: [core/redis_cache.py#L90-L99](file:///home/u/Рабочий стол/para/core/redis_cache.py#L90-L99)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, было ли сообщение с ДЗ уже решено и отправлено ранее. :param message_id: Telegram ID сообщения :return: True если решено, иначе False

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `key = f"hw_processed:{message_id}"`
2. `val = await cache_get(key)`
3. `return val == "1"`

---

### `mark_message_processed`
- **Signature**: `async def mark_message_processed(message_id: int) -> None`
- **Source Reference**: [core/redis_cache.py#L102-L109](file:///home/u/Рабочий стол/para/core/redis_cache.py#L102-L109)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отмечает сообщение с ДЗ как обработанное на 30 дней в Redis. :param message_id: Telegram ID сообщения

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `key = f"hw_processed:{message_id}"`
2. `await cache_set(key, "1", ttl=2592000)`

---

### `check_user_rate_limit`
- **Signature**: `async def check_user_rate_limit(user_id: int) -> bool`
- **Source Reference**: [core/redis_cache.py#L112-L132](file:///home/u/Рабочий стол/para/core/redis_cache.py#L112-L132)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет лимит запросов пользователя (максимум 3 запроса в минуту). Для администратора (ALLOWED_USER_ID) лимиты полностью отключены. :param user_id: Telegram ID пользователя :return: True если лимит не превышен или пользователь — админ

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if user_id == ALLOWED_USER_ID:`
2. `key = f"hw_rate:{user_id}"`
3. `try:`
4. `return True`

---

### `is_hash_processed`
- **Signature**: `async def is_hash_processed(content_hash: str) -> bool`
- **Source Reference**: [core/redis_cache.py#L135-L144](file:///home/u/Рабочий стол/para/core/redis_cache.py#L135-L144)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, отправлялось ли аналогичное задание (хэш текста/картинки) в последние 24 часа. :param content_hash: SHA256 хэш контента :return: True если такой контент уже решен

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `content_hash` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `key = f"hw_hash:{content_hash}"`
2. `val = await cache_get(key)`
3. `return val == "1"`

---

### `mark_hash_processed`
- **Signature**: `async def mark_hash_processed(content_hash: str) -> None`
- **Source Reference**: [core/redis_cache.py#L147-L154](file:///home/u/Рабочий стол/para/core/redis_cache.py#L147-L154)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет хэш выполненного задания на 24 часа. :param content_hash: SHA256 хэш

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `content_hash` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `key = f"hw_hash:{content_hash}"`
2. `await cache_set(key, "1", ttl=86400)`

---

### `push_hw_task`
- **Signature**: `async def push_hw_task(task_data: dict) -> bool`
- **Source Reference**: [core/redis_cache.py#L157-L174](file:///home/u/Рабочий стол/para/core/redis_cache.py#L157-L174)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Помещает задачу на решение ДЗ в конец очереди Redis. :param task_data: Словарь с параметрами сообщения и задания :return: True в случае успешной вставки

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `task_data` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`
2. `return False`

---

### `pop_hw_task`
- **Signature**: `async def pop_hw_task(timeout: int = 2) -> dict | None`
- **Source Reference**: [core/redis_cache.py#L177-L189](file:///home/u/Рабочий стол/para/core/redis_cache.py#L177-L189)
- **Async**: `Yes`
- **Return Type**: `dict | None`

#### Purpose & Architectural Intent
Атомарно перемещает задачу из очереди в processing и возвращает словарь.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `timeout` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`
2. `return None`

---

### `ack_hw_task`
- **Signature**: `async def ack_hw_task(task_data: dict) -> None`
- **Source Reference**: [core/redis_cache.py#L192-L201](file:///home/u/Рабочий стол/para/core/redis_cache.py#L192-L201)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет завершенную задачу из processing очереди после успешного решения.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `task_data` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `recover_stale_hw_tasks`
- **Signature**: `async def recover_stale_hw_tasks() -> int`
- **Source Reference**: [core/redis_cache.py#L204-L216](file:///home/u/Рабочий стол/para/core/redis_cache.py#L204-L216)
- **Async**: `Yes`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Возвращает зависшие задачи из processing обратно в очередь при старте.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `recovered = 0`
2. `try:`
3. `return recovered`

---

### `clear_hw_queue`
- **Signature**: `async def clear_hw_queue() -> int`
- **Source Reference**: [core/redis_cache.py#L219-L229](file:///home/u/Рабочий стол/para/core/redis_cache.py#L219-L229)
- **Async**: `Yes`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Очищает основную и processing очереди задач ДЗ в Redis.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `try:`
2. `return 0`

---

### `save_schedule_snapshot`
- **Signature**: `async def save_schedule_snapshot(snapshot: dict, meta: dict, ttl: int = 86400) -> None`
- **Source Reference**: [core/redis_cache.py#L232-L245](file:///home/u/Рабочий стол/para/core/redis_cache.py#L232-L245)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет отфильтрованный срез расписания группы и метаданные в Redis.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `snapshot` | `dict` | Input parameter |
| `meta` | `dict` | Input parameter |
| `ttl` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `load_schedule_snapshot`
- **Signature**: `async def load_schedule_snapshot() -> tuple[dict | None, dict | None]`
- **Source Reference**: [core/redis_cache.py#L248-L260](file:///home/u/Рабочий стол/para/core/redis_cache.py#L248-L260)
- **Async**: `Yes`
- **Return Type**: `tuple[dict | None, dict | None]`

#### Purpose & Architectural Intent
Загружает сохраненный срез расписания и метаданные из Redis.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `try:`
2. `return None, None`

---

### `is_reminder_sent`
- **Signature**: `async def is_reminder_sent(rem_key: str) -> bool`
- **Source Reference**: [core/redis_cache.py#L263-L266](file:///home/u/Рабочий стол/para/core/redis_cache.py#L263-L266)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, было ли уже отправлено напоминание с данным ключом сегодня.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `rem_key` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `val = await cache_get(f"rem:sent:{rem_key}")`
2. `return val == "1"`

---

### `mark_reminder_sent`
- **Signature**: `async def mark_reminder_sent(rem_key: str, ttl: int = 86400) -> None`
- **Source Reference**: [core/redis_cache.py#L269-L271](file:///home/u/Рабочий стол/para/core/redis_cache.py#L269-L271)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отмечает напоминание как отправленное в Redis с суточным TTL.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `rem_key` | `str` | Input parameter |
| `ttl` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `await cache_set(f"rem:sent:{rem_key}", "1", ttl=ttl)`

---

### `get_topic_state_redis`
- **Signature**: `async def get_topic_state_redis(key: str = "topic:main_msg_id") -> int | None`
- **Source Reference**: [core/redis_cache.py#L274-L277](file:///home/u/Рабочий стол/para/core/redis_cache.py#L274-L277)
- **Async**: `Yes`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Извлекает сохраненный ID сообщения топика из Redis.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `key` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `val = await cache_get(key)`
2. `return int(val) if val and val.isdigit() else None`

---

### `set_topic_state_redis`
- **Signature**: `async def set_topic_state_redis(val: int, key: str = "topic:main_msg_id") -> None`
- **Source Reference**: [core/redis_cache.py#L280-L282](file:///home/u/Рабочий стол/para/core/redis_cache.py#L280-L282)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет ID главного сообщения топика в Redis без экспирации.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `val` | `int` | Input parameter |
| `key` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `await cache_set(key, str(val), ttl=0)`

---

### `register_message_for_cleanup`
- **Signature**: `async def register_message_for_cleanup(chat_id: int, msg_id: int, delay_sec: int = 900) -> None`
- **Source Reference**: [core/redis_cache.py#L285-L294](file:///home/u/Рабочий стол/para/core/redis_cache.py#L285-L294)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Регистрирует сообщение в ZSET для гарантированного удаления через delay_sec.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |
| `msg_id` | `int` | Input parameter |
| `delay_sec` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `get_expired_messages_for_cleanup`
- **Signature**: `async def get_expired_messages_for_cleanup() -> list[tuple[int, int]]`
- **Source Reference**: [core/redis_cache.py#L297-L310](file:///home/u/Рабочий стол/para/core/redis_cache.py#L297-L310)
- **Async**: `Yes`
- **Return Type**: `list[tuple[int, int]]`

#### Purpose & Architectural Intent
Извлекает и удаляет из ZSET сообщения, чей срок хранения истёк.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `results: list[tuple[int, int]] = []`
2. `try:`
3. `return results`

---

### `redis_lock`
- **Signature**: `async def redis_lock(key: str, ttl: int = 20) -> AsyncGenerator[bool, None]`
- **Source Reference**: [core/redis_cache.py#L323-L345](file:///home/u/Рабочий стол/para/core/redis_cache.py#L323-L345)
- **Async**: `Yes`
- **Return Type**: `AsyncGenerator[bool, None]`

#### Purpose & Architectural Intent
Атомарный распределенный лок Redis с валидацией токена владельца (Lua). Предотвращает ошибочное удаление чужого лока при превышении TTL.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `key` | `str` | Input parameter |
| `ttl` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `import uuid`
2. `client = await init_redis()`
3. `token = str(uuid.uuid4())`
4. `acquired = False`
5. `if client:`
6. `try:`

---

### `nack_hw_task`
- **Signature**: `async def nack_hw_task(task_data: dict, max_retries: int = 3) -> bool`
- **Source Reference**: [core/redis_cache.py#L348-L363](file:///home/u/Рабочий стол/para/core/redis_cache.py#L348-L363)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Возвращает упавшую задачу в очередь или отправляет в DLQ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `task_data` | `dict` | Input parameter |
| `max_retries` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `client = await init_redis()`
2. `if not client:`
3. `retries = task_data.get("retries", 0) + 1`
4. `task_data["retries"] = retries`
5. `raw = json.dumps(task_data, ensure_ascii=False)`
6. `await client.lrem(HW_PROCESSING_KEY, 1, raw)`

---
