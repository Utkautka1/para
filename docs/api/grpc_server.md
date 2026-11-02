# Component Reference: `api/grpc/server.py`
> **File Path**: [`api/grpc/server.py`](../../api/grpc/server.py)
> **Subsystem**: `gRPC HTTP/2 Server`

## 1. Purpose
Управление асинхронным gRPC сервером para-api.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_wrap_unary_handler`](#_wrap_unary_handler) | Function | L35–L43 | `Any` | Оборачивает унарный RPC обработчик в спан OpenTelemetry... |
| [`GrpcTracingInterceptor.intercept_service`](#grpctracinginterceptorintercept_service) | Method | L49–L69 | `grpc.RpcMethodHandler` | Извлекает W3C TraceContext из метаданных и связывает до... |
| [`ApiKeyAuthInterceptor._abort_unauthenticated`](#apikeyauthinterceptor_abort_unauthenticated) | Method | L76–L82 | `Any` | Прерывает вызов с кодом UNAUTHENTICATED при невалидном ... |
| [`ApiKeyAuthInterceptor.intercept_service`](#apikeyauthinterceptorintercept_service) | Method | L84–L102 | `grpc.RpcMethodHandler` | Перехватывает RPC-вызов и проверяет соответствие ключа ... |
| [`_register_servicers`](#_register_servicers) | Function | L105–L115 | `None` | Регистрирует все gRPC сервисеры на экземпляре сервера. |
| [`create_grpc_server`](#create_grpc_server) | Function | L118–L142 | `grpc.aio.Server` | Создает и настраивает экземпляр gRPC сервера с HTTP/2 k... |
| [`start_grpc_server`](#start_grpc_server) | Function | L145–L157 | `None` | Привязывает сокет и запускает обработку входящих gRPC с... |
| [`stop_grpc_server`](#stop_grpc_server) | Function | L160–L171 | `None` | Останавливает gRPC сервер с ожиданием завершения активн... |

---

## 3. Comprehensive Function Specifications

### `_wrap_unary_handler`
```python
def _wrap_unary_handler(fn: Any, method: str, parent_ctx: Any) -> Any
```

- **Source Reference**: [`api/grpc/server.py#L35-L43`](../../api/grpc/server.py#L35-L43)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Оборачивает унарный RPC обработчик в спан OpenTelemetry.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fn` | `Any` | Yes | Parameter `fn` of type `Any`. |
| `method` | `str` | Yes | Parameter `method` of type `str`. |
| `parent_ctx` | `Any` | Yes | Parameter `parent_ctx` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.server import _wrap_unary_handler

# Execute call
result = _wrap_unary_handler(fn=..., method=..., parent_ctx=...)
```

---

## Class Model: `GrpcTracingInterceptor`

Интерцептор распределенного трейсинга OpenTelemetry для входящих gRPC вызовов.

### `GrpcTracingInterceptor.intercept_service`
```python
async def intercept_service( self, continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]], handler_call_details: grpc.HandlerCallDetails, ) -> grpc.RpcMethodHandler
```

- **Source Reference**: [`api/grpc/server.py#L49-L69`](../../api/grpc/server.py#L49-L69)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `grpc.RpcMethodHandler`

#### Overview & Architectural Purpose
Извлекает W3C TraceContext из метаданных и связывает дочерние спаны сервисеров.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `continuation` | `Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]]` | Yes | Parameter `continuation` of type `Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]]`. |
| `handler_call_details` | `grpc.HandlerCallDetails` | Yes | Parameter `handler_call_details` of type `grpc.HandlerCallDetails`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.server import intercept_service

# Execute call
result = await intercept_service(continuation=..., handler_call_details=...)
```

---

## Class Model: `ApiKeyAuthInterceptor`

Интерцептор проверки X-API-Key заголовка для защиты gRPC эндпоинтов.

### `ApiKeyAuthInterceptor._abort_unauthenticated`
```python
async def _abort_unauthenticated(_req: Any, context: grpc.aio.ServicerContext) -> Any
```

- **Source Reference**: [`api/grpc/server.py#L76-L82`](../../api/grpc/server.py#L76-L82)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Прерывает вызов с кодом UNAUTHENTICATED при невалидном ключе.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_req` | `Any` | Yes | Parameter `_req` of type `Any`. |
| `context` | `grpc.aio.ServicerContext` | Yes | Parameter `context` of type `grpc.aio.ServicerContext`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.server import _abort_unauthenticated

# Execute call
result = await _abort_unauthenticated(_req=..., context=...)
```

---

### `ApiKeyAuthInterceptor.intercept_service`
```python
async def intercept_service( self, continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]], handler_call_details: grpc.HandlerCallDetails, ) -> grpc.RpcMethodHandler
```

- **Source Reference**: [`api/grpc/server.py#L84-L102`](../../api/grpc/server.py#L84-L102)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `grpc.RpcMethodHandler`

#### Overview & Architectural Purpose
Перехватывает RPC-вызов и проверяет соответствие ключа авторизации в метаданных.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `continuation` | `Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]]` | Yes | Parameter `continuation` of type `Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]]`. |
| `handler_call_details` | `grpc.HandlerCallDetails` | Yes | Parameter `handler_call_details` of type `grpc.HandlerCallDetails`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.server import intercept_service

# Execute call
result = await intercept_service(continuation=..., handler_call_details=...)
```

---

### `_register_servicers`
```python
def _register_servicers(server: grpc.aio.Server) -> None
```

- **Source Reference**: [`api/grpc/server.py#L105-L115`](../../api/grpc/server.py#L105-L115)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Регистрирует все gRPC сервисеры на экземпляре сервера.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `server` | `grpc.aio.Server` | Yes | Parameter `server` of type `grpc.aio.Server`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.server import _register_servicers

# Execute call
result = _register_servicers(server=...)
```

---

### `create_grpc_server`
```python
def create_grpc_server() -> grpc.aio.Server
```

- **Source Reference**: [`api/grpc/server.py#L118-L142`](../../api/grpc/server.py#L118-L142)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `grpc.aio.Server`

#### Overview & Architectural Purpose
Создает и настраивает экземпляр gRPC сервера с HTTP/2 keepalive опциями.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.server import create_grpc_server

# Execute call
result = create_grpc_server()
```

---

### `start_grpc_server`
```python
async def start_grpc_server(server: grpc.aio.Server, host: str, port: int) -> None
```

- **Source Reference**: [`api/grpc/server.py#L145-L157`](../../api/grpc/server.py#L145-L157)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Привязывает сокет и запускает обработку входящих gRPC соединений.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `server` | `grpc.aio.Server` | Yes | Parameter `server` of type `grpc.aio.Server`. |
| `host` | `str` | Yes | Parameter `host` of type `str`. |
| `port` | `int` | Yes | Parameter `port` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.server import start_grpc_server

# Execute call
result = await start_grpc_server(server=..., host=..., port=...)
```

---

### `stop_grpc_server`
```python
async def stop_grpc_server(server: grpc.aio.Server | None, grace: float = 5.0) -> None
```

- **Source Reference**: [`api/grpc/server.py#L160-L171`](../../api/grpc/server.py#L160-L171)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Останавливает gRPC сервер с ожиданием завершения активных вызовов.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `server` | `grpc.aio.Server | None` | Yes | Parameter `server` of type `grpc.aio.Server | None`. |
| `grace` | `float` | Yes | Parameter `grace` of type `float`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.grpc.server import stop_grpc_server

# Execute call
result = await stop_grpc_server(server=..., grace=...)
```

---
