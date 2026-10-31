# Component Reference: `api/router/miniapp.py`
> **File Path**: [`api/router/miniapp.py`](../../api/router/miniapp.py)
> **Subsystem**: `MiniApp API`
> **Architecture Layer**: `Enterprise Microservice Subsystem`
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`
> **Persistence Backend**: `Redis 7 Persistent Store`
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `api/router/miniapp.py` module implements core operational logic for the `MiniApp API` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

### Component Architecture & Data Flow
```mermaid
graph LR
    Inbound[Inbound Request] --> Logic[Domain Service Logic]
    Logic --> Redis[(Redis 7 State Store)]
    Logic --> Outbound[Outbound Event Dispatch]
```

---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Core Invariant |
| :--- | :--- | :--- | :--- | :--- |
| [`_set_tester_cookie`](#_set_tester_cookie) | Function | L55–L73 | `None` | Executes core domain logic for `_set_tester_cookie`. |
| [`serve_miniapp_page`](#serve_miniapp_page) | Function | L77–L93 | `HTMLResponse` | Executes core domain logic for `serve_miniapp_page`. |
| [`_resolve_api_key_user`](#_resolve_api_key_user) | Function | L96–L106 | `tuple[int, str, str] | None` | Executes core domain logic for `_resolve_api_key_user`. |
| [`login_by_token`](#login_by_token) | Function | L110–L131 | `Response` | Executes core domain logic for `login_by_token`. |
| [`_auth_by_key`](#_auth_by_key) | Function | L134–L142 | `MiniappAuthResponse` | Executes core domain logic for `_auth_by_key`. |
| [`_auth_telegram_init`](#_auth_telegram_init) | Function | L145–L160 | `MiniappAuthResponse` | Executes core domain logic for `_auth_telegram_init`. |
| [`authenticate_miniapp`](#authenticate_miniapp) | Function | L164–L170 | `MiniappAuthResponse` | Executes core domain logic for `authenticate_miniapp`. |
| [`check_tester_status`](#check_tester_status) | Function | L174–L192 | `MiniappCheckResponse` | Executes core domain logic for `check_tester_status`. |
| [`resolve_action_uid`](#resolve_action_uid) | Function | L195–L205 | `int | None` | Executes core domain logic for `resolve_action_uid`. |
| [`_action_result`](#_action_result) | Function | L218–L227 | `MiniappActionResult` | Executes core domain logic for `_action_result`. |
| [`require_group_member`](#require_group_member) | Function | L230–L240 | `int` | Executes core domain logic for `require_group_member`. |
| [`trigger_miniapp_action`](#trigger_miniapp_action) | Function | L244–L258 | `MiniappActionResult` | Executes core domain logic for `trigger_miniapp_action`... |
| [`list_api_testers`](#list_api_testers) | Function | L262–L275 | `TesterListResponse` | Executes core domain logic for `list_api_testers`. |
| [`api_add_tester`](#api_add_tester) | Function | L279–L293 | `dict` | Executes core domain logic for `api_add_tester`. |
| [`api_remove_tester`](#api_remove_tester) | Function | L297–L311 | `dict` | Executes core domain logic for `api_remove_tester`. |

---

## 3. Comprehensive Function Specifications

### `_set_tester_cookie`
```python
def _set_tester_cookie(response: Response, user_id: int) -> None
```

- **Source Reference**: [`api/router/miniapp.py#L55-L73`](../../api/router/miniapp.py#L55-L73)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_set_tester_cookie`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `response` | `Response` | Yes | Parameter `response` of type `Response`. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.miniapp import _set_tester_cookie

# Execute call
result = _set_tester_cookie(response=..., user_id=...)
```

---

### `serve_miniapp_page`
```python
async def serve_miniapp_page() -> HTMLResponse
```

- **Source Reference**: [`api/router/miniapp.py#L77-L93`](../../api/router/miniapp.py#L77-L93)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `HTMLResponse`

#### Overview & Architectural Purpose
Executes core domain logic for `serve_miniapp_page`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from api.router.miniapp import serve_miniapp_page

# Execute call
result = await serve_miniapp_page()
```

---

### `_resolve_api_key_user`
```python
async def _resolve_api_key_user(key: str) -> tuple[int, str, str] | None
```

- **Source Reference**: [`api/router/miniapp.py#L96-L106`](../../api/router/miniapp.py#L96-L106)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[int, str, str] | None`

#### Overview & Architectural Purpose
Executes core domain logic for `_resolve_api_key_user`.

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
from api.router.miniapp import _resolve_api_key_user

# Execute call
result = await _resolve_api_key_user(key=...)
```

---

### `login_by_token`
```python
async def login_by_token( t: str = Query(..., description="Одноразовый токен входа из бота"), next_target: str = Query(default="miniapp", alias="next"), ) -> Response
```

- **Source Reference**: [`api/router/miniapp.py#L110-L131`](../../api/router/miniapp.py#L110-L131)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Response`

#### Overview & Architectural Purpose
Executes core domain logic for `login_by_token`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `t` | `str` | Yes | Parameter `t` of type `str`. |
| `next_target` | `str` | Yes | Parameter `next_target` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.miniapp import login_by_token

# Execute call
result = await login_by_token(t=..., next_target=...)
```

---

### `_auth_by_key`
```python
async def _auth_by_key(api_key: str, response: Response) -> MiniappAuthResponse
```

- **Source Reference**: [`api/router/miniapp.py#L134-L142`](../../api/router/miniapp.py#L134-L142)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappAuthResponse`

