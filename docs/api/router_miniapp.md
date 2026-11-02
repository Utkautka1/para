# Component Reference: `api/router/miniapp.py`
> **File Path**: [`api/router/miniapp.py`](../../api/router/miniapp.py)
> **Subsystem**: `MiniApp API`

## 1. Purpose
Роутер Telegram Mini App и аутентификации тестеров Swagger UI.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_set_tester_cookie`](#_set_tester_cookie) | Function | L60–L78 | `None` | Устанавливает подписанную защищенную сессионную куку те... |
| [`serve_miniapp_page`](#serve_miniapp_page) | Function | L82–L98 | `HTMLResponse` | Отдаёт одностраничный интерфейс Telegram Mini App порта... |
| [`_resolve_api_key_user`](#_resolve_api_key_user) | Function | L101–L111 | `tuple[int, str, str] \| None` | Определяет Telegram ID и профиль пользователя по мастер... |
| [`login_by_token`](#login_by_token) | Function | L115–L136 | `Response` | Обменивает одноразовый токен из ссылки бота на сессионн... |
| [`_auth_by_key`](#_auth_by_key) | Function | L139–L147 | `MiniappAuthResponse` | Проверяет ключ доступа и устанавливает сессионную куку ... |
| [`_auth_telegram_init`](#_auth_telegram_init) | Function | L150–L164 | `MiniappAuthResponse` | Валидирует подпись Telegram initData и проверяет права ... |
| [`authenticate_miniapp`](#authenticate_miniapp) | Function | L168–L174 | `MiniappAuthResponse` | Аутентифицирует пользователя по Telegram initData или к... |
| [`check_tester_status`](#check_tester_status) | Function | L178–L196 | `MiniappCheckResponse` | Проверяет статус авторизации и наличие прав тестера по ... |
| [`resolve_action_uid`](#resolve_action_uid) | Function | L199–L209 | `int \| None` | Определяет Telegram ID инициатора действия из сессии ил... |
| [`_action_result`](#_action_result) | Function | L222–L230 | `MiniappActionResult` | Собирает ответ action-эндпоинта с паспортом открытой ач... |
| [`require_group_member`](#require_group_member) | Function | L233–L243 | `int` | Пропускает только одногруппников: валидный initData ест... |
| [`trigger_miniapp_action`](#trigger_miniapp_action) | Function | L247–L259 | `MiniappActionResult` | Разблокирует клиентские достижения Mini App (пасхалки, ... |
| [`list_api_testers`](#list_api_testers) | Function | L263–L276 | `TesterListResponse` | Возвращает список всех зарегистрированных тестеров Swag... |
| [`api_add_tester`](#api_add_tester) | Function | L280–L294 | `TesterActionResponse` | Добавляет пользователя в постоянный список тестеров API... |
| [`api_remove_tester`](#api_remove_tester) | Function | L298–L312 | `TesterActionResponse` | Удаляет пользователя из списка авторизованных тестеров ... |

---

## 3. Comprehensive Function Specifications

### `_set_tester_cookie`
```python
def _set_tester_cookie(response: Response, user_id: int) -> None
```

- **Source Reference**: [`api/router/miniapp.py#L60-L78`](../../api/router/miniapp.py#L60-L78)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Устанавливает подписанную защищенную сессионную куку тестера.

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

- **Source Reference**: [`api/router/miniapp.py#L82-L98`](../../api/router/miniapp.py#L82-L98)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `HTMLResponse`

#### Overview & Architectural Purpose
Отдаёт одностраничный интерфейс Telegram Mini App портала со встроенным Swagger UI.

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

- **Source Reference**: [`api/router/miniapp.py#L101-L111`](../../api/router/miniapp.py#L101-L111)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[int, str, str] | None`

#### Overview & Architectural Purpose
Определяет Telegram ID и профиль пользователя по мастер-ключу или ключу тестера.

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

- **Source Reference**: [`api/router/miniapp.py#L115-L136`](../../api/router/miniapp.py#L115-L136)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Response`

#### Overview & Architectural Purpose
Обменивает одноразовый токен из ссылки бота на сессионную куку.

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

- **Source Reference**: [`api/router/miniapp.py#L139-L147`](../../api/router/miniapp.py#L139-L147)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappAuthResponse`

#### Overview & Architectural Purpose
Проверяет ключ доступа и устанавливает сессионную куку тестера.

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

- **Source Reference**: [`api/router/miniapp.py#L150-L164`](../../api/router/miniapp.py#L150-L164)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappAuthResponse`

#### Overview & Architectural Purpose
Валидирует подпись Telegram initData и проверяет права студента или тестера.

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

- **Source Reference**: [`api/router/miniapp.py#L168-L174`](../../api/router/miniapp.py#L168-L174)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappAuthResponse`

#### Overview & Architectural Purpose
Аутентифицирует пользователя по Telegram initData или ключу доступа.

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

- **Source Reference**: [`api/router/miniapp.py#L178-L196`](../../api/router/miniapp.py#L178-L196)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappCheckResponse`

#### Overview & Architectural Purpose
Проверяет статус авторизации и наличие прав тестера по сессионной куке.

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

- **Source Reference**: [`api/router/miniapp.py#L199-L209`](../../api/router/miniapp.py#L199-L209)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Определяет Telegram ID инициатора действия из сессии или init_data.

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

- **Source Reference**: [`api/router/miniapp.py#L222-L230`](../../api/router/miniapp.py#L222-L230)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `MiniappActionResult`

#### Overview & Architectural Purpose
Собирает ответ action-эндпоинта с паспортом открытой ачивки.

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

- **Source Reference**: [`api/router/miniapp.py#L233-L243`](../../api/router/miniapp.py#L233-L243)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
Пропускает только одногруппников: валидный initData есть у любого, кто открыл бота.

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

- **Source Reference**: [`api/router/miniapp.py#L247-L259`](../../api/router/miniapp.py#L247-L259)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `MiniappActionResult`

#### Overview & Architectural Purpose
Разблокирует клиентские достижения Mini App (пасхалки, темы, вкладки, профили).

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

- **Source Reference**: [`api/router/miniapp.py#L263-L276`](../../api/router/miniapp.py#L263-L276)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TesterListResponse`

#### Overview & Architectural Purpose
Возвращает список всех зарегистрированных тестеров Swagger UI.

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
async def api_add_tester(user_id: int) -> TesterActionResponse
```

- **Source Reference**: [`api/router/miniapp.py#L280-L294`](../../api/router/miniapp.py#L280-L294)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TesterActionResponse`

#### Overview & Architectural Purpose
Добавляет пользователя в постоянный список тестеров API (Admin only).

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
async def api_remove_tester(user_id: int) -> TesterActionResponse
```

- **Source Reference**: [`api/router/miniapp.py#L298-L312`](../../api/router/miniapp.py#L298-L312)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `TesterActionResponse`

#### Overview & Architectural Purpose
Удаляет пользователя из списка авторизованных тестеров API (Admin only).

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
