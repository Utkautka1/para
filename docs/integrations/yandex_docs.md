# Component Reference: `integrations/yandex_docs.py`
> **File Path**: [`integrations/yandex_docs.py`](../../integrations/yandex_docs.py)
> **Subsystem**: `WOPI Cloud Service`

## 1. Purpose
Сервис интеграции с Яндекс Документами через протокол WOPI.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`WopiSession.__init__`](#wopisession__init__) | Method | L56–L62 | `Any` | Executes core domain logic for `__init__`. |
| [`extract_client_config`](#extract_client_config) | Function | L65–L79 | `dict` | Извлекает JSON конфигурации редактора из HTML-разметки ... |
| [`merge_cookie_header`](#merge_cookie_header) | Function | L82–L98 | `str` | Объединяет текущую строку заголовка Cookie со свежими т... |
| [`get_yandex_cookie_header`](#get_yandex_cookie_header) | Function | L101–L116 | `str` | Формирует резервную строку Cookie из статических переме... |
| [`get_effective_yandex_cookie`](#get_effective_yandex_cookie) | Function | L119–L138 | `str` | Предоставляет наиболее свежие Cookie сессии с приоритет... |
| [`save_effective_yandex_cookie`](#save_effective_yandex_cookie) | Function | L141–L158 | `None` | Атомарно сохраняет актуальную строку Cookie в постоянны... |
| [`update_cookies_from_response`](#update_cookies_from_response) | Function | L161–L175 | `None` | Извлекает полученные от сервера Set-Cookie и синхронизи... |
| [`_build_dom_headers`](#_build_dom_headers) | Function | L178–L197 | `dict[str, str]` | Формирует заголовки браузерного эмулятора для загрузки ... |
| [`fetch_page_dom`](#fetch_page_dom) | Function | L200–L216 | `str` | Загружает исходный HTML-код страницы веб-редактора Янде... |
| [`get_active_wopi_lock`](#get_active_wopi_lock) | Function | L219–L234 | `str` | Определяет текущий активный идентификатор блокировки фа... |
| [`init_wopi_session`](#init_wopi_session) | Function | L237–L256 | `WopiSession` | Инициализирует сессию WOPI, извлекая resource_url, acce... |
| [`load_workbook_from_bytes`](#load_workbook_from_bytes) | Function | L259–L272 | `openpyxl.Workbook` | Синхронно десериализует байты книги openpyxl с подавлен... |
| [`compute_sheet_summary_counts`](#compute_sheet_summary_counts) | Function | L275–L297 | `dict[tuple[str, int], int]` | Вычисляет агрегированное количество отметок О, У, Н по ... |
| [`patch_sheet_xml_counts`](#patch_sheet_xml_counts) | Function | L300–L326 | `str` | Заменяет кэшированные теги формул <v></v> в XML листа н... |
| [`_write_summary_col_header`](#_write_summary_col_header) | Function | L329–L339 | `None` | Записывает текстовые заголовки и условные обозначения и... |
| [`_write_summary_formulas`](#_write_summary_formulas) | Function | L342–L355 | `None` | Проставляет формулы COUNTIF для подсчета отметок по стр... |
| [`ensure_all_summary_headers`](#ensure_all_summary_headers) | Function | L358–L380 | `None` | Гарантирует наличие заголовков, кодов и формул COUNTIF ... |
| [`inject_summary_cache`](#inject_summary_cache) | Function | L383–L403 | `bytes` | Инжектирует предрассчитанные значения формул COUNTIF пр... |
| [`save_workbook_to_bytes`](#save_workbook_to_bytes) | Function | L406–L421 | `bytes` | Сериализует книгу openpyxl в бинарные байты с принудите... |
| [`download_workbook`](#download_workbook) | Function | L424–L440 | `openpyxl.Workbook` | Скачивает актуальный контент таблицы по протоколу WOPI ... |
| [`acquire_wopi_lock`](#acquire_wopi_lock) | Function | L443–L455 | `bool` | Захватывает монопольную сессионную блокировку файла по ... |
| [`release_wopi_lock`](#release_wopi_lock) | Function | L458–L469 | `bool` | Снимает активную сессионную блокировку с файла по станд... |
| [`put_wopi_contents`](#put_wopi_contents) | Function | L472–L493 | `httpx.Response` | Выполняет HTTP POST-запрос с заголовком X-WOPI-Override... |
| [`_try_put_with_lock`](#_try_put_with_lock) | Function | L496–L515 | `bool` | Пробует зафиксировать файл сначала с текущей сессионной... |
| [`upload_workbook`](#upload_workbook) | Function | L518–L533 | `bool` | Сохраняет книгу openpyxl и выгружает обновленную версию... |
| [`verify_upload`](#verify_upload) | Function | L536–L555 | `bool` | Легковесно валидирует сохранение отметок путем прямого ... |
| [`_download_raw_bytes`](#_download_raw_bytes) | Function | L558–L572 | `bytes` | Скачивает сырые байты файла таблицы с сервера WOPI для ... |
| [`_find_sheet_rid`](#_find_sheet_rid) | Function | L575–L594 | `str \| None` | Находит relationship ID (r:id) листа в структуре workbo... |
| [`_resolve_sheet_target_path`](#_resolve_sheet_target_path) | Function | L597–L614 | `str \| None` | Определяет путь к файлу XML листа внутри zip-пакета по ... |
| [`_extract_sheet_xml`](#_extract_sheet_xml) | Function | L617–L640 | `str \| None` | Извлекает строковое XML-содержимое листа по имени напря... |
| [`_cell_has_expected_mark`](#_cell_has_expected_mark) | Function | L643–L653 | `bool` | Проверяет соответствие отметки посещаемости в XML-фрагм... |
| [`_marks_found_in_xml`](#_marks_found_in_xml) | Function | L656–L676 | `bool` | Проверяет наличие ожидаемых отметок в сыром XML-тексте ... |
| [`_verify_marks_in_raw`](#_verify_marks_in_raw) | Function | L679–L697 | `bool` | Координирует низкоуровневую верификацию отметок в байта... |
| [`get_month_sheet`](#get_month_sheet) | Function | L700–L711 | `Worksheet` | Возвращает рабочий лист книги openpyxl, соответствующий... |
| [`parse_date_cell`](#parse_date_cell) | Function | L714–L726 | `str \| None` | Приводит значение ячейки даты к стандартизированной стр... |
| [`find_date_column_start`](#find_date_column_start) | Function | L729–L743 | `int \| None` | Находит начальную колонку даты во второй строке таблицы... |
| [`find_lesson_column`](#find_lesson_column) | Function | L746–L764 | `int \| None` | Определяет точный номер колонки для конкретного номера ... |
| [`normalize_fio`](#normalize_fio) | Function | L767–L775 | `str` | Очищает строковое ФИО от неразрывных пробелов и лишних ... |
| [`get_students_list`](#get_students_list) | Function | L778–L794 | `list[tuple[int, str]]` | Извлекает список студентов академической группы из коло... |
| [`find_student_row`](#find_student_row) | Function | L797–L809 | `int \| None` | Находит номер строки студента в таблице по имени или фа... |
| [`write_student_mark`](#write_student_mark) | Function | L812–L832 | `None` | Записывает валидированную отметку посещаемости в целеву... |

---

## 3. Comprehensive Function Specifications

## Class Model: `WopiSession`

Сессия авторизованного доступа к документу по протоколу WOPI.

### `WopiSession.__init__`
```python
def __init__(self, resource_url: str, access_token: str, lock_id: str)
```

- **Source Reference**: [`integrations/yandex_docs.py#L56-L62`](../../integrations/yandex_docs.py#L56-L62)
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

- **Source Reference**: [`integrations/yandex_docs.py#L65-L79`](../../integrations/yandex_docs.py#L65-L79)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict`

#### Overview & Architectural Purpose
Извлекает JSON конфигурации редактора из HTML-разметки страницы документа.

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

- **Source Reference**: [`integrations/yandex_docs.py#L82-L98`](../../integrations/yandex_docs.py#L82-L98)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Объединяет текущую строку заголовка Cookie со свежими токенами из Set-Cookie.

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

- **Source Reference**: [`integrations/yandex_docs.py#L101-L116`](../../integrations/yandex_docs.py#L101-L116)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует резервную строку Cookie из статических переменных окружения.

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

- **Source Reference**: [`integrations/yandex_docs.py#L119-L138`](../../integrations/yandex_docs.py#L119-L138)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Предоставляет наиболее свежие Cookie сессии с приоритетом чтения из Redis.

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

- **Source Reference**: [`integrations/yandex_docs.py#L141-L158`](../../integrations/yandex_docs.py#L141-L158)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Атомарно сохраняет актуальную строку Cookie в постоянный кэш Redis с TTL.

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

- **Source Reference**: [`integrations/yandex_docs.py#L161-L175`](../../integrations/yandex_docs.py#L161-L175)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Извлекает полученные от сервера Set-Cookie и синхронизирует их с Redis.

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

- **Source Reference**: [`integrations/yandex_docs.py#L178-L197`](../../integrations/yandex_docs.py#L178-L197)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, str]`

#### Overview & Architectural Purpose
Формирует заголовки браузерного эмулятора для загрузки страницы документа.

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

- **Source Reference**: [`integrations/yandex_docs.py#L200-L216`](../../integrations/yandex_docs.py#L200-L216)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Загружает исходный HTML-код страницы веб-редактора Яндекс Документов.

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

- **Source Reference**: [`integrations/yandex_docs.py#L219-L234`](../../integrations/yandex_docs.py#L219-L234)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Определяет текущий активный идентификатор блокировки файла по стандарту WOPI.

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

- **Source Reference**: [`integrations/yandex_docs.py#L237-L256`](../../integrations/yandex_docs.py#L237-L256)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `WopiSession`

#### Overview & Architectural Purpose
Инициализирует сессию WOPI, извлекая resource_url, access_token и lock.

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

- **Source Reference**: [`integrations/yandex_docs.py#L259-L272`](../../integrations/yandex_docs.py#L259-L272)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `openpyxl.Workbook`

#### Overview & Architectural Purpose
Синхронно десериализует байты книги openpyxl с подавлением предупреждений.

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

- **Source Reference**: [`integrations/yandex_docs.py#L275-L297`](../../integrations/yandex_docs.py#L275-L297)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[tuple[str, int], int]`

#### Overview & Architectural Purpose
Вычисляет агрегированное количество отметок О, У, Н по строкам студентов.

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

- **Source Reference**: [`integrations/yandex_docs.py#L300-L326`](../../integrations/yandex_docs.py#L300-L326)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Заменяет кэшированные теги формул <v></v> в XML листа на вычисленные суммы.

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

- **Source Reference**: [`integrations/yandex_docs.py#L329-L339`](../../integrations/yandex_docs.py#L329-L339)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Записывает текстовые заголовки и условные обозначения итоговых колонок.

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

- **Source Reference**: [`integrations/yandex_docs.py#L342-L355`](../../integrations/yandex_docs.py#L342-L355)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Проставляет формулы COUNTIF для подсчета отметок по строкам 5-36.

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

- **Source Reference**: [`integrations/yandex_docs.py#L358-L380`](../../integrations/yandex_docs.py#L358-L380)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Гарантирует наличие заголовков, кодов и формул COUNTIF во всех листах месяцев.

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

- **Source Reference**: [`integrations/yandex_docs.py#L383-L403`](../../integrations/yandex_docs.py#L383-L403)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bytes`

#### Overview & Architectural Purpose
Инжектирует предрассчитанные значения формул COUNTIF прямо в zip-архив xlsx.

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

- **Source Reference**: [`integrations/yandex_docs.py#L406-L421`](../../integrations/yandex_docs.py#L406-L421)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bytes`

#### Overview & Architectural Purpose
Сериализует книгу openpyxl в бинарные байты с принудительным пересчетом формул.

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

- **Source Reference**: [`integrations/yandex_docs.py#L424-L440`](../../integrations/yandex_docs.py#L424-L440)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `openpyxl.Workbook`

#### Overview & Architectural Purpose
Скачивает актуальный контент таблицы по протоколу WOPI и возвращает объект книги.

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

- **Source Reference**: [`integrations/yandex_docs.py#L443-L455`](../../integrations/yandex_docs.py#L443-L455)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Захватывает монопольную сессионную блокировку файла по стандарту WOPI LOCK.

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

- **Source Reference**: [`integrations/yandex_docs.py#L458-L469`](../../integrations/yandex_docs.py#L458-L469)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Снимает активную сессионную блокировку с файла по стандарту WOPI UNLOCK.

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

- **Source Reference**: [`integrations/yandex_docs.py#L472-L493`](../../integrations/yandex_docs.py#L472-L493)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `httpx.Response`

#### Overview & Architectural Purpose
Выполняет HTTP POST-запрос с заголовком X-WOPI-Override: PUT для перезаписи файла.

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
async def _try_put_with_lock(session: WopiSession, client: httpx.AsyncClient, data: bytes) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L496-L515`](../../integrations/yandex_docs.py#L496-L515)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Пробует зафиксировать файл сначала с текущей сессионной блокировкой, затем с новой.

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

- **Source Reference**: [`integrations/yandex_docs.py#L518-L533`](../../integrations/yandex_docs.py#L518-L533)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Сохраняет книгу openpyxl и выгружает обновленную версию на Яндекс Диск по WOPI.

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

- **Source Reference**: [`integrations/yandex_docs.py#L536-L555`](../../integrations/yandex_docs.py#L536-L555)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Легковесно валидирует сохранение отметок путем прямого анализа XML листа.

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

- **Source Reference**: [`integrations/yandex_docs.py#L558-L572`](../../integrations/yandex_docs.py#L558-L572)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bytes`

#### Overview & Architectural Purpose
Скачивает сырые байты файла таблицы с сервера WOPI для верификации.

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

- **Source Reference**: [`integrations/yandex_docs.py#L575-L594`](../../integrations/yandex_docs.py#L575-L594)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Находит relationship ID (r:id) листа в структуре workbook.xml.

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

- **Source Reference**: [`integrations/yandex_docs.py#L597-L614`](../../integrations/yandex_docs.py#L597-L614)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Определяет путь к файлу XML листа внутри zip-пакета по его relationship ID.

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

- **Source Reference**: [`integrations/yandex_docs.py#L617-L640`](../../integrations/yandex_docs.py#L617-L640)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Извлекает строковое XML-содержимое листа по имени напрямую из zip-архива xlsx.

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

- **Source Reference**: [`integrations/yandex_docs.py#L643-L653`](../../integrations/yandex_docs.py#L643-L653)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет соответствие отметки посещаемости в XML-фрагменте ячейки.

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
def _marks_found_in_xml(xml_text: str, check_marks: dict[str, str]) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L656-L676`](../../integrations/yandex_docs.py#L656-L676)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет наличие ожидаемых отметок в сыром XML-тексте листа.

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
def _verify_marks_in_raw(raw: bytes, target_date: date, expected_marks: dict[str, str]) -> bool
```

- **Source Reference**: [`integrations/yandex_docs.py#L679-L697`](../../integrations/yandex_docs.py#L679-L697)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Координирует низкоуровневую верификацию отметок в байтах книги.

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

- **Source Reference**: [`integrations/yandex_docs.py#L700-L711`](../../integrations/yandex_docs.py#L700-L711)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Worksheet`

#### Overview & Architectural Purpose
Возвращает рабочий лист книги openpyxl, соответствующий месяцу даты.

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

- **Source Reference**: [`integrations/yandex_docs.py#L714-L726`](../../integrations/yandex_docs.py#L714-L726)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Приводит значение ячейки даты к стандартизированной строке 'ДД.ММ'.

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

- **Source Reference**: [`integrations/yandex_docs.py#L729-L743`](../../integrations/yandex_docs.py#L729-L743)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Находит начальную колонку даты во второй строке таблицы посещаемости.

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

- **Source Reference**: [`integrations/yandex_docs.py#L746-L764`](../../integrations/yandex_docs.py#L746-L764)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Определяет точный номер колонки для конкретного номера учебной пары дня.

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

- **Source Reference**: [`integrations/yandex_docs.py#L767-L775`](../../integrations/yandex_docs.py#L767-L775)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Очищает строковое ФИО от неразрывных пробелов и лишних краевых знаков.

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

- **Source Reference**: [`integrations/yandex_docs.py#L778-L794`](../../integrations/yandex_docs.py#L778-L794)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[tuple[int, str]]`

#### Overview & Architectural Purpose
Извлекает список студентов академической группы из колонки B таблицы.

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

- **Source Reference**: [`integrations/yandex_docs.py#L797-L809`](../../integrations/yandex_docs.py#L797-L809)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Находит номер строки студента в таблице по имени или фамилии.

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

- **Source Reference**: [`integrations/yandex_docs.py#L812-L832`](../../integrations/yandex_docs.py#L812-L832)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Записывает валидированную отметку посещаемости в целевую ячейку листа.

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