#### Overview & Architectural Purpose
Executes core domain logic for `_auth_by_key`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `api_key` | `str` | Yes | Parameter `api_key` of type `str`. |
| `response` | `Response` | Yes | Parameter `response` of type `Response`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.miniapp import _auth_by_key

# Execute call
result = await _auth_by_key(api_key=..., response=...)
```

---

### `_auth_telegram_init`
```python
async def _auth_telegram_init(init_data: str, response: Response) -> MiniappAuthResponse
```

- **Source Reference**: [`api/router/miniapp.py#L145-L160`](../../api/router/miniapp.py#L145-L160)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappAuthResponse`

#### Overview & Architectural Purpose
Executes core domain logic for `_auth_telegram_init`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `init_data` | `str` | Yes | Parameter `init_data` of type `str`. |
| `response` | `Response` | Yes | Parameter `response` of type `Response`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.miniapp import _auth_telegram_init

# Execute call
result = await _auth_telegram_init(init_data=..., response=...)
```

---

### `authenticate_miniapp`
```python
async def authenticate_miniapp(payload: MiniappAuthRequest, response: Response) -> MiniappAuthResponse
```

- **Source Reference**: [`api/router/miniapp.py#L164-L170`](../../api/router/miniapp.py#L164-L170)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappAuthResponse`

#### Overview & Architectural Purpose
Executes core domain logic for `authenticate_miniapp`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `payload` | `MiniappAuthRequest` | Yes | Parameter `payload` of type `MiniappAuthRequest`. |
| `response` | `Response` | Yes | Parameter `response` of type `Response`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.miniapp import authenticate_miniapp

# Execute call
result = await authenticate_miniapp(payload=..., response=...)
```

---

### `check_tester_status`
```python
async def check_tester_status(para_session: str = Cookie(default=None)) -> MiniappCheckResponse
```

- **Source Reference**: [`api/router/miniapp.py#L174-L192`](../../api/router/miniapp.py#L174-L192)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappCheckResponse`

#### Overview & Architectural Purpose
Executes core domain logic for `check_tester_status`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `para_session` | `str` | Yes | Parameter `para_session` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.miniapp import check_tester_status

# Execute call
result = await check_tester_status(para_session=...)
```

---

### `resolve_action_uid`
```python
def resolve_action_uid(init_data: str | None, session: str | None) -> int | None
```

- **Source Reference**: [`api/router/miniapp.py#L195-L205`](../../api/router/miniapp.py#L195-L205)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Executes core domain logic for `resolve_action_uid`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `init_data` | `str | None` | Yes | Parameter `init_data` of type `str | None`. |
| `session` | `str | None` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.miniapp import resolve_action_uid

# Execute call
result = resolve_action_uid(init_data=..., session=...)
```

---

### `_action_result`
```python
def _action_result(ach_id: str | None, unlocked: bool) -> MiniappActionResult
```

- **Source Reference**: [`api/router/miniapp.py#L218-L227`](../../api/router/miniapp.py#L218-L227)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `MiniappActionResult`

#### Overview & Architectural Purpose
Executes core domain logic for `_action_result`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `ach_id` | `str | None` | Yes | Parameter `ach_id` of type `str | None`. |
| `unlocked` | `bool` | Yes | Parameter `unlocked` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.miniapp import _action_result

# Execute call
result = _action_result(ach_id=..., unlocked=...)
```

---

### `require_group_member`
```python
def require_group_member(uid: int | None) -> int
```

- **Source Reference**: [`api/router/miniapp.py#L230-L240`](../../api/router/miniapp.py#L230-L240)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Executes core domain logic for `require_group_member`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `uid` | `int | None` | Yes | Parameter `uid` of type `int | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.miniapp import require_group_member

# Execute call
result = require_group_member(uid=...)
```

---

### `trigger_miniapp_action`
```python
async def trigger_miniapp_action( payload: MiniappActionRequest, para_session: str | None = Cookie(default=None) ) -> MiniappActionResult
```

- **Source Reference**: [`api/router/miniapp.py#L244-L258`](../../api/router/miniapp.py#L244-L258)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappActionResult`

#### Overview & Architectural Purpose
Executes core domain logic for `trigger_miniapp_action`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `payload` | `MiniappActionRequest` | Yes | Parameter `payload` of type `MiniappActionRequest`. |
| `para_session` | `str | None` | Yes | Parameter `para_session` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.miniapp import trigger_miniapp_action

# Execute call
result = await trigger_miniapp_action(payload=..., para_session=...)
```

---

### `list_api_testers`
```python
async def list_api_testers() -> TesterListResponse
```

- **Source Reference**: [`api/router/miniapp.py#L262-L275`](../../api/router/miniapp.py#L262-L275)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TesterListResponse`

#### Overview & Architectural Purpose
Executes core domain logic for `list_api_testers`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.miniapp import list_api_testers

# Execute call
result = await list_api_testers()
```

---

### `api_add_tester`
```python
async def api_add_tester(user_id: int) -> dict
```

- **Source Reference**: [`api/router/miniapp.py#L279-L293`](../../api/router/miniapp.py#L279-L293)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict`

#### Overview & Architectural Purpose
Executes core domain logic for `api_add_tester`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.miniapp import api_add_tester

# Execute call
result = await api_add_tester(user_id=...)
```

---

### `api_remove_tester`
```python
async def api_remove_tester(user_id: int) -> dict
```

- **Source Reference**: [`api/router/miniapp.py#L297-L311`](../../api/router/miniapp.py#L297-L311)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict`

#### Overview & Architectural Purpose
Executes core domain logic for `api_remove_tester`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.miniapp import api_remove_tester

# Execute call
result = await api_remove_tester(user_id=...)
```

---
