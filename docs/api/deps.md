# Module Specification: `api/deps.py`
> **Path**: [`api/deps.py`](file:///home/u/Рабочий стол/para/api/deps.py)  
> **Subsystem**: `Security Dependencies`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Зависимости FastAPI: авторизация по персональным API-ключам тестеров и сессиям. Обеспечивает сквозной аудит: логирует кто (ID тестера), когда и какой метод вызвал.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_resolve_key_identity`](#_resolve_key_identity) | Function | L28–L37 | `str | None` | Определяет владельца API-ключа (мастер-ключ или персональный |
| [`_resolve_token_identity`](#_resolve_token_identity) | Function | L40–L48 | `str | None` | Проверяет токен (сессия Mini App или персональный ключ в Bea |
| [`_log_audit_access`](#_log_audit_access) | Function | L51–L54 | `None` | Записывает событие успешного доступа в системный журнал ауди |
| [`verify_api_or_tester`](#verify_api_or_tester) | Function | L57–L72 | `str` | Универсальная авторизация по API-ключу, Bearer-токену или co |
| [`verify_admin_access`](#verify_admin_access) | Function | L75–L84 | `str` | Ограничивает доступ только системным администраторам и масте |
| [`verify_api_key`](#verify_api_key) | Function | L87–L97 | `str` | Проверяет статический API-ключ мастер-администратора (legacy |

---

## 3. Exhaustive Function Specifications

### `_resolve_key_identity`
- **Signature**: `async def _resolve_key_identity(key: str | None) -> str | None`
- **Source Reference**: [api/deps.py#L28-L37](file:///home/u/Рабочий стол/para/api/deps.py#L28-L37)
- **Async**: `Yes`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Определяет владельца API-ключа (мастер-ключ или персональный ключ тестера).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `key` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not key:`
2. `if hmac.compare_digest(key, API_SECRET_KEY):`
3. `uid = await get_tester_by_key(key)`
4. `if uid and await is_tester_allowed(uid):`
5. `return None`

---

### `_resolve_token_identity`
- **Signature**: `async def _resolve_token_identity(token: str | None) -> str | None`
- **Source Reference**: [api/deps.py#L40-L48](file:///home/u/Рабочий стол/para/api/deps.py#L40-L48)
- **Async**: `Yes`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Проверяет токен (сессия Mini App или персональный ключ в Bearer).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `token` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not token:`
2. `if token.startswith(API_TESTER_KEY_PREFIX):`
3. `uid = verify_tester_session(token)`
4. `return f"tester:{uid}" if uid and await is_tester_allowed(uid) else None`

---

### `_log_audit_access`
- **Signature**: `def _log_audit_access(identity: str, request: Request) -> None`
- **Source Reference**: [api/deps.py#L51-L54](file:///home/u/Рабочий стол/para/api/deps.py#L51-L54)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Записывает событие успешного доступа в системный журнал аудита.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `identity` | `str` | Input parameter |
| `request` | `Request` | Input parameter |

#### Step-by-Step Logic Execution
1. `client_ip = request.client.host if request.client else "unknown"`
2. `log.info(f"🔎 [AUDIT] {identity} -> {request.method} {request.url.path} (IP: {client_i`

---

### `verify_api_or_tester`
- **Signature**: `async def verify_api_or_tester( request: Request, key: str | None = Security(_api_key_header), bearer: HTTPAuthorizationCredentials | None = Security(_bearer_scheme), para_session: str | None = Cookie(default=None), ) -> str`
- **Source Reference**: [api/deps.py#L57-L72](file:///home/u/Рабочий стол/para/api/deps.py#L57-L72)
- **Async**: `Yes`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Универсальная авторизация по API-ключу, Bearer-токену или cookie с аудитом.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `request` | `Request` | Input parameter |
| `key` | `str | None` | Input parameter |
| `bearer` | `HTTPAuthorizationCredentials | None` | Input parameter |
| `para_session` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `ident = await _resolve_key_identity(key)`
2. `if not ident:`
3. `if ident:`
4. `log.warning(f"⚠️ Неавторизованный запрос к {request.method} {request.url.path}")`
5. `raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key`

---

### `verify_admin_access`
- **Signature**: `async def verify_admin_access(auth_identity: str = Depends(verify_api_or_tester)) -> str`
- **Source Reference**: [api/deps.py#L75-L84](file:///home/u/Рабочий стол/para/api/deps.py#L75-L84)
- **Async**: `Yes`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Ограничивает доступ только системным администраторам и мастер-ключу.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `auth_identity` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if auth_identity == "master_admin":`
2. `if auth_identity.startswith("tester:"):`
3. `log.warning(f"🚫 Попытка несанкционированного доступа: {auth_identity}")`
4. `raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access requi`

---

### `verify_api_key`
- **Signature**: `async def verify_api_key(key: str | None = Security(_api_key_header)) -> str`
- **Source Reference**: [api/deps.py#L87-L97](file:///home/u/Рабочий стол/para/api/deps.py#L87-L97)
- **Async**: `Yes`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Проверяет статический API-ключ мастер-администратора (legacy-совместимость). Использует hmac.compare_digest для защиты от атак по времени (timing attack). Возвращает строку ключа или выбрасывает HTTP 403 Forbidden.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `key` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not key or not hmac.compare_digest(key, API_SECRET_KEY):`
2. `return key`

---
