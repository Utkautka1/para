# Component Reference: `api/router/gamification.py`
> **File Path**: [`api/router/gamification.py`](../../api/router/gamification.py)
> **Subsystem**: `Gamification API`

## 1. Purpose
Роутер API академической геймификации, рейтинга и 80 достижений.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_calculate_group_pulse`](#_calculate_group_pulse) | Function | L41–L45 | `float` | Вычисляет средний пульс академической посещаемости груп... |
| [`_resolve_target_fio`](#_resolve_target_fio) | Function | L48–L61 | `str \| None` | Разрешает ФИО студента по переданному параметру fio или... |
| [`_viewer_fio`](#_viewer_fio) | Function | L64–L75 | `str \| None` | Определяет ФИО зрителя по идентичности из verify_api_or... |
| [`_public_schema`](#_public_schema) | Function | L78–L80 | `StudentProfileSchema` | Сериализует профиль, скрывая секретные ачивки от чужих ... |
| [`get_leaderboard_endpoint`](#get_leaderboard_endpoint) | Function | L84–L101 | `LeaderboardResponse` | Возвращает рейтинг соревнующихся студентов с выделенным... |
| [`get_student_profile_endpoint`](#get_student_profile_endpoint) | Function | L105–L123 | `StudentProfileSchema` | Возвращает персональный профиль студента по ФИО или Tel... |
| [`get_achievements_catalog_endpoint`](#get_achievements_catalog_endpoint) | Function | L127–L146 | `AchievementsCatalogResponse` | Возвращает полный каталог из 80 достижений с категориям... |
| [`get_ranks_catalog_endpoint`](#get_ranks_catalog_endpoint) | Function | L150–L152 | `list[dict[str, str]]` | Возвращает каталог всех академических рангов системы. |

---

## 3. Comprehensive Function Specifications

### `_calculate_group_pulse`
```python
def _calculate_group_pulse(profiles: list) -> float
```

- **Source Reference**: [`api/router/gamification.py#L41-L45`](../../api/router/gamification.py#L41-L45)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `float`

#### Overview & Architectural Purpose
Вычисляет средний пульс академической посещаемости группы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `profiles` | `list` | Yes | Parameter `profiles` of type `list`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.gamification import _calculate_group_pulse

# Execute call
result = _calculate_group_pulse(profiles=...)
```

---

### `_resolve_target_fio`
```python
def _resolve_target_fio(fio: str | None, tg_id: int | None) -> str | None
```

- **Source Reference**: [`api/router/gamification.py#L48-L61`](../../api/router/gamification.py#L48-L61)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Разрешает ФИО студента по переданному параметру fio или идентификатору Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str | None` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `tg_id` | `int | None` | Yes | Telegram user identifier for identity verification. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.gamification import _resolve_target_fio

# Execute call
result = _resolve_target_fio(fio=..., tg_id=...)
```

---

### `_viewer_fio`
```python
def _viewer_fio(identity: str) -> str | None
```

- **Source Reference**: [`api/router/gamification.py#L64-L75`](../../api/router/gamification.py#L64-L75)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Определяет ФИО зрителя по идентичности из verify_api_or_tester.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `identity` | `str` | Yes | Parameter `identity` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.gamification import _viewer_fio

# Execute call
result = _viewer_fio(identity=...)
```

---

### `_public_schema`
```python
def _public_schema(profile: StudentProfile, viewer: str | None) -> StudentProfileSchema
```

- **Source Reference**: [`api/router/gamification.py#L78-L80`](../../api/router/gamification.py#L78-L80)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `StudentProfileSchema`

#### Overview & Architectural Purpose
Сериализует профиль, скрывая секретные ачивки от чужих глаз.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `profile` | `StudentProfile` | Yes | Parameter `profile` of type `StudentProfile`. |
| `viewer` | `str | None` | Yes | Parameter `viewer` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.gamification import _public_schema

# Execute call
result = _public_schema(profile=..., viewer=...)
```

---

### `get_leaderboard_endpoint`
```python
async def get_leaderboard_endpoint(identity: str = Depends(verify_api_or_tester)) -> LeaderboardResponse
```

- **Source Reference**: [`api/router/gamification.py#L84-L101`](../../api/router/gamification.py#L84-L101)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `LeaderboardResponse`

#### Overview & Architectural Purpose
Возвращает рейтинг соревнующихся студентов с выделенным старостой вне конкурса.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `identity` | `str` | Yes | Parameter `identity` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.gamification import get_leaderboard_endpoint

# Execute call
result = await get_leaderboard_endpoint(identity=...)
```

---

### `get_student_profile_endpoint`
```python
async def get_student_profile_endpoint( fio: str | None = Query(default=None, description="Фамилия или ФИО студента"), tg_id: int | None = Query(default=None, description="Telegram ID студента"), identity: str = Depends(verify_api_or_tester), ) -> StudentProfileSchema
```

- **Source Reference**: [`api/router/gamification.py#L105-L123`](../../api/router/gamification.py#L105-L123)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `StudentProfileSchema`

#### Overview & Architectural Purpose
Возвращает персональный профиль студента по ФИО или Telegram ID.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str | None` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `tg_id` | `int | None` | Yes | Telegram user identifier for identity verification. |
| `identity` | `str` | Yes | Parameter `identity` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.gamification import get_student_profile_endpoint

# Execute call
result = await get_student_profile_endpoint(fio=..., tg_id=..., identity=...)
```

---

### `get_achievements_catalog_endpoint`
```python
async def get_achievements_catalog_endpoint() -> AchievementsCatalogResponse
```

- **Source Reference**: [`api/router/gamification.py#L127-L146`](../../api/router/gamification.py#L127-L146)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AchievementsCatalogResponse`

#### Overview & Architectural Purpose
Возвращает полный каталог из 80 достижений с категориями, редкостью и XP.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.gamification import get_achievements_catalog_endpoint

# Execute call
result = await get_achievements_catalog_endpoint()
```

---

### `get_ranks_catalog_endpoint`
```python
async def get_ranks_catalog_endpoint() -> list[dict[str, str]]
```

- **Source Reference**: [`api/router/gamification.py#L150-L152`](../../api/router/gamification.py#L150-L152)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[dict[str, str]]`

#### Overview & Architectural Purpose
Возвращает каталог всех академических рангов системы.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.gamification import get_ranks_catalog_endpoint

# Execute call
result = await get_ranks_catalog_endpoint()
```

---
