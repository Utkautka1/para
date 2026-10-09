# Module Specification: `api/router/system.py`
> **Path**: [`api/router/system.py`](file:///home/u/Рабочий стол/para/api/router/system.py)  
> **Subsystem**: `System Admin API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер системной диагностики — GET /system/info, POST /system/cache/flush.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_system_info`](#get_system_info) | Function | L23–L43 | `SystemInfoResponse` | Сводная информация о состоянии сервиса и вспомогательных под |
| [`_validate_flush_pattern`](#_validate_flush_pattern) | Function | L46–L52 | `None` | Проверяет безопасность маски для предотвращения сброса служе |
| [`flush_cache`](#flush_cache) | Function | L56–L63 | `CacheFlushResponse` | Принудительная очистка ключей Redis по безопасной маске (Adm |

---

## 3. Exhaustive Function Specifications

### `get_system_info`
- **Signature**: `async def get_system_info() -> SystemInfoResponse`
- **Source Reference**: [api/router/system.py#L23-L43](file:///home/u/Рабочий стол/para/api/router/system.py#L23-L43)
- **Async**: `Yes`
- **Return Type**: `SystemInfoResponse`

#### Purpose & Architectural Intent
Сводная информация о состоянии сервиса и вспомогательных подсистем.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `client = await init_redis()`
2. `redis_alive = client is not None`
3. `now_str = datetime.now(TIMEZONE).isoformat()`
4. `feats = {`
5. `return SystemInfoResponse(`

---

### `_validate_flush_pattern`
- **Signature**: `def _validate_flush_pattern(pattern: str) -> None`
- **Source Reference**: [api/router/system.py#L46-L52](file:///home/u/Рабочий стол/para/api/router/system.py#L46-L52)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Проверяет безопасность маски для предотвращения сброса служебных ключей Redis.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `pattern` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `clean = pattern.strip()`
2. `if clean in ("*", "", "*:*") or any(clean.startswith(d) for d in ("api:", "hw:tasks:"`
3. `if not any(clean.startswith(p) for p in SAFE_CACHE_FLUSH_PREFIXES):`

---

### `flush_cache`
- **Signature**: `async def flush_cache(payload: CacheFlushRequest) -> CacheFlushResponse`
- **Source Reference**: [api/router/system.py#L56-L63](file:///home/u/Рабочий стол/para/api/router/system.py#L56-L63)
- **Async**: `Yes`
- **Return Type**: `CacheFlushResponse`

#### Purpose & Architectural Intent
Принудительная очистка ключей Redis по безопасной маске (Admin only).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `payload` | `CacheFlushRequest` | Input parameter |

#### Step-by-Step Logic Execution
1. `_validate_flush_pattern(payload.pattern)`
2. `if payload.pattern.startswith("sched:"):`
3. `count = await cache_flush(pattern=payload.pattern)`
4. `return CacheFlushResponse(status="ok", pattern=payload.pattern, deleted_keys=count)`

---
