# Module Specification: `api/router/subscribers.py`
> **Path**: [`api/router/subscribers.py`](file:///home/u/Рабочий стол/para/api/router/subscribers.py)  
> **Subsystem**: `Subscribers API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер подписчиков — GET /subscribers, count, {chat_id}, POST/DELETE {chat_id}. Управляет списком получателей утренних дайджестов и 10-минутных напоминаний.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`list_subscribers`](#list_subscribers) | Function | L27–L30 | `SubscribersListResponse` | Список всех активных подписчиков персональных напоминаний. |
| [`count_subscribers`](#count_subscribers) | Function | L34–L37 | `SubscriberCountResponse` | Общее количество пользователей с включёнными напоминаниями. |
| [`check_subscription`](#check_subscription) | Function | L41–L44 | `SubscriberStatusResponse` | Проверка активности подписки для конкретного Telegram Chat I |
| [`subscribe_user`](#subscribe_user) | Function | L48–L52 | `SubscriberActionResponse` | Включение подписки пользователя на уведомления (Admin only). |
| [`unsubscribe_user`](#unsubscribe_user) | Function | L56–L60 | `SubscriberActionResponse` | Отключение подписки пользователя на уведомления (Admin only) |

---

## 3. Exhaustive Function Specifications

### `list_subscribers`
- **Signature**: `async def list_subscribers() -> SubscribersListResponse`
- **Source Reference**: [api/router/subscribers.py#L27-L30](file:///home/u/Рабочий стол/para/api/router/subscribers.py#L27-L30)
- **Async**: `Yes`
- **Return Type**: `SubscribersListResponse`

#### Purpose & Architectural Intent
Список всех активных подписчиков персональных напоминаний.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `subs = sorted(load_subscribers())`
2. `return SubscribersListResponse(count=len(subs), subscribers=subs)`

---

### `count_subscribers`
- **Signature**: `async def count_subscribers() -> SubscriberCountResponse`
- **Source Reference**: [api/router/subscribers.py#L34-L37](file:///home/u/Рабочий стол/para/api/router/subscribers.py#L34-L37)
- **Async**: `Yes`
- **Return Type**: `SubscriberCountResponse`

#### Purpose & Architectural Intent
Общее количество пользователей с включёнными напоминаниями.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `count = len(load_subscribers())`
2. `return SubscriberCountResponse(count=count)`

---

### `check_subscription`
- **Signature**: `async def check_subscription(chat_id: int) -> SubscriberStatusResponse`
- **Source Reference**: [api/router/subscribers.py#L41-L44](file:///home/u/Рабочий стол/para/api/router/subscribers.py#L41-L44)
- **Async**: `Yes`
- **Return Type**: `SubscriberStatusResponse`

#### Purpose & Architectural Intent
Проверка активности подписки для конкретного Telegram Chat ID.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `active = is_subscribed(chat_id)`
2. `return SubscriberStatusResponse(chat_id=chat_id, is_subscribed=active)`

---

### `subscribe_user`
- **Signature**: `async def subscribe_user(chat_id: int) -> SubscriberActionResponse`
- **Source Reference**: [api/router/subscribers.py#L48-L52](file:///home/u/Рабочий стол/para/api/router/subscribers.py#L48-L52)
- **Async**: `Yes`
- **Return Type**: `SubscriberActionResponse`

#### Purpose & Architectural Intent
Включение подписки пользователя на уведомления (Admin only).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `added = add_subscriber(chat_id)`
2. `msg = "Подписка успешно активирована" if added else "Пользователь уже подписан"`
3. `return SubscriberActionResponse(chat_id=chat_id, is_subscribed=True, message=msg)`

---

### `unsubscribe_user`
- **Signature**: `async def unsubscribe_user(chat_id: int) -> SubscriberActionResponse`
- **Source Reference**: [api/router/subscribers.py#L56-L60](file:///home/u/Рабочий стол/para/api/router/subscribers.py#L56-L60)
- **Async**: `Yes`
- **Return Type**: `SubscriberActionResponse`

#### Purpose & Architectural Intent
Отключение подписки пользователя на уведомления (Admin only).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `removed = remove_subscriber(chat_id)`
2. `msg = "Подписка отключена" if removed else "Пользователь не был подписан"`
3. `return SubscriberActionResponse(chat_id=chat_id, is_subscribed=False, message=msg)`

---
