# Component Reference: `api/deps.py`
> **File Path**: [`api/deps.py`](../../api/deps.py)
> **Subsystem**: `Security Dependencies`

## 1. Purpose
Зависимости FastAPI: авторизация по персональным API-ключам тестеров и сессиям.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_resolve_key_identity`](#_resolve_key_identity) | Function | L36–L54 | `str \| None` | Определяет владельца API-ключа (мастер-ключ или персона... |
| [`_resolve_token_identity`](#_resolve_token_identity) | Function | L57–L77 | `str \| None` | Проверяет токен (сессия Mini App или персональный ключ ... |
| [`_log_audit_access`](#_log_audit_access) | Function | L80–L89 | `None` | Записывает событие успешного доступа в системный журнал... |
| [`_extract_identity_candidates`](#_extract_identity_candidates) | Function | L92–L108 | `tuple[str \| None, bool]` | Извлекает и верифицирует идентификатор из заголовков ил... |
| [`_is_cross_site`](#_is_cross_site) | Function | L111–L125 | `bool` | Определяет, что запрос пришёл со сторонней страницы. |
| [`_reject_cookie_csrf`](#_reject_cookie_csrf) | Function | L128–L141 | `None` | Блокирует изменяющие запросы со сторонних сайтов, автор... |
| [`verify_api_or_tester`](#verify_api_or_tester) | Function | L144–L164 | `str` | Универсальная зависимость авторизации по API-ключу в за... |
| [`_identity_uid`](#_identity_uid) | Function | L167–L179 | `int \| None` | Достаёт Telegram ID из идентификатора 'tester:<uid>' ил... |
| [`verify_admin_access`](#verify_admin_access) | Function | L182–L194 | `str` | Ограничивает доступ к эндпоинту только системным админи... |
| [`verify_api_key`](#verify_api_key) | Function | L197–L209 | `str` | Проверяет статический API-ключ мастер-администратора (l... |

---

## 3. Comprehensive Function Specifications

### `_resolve_key_identity`
```python
async def _resolve_key_identity(key: str | None) -> str | None
```

- **Source Reference**: [`api/deps.py#L36-L54`](../../api/deps.py#L36-L54)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Определяет владельца API-ключа (мастер-ключ или персональный ключ тестера).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str | None` | Yes | Parameter `key` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.deps import _resolve_key_identity

# Execute call
result = await _resolve_key_identity(key=...)
```

---

### `_resolve_token_identity`
```python
async def _resolve_token_identity(token: str | None) -> str | None
```

- **Source Reference**: [`api/deps.py#L57-L77`](../../api/deps.py#L57-L77)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Проверяет токен (сессия Mini App или персональный ключ в заголовке Bearer).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `token` | `str | None` | Yes | Parameter `token` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.deps import _resolve_token_identity

# Execute call
result = await _resolve_token_identity(token=...)
```

---

### `_log_audit_access`
```python
def _log_audit_access(identity: str, request: Request) -> None
```

- **Source Reference**: [`api/deps.py#L80-L89`](../../api/deps.py#L80-L89)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Записывает событие успешного доступа в системный журнал аудита безопасности.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `identity` | `str` | Yes | Parameter `identity` of type `str`. |
| `request` | `Request` | Yes | Parameter `request` of type `Request`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.deps import _log_audit_access

# Execute call
result = _log_audit_access(identity=..., request=...)
```

---

### `_extract_identity_candidates`
```python
async def _extract_identity_candidates( key: str | None, bearer: HTTPAuthorizationCredentials | None, para_session: str | None ) -> tuple[str | None, bool]
```

- **Source Reference**: [`api/deps.py#L92-L108`](../../api/deps.py#L92-L108)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[str | None, bool]`

#### Overview & Architectural Purpose
Извлекает и верифицирует идентификатор из заголовков или cookies.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str | None` | Yes | Parameter `key` of type `str | None`. |
| `bearer` | `HTTPAuthorizationCredentials | None` | Yes | Parameter `bearer` of type `HTTPAuthorizationCredentials | None`. |
| `para_session` | `str | None` | Yes | Parameter `para_session` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.deps import _extract_identity_candidates

# Execute call
result = await _extract_identity_candidates(key=..., bearer=..., para_session=...)
```

---

### `_is_cross_site`
```python
def _is_cross_site(request: Request) -> bool
```

- **Source Reference**: [`api/deps.py#L111-L125`](../../api/deps.py#L111-L125)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Определяет, что запрос пришёл со сторонней страницы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request` | `Request` | Yes | Parameter `request` of type `Request`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.deps import _is_cross_site

# Execute call
result = _is_cross_site(request=...)
```

---

### `_reject_cookie_csrf`
```python
def _reject_cookie_csrf(request: Request) -> None
```

- **Source Reference**: [`api/deps.py#L128-L141`](../../api/deps.py#L128-L141)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Блокирует изменяющие запросы со сторонних сайтов, авторизованные кукой.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request` | `Request` | Yes | Parameter `request` of type `Request`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.deps import _reject_cookie_csrf

# Execute call
result = _reject_cookie_csrf(request=...)
```

---

### `verify_api_or_tester`
```python
async def verify_api_or_tester( request: Request, key: str | None = Security(_api_key_header), bearer: HTTPAuthorizationCredentials | None = Security(_bearer_scheme), para_session: str | None = Cookie(default=None), ) -> str
```

- **Source Reference**: [`api/deps.py#L144-L164`](../../api/deps.py#L144-L164)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Универсальная зависимость авторизации по API-ключу в заголовке, Bearer-токену или cookie.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request` | `Request` | Yes | Parameter `request` of type `Request`. |
| `key` | `str | None` | Yes | Parameter `key` of type `str | None`. |
| `bearer` | `HTTPAuthorizationCredentials | None` | Yes | Parameter `bearer` of type `HTTPAuthorizationCredentials | None`. |
| `para_session` | `str | None` | Yes | Parameter `para_session` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.deps import verify_api_or_tester

# Execute call
result = await verify_api_or_tester(request=..., key=..., bearer=...)
```

---

### `_identity_uid`
```python
def _identity_uid(identity: str) -> int | None
```

- **Source Reference**: [`api/deps.py#L167-L179`](../../api/deps.py#L167-L179)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Достаёт Telegram ID из идентификатора 'tester:<uid>' или 'classmate:<uid>'.

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
from api.deps import _identity_uid

# Execute call
result = _identity_uid(identity=...)
```

---

### `verify_admin_access`
```python
async def verify_admin_access(auth_identity: str = Depends(verify_api_or_tester)) -> str
```

- **Source Reference**: [`api/deps.py#L182-L194`](../../api/deps.py#L182-L194)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Ограничивает доступ к эндпоинту только системным администраторам и старостату.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `auth_identity` | `str` | Yes | Parameter `auth_identity` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.deps import verify_admin_access

# Execute call
result = await verify_admin_access(auth_identity=...)
```

---

### `verify_api_key`
```python
async def verify_api_key(key: str | None = Security(_api_key_header)) -> str
```

- **Source Reference**: [`api/deps.py#L197-L209`](../../api/deps.py#L197-L209)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Проверяет статический API-ключ мастер-администратора (legacy-совместимость).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `key` | `str | None` | Yes | Parameter `key` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.deps import verify_api_key

# Execute call
result = await verify_api_key(key=...)
```

---
