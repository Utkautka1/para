# Component Reference: `scripts/sync_yandex_cookie.py`
> **File Path**: [`scripts/sync_yandex_cookie.py`](../../scripts/sync_yandex_cookie.py)
> **Subsystem**: `Yandex Cookie Sync`

## 1. Purpose
Утилита автоматической синхронизации Cookie Яндекс Документов из Zen Browser.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_validate_ssh_target`](#_validate_ssh_target) | Function | L41–L53 | `None` | Проверяет безопасность целевого SSH-хоста и пути на сер... |
| [`get_target_doc_url`](#get_target_doc_url) | Function | L56–L70 | `str` | Получает целевой URL таблицы посещаемости из боевой кон... |
| [`find_zen_cookies_db`](#find_zen_cookies_db) | Function | L73–L88 | `Path` | Определяет путь к активной базе данных cookies.sqlite б... |
| [`extract_raw_yandex_cookies`](#extract_raw_yandex_cookies) | Function | L91–L119 | `dict[str, str]` | Извлекает куки авторизации Яндекс из базы данных профил... |
| [`refresh_yandex_session`](#refresh_yandex_session) | Function | L122–L150 | `dict[str, str]` | Продлевает срок жизни сессии Яндекс через эндпоинт обно... |
| [`build_cookie_header`](#build_cookie_header) | Function | L153–L168 | `str` | Формирует строку HTTP-заголовка Cookie из словаря парам... |
| [`verify_yandex_cookie`](#verify_yandex_cookie) | Function | L171–L196 | `bool` | Проверяет валидность сгенерированного Cookie-заголовка ... |
| [`update_env_file`](#update_env_file) | Function | L199–L221 | `None` | Обновляет переменную YANDEX_COOKIE в локальном файле пе... |
| [`send_cookie_to_remote_env`](#send_cookie_to_remote_env) | Function | L224–L244 | `None` | Передает и обновляет YANDEX_COOKIE в файле .env на удал... |
| [`_build_env_update_script`](#_build_env_update_script) | Function | L247–L269 | `str` | Генерирует безопасную команду python с base64-скриптом ... |
| [`send_api_urls_to_remote_env`](#send_api_urls_to_remote_env) | Function | L272–L289 | `None` | Синхронизирует основной и резервный URL-адреса API расп... |
| [`update_remote_redis_and_restart`](#update_remote_redis_and_restart) | Function | L292–L311 | `None` | Записывает актуальные Cookie в Redis на сервере и перез... |
| [`sync_cookies`](#sync_cookies) | Function | L314–L342 | `bool` | Выполняет полный цикл синхронизации учетных данных Янде... |

---

## 3. Comprehensive Function Specifications

### `_validate_ssh_target`
```python
def _validate_ssh_target(host: str, remote_dir: str) -> None
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L41-L53`](../../scripts/sync_yandex_cookie.py#L41-L53)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Проверяет безопасность целевого SSH-хоста и пути на сервере.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `host` | `str` | Yes | Parameter `host` of type `str`. |
| `remote_dir` | `str` | Yes | Parameter `remote_dir` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import _validate_ssh_target

# Execute call
result = _validate_ssh_target(host=..., remote_dir=...)
```

---

