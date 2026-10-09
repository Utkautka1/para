# Module Specification: `scripts/tunnel_sync.py`
> **Path**: [`scripts/tunnel_sync.py`](file:///home/u/Рабочий стол/para/scripts/tunnel_sync.py)  
> **Subsystem**: `Cloudflare Tunnel Syncer`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Синхронизатор Cloudflare Tunnel (trycloudflare.com) для Telegram Mini App Swagger UI. Зачем существует этот модуль: Сервер para развёрнут на хосте за NAT без белого IP. Telegram Mini App и удаленные тестировщики требуют защищенный публичный HTTPS-эндпоинт. Модуль запускает официальный cloudflared туннель через глобальную сеть Cloudflare, автоматически обновляет MINIAPP_URL и SWAGGER_URL в .env и перезапускает бота.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`parse_tunnel_url`](#parse_tunnel_url) | Function | L22–L25 | `str | None` | Извлекает HTTPS-ссылку Cloudflare из строки вывода cloudflar |
| [`update_env_urls`](#update_env_urls) | Function | L28–L38 | `bool` | Обновляет значения MINIAPP_URL и SWAGGER_URL в файле .env. |
| [`restart_bot_service`](#restart_bot_service) | Function | L44–L47 | `None` | Перезапускает контейнер para-bot с перечитыванием обновленно |
| [`monitor_tunnel_stream`](#monitor_tunnel_stream) | Function | L50–L65 | `None` | Слушает лог cloudflared и применяет новый HTTPS URL при подк |
| [`run_tunnel_process`](#run_tunnel_process) | Function | L68–L78 | `None` | Запускает официальный клиент Cloudflare Quick Tunnel. |
| [`main`](#main) | Function | L81–L90 | `None` | Бесконечный цикл синхронизации Cloudflare Tunnel с авто-восс |

---

## 3. Exhaustive Function Specifications

### `parse_tunnel_url`
- **Signature**: `def parse_tunnel_url(line: str) -> str | None`
- **Source Reference**: [scripts/tunnel_sync.py#L22-L25](file:///home/u/Рабочий стол/para/scripts/tunnel_sync.py#L22-L25)
- **Async**: `No`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Извлекает HTTPS-ссылку Cloudflare из строки вывода cloudflared.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `line` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `match = URL_REGEX.search(line)`
2. `return match.group(0) if match else None`

---

### `update_env_urls`
- **Signature**: `def update_env_urls(new_url: str) -> bool`
- **Source Reference**: [scripts/tunnel_sync.py#L28-L38](file:///home/u/Рабочий стол/para/scripts/tunnel_sync.py#L28-L38)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Обновляет значения MINIAPP_URL и SWAGGER_URL в файле .env.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `new_url` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not ENV_FILE.exists():`
2. `content = ENV_FILE.read_text(encoding="utf-8")`
3. `miniapp_ep = f"{new_url.rstrip('/')}/miniapp"`
4. `swagger_ep = f"{new_url.rstrip('/')}/docs"`
5. `content = re.sub(r"MINIAPP_URL=.*", f"MINIAPP_URL={miniapp_ep}", content)`
6. `content = re.sub(r"SWAGGER_URL=.*", f"SWAGGER_URL={swagger_ep}", content)`

---

### `restart_bot_service`
- **Signature**: `def restart_bot_service() -> None`
- **Source Reference**: [scripts/tunnel_sync.py#L44-L47](file:///home/u/Рабочий стол/para/scripts/tunnel_sync.py#L44-L47)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Перезапускает контейнер para-bot с перечитыванием обновленного .env.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `cmd = ["docker", "compose", "up", "-d", "bot"]`
2. `subprocess.run(cmd, cwd=ENV_FILE.parent, check=False)  # nosec B603`

---

### `monitor_tunnel_stream`
- **Signature**: `async def monitor_tunnel_stream(proc: asyncio.subprocess.Process) -> None`
- **Source Reference**: [scripts/tunnel_sync.py#L50-L65](file:///home/u/Рабочий стол/para/scripts/tunnel_sync.py#L50-L65)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Слушает лог cloudflared и применяет новый HTTPS URL при подключении.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `proc` | `asyncio.subprocess.Process` | Input parameter |

#### Step-by-Step Logic Execution
1. `last_url = None`
2. `while proc.returncode is None:`

---

### `run_tunnel_process`
- **Signature**: `async def run_tunnel_process() -> None`
- **Source Reference**: [scripts/tunnel_sync.py#L68-L78](file:///home/u/Рабочий стол/para/scripts/tunnel_sync.py#L68-L78)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Запускает официальный клиент Cloudflare Quick Tunnel.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `bin_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"`
2. `cmd = [bin_path, "tunnel", "--url", f"http://127.0.0.1:{TARGET_PORT}", "--no-autoupda`
3. `proc = await asyncio.create_subprocess_exec(`
4. `await monitor_tunnel_stream(proc)`
5. `await proc.wait()`

---

### `main`
- **Signature**: `async def main() -> None`
- **Source Reference**: [scripts/tunnel_sync.py#L81-L90](file:///home/u/Рабочий стол/para/scripts/tunnel_sync.py#L81-L90)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Бесконечный цикл синхронизации Cloudflare Tunnel с авто-восстановлением.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `print("🚀 Запуск службы Cloudflare Tunnel для Swagger UI и Mini App", flush=True)`
2. `while True:`

---
