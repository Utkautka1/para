# Module Specification: `api/handlers.py`
> **Path**: [`api/handlers.py`](file:///home/u/Рабочий стол/para/api/handlers.py)  
> **Subsystem**: `REST Request Handlers`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Централизованные обработчики исключений (Exception Handlers) для para-api. Зачем существует этот модуль: Перехватывает все исключения приложения, обеспечивает единый формат JSON-ответов (совместимый с Pydantic ErrorDetail) и логирует критические ошибки.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`http_exception_handler`](#http_exception_handler) | Function | L19–L22 | `JSONResponse` | Обрабатывает стандартные HTTPException и возвращает унифицир |
| [`validation_exception_handler`](#validation_exception_handler) | Function | L25–L31 | `JSONResponse` | Обрабатывает ошибки валидации параметров Pydantic (HTTP 422) |
| [`unhandled_exception_handler`](#unhandled_exception_handler) | Function | L34–L38 | `JSONResponse` | Перехватывает любые непредвиденные сбои, логирует стек и воз |
| [`register_exception_handlers`](#register_exception_handlers) | Function | L41–L45 | `None` | Регистрирует все централизованные обработчики исключений в п |

---

## 3. Exhaustive Function Specifications

### `http_exception_handler`
- **Signature**: `async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse`
- **Source Reference**: [api/handlers.py#L19-L22](file:///home/u/Рабочий стол/para/api/handlers.py#L19-L22)
- **Async**: `Yes`
- **Return Type**: `JSONResponse`

#### Purpose & Architectural Intent
Обрабатывает стандартные HTTPException и возвращает унифицированный JSON.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `request` | `Request` | Input parameter |
| `exc` | `HTTPException` | Input parameter |

#### Step-by-Step Logic Execution
1. `payload = ErrorDetail(detail=str(exc.detail), code=f"HTTP_{exc.status_code}")`
2. `return JSONResponse(status_code=exc.status_code, content=payload.model_dump())`

---

### `validation_exception_handler`
- **Signature**: `async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse`
- **Source Reference**: [api/handlers.py#L25-L31](file:///home/u/Рабочий стол/para/api/handlers.py#L25-L31)
- **Async**: `Yes`
- **Return Type**: `JSONResponse`

#### Purpose & Architectural Intent
Обрабатывает ошибки валидации параметров Pydantic (HTTP 422).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `request` | `Request` | Input parameter |
| `exc` | `RequestValidationError` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.warning(f"⚠️ Ошибка валидации {request.method} {request.url.path}: {exc.errors()}`
2. `return JSONResponse(`

---

### `unhandled_exception_handler`
- **Signature**: `async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse`
- **Source Reference**: [api/handlers.py#L34-L38](file:///home/u/Рабочий стол/para/api/handlers.py#L34-L38)
- **Async**: `Yes`
- **Return Type**: `JSONResponse`

#### Purpose & Architectural Intent
Перехватывает любые непредвиденные сбои, логирует стек и возвращает HTTP 500.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `request` | `Request` | Input parameter |
| `exc` | `Exception` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.error(f"❌ Критический сбой при вызове {request.method} {request.url.path}: {exc}"`
2. `payload = ErrorDetail(detail="Внутренняя ошибка сервера", code="INTERNAL_SERVER_ERROR`
3. `return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payloa`

---

### `register_exception_handlers`
- **Signature**: `def register_exception_handlers(app: FastAPI) -> None`
- **Source Reference**: [api/handlers.py#L41-L45](file:///home/u/Рабочий стол/para/api/handlers.py#L41-L45)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Регистрирует все централизованные обработчики исключений в приложении.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `app` | `FastAPI` | Input parameter |

#### Step-by-Step Logic Execution
1. `app.add_exception_handler(HTTPException, http_exception_handler)`
2. `app.add_exception_handler(RequestValidationError, validation_exception_handler)`
3. `app.add_exception_handler(Exception, unhandled_exception_handler)`

---
