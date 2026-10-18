# Component Reference: `integrations/yandex_docs.py`
> **File Path**: [`integrations/yandex_docs.py`](../../integrations/yandex_docs.py)  
> **Subsystem**: `WOPI Cloud Service`  
> **Architecture Layer**: `Enterprise Microservice Subsystem`  
> **Concurrency Model**: `AsyncIO Non-blocking Concurrency`  
> **Persistence Backend**: `Redis 7 Persistent Store`  
> **Service Level Objective**: `High-Availability Academic Telemetry`

## 1. Architectural Role & Responsibilities
The `integrations/yandex_docs.py` module implements core operational logic for the `WOPI Cloud Service` domain. It operates within an asynchronous microservices topology designed for ultra-low latency, zero-loss persistence guarantees, and strict single-responsibility function decomposition (≤25 lines).

### Component Architecture & Data Flow
```mermaid
graph LR
    Inbound[Inbound Request] --> Logic[Domain Service Logic]
    Logic --> Redis[(Redis 7 State Store)]
    Logic --> Outbound[Outbound Event Dispatch]
```

---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Core Invariant |
| :--- | :--- | :--- | :--- | :--- |
| [`WopiSession.__init__`](#wopisession__init__) | Method | L46–L52 | `Any` | Executes core domain logic for `__init__`. |
| [`extract_client_config`](#extract_client_config) | Function | L55–L69 | `dict` | Executes core domain logic for `extract_client_config`. |
| [`merge_cookie_header`](#merge_cookie_header) | Function | L72–L88 | `str` | Executes core domain logic for `merge_cookie_header`. |
| [`get_yandex_cookie_header`](#get_yandex_cookie_header) | Function | L91–L106 | `str` | Retrieves and resolves domain data for `get_yandex_cook... |
| [`get_effective_yandex_cookie`](#get_effective_yandex_cookie) | Function | L109–L128 | `str` | Retrieves and resolves domain data for `get_effective_y... |
| [`save_effective_yandex_cookie`](#save_effective_yandex_cookie) | Function | L131–L148 | `None` | Saves serialized entity data to storage for `save_effec... |
| [`update_cookies_from_response`](#update_cookies_from_response) | Function | L151–L165 | `None` | Synchronizes and updates domain state for `update_cooki... |
| [`_build_dom_headers`](#_build_dom_headers) | Function | L168–L187 | `dict[str, str]` | Executes core domain logic for `_build_dom_headers`. |
| [`fetch_page_dom`](#fetch_page_dom) | Function | L190–L206 | `str` | Executes core domain logic for `fetch_page_dom`. |
| [`get_active_wopi_lock`](#get_active_wopi_lock) | Function | L209–L224 | `str` | Retrieves and resolves domain data for `get_active_wopi... |
| [`init_wopi_session`](#init_wopi_session) | Function | L227–L246 | `WopiSession` | Executes core domain logic for `init_wopi_session`. |
| [`load_workbook_from_bytes`](#load_workbook_from_bytes) | Function | L249–L262 | `openpyxl.Workbook` | Executes core domain logic for `load_workbook_from_byte... |
| [`compute_sheet_summary_counts`](#compute_sheet_summary_counts) | Function | L265–L287 | `dict[tuple[str, int], int]` | Executes core domain logic for `compute_sheet_summary_c... |
| [`patch_sheet_xml_counts`](#patch_sheet_xml_counts) | Function | L290–L315 | `str` | Executes core domain logic for `patch_sheet_xml_counts`... |
| [`_write_summary_col_header`](#_write_summary_col_header) | Function | L318–L328 | `None` | Executes core domain logic for `_write_summary_col_head... |
| [`_write_summary_formulas`](#_write_summary_formulas) | Function | L331–L344 | `None` | Executes core domain logic for `_write_summary_formulas... |
| [`ensure_all_summary_headers`](#ensure_all_summary_headers) | Function | L347–L369 | `None` | Executes core domain logic for `ensure_all_summary_head... |
| [`inject_summary_cache`](#inject_summary_cache) | Function | L372–L392 | `bytes` | Executes core domain logic for `inject_summary_cache`. |
| [`save_workbook_to_bytes`](#save_workbook_to_bytes) | Function | L395–L410 | `bytes` | Saves serialized entity data to storage for `save_workb... |
| [`download_workbook`](#download_workbook) | Function | L413–L429 | `openpyxl.Workbook` | Executes core domain logic for `download_workbook`. |
| [`acquire_wopi_lock`](#acquire_wopi_lock) | Function | L432–L444 | `bool` | Executes core domain logic for `acquire_wopi_lock`. |
| [`release_wopi_lock`](#release_wopi_lock) | Function | L447–L458 | `bool` | Executes core domain logic for `release_wopi_lock`. |
| [`put_wopi_contents`](#put_wopi_contents) | Function | L461–L482 | `httpx.Response` | Executes core domain logic for `put_wopi_contents`. |
| [`_try_put_with_lock`](#_try_put_with_lock) | Function | L485–L506 | `bool` | Executes core domain logic for `_try_put_with_lock`. |
| [`upload_workbook`](#upload_workbook) | Function | L509–L524 | `bool` | Executes core domain logic for `upload_workbook`. |
| [`verify_upload`](#verify_upload) | Function | L527–L546 | `bool` | Executes core domain logic for `verify_upload`. |
| [`_download_raw_bytes`](#_download_raw_bytes) | Function | L549–L563 | `bytes` | Executes core domain logic for `_download_raw_bytes`. |
| [`_find_sheet_rid`](#_find_sheet_rid) | Function | L566–L585 | `str | None` | Executes core domain logic for `_find_sheet_rid`. |
| [`_resolve_sheet_target_path`](#_resolve_sheet_target_path) | Function | L588–L605 | `str | None` | Executes core domain logic for `_resolve_sheet_target_p... |
| [`_extract_sheet_xml`](#_extract_sheet_xml) | Function | L608–L631 | `str | None` | Executes core domain logic for `_extract_sheet_xml`. |
| [`_cell_has_expected_mark`](#_cell_has_expected_mark) | Function | L634–L644 | `bool` | Executes core domain logic for `_cell_has_expected_mark... |
| [`_marks_found_in_xml`](#_marks_found_in_xml) | Function | L647–L669 | `bool` | Executes core domain logic for `_marks_found_in_xml`. |
| [`_verify_marks_in_raw`](#_verify_marks_in_raw) | Function | L672–L692 | `bool` | Executes core domain logic for `_verify_marks_in_raw`. |
| [`get_month_sheet`](#get_month_sheet) | Function | L695–L706 | `Worksheet` | Retrieves and resolves domain data for `get_month_sheet... |
| [`parse_date_cell`](#parse_date_cell) | Function | L709–L721 | `str | None` | Parses and extracts structured entities from `parse_dat... |
| [`find_date_column_start`](#find_date_column_start) | Function | L724–L738 | `int | None` | Executes core domain logic for `find_date_column_start`... |
| [`find_lesson_column`](#find_lesson_column) | Function | L741–L759 | `int | None` | Executes core domain logic for `find_lesson_column`. |
| [`normalize_fio`](#normalize_fio) | Function | L762–L770 | `str` | Executes core domain logic for `normalize_fio`. |
| [`get_students_list`](#get_students_list) | Function | L773–L789 | `list[tuple[int, str]]` | Retrieves and resolves domain data for `get_students_li... |
| [`find_student_row`](#find_student_row) | Function | L792–L804 | `int | None` | Executes core domain logic for `find_student_row`. |
| [`write_student_mark`](#write_student_mark) | Function | L807–L827 | `None` | Executes core domain logic for `write_student_mark`. |

---

## 3. Comprehensive Function Specifications

## Class Model: `WopiSession`

Encapsulates domain entities and data transfer logic for `WopiSession`.

### `WopiSession.__init__`
```python
def __init__(self, resource_url: str, access_token: str, lock_id: str)
```

- **Source Reference**: [`integrations/yandex_docs.py#L46-L52`](../../integrations/yandex_docs.py#L46-L52)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Executes core domain logic for `__init__`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `resource_url` | `str` | Yes | Parameter `resource_url` of type `str`. |
| `access_token` | `str` | Yes | Parameter `access_token` of type `str`. |
| `lock_id` | `str` | Yes | Parameter `lock_id` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import __init__

# Execute call
result = __init__(resource_url=..., access_token=..., lock_id=...)
```

---

### `extract_client_config`
```python
def extract_client_config(html_content: str) -> dict
```

- **Source Reference**: [`integrations/yandex_docs.py#L55-L69`](../../integrations/yandex_docs.py#L55-L69)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict`

#### Overview & Architectural Purpose
Executes core domain logic for `extract_client_config`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `html_content` | `str` | Yes | Parameter `html_content` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.yandex_docs import extract_client_config

# Execute call
result = extract_client_config(html_content=...)
```

---

### `merge_cookie_header`
```python
def merge_cookie_header(current_cookie: str, new_cookies: dict[str, str]) -> str
```

- **Source Reference**: [`integrations/yandex_docs.py#L72-L88`](../../integrations/yandex_docs.py#L72-L88)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Executes core domain logic for `merge_cookie_header`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `current_cookie` | `str` | Yes | Parameter `current_cookie` of type `str`. |
| `new_cookies` | `dict[str, str]` | Yes | Parameter `new_cookies` of type `dict[str, str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import merge_cookie_header

# Execute call
result = merge_cookie_header(current_cookie=..., new_cookies=...)
```

---

### `get_yandex_cookie_header`
```python
def get_yandex_cookie_header() -> str
```

- **Source Reference**: [`integrations/yandex_docs.py#L91-L106`](../../integrations/yandex_docs.py#L91-L106)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_yandex_cookie_header`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import get_yandex_cookie_header

# Execute call
result = get_yandex_cookie_header()
```

---

### `get_effective_yandex_cookie`
```python
async def get_effective_yandex_cookie() -> str
```

- **Source Reference**: [`integrations/yandex_docs.py#L109-L128`](../../integrations/yandex_docs.py#L109-L128)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_effective_yandex_cookie`.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from integrations.yandex_docs import get_effective_yandex_cookie

# Execute call
result = await get_effective_yandex_cookie()
```

---

### `save_effective_yandex_cookie`
```python
async def save_effective_yandex_cookie(cookie_str: str) -> None
```

- **Source Reference**: [`integrations/yandex_docs.py#L131-L148`](../../integrations/yandex_docs.py#L131-L148)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Saves serialized entity data to storage for `save_effective_yandex_cookie`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cookie_str` | `str` | Yes | Parameter `cookie_str` of type `str`. |

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from integrations.yandex_docs import save_effective_yandex_cookie

# Execute call
result = await save_effective_yandex_cookie(cookie_str=...)
```

---

### `update_cookies_from_response`
```python
async def update_cookies_from_response(res: httpx.Response, current_cookie: str) -> None
```

- **Source Reference**: [`integrations/yandex_docs.py#L151-L165`](../../integrations/yandex_docs.py#L151-L165)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Synchronizes and updates domain state for `update_cookies_from_response`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `res` | `httpx.Response` | Yes | Parameter `res` of type `httpx.Response`. |
| `current_cookie` | `str` | Yes | Parameter `current_cookie` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import update_cookies_from_response

# Execute call
result = await update_cookies_from_response(res=..., current_cookie=...)
```

---

### `_build_dom_headers`
```python
def _build_dom_headers(cookie_hdr: str) -> dict[str, str]
```

- **Source Reference**: [`integrations/yandex_docs.py#L168-L187`](../../integrations/yandex_docs.py#L168-L187)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, str]`

#### Overview & Architectural Purpose
Executes core domain logic for `_build_dom_headers`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cookie_hdr` | `str` | Yes | Parameter `cookie_hdr` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import _build_dom_headers

# Execute call
result = _build_dom_headers(cookie_hdr=...)
```

---

### `fetch_page_dom`
```python
async def fetch_page_dom(doc_url: str) -> str
```

- **Source Reference**: [`integrations/yandex_docs.py#L190-L206`](../../integrations/yandex_docs.py#L190-L206)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Executes core domain logic for `fetch_page_dom`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc_url` | `str` | Yes | Parameter `doc_url` of type `str`. |

#### Concurrency & Side Effects
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.yandex_docs import fetch_page_dom

# Execute call
result = await fetch_page_dom(doc_url=...)
```

---

### `get_active_wopi_lock`
```python
async def get_active_wopi_lock(resource_url: str, token: str) -> str
```

- **Source Reference**: [`integrations/yandex_docs.py#L209-L224`](../../integrations/yandex_docs.py#L209-L224)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_active_wopi_lock`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `resource_url` | `str` | Yes | Parameter `resource_url` of type `str`. |
| `token` | `str` | Yes | Parameter `token` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import get_active_wopi_lock

# Execute call
result = await get_active_wopi_lock(resource_url=..., token=...)
```

---

### `init_wopi_session`
```python
async def init_wopi_session(doc_url: str = ATTENDANCE_DOC_URL) -> WopiSession
```

- **Source Reference**: [`integrations/yandex_docs.py#L227-L246`](../../integrations/yandex_docs.py#L227-L246)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `WopiSession`

#### Overview & Architectural Purpose
Executes core domain logic for `init_wopi_session`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc_url` | `str` | Yes | Parameter `doc_url` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.yandex_docs import init_wopi_session

# Execute call
result = await init_wopi_session(doc_url=...)
```

---

### `load_workbook_from_bytes`
```python
def load_workbook_from_bytes(content: bytes) -> openpyxl.Workbook
```

- **Source Reference**: [`integrations/yandex_docs.py#L249-L262`](../../integrations/yandex_docs.py#L249-L262)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `openpyxl.Workbook`

#### Overview & Architectural Purpose
Executes core domain logic for `load_workbook_from_bytes`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `content` | `bytes` | Yes | Parameter `content` of type `bytes`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import load_workbook_from_bytes

# Execute call
result = load_workbook_from_bytes(content=...)
```

---

### `compute_sheet_summary_counts`
```python
def compute_sheet_summary_counts(sheet: Worksheet) -> dict[tuple[str, int], int]
```

- **Source Reference**: [`integrations/yandex_docs.py#L265-L287`](../../integrations/yandex_docs.py#L265-L287)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[tuple[str, int], int]`

#### Overview & Architectural Purpose
Executes core domain logic for `compute_sheet_summary_counts`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import compute_sheet_summary_counts

# Execute call
result = compute_sheet_summary_counts(sheet=...)
```

---

### `patch_sheet_xml_counts`
```python
def patch_sheet_xml_counts(xml_text: str, counts: dict[tuple[str, int], int]) -> str
```

- **Source Reference**: [`integrations/yandex_docs.py#L290-L315`](../../integrations/yandex_docs.py#L290-L315)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Executes core domain logic for `patch_sheet_xml_counts`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `xml_text` | `str` | Yes | Parameter `xml_text` of type `str`. |
| `counts` | `dict[tuple[str, int], int]` | Yes | Parameter `counts` of type `dict[tuple[str, int], int]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import patch_sheet_xml_counts

# Execute call
result = patch_sheet_xml_counts(xml_text=..., counts=...)
```

---

### `_write_summary_col_header`
```python
def _write_summary_col_header(sheet: Worksheet, col: int, title: str, code: str) -> None
```

- **Source Reference**: [`integrations/yandex_docs.py#L318-L328`](../../integrations/yandex_docs.py#L318-L328)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_write_summary_col_header`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `col` | `int` | Yes | Parameter `col` of type `int`. |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `code` | `str` | Yes | Parameter `code` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import _write_summary_col_header

# Execute call
result = _write_summary_col_header(sheet=..., col=..., title=...)
```

---

### `_write_summary_formulas`
```python
def _write_summary_formulas(sheet: Worksheet, mc: int, l_o: str, l_u: str, l_n: str, end_col: str) -> None
```

- **Source Reference**: [`integrations/yandex_docs.py#L331-L344`](../../integrations/yandex_docs.py#L331-L344)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `_write_summary_formulas`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `mc` | `int` | Yes | Parameter `mc` of type `int`. |
| `l_o` | `str` | Yes | Parameter `l_o` of type `str`. |
| `l_u` | `str` | Yes | Parameter `l_u` of type `str`. |
| `l_n` | `str` | Yes | Parameter `l_n` of type `str`. |
| `end_col` | `str` | Yes | Parameter `end_col` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import _write_summary_formulas

# Execute call
result = _write_summary_formulas(sheet=..., mc=..., l_o=...)
```

---

### `ensure_all_summary_headers`
```python
def ensure_all_summary_headers(wb: openpyxl.Workbook) -> None
```

- **Source Reference**: [`integrations/yandex_docs.py#L347-L369`](../../integrations/yandex_docs.py#L347-L369)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `ensure_all_summary_headers`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `wb` | `openpyxl.Workbook` | Yes | Openpyxl workbook instance containing academic attendance sheets. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import ensure_all_summary_headers

# Execute call
result = ensure_all_summary_headers(wb=...)
```

---

### `inject_summary_cache`
```python
def inject_summary_cache(raw_bytes: bytes, wb: openpyxl.Workbook) -> bytes
```

- **Source Reference**: [`integrations/yandex_docs.py#L372-L392`](../../integrations/yandex_docs.py#L372-L392)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bytes`

#### Overview & Architectural Purpose
Executes core domain logic for `inject_summary_cache`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw_bytes` | `bytes` | Yes | Parameter `raw_bytes` of type `bytes`. |
| `wb` | `openpyxl.Workbook` | Yes | Openpyxl workbook instance containing academic attendance sheets. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import inject_summary_cache

# Execute call
result = inject_summary_cache(raw_bytes=..., wb=...)
```

---

### `save_workbook_to_bytes`
```python
def save_workbook_to_bytes(wb: openpyxl.Workbook) -> bytes
```

- **Source Reference**: [`integrations/yandex_docs.py#L395-L410`](../../integrations/yandex_docs.py#L395-L410)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bytes`

#### Overview & Architectural Purpose
Saves serialized entity data to storage for `save_workbook_to_bytes`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `wb` | `openpyxl.Workbook` | Yes | Openpyxl workbook instance containing academic attendance sheets. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import save_workbook_to_bytes

# Execute call
result = save_workbook_to_bytes(wb=...)
```

---

### `download_workbook`
```python
async def download_workbook(session: WopiSession) -> openpyxl.Workbook
```

- **Source Reference**: [`integrations/yandex_docs.py#L413-L429`](../../integrations/yandex_docs.py#L413-L429)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `openpyxl.Workbook`

#### Overview & Architectural Purpose
Executes core domain logic for `download_workbook`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `WopiSession` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.yandex_docs import download_workbook

# Execute call
result = await download_workbook(session=...)
```

---

### `acquire_wopi_lock`
```python
async def acquire_wopi_lock(session: WopiSession, client: httpx.AsyncClient, lock_id: str) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L432-L444`](../../integrations/yandex_docs.py#L432-L444)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `acquire_wopi_lock`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `WopiSession` | Yes | Active domain session instance containing current student index and marks. |
| `client` | `httpx.AsyncClient` | Yes | Active asynchronous Redis client or HTTP connection pool instance. |
| `lock_id` | `str` | Yes | Parameter `lock_id` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import acquire_wopi_lock

# Execute call
result = await acquire_wopi_lock(session=..., client=..., lock_id=...)
```

---

### `release_wopi_lock`
```python
async def release_wopi_lock(session: WopiSession, client: httpx.AsyncClient, lock_id: str) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L447-L458`](../../integrations/yandex_docs.py#L447-L458)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `release_wopi_lock`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `WopiSession` | Yes | Active domain session instance containing current student index and marks. |
| `client` | `httpx.AsyncClient` | Yes | Active asynchronous Redis client or HTTP connection pool instance. |
| `lock_id` | `str` | Yes | Parameter `lock_id` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import release_wopi_lock

# Execute call
result = await release_wopi_lock(session=..., client=..., lock_id=...)
```

---

### `put_wopi_contents`
```python
async def put_wopi_contents( session: WopiSession, client: httpx.AsyncClient, data: bytes, lock_id: str ) -> httpx.Response
```

- **Source Reference**: [`integrations/yandex_docs.py#L461-L482`](../../integrations/yandex_docs.py#L461-L482)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `httpx.Response`

#### Overview & Architectural Purpose
Executes core domain logic for `put_wopi_contents`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `WopiSession` | Yes | Active domain session instance containing current student index and marks. |
| `client` | `httpx.AsyncClient` | Yes | Active asynchronous Redis client or HTTP connection pool instance. |
| `data` | `bytes` | Yes | Parameter `data` of type `bytes`. |
| `lock_id` | `str` | Yes | Parameter `lock_id` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import put_wopi_contents

# Execute call
result = await put_wopi_contents(session=..., client=..., data=...)
```

---

### `_try_put_with_lock`
```python
async def _try_put_with_lock( session: WopiSession, client: httpx.AsyncClient, data: bytes ) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L485-L506`](../../integrations/yandex_docs.py#L485-L506)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_try_put_with_lock`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `WopiSession` | Yes | Active domain session instance containing current student index and marks. |
| `client` | `httpx.AsyncClient` | Yes | Active asynchronous Redis client or HTTP connection pool instance. |
| `data` | `bytes` | Yes | Parameter `data` of type `bytes`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import _try_put_with_lock

# Execute call
result = await _try_put_with_lock(session=..., client=..., data=...)
```

---

### `upload_workbook`
```python
async def upload_workbook(session: WopiSession, wb: openpyxl.Workbook) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L509-L524`](../../integrations/yandex_docs.py#L509-L524)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `upload_workbook`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `WopiSession` | Yes | Active domain session instance containing current student index and marks. |
| `wb` | `openpyxl.Workbook` | Yes | Openpyxl workbook instance containing academic attendance sheets. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import upload_workbook

# Execute call
result = await upload_workbook(session=..., wb=...)
```

---

### `verify_upload`
```python
async def verify_upload( session: WopiSession, target_date: date, lesson_num: int, expected_marks: dict[str, str], ) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L527-L546`](../../integrations/yandex_docs.py#L527-L546)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `verify_upload`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `WopiSession` | Yes | Active domain session instance containing current student index and marks. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `expected_marks` | `dict[str, str]` | Yes | Parameter `expected_marks` of type `dict[str, str]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from integrations.yandex_docs import verify_upload

# Execute call
result = await verify_upload(session=..., target_date=..., lesson_num=...)
```

---

### `_download_raw_bytes`
```python
async def _download_raw_bytes(session: WopiSession) -> bytes
```

- **Source Reference**: [`integrations/yandex_docs.py#L549-L563`](../../integrations/yandex_docs.py#L549-L563)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bytes`

#### Overview & Architectural Purpose
Executes core domain logic for `_download_raw_bytes`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `WopiSession` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.yandex_docs import _download_raw_bytes

# Execute call
result = await _download_raw_bytes(session=...)
```

---

### `_find_sheet_rid`
```python
def _find_sheet_rid(wb_xml: str, sheet_name: str) -> str | None
```

- **Source Reference**: [`integrations/yandex_docs.py#L566-L585`](../../integrations/yandex_docs.py#L566-L585)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Executes core domain logic for `_find_sheet_rid`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `wb_xml` | `str` | Yes | Parameter `wb_xml` of type `str`. |
| `sheet_name` | `str` | Yes | Parameter `sheet_name` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from integrations.yandex_docs import _find_sheet_rid

# Execute call
result = _find_sheet_rid(wb_xml=..., sheet_name=...)
```

---

### `_resolve_sheet_target_path`
```python
def _resolve_sheet_target_path(rels_xml: str, rid: str) -> str | None
```

- **Source Reference**: [`integrations/yandex_docs.py#L588-L605`](../../integrations/yandex_docs.py#L588-L605)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Executes core domain logic for `_resolve_sheet_target_path`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `rels_xml` | `str` | Yes | Parameter `rels_xml` of type `str`. |
| `rid` | `str` | Yes | Parameter `rid` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from integrations.yandex_docs import _resolve_sheet_target_path

# Execute call
result = _resolve_sheet_target_path(rels_xml=..., rid=...)
```

---

### `_extract_sheet_xml`
```python
def _extract_sheet_xml(raw: bytes, sheet_name: str) -> str | None
```

- **Source Reference**: [`integrations/yandex_docs.py#L608-L631`](../../integrations/yandex_docs.py#L608-L631)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Executes core domain logic for `_extract_sheet_xml`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw` | `bytes` | Yes | Parameter `raw` of type `bytes`. |
| `sheet_name` | `str` | Yes | Parameter `sheet_name` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from integrations.yandex_docs import _extract_sheet_xml

# Execute call
result = _extract_sheet_xml(raw=..., sheet_name=...)
```

---

### `_cell_has_expected_mark`
```python
def _cell_has_expected_mark(cell_xml: str, mark: str) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L634-L644`](../../integrations/yandex_docs.py#L634-L644)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_cell_has_expected_mark`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cell_xml` | `str` | Yes | Parameter `cell_xml` of type `str`. |
| `mark` | `str` | Yes | Attendance evaluation symbol assigned to the student. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import _cell_has_expected_mark

# Execute call
result = _cell_has_expected_mark(cell_xml=..., mark=...)
```

---

### `_marks_found_in_xml`
```python
def _marks_found_in_xml( xml_text: str, check_marks: dict[str, str] ) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L647-L669`](../../integrations/yandex_docs.py#L647-L669)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_marks_found_in_xml`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `xml_text` | `str` | Yes | Parameter `xml_text` of type `str`. |
| `check_marks` | `dict[str, str]` | Yes | Parameter `check_marks` of type `dict[str, str]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import _marks_found_in_xml

# Execute call
result = _marks_found_in_xml(xml_text=..., check_marks=...)
```

---

### `_verify_marks_in_raw`
```python
def _verify_marks_in_raw( raw: bytes, target_date: date, expected_marks: dict[str, str] ) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L672-L692`](../../integrations/yandex_docs.py#L672-L692)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Executes core domain logic for `_verify_marks_in_raw`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw` | `bytes` | Yes | Parameter `raw` of type `bytes`. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `expected_marks` | `dict[str, str]` | Yes | Parameter `expected_marks` of type `dict[str, str]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import _verify_marks_in_raw

# Execute call
result = _verify_marks_in_raw(raw=..., target_date=..., expected_marks=...)
```

---

### `get_month_sheet`
```python
def get_month_sheet(wb: openpyxl.Workbook, target_date: date) -> Worksheet
```

- **Source Reference**: [`integrations/yandex_docs.py#L695-L706`](../../integrations/yandex_docs.py#L695-L706)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Worksheet`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_month_sheet`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `wb` | `openpyxl.Workbook` | Yes | Openpyxl workbook instance containing academic attendance sheets. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.yandex_docs import get_month_sheet

# Execute call
result = get_month_sheet(wb=..., target_date=...)
```

---

### `parse_date_cell`
```python
def parse_date_cell(cell_value: object) -> str | None
```

- **Source Reference**: [`integrations/yandex_docs.py#L709-L721`](../../integrations/yandex_docs.py#L709-L721)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Parses and extracts structured entities from `parse_date_cell`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cell_value` | `object` | Yes | Parameter `cell_value` of type `object`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import parse_date_cell

# Execute call
result = parse_date_cell(cell_value=...)
```

---

### `find_date_column_start`
```python
def find_date_column_start(sheet: Worksheet, target_date: date) -> int | None
```

- **Source Reference**: [`integrations/yandex_docs.py#L724-L738`](../../integrations/yandex_docs.py#L724-L738)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Executes core domain logic for `find_date_column_start`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import find_date_column_start

# Execute call
result = find_date_column_start(sheet=..., target_date=...)
```

---

### `find_lesson_column`
```python
def find_lesson_column(sheet: Worksheet, target_date: date, lesson_num: int) -> int | None
```

- **Source Reference**: [`integrations/yandex_docs.py#L741-L759`](../../integrations/yandex_docs.py#L741-L759)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Executes core domain logic for `find_lesson_column`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import find_lesson_column

# Execute call
result = find_lesson_column(sheet=..., target_date=..., lesson_num=...)
```

---

### `normalize_fio`
```python
def normalize_fio(name: str) -> str
```

- **Source Reference**: [`integrations/yandex_docs.py#L762-L770`](../../integrations/yandex_docs.py#L762-L770)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Executes core domain logic for `normalize_fio`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` | Yes | Parameter `name` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import normalize_fio

# Execute call
result = normalize_fio(name=...)
```

---

### `get_students_list`
```python
def get_students_list(sheet: Worksheet) -> list[tuple[int, str]]
```

- **Source Reference**: [`integrations/yandex_docs.py#L773-L789`](../../integrations/yandex_docs.py#L773-L789)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[tuple[int, str]]`

#### Overview & Architectural Purpose
Retrieves and resolves domain data for `get_students_list`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import get_students_list

# Execute call
result = get_students_list(sheet=...)
```

---

### `find_student_row`
```python
def find_student_row(sheet: Worksheet, student_name: str) -> int | None
```

- **Source Reference**: [`integrations/yandex_docs.py#L792-L804`](../../integrations/yandex_docs.py#L792-L804)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Executes core domain logic for `find_student_row`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `student_name` | `str` | Yes | Full name of the student recorded in the academic roster. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.yandex_docs import find_student_row

# Execute call
result = find_student_row(sheet=..., student_name=...)
```

---

### `write_student_mark`
```python
def write_student_mark( sheet: Worksheet, row: int, col: int, mark: str, ) -> None
```

- **Source Reference**: [`integrations/yandex_docs.py#L807-L827`](../../integrations/yandex_docs.py#L807-L827)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `write_student_mark`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `row` | `int` | Yes | Parameter `row` of type `int`. |
| `col` | `int` | Yes | Parameter `col` of type `int`. |
| `mark` | `str` | Yes | Attendance evaluation symbol assigned to the student. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.yandex_docs import write_student_mark

# Execute call
result = write_student_mark(sheet=..., row=..., col=...)
```

---
