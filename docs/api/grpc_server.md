# Module Specification: `api/grpc/server.py`
> **Path**: [`api/grpc/server.py`](file:///home/u/Рабочий стол/para/api/grpc/server.py)  
> **Subsystem**: `gRPC HTTP/2 Server`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Управление асинхронным gRPC сервером para-api. Запускает gRPC сервер на базе grpc.aio с пулом потоков и регистрацией сервисеров расписания, экзаменов и преподавателей.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_register_servicers`](#_register_servicers) | Function | L26–L30 | `None` | Регистрирует все gRPC сервисеры на сервере. |
| [`create_grpc_server`](#create_grpc_server) | Function | L33–L46 | `grpc.aio.Server` | Создает и настраивает экземпляр gRPC сервера с HTTP/2 keepal |
| [`start_grpc_server`](#start_grpc_server) | Function | L49–L54 | `None` | Привязывает сокет и запускает обработку gRPC соединений. |
| [`stop_grpc_server`](#stop_grpc_server) | Function | L57–L62 | `None` | Останавливает gRPC сервер с ожиданием завершения активных вы |

---

## 3. Exhaustive Function Specifications

### `_register_servicers`
- **Signature**: `def _register_servicers(server: grpc.aio.Server) -> None`
- **Source Reference**: [api/grpc/server.py#L26-L30](file:///home/u/Рабочий стол/para/api/grpc/server.py#L26-L30)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Регистрирует все gRPC сервисеры на сервере.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `server` | `grpc.aio.Server` | Input parameter |

#### Step-by-Step Logic Execution
1. `schedule_pb2_grpc.add_ScheduleServiceServicer_to_server(ScheduleServicer(), server)`
2. `exams_pb2_grpc.add_ExamsServiceServicer_to_server(ExamsServicer(), server)`
3. `teachers_pb2_grpc.add_TeachersServiceServicer_to_server(TeachersServicer(), server)`

---

### `create_grpc_server`
- **Signature**: `def create_grpc_server() -> grpc.aio.Server`
- **Source Reference**: [api/grpc/server.py#L33-L46](file:///home/u/Рабочий стол/para/api/grpc/server.py#L33-L46)
- **Async**: `No`
- **Return Type**: `grpc.aio.Server`

#### Purpose & Architectural Intent
Создает и настраивает экземпляр gRPC сервера с HTTP/2 keepalive опциями.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `options = [`
2. `server = grpc.aio.server(options=options)`
3. `_register_servicers(server)`
4. `return server`

---

### `start_grpc_server`
- **Signature**: `async def start_grpc_server(server: grpc.aio.Server, host: str, port: int) -> None`
- **Source Reference**: [api/grpc/server.py#L49-L54](file:///home/u/Рабочий стол/para/api/grpc/server.py#L49-L54)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Привязывает сокет и запускает обработку gRPC соединений.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `server` | `grpc.aio.Server` | Input parameter |
| `host` | `str` | Input parameter |
| `port` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `listen_addr = f"{host}:{port}"`
2. `server.add_insecure_port(listen_addr)`
3. `log.info(f"🚀 Запуск gRPC сервера на {listen_addr}")`
4. `await server.start()`

---

### `stop_grpc_server`
- **Signature**: `async def stop_grpc_server(server: grpc.aio.Server | None, grace: float = 5.0) -> None`
- **Source Reference**: [api/grpc/server.py#L57-L62](file:///home/u/Рабочий стол/para/api/grpc/server.py#L57-L62)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Останавливает gRPC сервер с ожиданием завершения активных вызовов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `server` | `grpc.aio.Server | None` | Input parameter |
| `grace` | `float` | Input parameter |

#### Step-by-Step Logic Execution
1. `if server is not None:`

---
