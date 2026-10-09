# Module Specification: `bot/filters/auth.py`
> **Path**: [`bot/filters/auth.py`](file:///home/u/Рабочий стол/para/bot/filters/auth.py)  
> **Subsystem**: `Bot Auth Filters`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Фильтр авторизации пользователей. Проверяет, соответствует ли Telegram ID отправителя единственному разрешенному пользователю из конфигурации (ALLOWED_USER_ID).

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`AuthFilter.__call__`](#authfilter__call__) | Method | L18–L28 | `bool` | Проверяет ID пользователя на соответствие ALLOWED_USER_ID. |
| [`ClassmateAuthFilter.__call__`](#classmateauthfilter__call__) | Method | L34–L43 | `bool` | Проверяет, авторизован ли пользователь для доступа к расписа |
| [`AttendanceAuthFilter.__call__`](#attendanceauthfilter__call__) | Method | L49–L55 | `bool` | Проверяет принадлежность ID пользователя к списку старост. |

---

## 3. Exhaustive Function Specifications

## Class: `AuthFilter`
Фильтр доступа по Telegram ID исключительно для Главного Администратора.

### `AuthFilter.__call__`
- **Signature**: `async def __call__(self, event: Message | CallbackQuery) -> bool`
- **Source Reference**: [bot/filters/auth.py#L18-L28](file:///home/u/Рабочий стол/para/bot/filters/auth.py#L18-L28)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет ID пользователя на соответствие ALLOWED_USER_ID. :param event: Входящее сообщение или callback Telegram :return: True, если доступ разрешен

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `event` | `Message | CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `user = getattr(event, "from_user", None)`
2. `if not user:`
3. `return user.id == ALLOWED_USER_ID`

---

## Class: `ClassmateAuthFilter`
Фильтр доступа для администратора и авторизованных студентов группы.

### `ClassmateAuthFilter.__call__`
- **Signature**: `async def __call__(self, event: Message | CallbackQuery) -> bool`
- **Source Reference**: [bot/filters/auth.py#L34-L43](file:///home/u/Рабочий стол/para/bot/filters/auth.py#L34-L43)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, авторизован ли пользователь для доступа к расписанию. :param event: Сообщение или callback Telegram :return: True, если пользователь админ или подтвержденный одногруппник

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `event` | `Message | CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `from services.classmates_auth import is_authorized_user`
2. `user = getattr(event, "from_user", None)`
3. `return is_authorized_user(user)`

---

## Class: `AttendanceAuthFilter`
Фильтр доступа для старосты и замстаросты к отметке посещаемости.

### `AttendanceAuthFilter.__call__`
- **Signature**: `async def __call__(self, event: Message | CallbackQuery) -> bool`
- **Source Reference**: [bot/filters/auth.py#L49-L55](file:///home/u/Рабочий стол/para/bot/filters/auth.py#L49-L55)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет принадлежность ID пользователя к списку старост.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `event` | `Message | CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `from config import ALLOWED_ATTENDANCE_USER_IDS`
2. `user = getattr(event, "from_user", None)`
3. `if not user:`
4. `return user.id in ALLOWED_ATTENDANCE_USER_IDS`

---
