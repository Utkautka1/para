# Component Reference: `services/gamification.py`
> **File Path**: [`services/gamification.py`](../../services/gamification.py)
> **Subsystem**: `Academic Gamification Engine`
> **Architecture Layer**: `Domain Business Service`
> **Concurrency Model**: `AsyncIO Event Loop + In-Memory Ranks`
> **Persistence Backend**: `Redis L2 + SQLite Attendance Stats`
> **Service Level Objective**: `Sub-5ms Profile Calculation`

## 1. Architectural Role & Responsibilities
The `services/gamification.py` module implements core operational logic for the `Academic Gamification Engine` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

### Component Architecture & Data Flow
```mermaid
graph TD
    A[Student / Mini App] --> B[api.router.gamification / bot.handlers.user.profile]
    B --> C[services.gamification.GamificationService]
    C --> D[services.gamification_registry.ACHIEVEMENTS_REGISTRY]
    C --> E[services.attendance_stats.fetch_all_time_attendance]
    C --> F[Student Profile, XP, Rank & Achievements]
```

---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Core Invariant |
| :--- | :--- | :--- | :--- | :--- |
| [`resolve_student_rank`](#resolve_student_rank) | Function | L32–L48 | `RankDefinition` | Executes core domain logic for `resolve_student_rank`. |
| [`_check_attendance_rules`](#_check_attendance_rules) | Function | L51–L64 | `None` | Executes core domain logic for `_check_attendance_rules... |
| [`_check_punctuality_rules`](#_check_punctuality_rules) | Function | L67–L74 | `None` | Executes core domain logic for `_check_punctuality_rule... |
| [`_check_mastery_rules`](#_check_mastery_rules) | Function | L77–L84 | `None` | Executes core domain logic for `_check_mastery_rules`. |
| [`_evaluate_all_rules`](#_evaluate_all_rules) | Function | L87–L95 | `list[str]` | Executes core domain logic for `_evaluate_all_rules`. |
| [`calculate_student_xp`](#calculate_student_xp) | Function | L98–L111 | `int` | Executes core domain logic for `calculate_student_xp`. |
| [`_extract_student_metrics`](#_extract_student_metrics) | Function | L114–L121 | `dict[str, Any]` | Executes core domain logic for `_extract_student_metric... |
| [`is_starosta`](#is_starosta) | Function | L124–L126 | `bool` | Executes core domain logic for `is_starosta`. |
| [`build_student_profile`](#build_student_profile) | Function | L129–L152 | `StudentProfile` | Executes core domain logic for `build_student_profile`. |
| [`_load_cached_leaderboard`](#_load_cached_leaderboard) | Function | L155–L165 | `list[StudentProfile] | None` | Executes core domain logic for `_load_cached_leaderboar... |
| [`_save_cached_leaderboard`](#_save_cached_leaderboard) | Function | L168–L175 | `None` | Executes core domain logic for `_save_cached_leaderboar... |
| [`get_group_leaderboard`](#get_group_leaderboard) | Function | L178–L193 | `list[StudentProfile]` | Retrieves and resolves domain data for `get_group_leade... |
| [`get_student_profile_by_fio`](#get_student_profile_by_fio) | Function | L196–L210 | `StudentProfile | None` | Retrieves and resolves domain data for `get_student_pro... |

---

## 3. Comprehensive Function Specifications

### `resolve_student_rank`
```python
def resolve_student_rank(pct: float, n_count: int, o_count: int) -> RankDefinition
```

- **Source Reference**: [`services/gamification.py#L32-L48`](../../services/gamification.py#L32-L48)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `RankDefinition`

#### Overview & Architectural Purpose
Executes core domain logic for `resolve_student_rank`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `pct` | `float` | Yes | Parameter `pct` of type `float`. |
| `n_count` | `int` | Yes | Parameter `n_count` of type `int`. |
| `o_count` | `int` | Yes | Parameter `o_count` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import resolve_student_rank

# Execute call
result = resolve_student_rank(pct=..., n_count=..., o_count=...)
```

---

### `_check_attendance_rules`
```python
def _check_attendance_rules(s: dict[str, Any], unlocked: set[str]) -> None
```

- **Source Reference**: [`services/gamification.py#L51-L64`](../../services/gamification.py#L51-L64)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_check_attendance_rules`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `s` | `dict[str, Any]` | Yes | Parameter `s` of type `dict[str, Any]`. |
| `unlocked` | `set[str]` | Yes | Parameter `unlocked` of type `set[str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import _check_attendance_rules

# Execute call
result = _check_attendance_rules(s=..., unlocked=...)
```

---

### `_check_punctuality_rules`
```python
def _check_punctuality_rules(s: dict[str, Any], unlocked: set[str]) -> None
```

- **Source Reference**: [`services/gamification.py#L67-L74`](../../services/gamification.py#L67-L74)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_check_punctuality_rules`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `s` | `dict[str, Any]` | Yes | Parameter `s` of type `dict[str, Any]`. |
| `unlocked` | `set[str]` | Yes | Parameter `unlocked` of type `set[str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import _check_punctuality_rules

# Execute call
result = _check_punctuality_rules(s=..., unlocked=...)
```

---

### `_check_mastery_rules`
```python
def _check_mastery_rules(s: dict[str, Any], unlocked: set[str]) -> None
```

- **Source Reference**: [`services/gamification.py#L77-L84`](../../services/gamification.py#L77-L84)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_check_mastery_rules`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `s` | `dict[str, Any]` | Yes | Parameter `s` of type `dict[str, Any]`. |
| `unlocked` | `set[str]` | Yes | Parameter `unlocked` of type `set[str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import _check_mastery_rules

# Execute call
result = _check_mastery_rules(s=..., unlocked=...)
```

---

### `_evaluate_all_rules`
```python
def _evaluate_all_rules(s: dict[str, Any], extra: set[str] | None) -> list[str]
```

- **Source Reference**: [`services/gamification.py#L87-L95`](../../services/gamification.py#L87-L95)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[str]`

#### Overview & Architectural Purpose
Executes core domain logic for `_evaluate_all_rules`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `s` | `dict[str, Any]` | Yes | Parameter `s` of type `dict[str, Any]`. |
| `extra` | `set[str] | None` | Yes | Parameter `extra` of type `set[str] | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import _evaluate_all_rules

# Execute call
result = _evaluate_all_rules(s=..., extra=...)
```

---

### `calculate_student_xp`
```python
def calculate_student_xp(stat: dict[str, Any], unlocked_ach_ids: list[str]) -> int
```

- **Source Reference**: [`services/gamification.py#L98-L111`](../../services/gamification.py#L98-L111)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Executes core domain logic for `calculate_student_xp`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `stat` | `dict[str, Any]` | Yes | Parameter `stat` of type `dict[str, Any]`. |
| `unlocked_ach_ids` | `list[str]` | Yes | Parameter `unlocked_ach_ids` of type `list[str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import calculate_student_xp

# Execute call
result = calculate_student_xp(stat=..., unlocked_ach_ids=...)
```

---

### `_extract_student_metrics`
```python
def _extract_student_metrics(fio: str, raw_data: dict[str, Any]) -> dict[str, Any]
```

- **Source Reference**: [`services/gamification.py#L114-L121`](../../services/gamification.py#L114-L121)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Executes core domain logic for `_extract_student_metrics`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `raw_data` | `dict[str, Any]` | Yes | Parameter `raw_data` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import _extract_student_metrics

# Execute call
result = _extract_student_metrics(fio=..., raw_data=...)
```

---

### `is_starosta`
```python
def is_starosta(fio: str) -> bool
```

- **Source Reference**: [`services/gamification.py#L124-L126`](../../services/gamification.py#L124-L126)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `is_starosta`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import is_starosta

# Execute call
result = is_starosta(fio=...)
```

---

### `build_student_profile`
```python
def build_student_profile(fio: str, raw_data: dict[str, Any], extra: set[str] | None = None) -> StudentProfile
```

- **Source Reference**: [`services/gamification.py#L129-L152`](../../services/gamification.py#L129-L152)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `StudentProfile`

#### Overview & Architectural Purpose
Executes core domain logic for `build_student_profile`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `raw_data` | `dict[str, Any]` | Yes | Parameter `raw_data` of type `dict[str, Any]`. |
| `extra` | `set[str] | None` | Yes | Parameter `extra` of type `set[str] | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import build_student_profile

# Execute call
result = build_student_profile(fio=..., raw_data=..., extra=...)
```

---

### `_load_cached_leaderboard`
```python
async def _load_cached_leaderboard() -> list[StudentProfile] | None
```

- **Source Reference**: [`services/gamification.py#L155-L165`](../../services/gamification.py#L155-L165)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[StudentProfile] | None`

#### Overview & Architectural Purpose
Executes core domain logic for `_load_cached_leaderboard`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.gamification import _load_cached_leaderboard

# Execute call
result = await _load_cached_leaderboard()
```

---

### `_save_cached_leaderboard`
```python
async def _save_cached_leaderboard(profiles: list[StudentProfile]) -> None
```

- **Source Reference**: [`services/gamification.py#L168-L175`](../../services/gamification.py#L168-L175)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_save_cached_leaderboard`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `profiles` | `list[StudentProfile]` | Yes | Parameter `profiles` of type `list[StudentProfile]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.gamification import _save_cached_leaderboard

# Execute call
result = await _save_cached_leaderboard(profiles=...)
```

---

### `get_group_leaderboard`
```python
async def get_group_leaderboard( provided_stats: dict[str, Any] | None = None, force_refresh: bool = False, ) -> list[StudentProfile]
```

- **Source Reference**: [`services/gamification.py#L178-L193`](../../services/gamification.py#L178-L193)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[StudentProfile]`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_group_leaderboard`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `provided_stats` | `dict[str, Any] | None` | Yes | Parameter `provided_stats` of type `dict[str, Any] | None`. |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import get_group_leaderboard

# Execute call
result = await get_group_leaderboard(provided_stats=..., force_refresh=...)
```

---

### `get_student_profile_by_fio`
```python
async def get_student_profile_by_fio(fio: str, extra: set[str] | None = None) -> StudentProfile | None
```

- **Source Reference**: [`services/gamification.py#L196-L210`](../../services/gamification.py#L196-L210)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `StudentProfile | None`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_student_profile_by_fio`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |
| `extra` | `set[str] | None` | Yes | Parameter `extra` of type `set[str] | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.gamification import get_student_profile_by_fio

# Execute call
result = await get_student_profile_by_fio(fio=..., extra=...)
```

---
