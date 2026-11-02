# Component Reference: `api/router/jaeger.py`
> **File Path**: [`api/router/jaeger.py`](../../api/router/jaeger.py)
> **Subsystem**: `Jaeger Tracing Proxy API`

## 1. Purpose
Роутер реверс-проксирования интерфейса Jaeger UI в защищенный портал Mini App.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_filter_headers`](#_filter_headers) | Function | L54–L62 | `dict[str, str]` | Фильтрует транзитные сетевые заголовки HTTP/1.1 (hop-by... |
| [`_filter_request_headers`](#_filter_request_headers) | Function | L65–L71 | `dict[str, str]` | Готовит заголовки запроса к Jaeger: убирает hop-by-hop ... |
| [`_get_client`](#_get_client) | Function | L74–L79 | `httpx.AsyncClient` | Возвращает общий HTTP-клиент к Jaeger, создавая его при... |
| [`close_jaeger_client`](#close_jaeger_client) | Function | L82–L87 | `None` | Закрывает пул соединений к Jaeger при остановке API. |
| [`_sanitize_proxy_path`](#_sanitize_proxy_path) | Function | L90–L103 | `str` | Очищает и нормализует путь проксирования, блокируя попы... |
| [`_build_target_url`](#_build_target_url) | Function | L106–L117 | `str` | Формирует проверенный целевой адрес Jaeger с учетом без... |
| [`_forward_request`](#_forward_request) | Function | L120–L142 | `Response` | Выполняет асинхронный HTTP-запрос к бэкенду Jaeger UI и... |
| [`redirect_jaeger_root`](#redirect_jaeger_root) | Function | L146–L154 | `RedirectResponse` | Перенаправляет запрос с /jaeger на /jaeger/ со слэшем. |
| [`proxy_jaeger`](#proxy_jaeger) | Function | L158–L169 | `Response` | Проксирует все статические ресурсы, HTML и REST API Jae... |

---

## 3. Comprehensive Function Specifications

### `_filter_headers`
```python
def _filter_headers(headers: Any) -> dict[str, str]
```

- **Source Reference**: [`api/router/jaeger.py#L54-L62`](../../api/router/jaeger.py#L54-L62)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, str]`

#### Overview & Architectural Purpose
Фильтрует транзитные сетевые заголовки HTTP/1.1 (hop-by-hop).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `headers` | `Any` | Yes | Parameter `headers` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.jaeger import _filter_headers

# Execute call
result = _filter_headers(headers=...)
```

---

### `_filter_request_headers`
```python
def _filter_request_headers(headers: Any) -> dict[str, str]
```

- **Source Reference**: [`api/router/jaeger.py#L65-L71`](../../api/router/jaeger.py#L65-L71)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, str]`

#### Overview & Architectural Purpose
Готовит заголовки запроса к Jaeger: убирает hop-by-hop и учётные данные.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `headers` | `Any` | Yes | Parameter `headers` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.jaeger import _filter_request_headers

# Execute call
result = _filter_request_headers(headers=...)
```

---

### `_get_client`
```python
def _get_client() -> httpx.AsyncClient
```

- **Source Reference**: [`api/router/jaeger.py#L74-L79`](../../api/router/jaeger.py#L74-L79)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `httpx.AsyncClient`

#### Overview & Architectural Purpose
Возвращает общий HTTP-клиент к Jaeger, создавая его при первом обращении.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.jaeger import _get_client

# Execute call
result = _get_client()
```

---

### `close_jaeger_client`
```python
async def close_jaeger_client() -> None
```

- **Source Reference**: [`api/router/jaeger.py#L82-L87`](../../api/router/jaeger.py#L82-L87)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Закрывает пул соединений к Jaeger при остановке API.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.jaeger import close_jaeger_client

# Execute call
result = await close_jaeger_client()
```

---

### `_sanitize_proxy_path`
```python
def _sanitize_proxy_path(raw_path: str) -> str
```

- **Source Reference**: [`api/router/jaeger.py#L90-L103`](../../api/router/jaeger.py#L90-L103)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Очищает и нормализует путь проксирования, блокируя попытки Path Traversal.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw_path` | `str` | Yes | Parameter `raw_path` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.jaeger import _sanitize_proxy_path

# Execute call
result = _sanitize_proxy_path(raw_path=...)
```

---

### `_build_target_url`
```python
def _build_target_url(path: str, query: str) -> str
```

- **Source Reference**: [`api/router/jaeger.py#L106-L117`](../../api/router/jaeger.py#L106-L117)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует проверенный целевой адрес Jaeger с учетом безопасного пути.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `path` | `str` | Yes | Parameter `path` of type `str`. |
| `query` | `str` | Yes | Parameter `query` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.jaeger import _build_target_url

# Execute call
result = _build_target_url(path=..., query=...)
```

---

### `_forward_request`
```python
async def _forward_request(method: str, url: str, headers: dict[str, str], body: bytes | None) -> Response
```

- **Source Reference**: [`api/router/jaeger.py#L120-L142`](../../api/router/jaeger.py#L120-L142)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Response`

#### Overview & Architectural Purpose
Выполняет асинхронный HTTP-запрос к бэкенду Jaeger UI и проксирует ответ.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `method` | `str` | Yes | Parameter `method` of type `str`. |
| `url` | `str` | Yes | Parameter `url` of type `str`. |
| `headers` | `dict[str, str]` | Yes | Parameter `headers` of type `dict[str, str]`. |
| `body` | `bytes | None` | Yes | Parameter `body` of type `bytes | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from api.router.jaeger import _forward_request

# Execute call
result = await _forward_request(method=..., url=..., headers=...)
```

---

### `redirect_jaeger_root`
```python
async def redirect_jaeger_root() -> RedirectResponse
```

- **Source Reference**: [`api/router/jaeger.py#L146-L154`](../../api/router/jaeger.py#L146-L154)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `RedirectResponse`

#### Overview & Architectural Purpose
Перенаправляет запрос с /jaeger на /jaeger/ со слэшем.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.jaeger import redirect_jaeger_root

# Execute call
result = await redirect_jaeger_root()
```

---

### `proxy_jaeger`
```python
async def proxy_jaeger(request: Request, path: str = "") -> Response
```

- **Source Reference**: [`api/router/jaeger.py#L158-L169`](../../api/router/jaeger.py#L158-L169)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Response`

#### Overview & Architectural Purpose
Проксирует все статические ресурсы, HTML и REST API Jaeger UI.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request` | `Request` | Yes | Parameter `request` of type `Request`. |
| `path` | `str` | Yes | Parameter `path` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.jaeger import proxy_jaeger

# Execute call
result = await proxy_jaeger(request=..., path=...)
```

---
