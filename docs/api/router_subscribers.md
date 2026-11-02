# Component Reference: `api/router/subscribers.py`
> **File Path**: [`api/router/subscribers.py`](../../api/router/subscribers.py)
> **Subsystem**: `Subscribers API`

## 1. Purpose
Роутер подписчиков — GET /subscribers, count, {chat_id}, POST/DELETE {chat_id}.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`list_subscribers`](#list_subscribers) | Function | L27–L39 | `SubscribersListResponse` | Возвращает список всех активных подписчиков утренних да... |
| [`count_subscribers`](#count_subscribers) | Function | L43–L55 | `SubscriberCountResponse` | Возвращает суммарное число активных подписчиков расписа... |
| [`check_subscription`](#check_subscription) | Function | L59–L71 | `SubscriberStatusResponse` | Проверяет активность подписки для указанного Telegram C... |
| [`subscribe_user`](#subscribe_user) | Function | L75–L88 | `SubscriberActionResponse` | Принудительно подписывает чат или пользователя на распи... |
| [`unsubscribe_user`](#unsubscribe_user) | Function | L92–L105 | `SubscriberActionResponse` | Отключает автоматическую рассылку уведомлений для чата ... |

---

## 3. Comprehensive Function Specifications

### `list_subscribers`
```python
async def list_subscribers() -> SubscribersListResponse
```

- **Source Reference**: [`api/router/subscribers.py#L27-L39`](../../api/router/subscribers.py#L27-L39)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `SubscribersListResponse`

#### Overview & Architectural Purpose
Возвращает список всех активных подписчиков утренних дайджестов расписания.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.subscribers import list_subscribers

# Execute call
result = await list_subscribers()
```

---

### `count_subscribers`
```python
async def count_subscribers() -> SubscriberCountResponse
```

- **Source Reference**: [`api/router/subscribers.py#L43-L55`](../../api/router/subscribers.py#L43-L55)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `SubscriberCountResponse`

#### Overview & Architectural Purpose
Возвращает суммарное число активных подписчиков расписания.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.subscribers import count_subscribers

# Execute call
result = await count_subscribers()
```

---

### `check_subscription`
```python
async def check_subscription(chat_id: int) -> SubscriberStatusResponse
```

- **Source Reference**: [`api/router/subscribers.py#L59-L71`](../../api/router/subscribers.py#L59-L71)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `SubscriberStatusResponse`

#### Overview & Architectural Purpose
Проверяет активность подписки для указанного Telegram Chat ID.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.subscribers import check_subscription

# Execute call
result = await check_subscription(chat_id=...)
```

---

### `subscribe_user`
```python
async def subscribe_user(chat_id: int) -> SubscriberActionResponse
```

- **Source Reference**: [`api/router/subscribers.py#L75-L88`](../../api/router/subscribers.py#L75-L88)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `SubscriberActionResponse`

#### Overview & Architectural Purpose
Принудительно подписывает чат или пользователя на расписание (Admin only).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.subscribers import subscribe_user

# Execute call
result = await subscribe_user(chat_id=...)
```

---

### `unsubscribe_user`
```python
async def unsubscribe_user(chat_id: int) -> SubscriberActionResponse
```

- **Source Reference**: [`api/router/subscribers.py#L92-L105`](../../api/router/subscribers.py#L92-L105)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `SubscriberActionResponse`

#### Overview & Architectural Purpose
Отключает автоматическую рассылку уведомлений для чата (Admin only).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.subscribers import unsubscribe_user

# Execute call
result = await unsubscribe_user(chat_id=...)
```

---
