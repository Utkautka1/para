# Module Specification: `api/router/health.py`
> **Path**: [`api/router/health.py`](file:///home/u/Рабочий стол/para/api/router/health.py)  
> **Subsystem**: `Healthcheck API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Healthcheck роутер — GET /health. Не требует авторизации — используется Docker healthcheck для проверки жизнеспособности контейнера para-api.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`healthcheck`](#healthcheck) | Function | L20–L22 | `HealthResponse` | Простая проверка жизнеспособности API-сервиса. |

---

## 3. Exhaustive Function Specifications

## Class: `HealthResponse`
Ответ healthcheck.

### `healthcheck`
- **Signature**: `async def healthcheck() -> HealthResponse`
- **Source Reference**: [api/router/health.py#L20-L22](file:///home/u/Рабочий стол/para/api/router/health.py#L20-L22)
- **Async**: `Yes`
- **Return Type**: `HealthResponse`

#### Purpose & Architectural Intent
Простая проверка жизнеспособности API-сервиса.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return HealthResponse(status="ok")`

---
