# Component Reference: `scripts/tunnel_sync.py`
> **File Path**: [`scripts/tunnel_sync.py`](../../scripts/tunnel_sync.py)
> **Subsystem**: `Cloudflare Tunnel Syncer`

## 1. Purpose
Синхронизатор Cloudflare Tunnel (trycloudflare.com) для Telegram Mini App Swagger UI.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`parse_tunnel_url`](#parse_tunnel_url) | Function | L30–L40 | `str \| None` | Извлекает публичный HTTPS-адрес туннеля из строкового п... |
| [`update_env_urls`](#update_env_urls) | Function | L43–L60 | `bool` | Атомарно обновляет параметры MINIAPP_URL и SWAGGER_URL ... |
| [`restart_bot_service`](#restart_bot_service) | Function | L66–L76 | `None` | Перезапускает docker-контейнер бота para-bot для примен... |
| [`monitor_tunnel_stream`](#monitor_tunnel_stream) | Function | L79–L101 | `None` | Асинхронно считывает поток stderr процесса cloudflared ... |
| [`run_tunnel_process`](#run_tunnel_process) | Function | L104–L121 | `None` | Запускает бинарник cloudflared в режиме быстрого времен... |
| [`main`](#main) | Function | L124–L140 | `None` | Основной бесконечный цикл супервизора туннеля Cloudflar... |

---

## 3. Comprehensive Function Specifications

### `parse_tunnel_url`
```python
def parse_tunnel_url(line: str) -> str | None
```

- **Source Reference**: [`scripts/tunnel_sync.py#L30-L40`](../../scripts/tunnel_sync.py#L30-L40)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Извлекает публичный HTTPS-адрес туннеля из строкового потока вывода cloudflared.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `line` | `str` | Yes | Parameter `line` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.tunnel_sync import parse_tunnel_url

# Execute call
result = parse_tunnel_url(line=...)
```

---

### `update_env_urls`
```python
def update_env_urls(new_url: str) -> bool
```

- **Source Reference**: [`scripts/tunnel_sync.py#L43-L60`](../../scripts/tunnel_sync.py#L43-L60)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Атомарно обновляет параметры MINIAPP_URL и SWAGGER_URL в локальном файле .env.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `new_url` | `str` | Yes | Parameter `new_url` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.tunnel_sync import update_env_urls

# Execute call
result = update_env_urls(new_url=...)
```

---

### `restart_bot_service`
```python
def restart_bot_service() -> None
```

- **Source Reference**: [`scripts/tunnel_sync.py#L66-L76`](../../scripts/tunnel_sync.py#L66-L76)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Перезапускает docker-контейнер бота para-bot для применения новых переменных окружения.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.tunnel_sync import restart_bot_service

# Execute call
result = restart_bot_service()
```

---

### `monitor_tunnel_stream`
```python
async def monitor_tunnel_stream(proc: asyncio.subprocess.Process) -> None
```

- **Source Reference**: [`scripts/tunnel_sync.py#L79-L101`](../../scripts/tunnel_sync.py#L79-L101)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Асинхронно считывает поток stderr процесса cloudflared и применяет новые URL.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `proc` | `asyncio.subprocess.Process` | Yes | Parameter `proc` of type `asyncio.subprocess.Process`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.tunnel_sync import monitor_tunnel_stream

# Execute call
result = await monitor_tunnel_stream(proc=...)
```

---

### `run_tunnel_process`
```python
async def run_tunnel_process() -> None
```

- **Source Reference**: [`scripts/tunnel_sync.py#L104-L121`](../../scripts/tunnel_sync.py#L104-L121)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Запускает бинарник cloudflared в режиме быстрого временного туннеля (Quick Tunnel).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.tunnel_sync import run_tunnel_process

# Execute call
result = await run_tunnel_process()
```

---

### `main`
```python
async def main() -> None
```

- **Source Reference**: [`scripts/tunnel_sync.py#L124-L140`](../../scripts/tunnel_sync.py#L124-L140)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Основной бесконечный цикл супервизора туннеля Cloudflare с авто-восстановлением.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from scripts.tunnel_sync import main

# Execute call
result = await main()
```

---
