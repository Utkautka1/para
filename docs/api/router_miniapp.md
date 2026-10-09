# Module Specification: `api/router/miniapp.py`
> **Path**: [`api/router/miniapp.py`](file:///home/u/Рабочий стол/para/api/router/miniapp.py)  
> **Subsystem**: `MiniApp API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер Telegram Mini App и аутентификации тестеров Swagger UI. Обеспечивает защищённый доступ к документации и эндпоинтам API через валидацию HMAC-SHA256 подписи Telegram initData и управление сессионными куками.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_set_tester_cookie`](#_set_tester_cookie) | Function | L42–L52 | `None` | Устанавливает подписанную защищенную сессионную куку тестера |
| [`serve_miniapp_page`](#serve_miniapp_page) | Function | L56–L60 | `HTMLResponse` | Отдаёт интерфейс Telegram Mini App портала со встроенным Swa |
| [`authenticate_miniapp`](#authenticate_miniapp) | Function | L64–L74 | `MiniappAuthResponse` | Аутентифицирует пользователя по Telegram initData и выдает с |
| [`check_tester_status`](#check_tester_status) | Function | L78–L86 | `MiniappCheckResponse` | Возвращает статус авторизации текущего пользователя. |
| [`list_api_testers`](#list_api_testers) | Function | L90–L94 | `TesterListResponse` | Возвращает список всех зарегистрированных тестеров API. |
| [`api_add_tester`](#api_add_tester) | Function | L98–L103 | `dict` | Добавляет пользователя в белый список тестеров API (Admin on |
| [`api_remove_tester`](#api_remove_tester) | Function | L107–L112 | `dict` | Удаляет пользователя из белого списка тестеров API (Admin on |

---

## 3. Exhaustive Function Specifications

### `_set_tester_cookie`
- **Signature**: `def _set_tester_cookie(response: Response, user_id: int) -> None`
- **Source Reference**: [api/router/miniapp.py#L42-L52](file:///home/u/Рабочий стол/para/api/router/miniapp.py#L42-L52)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Устанавливает подписанную защищенную сессионную куку тестера.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `response` | `Response` | Input parameter |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `token = generate_tester_session(user_id)`
2. `response.set_cookie(`

---

### `serve_miniapp_page`
- **Signature**: `async def serve_miniapp_page() -> HTMLResponse`
- **Source Reference**: [api/router/miniapp.py#L56-L60](file:///home/u/Рабочий стол/para/api/router/miniapp.py#L56-L60)
- **Async**: `Yes`
- **Return Type**: `HTMLResponse`

#### Purpose & Architectural Intent
Отдаёт интерфейс Telegram Mini App портала со встроенным Swagger UI.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `if _HTML_PATH.exists():`
2. `return HTMLResponse(content="<h1>para-api Mini App</h1>", status_code=200)`

---

### `authenticate_miniapp`
- **Signature**: `async def authenticate_miniapp(payload: MiniappAuthRequest, response: Response) -> MiniappAuthResponse`
- **Source Reference**: [api/router/miniapp.py#L64-L74](file:///home/u/Рабочий стол/para/api/router/miniapp.py#L64-L74)
- **Async**: `Yes`
- **Return Type**: `MiniappAuthResponse`

#### Purpose & Architectural Intent
Аутентифицирует пользователя по Telegram initData и выдает сессию.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `payload` | `MiniappAuthRequest` | Input parameter |
| `response` | `Response` | Input parameter |

#### Step-by-Step Logic Execution
1. `info = validate_telegram_init_data(payload.init_data)`
2. `if not info or "id" not in info:`
3. `user_id = int(info["id"])`
4. `if not await is_tester_allowed(user_id):`
5. `_set_tester_cookie(response, user_id)`
6. `return MiniappAuthResponse(user_id=user_id, first_name=info.get("first_name"), userna`

---

### `check_tester_status`
- **Signature**: `async def check_tester_status(para_session: str = Cookie(default=None)) -> MiniappCheckResponse`
- **Source Reference**: [api/router/miniapp.py#L78-L86](file:///home/u/Рабочий стол/para/api/router/miniapp.py#L78-L86)
- **Async**: `Yes`
- **Return Type**: `MiniappCheckResponse`

#### Purpose & Architectural Intent
Возвращает статус авторизации текущего пользователя.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `para_session` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not para_session:`
2. `uid = verify_tester_session(para_session)`
3. `if uid is None:`
4. `allowed = await is_tester_allowed(uid)`
5. `return MiniappCheckResponse(authenticated=True, user_id=uid, is_tester=allowed)`

---

### `list_api_testers`
- **Signature**: `async def list_api_testers() -> TesterListResponse`
- **Source Reference**: [api/router/miniapp.py#L90-L94](file:///home/u/Рабочий стол/para/api/router/miniapp.py#L90-L94)
- **Async**: `Yes`
- **Return Type**: `TesterListResponse`

#### Purpose & Architectural Intent
Возвращает список всех зарегистрированных тестеров API.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `uids = await get_all_testers()`
2. `items = [TesterItemResponse(user_id=u, is_admin=(u in {ALLOWED_USER_ID, DEPUTY_USER_I`
3. `return TesterListResponse(count=len(items), testers=items)`

---

### `api_add_tester`
- **Signature**: `async def api_add_tester(user_id: int) -> dict`
- **Source Reference**: [api/router/miniapp.py#L98-L103](file:///home/u/Рабочий стол/para/api/router/miniapp.py#L98-L103)
- **Async**: `Yes`
- **Return Type**: `dict`

#### Purpose & Architectural Intent
Добавляет пользователя в белый список тестеров API (Admin only).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `success = await add_tester(user_id)`
2. `if not success:`
3. `return {"status": "ok", "user_id": user_id}`

---

### `api_remove_tester`
- **Signature**: `async def api_remove_tester(user_id: int) -> dict`
- **Source Reference**: [api/router/miniapp.py#L107-L112](file:///home/u/Рабочий стол/para/api/router/miniapp.py#L107-L112)
- **Async**: `Yes`
- **Return Type**: `dict`

#### Purpose & Architectural Intent
Удаляет пользователя из белого списка тестеров API (Admin only).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `success = await remove_tester(user_id)`
2. `if not success:`
3. `return {"status": "ok", "user_id": user_id}`

---
