# Module Specification: `api.py`
> **Path**: [`api.py`](file:///home/u/Рабочий стол/para/api.py)  
> **Subsystem**: `Ingress Gateway`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Точка входа сервиса para-api (FastAPI + gRPC Server + Swagger UI). Единая точка доступа к данным расписания, экзаменов, преподавателей и посещаемости. Поддерживает gRPC (порт GRPC_PORT) и HTTP REST со Swagger UI (порт 8000).

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_InvalidHttpFilter.filter`](#_invalidhttpfilterfilter) | Method | L25–L26 | `bool` | Method |
| [`lifespan`](#lifespan) | Function | L30–L38 | `AsyncGenerator[None, None]` | Управляет жизненным циклом gRPC-сервера параллельно с FastAP |

---

## 3. Exhaustive Function Specifications

## Class: `_InvalidHttpFilter`
Подавляет спам от сетевых сканеров и SSL-хэндшейков на чистом HTTP-порту.

### `_InvalidHttpFilter.filter`
- **Signature**: `def filter(self, record: logging.LogRecord) -> bool`
- **Source Reference**: [api.py#L25-L26](file:///home/u/Рабочий стол/para/api.py#L25-L26)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Executes internal domain logic according to service invariants.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `record` | `logging.LogRecord` | Input parameter |

#### Step-by-Step Logic Execution
1. `return "Invalid HTTP request received" not in record.getMessage()`

---

### `lifespan`
- **Signature**: `async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]`
- **Source Reference**: [api.py#L30-L38](file:///home/u/Рабочий стол/para/api.py#L30-L38)
- **Async**: `Yes`
- **Return Type**: `AsyncGenerator[None, None]`

#### Purpose & Architectural Intent
Управляет жизненным циклом gRPC-сервера параллельно с FastAPI.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `app` | `FastAPI` | Input parameter |

#### Step-by-Step Logic Execution
1. `grpc_server = create_grpc_server()`
2. `await start_grpc_server(grpc_server, GRPC_HOST, GRPC_PORT)`
3. `log.info(f"⚡ gRPC сервер активен на {GRPC_HOST}:{GRPC_PORT}")`
4. `try:`

---
