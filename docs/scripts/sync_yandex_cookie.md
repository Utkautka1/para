# Component Reference: `scripts/sync_yandex_cookie.py`
> **File Path**: [`scripts/sync_yandex_cookie.py`](../../scripts/sync_yandex_cookie.py)  
> **Subsystem**: `Yandex Office Integration & Telemetry`  
> **Architecture Layer**: `Operational Automation Utility`  
> **Concurrency Model**: `Synchronous Execution & Subprocess Orchestration`  
> **Persistence Backend**: `Redis 7 State Store & Local / Remote .env`  
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `scripts/sync_yandex_cookie.py` utility automates the extraction, validation, and distributed synchronization of Yandex Documents authorization credentials from the local Zen Browser (`cookies.sqlite`) to both the local development environment and the remote production server (`home`). It ensures uninterrupted attendance table telemetry and background sync without human intervention.

### Component Architecture & Data Flow
```mermaid
graph LR
    Zen[(Zen Browser SQLite)] --> Sync[Sync Script]
    Sync --> Check{HTTP Verification}
    Check -->|Valid 200| LocalEnv[.env (Local)]
    Check -->|Valid 200| RemoteEnv[.env (Remote Host)]
    Check -->|Valid 200| Redis[(Redis yandex:session_cookie)]
    Redis --> Worker[para-worker Container]
```

---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Core Invariant |
| :--- | :--- | :--- | :--- | :--- |
| [`find_zen_cookies_db`](#find_zen_cookies_db) | Function | L30–L45 | `Path` | Locates the most recently modified Zen Browser SQLite database. |
| [`extract_raw_yandex_cookies`](#extract_raw_yandex_cookies) | Function | L48–L72 | `dict[str, str]` | Extracts yandex.ru cookies bypassing active file lock. |
| [`build_cookie_header`](#build_cookie_header) | Function | L75–L87 | `str` | Constructs valid HTTP Cookie header string. |
| [`verify_yandex_cookie`](#verify_yandex_cookie) | Function | L90–L113 | `bool` | Validates session against Yandex Docs endpoint. |
| [`update_env_file`](#update_env_file) | Function | L116–L134 | `None` | Idempotently updates YANDEX_COOKIE in target .env. |
| [`send_cookie_to_remote_env`](#send_cookie_to_remote_env) | Function | L137–L153 | `None` | Safely transfers Cookie header to remote host via SSH. |
| [`update_remote_redis_and_restart`](#update_remote_redis_and_restart) | Function | L156–L166 | `None` | Updates Redis cache and restarts worker container. |
| [`sync_cookies`](#sync_cookies) | Function | L169–L189 | `bool` | Coordinates end-to-end sync workflow. |

---

## 3. Comprehensive Function Specifications

### `find_zen_cookies_db`
```python
def find_zen_cookies_db() -> Path
```
Locates the active `cookies.sqlite` database in `~/.config/zen`.

### `extract_raw_yandex_cookies`
```python
def extract_raw_yandex_cookies(db_path: Path) -> dict[str, str]
```
Safely clones the database into `/tmp` and extracts cookies for `.yandex.ru` in the default context.

### `build_cookie_header`
```python
def build_cookie_header(cookies: dict[str, str]) -> str
```
Builds the required header string containing `Session_id`, `sessionid2`, `sessar`, `_yasc`, `yandexuid`, `i`, `yandex_login`, `yp`, `L`.

### `verify_yandex_cookie`
```python
def verify_yandex_cookie(cookie_hdr: str, test_url: str = TEST_DOC_URL) -> bool
```
Performs a live HTTP GET request to check whether `client-config` is present and authorization succeeds.

### `sync_cookies`
```python
def sync_cookies(host: str = "home") -> bool
```
Top-level entrypoint executing the complete verification, replication, and container reload flow.