### `get_target_doc_url`
```python
def get_target_doc_url() -> str
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L56-L70`](../../scripts/sync_yandex_cookie.py#L56-L70)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Получает целевой URL таблицы посещаемости из боевой конфигурации.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import get_target_doc_url

# Execute call
result = get_target_doc_url()
```

---

### `find_zen_cookies_db`
```python
def find_zen_cookies_db() -> Path
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L73-L88`](../../scripts/sync_yandex_cookie.py#L73-L88)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Path`

#### Overview & Architectural Purpose
Определяет путь к активной базе данных cookies.sqlite браузера Zen.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import find_zen_cookies_db

# Execute call
result = find_zen_cookies_db()
```

---

### `extract_raw_yandex_cookies`
```python
def extract_raw_yandex_cookies(db_path: Path) -> dict[str, str]
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L91-L119`](../../scripts/sync_yandex_cookie.py#L91-L119)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, str]`

#### Overview & Architectural Purpose
Извлекает куки авторизации Яндекс из базы данных профиля браузера.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `db_path` | `Path` | Yes | Parameter `db_path` of type `Path`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import extract_raw_yandex_cookies

# Execute call
result = extract_raw_yandex_cookies(db_path=...)
```

---

### `refresh_yandex_session`
```python
def refresh_yandex_session(cookies: dict[str, str], target_url: str) -> dict[str, str]
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L122-L150`](../../scripts/sync_yandex_cookie.py#L122-L150)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, str]`

#### Overview & Architectural Purpose
Продлевает срок жизни сессии Яндекс через эндпоинт обновления Паспорта.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cookies` | `dict[str, str]` | Yes | Parameter `cookies` of type `dict[str, str]`. |
| `target_url` | `str` | Yes | Parameter `target_url` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import refresh_yandex_session

# Execute call
result = refresh_yandex_session(cookies=..., target_url=...)
```

---

### `build_cookie_header`
```python
def build_cookie_header(cookies: dict[str, str]) -> str
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L153-L168`](../../scripts/sync_yandex_cookie.py#L153-L168)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует строку HTTP-заголовка Cookie из словаря параметров сессии.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cookies` | `dict[str, str]` | Yes | Parameter `cookies` of type `dict[str, str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import build_cookie_header

# Execute call
result = build_cookie_header(cookies=...)
```

---

### `verify_yandex_cookie`
```python
def verify_yandex_cookie(cookie_hdr: str, test_url: str = TEST_DOC_URL) -> bool
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L171-L196`](../../scripts/sync_yandex_cookie.py#L171-L196)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет валидность сгенерированного Cookie-заголовка прямым HTTP-запросом.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cookie_hdr` | `str` | Yes | Parameter `cookie_hdr` of type `str`. |
| `test_url` | `str` | Yes | Parameter `test_url` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import verify_yandex_cookie

# Execute call
result = verify_yandex_cookie(cookie_hdr=..., test_url=...)
```

---

### `update_env_file`
```python
def update_env_file(env_path: Path, cookie_hdr: str) -> None
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L199-L221`](../../scripts/sync_yandex_cookie.py#L199-L221)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Обновляет переменную YANDEX_COOKIE в локальном файле переменных окружения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `env_path` | `Path` | Yes | Parameter `env_path` of type `Path`. |
| `cookie_hdr` | `str` | Yes | Parameter `cookie_hdr` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import update_env_file

# Execute call
result = update_env_file(env_path=..., cookie_hdr=...)
```

---

### `send_cookie_to_remote_env`
```python
def send_cookie_to_remote_env(cookie_hdr: str, host: str = "home", remote_dir: str = "/root/para") -> None
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L224-L244`](../../scripts/sync_yandex_cookie.py#L224-L244)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Передает и обновляет YANDEX_COOKIE в файле .env на удаленном сервере через SSH.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cookie_hdr` | `str` | Yes | Parameter `cookie_hdr` of type `str`. |
| `host` | `str` | Yes | Parameter `host` of type `str`. |
| `remote_dir` | `str` | Yes | Parameter `remote_dir` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import send_cookie_to_remote_env

# Execute call
result = send_cookie_to_remote_env(cookie_hdr=..., host=..., remote_dir=...)
```

---

### `_build_env_update_script`
```python
def _build_env_update_script(remote_dir: str, b64_payload: str) -> str
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L247-L269`](../../scripts/sync_yandex_cookie.py#L247-L269)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Генерирует безопасную команду python с base64-скриптом обновления .env файла.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `remote_dir` | `str` | Yes | Parameter `remote_dir` of type `str`. |
| `b64_payload` | `str` | Yes | Parameter `b64_payload` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import _build_env_update_script

# Execute call
result = _build_env_update_script(remote_dir=..., b64_payload=...)
```

---

### `send_api_urls_to_remote_env`
```python
def send_api_urls_to_remote_env( primary_url: str = "https://raspisanie-ktmu.ru/api/storage/schedule-data-v2", fallback_url: str = "https://nikkhl0358-max-time-f5e2.twc1.net/api/storage/schedule-data-v2", host: str = "home", remote_dir: str = "/root/para", ) -> None
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L272-L289`](../../scripts/sync_yandex_cookie.py#L272-L289)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Синхронизирует основной и резервный URL-адреса API расписания на сервере.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `primary_url` | `str` | Yes | Parameter `primary_url` of type `str`. |
| `fallback_url` | `str` | Yes | Parameter `fallback_url` of type `str`. |
| `host` | `str` | Yes | Parameter `host` of type `str`. |
| `remote_dir` | `str` | Yes | Parameter `remote_dir` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import send_api_urls_to_remote_env

# Execute call
result = send_api_urls_to_remote_env(primary_url=..., fallback_url=..., host=...)
```

---

### `update_remote_redis_and_restart`
```python
def update_remote_redis_and_restart(cookie_hdr: str, host: str = "home", remote_dir: str = "/root/para") -> None
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L292-L311`](../../scripts/sync_yandex_cookie.py#L292-L311)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Записывает актуальные Cookie в Redis на сервере и перезапускает сервисы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cookie_hdr` | `str` | Yes | Parameter `cookie_hdr` of type `str`. |
| `host` | `str` | Yes | Parameter `host` of type `str`. |
| `remote_dir` | `str` | Yes | Parameter `remote_dir` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import update_remote_redis_and_restart

# Execute call
result = update_remote_redis_and_restart(cookie_hdr=..., host=..., remote_dir=...)
```

---

### `sync_cookies`
```python
def sync_cookies(host: str = "home") -> bool
```

- **Source Reference**: [`scripts/sync_yandex_cookie.py#L314-L342`](../../scripts/sync_yandex_cookie.py#L314-L342)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Выполняет полный цикл синхронизации учетных данных Яндекса из браузера на сервер.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `host` | `str` | Yes | Parameter `host` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from scripts.sync_yandex_cookie import sync_cookies

# Execute call
result = sync_cookies(host=...)
```

---
