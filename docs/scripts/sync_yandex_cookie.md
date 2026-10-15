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
| [`get_target_doc_url`](#get_target_doc_url) | Function | L32–L40 | `str` | Returns actual attendance doc URL from config or fallback. |
| [`find_zen_cookies_db`](#find_zen_cookies_db) | Function | L42–L56 | `Path` | Locates the most recently modified Zen Browser SQLite database. |
| [`extract_raw_yandex_cookies`](#extract_raw_yandex_cookies) | Function | L58–L80 | `dict[str, str]` | Extracts yandex.ru cookies bypassing active file lock. |
| [`refresh_yandex_session`](#refresh_yandex_session) | Function | L83–L105 | `dict[str, str]` | Extends Yandex session via Passport auth update endpoint. |
| [`build_cookie_header`](#build_cookie_header) | Function | L107–L119 | `str` | Constructs valid HTTP Cookie header string. |
| [`verify_yandex_cookie`](#verify_yandex_cookie) | Function | L122–L145 | `bool` | Validates session against Yandex Docs endpoint. |
| [`update_env_file`](#update_env_file) | Function | L147–L166 | `None` | Idempotently updates YANDEX_COOKIE in target .env. |
| [`send_cookie_to_remote_env`](#send_cookie_to_remote_env) | Function | L168–L184 | `None` | Safely transfers Cookie header to remote host via SSH. |
| [`send_api_urls_to_remote_env`](#send_api_urls_to_remote_env) | Function | L186–L201 | `None` | Synchronizes SCHEDULE_API_URL and EXAM_SCHEDULE_API_URL on remote host. |
| [`update_remote_redis_and_restart`](#update_remote_redis_and_restart) | Function | L203–L217 | `None` | Updates Redis cache and recreates worker and bot containers. |
| [`sync_cookies`](#sync_cookies) | Function | L219–L242 | `bool` | Coordinates end-to-end sync workflow. |

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
