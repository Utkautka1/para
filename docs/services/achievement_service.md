# Component Reference: `services/achievement_service.py`
> **File Path**: [`services/achievement_service.py`](../../services/achievement_service.py)
> **Subsystem**: `Achievement Service`

## 1. Purpose
Сервис разблокировки академических достижений и мгновенных уведомлений в Telegram.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`resolve_student_fio`](#resolve_student_fio) | Function | L27–L32 | `str` | Определяет ФИО студента по Telegram ID из реестра или в... |
| [`format_achievement_notification`](#format_achievement_notification) | Function | L35–L44 | `str` | Форматирует поздравительное сообщение о новом достижени... |
| [`format_achievements_digest`](#format_achievements_digest) | Function | L47–L62 | `str` | Форматирует одно сообщение сразу о нескольких новых ачи... |
| [`send_achievement_message`](#send_achievement_message) | Function | L65–L70 | `None` | Безопасно отправляет студенту уведомление — ошибка дост... |
| [`invalidate_leaderboard_cache`](#invalidate_leaderboard_cache) | Function | L73–L78 | `None` | Инвалидирует кэш лидерборда в Redis для мгновенного обн... |
| [`unlock_for_fio`](#unlock_for_fio) | Function | L81–L91 | `AchievementDefinition \| None` | Сохраняет ачивку за студентом без уведомления. |
| [`award_achievement`](#award_achievement) | Function | L94–L112 | `bool` | Разблокирует ачивку за действие в боте, сбрасывает кэш ... |

---

## 3. Comprehensive Function Specifications

### `resolve_student_fio`
```python
def resolve_student_fio(user_id: int, fallback_name: str | None = None) -> str
```

- **Source Reference**: [`services/achievement_service.py#L27-L32`](../../services/achievement_service.py#L27-L32)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Определяет ФИО студента по Telegram ID из реестра или возвращает имя профиля.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `fallback_name` | `str | None` | Yes | Parameter `fallback_name` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_service import resolve_student_fio

# Execute call
result = resolve_student_fio(user_id=..., fallback_name=...)
```

---

### `format_achievement_notification`
```python
def format_achievement_notification(ach: AchievementDefinition) -> str
```

- **Source Reference**: [`services/achievement_service.py#L35-L44`](../../services/achievement_service.py#L35-L44)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Форматирует поздравительное сообщение о новом достижении.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `ach` | `AchievementDefinition` | Yes | Parameter `ach` of type `AchievementDefinition`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_service import format_achievement_notification

# Execute call
result = format_achievement_notification(ach=...)
```

---

### `format_achievements_digest`
```python
def format_achievements_digest(achs: list[AchievementDefinition]) -> str
```

- **Source Reference**: [`services/achievement_service.py#L47-L62`](../../services/achievement_service.py#L47-L62)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Форматирует одно сообщение сразу о нескольких новых ачивках.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `achs` | `list[AchievementDefinition]` | Yes | Parameter `achs` of type `list[AchievementDefinition]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_service import format_achievements_digest

# Execute call
result = format_achievements_digest(achs=...)
```

---

### `send_achievement_message`
```python
async def send_achievement_message(bot: Any, user_id: int, text: str) -> None
```

- **Source Reference**: [`services/achievement_service.py#L65-L70`](../../services/achievement_service.py#L65-L70)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Безопасно отправляет студенту уведомление — ошибка доставки не ломает выдачу.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.achievement_service import send_achievement_message

# Execute call
result = await send_achievement_message(bot=..., user_id=..., text=...)
```

---

### `invalidate_leaderboard_cache`
```python
async def invalidate_leaderboard_cache() -> None
```

- **Source Reference**: [`services/achievement_service.py#L73-L78`](../../services/achievement_service.py#L73-L78)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Инвалидирует кэш лидерборда в Redis для мгновенного обновления MiniApp.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.achievement_service import invalidate_leaderboard_cache

# Execute call
result = await invalidate_leaderboard_cache()
```

---

### `unlock_for_fio`
```python
async def unlock_for_fio(fio: str, achievement_id: str) -> AchievementDefinition | None
```

- **Source Reference**: [`services/achievement_service.py#L81-L91`](../../services/achievement_service.py#L81-L91)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AchievementDefinition | None`

#### Overview & Architectural Purpose
Сохраняет ачивку за студентом без уведомления.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `achievement_id` | `str` | Yes | Unique identifier of academic milestone achievement. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_service import unlock_for_fio

# Execute call
result = await unlock_for_fio(fio=..., achievement_id=...)
```

---

### `award_achievement`
```python
async def award_achievement( user_id: int, achievement_id: str, bot: Any | None = None, user_full_name: str | None = None, ) -> bool
```

- **Source Reference**: [`services/achievement_service.py#L94-L112`](../../services/achievement_service.py#L94-L112)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Разблокирует ачивку за действие в боте, сбрасывает кэш и шлёт уведомление.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `achievement_id` | `str` | Yes | Unique identifier of academic milestone achievement. |
| `bot` | `Any | None` | Yes | Parameter `bot` of type `Any | None`. |
| `user_full_name` | `str | None` | Yes | Parameter `user_full_name` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.achievement_service import award_achievement

# Execute call
result = await award_achievement(user_id=..., achievement_id=..., bot=...)
```

---
