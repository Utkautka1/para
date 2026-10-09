# Module Specification: `db/subscribers.py`
> **Path**: [`db/subscribers.py`](file:///home/u/Рабочий стол/para/db/subscribers.py)  
> **Subsystem**: `Subscriber Store`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль локального хранения подписчиков бота. Сохраняет и считывает список Telegram chat_id из файла data/subscribers.json. Обеспечивает атомарную запись через временный файл и fsync.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`load_subscribers`](#load_subscribers) | Function | L16–L23 | `set[int]` | Загружает множество ID подписанных пользователей из файла. |
| [`save_subscribers`](#save_subscribers) | Function | L26–L36 | `bool` | Атомарно сохраняет актуальное множество подписчиков в JSON ф |
| [`add_subscriber`](#add_subscriber) | Function | L39–L52 | `bool` | Добавляет новый chat_id в список подписчиков. |
| [`remove_subscriber`](#remove_subscriber) | Function | L55–L68 | `bool` | Удаляет chat_id из списка подписчиков. |
| [`is_subscribed`](#is_subscribed) | Function | L71–L78 | `bool` | Проверяет, подписан ли пользователь на 10-минутные напоминан |
| [`toggle_subscriber`](#toggle_subscriber) | Function | L81–L97 | `bool` | Инвертирует статус подписки пользователя на напоминания в ЛС |

---

## 3. Exhaustive Function Specifications

### `load_subscribers`
- **Signature**: `def load_subscribers() -> set[int]`
- **Source Reference**: [db/subscribers.py#L16-L23](file:///home/u/Рабочий стол/para/db/subscribers.py#L16-L23)
- **Async**: `No`
- **Return Type**: `set[int]`

#### Purpose & Architectural Intent
Загружает множество ID подписанных пользователей из файла. :return: Сет с Telegram chat_id

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `data = sync_load_json(SUBSCRIBERS_FILE_PATH, default=[])`
2. `return set(data) if isinstance(data, list) else set()`

---

### `save_subscribers`
- **Signature**: `def save_subscribers(subs: set[int]) -> bool`
- **Source Reference**: [db/subscribers.py#L26-L36](file:///home/u/Рабочий стол/para/db/subscribers.py#L26-L36)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Атомарно сохраняет актуальное множество подписчиков в JSON файл. :param subs: Множество ID подписчиков :return: True в случае успеха

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `subs` | `set[int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `ok = sync_atomic_save_json(SUBSCRIBERS_FILE_PATH, list(subs))`
2. `if ok:`
3. `return ok`

---

### `add_subscriber`
- **Signature**: `def add_subscriber(chat_id: int) -> bool`
- **Source Reference**: [db/subscribers.py#L39-L52](file:///home/u/Рабочий стол/para/db/subscribers.py#L39-L52)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Добавляет новый chat_id в список подписчиков. :param chat_id: Telegram ID чата :return: True, если пользователь был добавлен впервые

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `subs = load_subscribers()`
2. `if chat_id not in subs:`
3. `return False`

---

### `remove_subscriber`
- **Signature**: `def remove_subscriber(chat_id: int) -> bool`
- **Source Reference**: [db/subscribers.py#L55-L68](file:///home/u/Рабочий стол/para/db/subscribers.py#L55-L68)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Удаляет chat_id из списка подписчиков. :param chat_id: Telegram ID чата :return: True, если пользователь был успешно удален

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `subs = load_subscribers()`
2. `if chat_id in subs:`
3. `return False`

---

### `is_subscribed`
- **Signature**: `def is_subscribed(chat_id: int) -> bool`
- **Source Reference**: [db/subscribers.py#L71-L78](file:///home/u/Рабочий стол/para/db/subscribers.py#L71-L78)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, подписан ли пользователь на 10-минутные напоминания в ЛС. :param chat_id: Telegram ID чата :return: True, если напоминания включены

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `return chat_id in load_subscribers()`

---

### `toggle_subscriber`
- **Signature**: `def toggle_subscriber(chat_id: int) -> bool`
- **Source Reference**: [db/subscribers.py#L81-L97](file:///home/u/Рабочий стол/para/db/subscribers.py#L81-L97)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Инвертирует статус подписки пользователя на напоминания в ЛС. :param chat_id: Telegram ID чата :return: Новый статус (True = включено, False = выключено)

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `subs = load_subscribers()`
2. `if chat_id in subs:`
3. `subs.add(chat_id)`
4. `save_subscribers(subs)`
5. `log.info(f"🔔 Пользователь включил напоминания: {chat_id}")`
6. `return True`

---
