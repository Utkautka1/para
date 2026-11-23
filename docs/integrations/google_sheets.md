# Component Reference: `integrations/google_sheets.py`
> **File Path**: [`integrations/google_sheets.py`](../../integrations/google_sheets.py)
> **Subsystem**: `Google Sheets Attendance Service`

## 1. Purpose
Сервис интеграции с Google Sheets и Google Drive API для журнала посещаемости.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_GoogleAuthResponse.__init__`](#_googleauthresponse__init__) | Method | L59–L61 | `None` | Executes core domain logic for `__init__`. |
| [`_GoogleAuthResponse.status`](#_googleauthresponsestatus) | Method | L64–L66 | `int` | HTTP-статус код ответа сервера авторизации Google. |
| [`_GoogleAuthResponse.headers`](#_googleauthresponseheaders) | Method | L69–L71 | `Any` | Заголовки ответа сервера авторизации Google. |
| [`_GoogleAuthResponse.data`](#_googleauthresponsedata) | Method | L74–L76 | `bytes` | Бинарное тело ответа сервера с OAuth-токеном. |
| [`_GoogleAuthRequest.__call__`](#_googleauthrequest__call__) | Method | L82–L101 | `_GoogleAuthResponse` | Выполняет синхронный запрос к OAuth-эндпоинту Google че... |
| [`_load_credentials`](#_load_credentials) | Function | L104–L116 | `Any` | Загружает учетные данные сервисного аккаунта Google из ... |
| [`_fetch_token_sync`](#_fetch_token_sync) | Function | L119–L130 | `str` | Синхронно обновляет и возвращает OAuth токен Google API... |
| [`get_access_token`](#get_access_token) | Function | L133–L141 | `str` | Асинхронно получает валидный токен авторизации для Goog... |
| [`col_to_letter`](#col_to_letter) | Function | L144–L156 | `str` | Преобразует 1-based числовой индекс колонки в буквенное... |
| [`normalize_fio`](#normalize_fio) | Function | L159–L167 | `str` | Очищает строковое ФИО от неразрывных пробелов и краевых... |
| [`get_month_sheet_name`](#get_month_sheet_name) | Function | L170–L181 | `str` | Возвращает название листа месяца по дате. |
| [`get_month_sheet`](#get_month_sheet) | Function | L184–L195 | `Worksheet` | Возвращает рабочий лист книги openpyxl, соответствующий... |
| [`export_attendance_xlsx`](#export_attendance_xlsx) | Function | L198–L214 | `bytes` | Экспортирует Google Таблицу посещаемости целиком в бина... |
| [`download_workbook`](#download_workbook) | Function | L217–L226 | `openpyxl.Workbook` | Скачивает всю Google Таблицу и преобразует её в книгу o... |
| [`fetch_students_from_google`](#fetch_students_from_google) | Function | L229–L247 | `list[tuple[int, str]]` | Считывает список студентов академической группы из коло... |
| [`find_lesson_column_in_grid`](#find_lesson_column_in_grid) | Function | L250–L268 | `int \| None` | Находит 1-based номер колонки пары по строкам дат и ном... |
| [`parse_date_cell`](#parse_date_cell) | Function | L271–L283 | `str \| None` | Приводит значение ячейки даты к стандартизированной стр... |
| [`find_date_column_start`](#find_date_column_start) | Function | L286–L299 | `int \| None` | Находит начальную колонку даты во второй строке листа o... |
| [`get_students_list`](#get_students_list) | Function | L302–L318 | `list[tuple[int, str]]` | Извлекает список студентов группы из колонки B листа op... |
| [`find_student_row`](#find_student_row) | Function | L321–L333 | `int \| None` | Находит номер строки студента в листе openpyxl по имени... |
| [`find_lesson_column`](#find_lesson_column) | Function | L336–L352 | `int \| None` | Находит номер колонки пары в openpyxl листе или передан... |
| [`write_student_mark`](#write_student_mark) | Function | L355–L368 | `None` | Записывает отметку посещаемости в ячейку листа openpyxl... |
| [`_fetch_header_grid`](#_fetch_header_grid) | Function | L371–L387 | `tuple[list[str], list[str]]` | Считывает строки дат (строка 2) и пар (строка 4) из Goo... |
| [`_build_batch_data`](#_build_batch_data) | Function | L390–L404 | `list[dict[str, Any]]` | Формирует массив обновлений ячеек для Google Sheets API... |
| [`_send_batch_update`](#_send_batch_update) | Function | L407–L416 | `None` | Отправляет POST-запрос пакетного обновления batchUpdate... |
| [`write_lesson_marks`](#write_lesson_marks) | Function | L419–L441 | `bool` | Атомарно записывает отметки посещаемости пары в Google ... |

---

## 3. Comprehensive Function Specifications

## Class Model: `_GoogleAuthResponse`

Адаптер ответа HTTP-клиента под интерфейс google.auth.transport.Response.

### `_GoogleAuthResponse.__init__`
```python
def __init__(self, response: httpx.Response) -> None
```

- **Source Reference**: [`integrations/google_sheets.py#L59-L61`](../../integrations/google_sheets.py#L59-L61)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Executes core domain logic for `__init__`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `response` | `httpx.Response` | Yes | Parameter `response` of type `httpx.Response`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import __init__

# Execute call
result = __init__(response=...)
```

---

### `_GoogleAuthResponse.status`
```python
def status(self) -> int
```

- **Source Reference**: [`integrations/google_sheets.py#L64-L66`](../../integrations/google_sheets.py#L64-L66)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int`

#### Overview & Architectural Purpose
HTTP-статус код ответа сервера авторизации Google.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import status

# Execute call
result = status()
```

---

### `_GoogleAuthResponse.headers`
```python
def headers(self) -> Any
```

- **Source Reference**: [`integrations/google_sheets.py#L69-L71`](../../integrations/google_sheets.py#L69-L71)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Заголовки ответа сервера авторизации Google.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import headers

# Execute call
result = headers()
```

---

### `_GoogleAuthResponse.data`
```python
def data(self) -> bytes
```

- **Source Reference**: [`integrations/google_sheets.py#L74-L76`](../../integrations/google_sheets.py#L74-L76)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bytes`

#### Overview & Architectural Purpose
Бинарное тело ответа сервера с OAuth-токеном.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import data

# Execute call
result = data()
```

---

## Class Model: `_GoogleAuthRequest`

Адаптер HTTP-транспорта на базе httpx для обновления токенов google-auth.

### `_GoogleAuthRequest.__call__`
```python
def __call__( self, url: str, method: str = "GET", body: Any = None, headers: Any = None, timeout: float | None = None, **kwargs: Any,
```

- **Source Reference**: [`integrations/google_sheets.py#L82-L101`](../../integrations/google_sheets.py#L82-L101)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `_GoogleAuthResponse`

#### Overview & Architectural Purpose
Выполняет синхронный запрос к OAuth-эндпоинту Google через httpx.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `url` | `str` | Yes | Parameter `url` of type `str`. |
| `method` | `str` | Yes | Parameter `method` of type `str`. |
| `body` | `Any` | Yes | Parameter `body` of type `Any`. |
| `headers` | `Any` | Yes | Parameter `headers` of type `Any`. |
| `timeout` | `float | None` | Yes | Parameter `timeout` of type `float | None`. |

#### Concurrency & Side Effects
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import __call__

# Execute call
result = __call__(url=..., method=..., body=...)
```

---

### `_load_credentials`
```python
def _load_credentials() -> Any
```

- **Source Reference**: [`integrations/google_sheets.py#L104-L116`](../../integrations/google_sheets.py#L104-L116)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Загружает учетные данные сервисного аккаунта Google из JSON-строки или файла.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import _load_credentials

# Execute call
result = _load_credentials()
```

---

### `_fetch_token_sync`
```python
def _fetch_token_sync() -> str
```

- **Source Reference**: [`integrations/google_sheets.py#L119-L130`](../../integrations/google_sheets.py#L119-L130)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Синхронно обновляет и возвращает OAuth токен Google API.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import _fetch_token_sync

# Execute call
result = _fetch_token_sync()
```

---

### `get_access_token`
```python
async def get_access_token() -> str
```

- **Source Reference**: [`integrations/google_sheets.py#L133-L141`](../../integrations/google_sheets.py#L133-L141)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Асинхронно получает валидный токен авторизации для Google API.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import get_access_token

# Execute call
result = await get_access_token()
```

---

### `col_to_letter`
```python
def col_to_letter(col: int) -> str
```

- **Source Reference**: [`integrations/google_sheets.py#L144-L156`](../../integrations/google_sheets.py#L144-L156)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Преобразует 1-based числовой индекс колонки в буквенное обозначение формата A1.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `col` | `int` | Yes | Parameter `col` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import col_to_letter

# Execute call
result = col_to_letter(col=...)
```

---

### `normalize_fio`
```python
def normalize_fio(name: str) -> str
```

- **Source Reference**: [`integrations/google_sheets.py#L159-L167`](../../integrations/google_sheets.py#L159-L167)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Очищает строковое ФИО от неразрывных пробелов и краевых символов.

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
from integrations.google_sheets import normalize_fio

# Execute call
result = normalize_fio(name=...)
```

---

### `get_month_sheet_name`
```python
def get_month_sheet_name(target_date: date) -> str
```

- **Source Reference**: [`integrations/google_sheets.py#L170-L181`](../../integrations/google_sheets.py#L170-L181)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает название листа месяца по дате.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.google_sheets import get_month_sheet_name

# Execute call
result = get_month_sheet_name(target_date=...)
```

---

### `get_month_sheet`
```python
def get_month_sheet(wb: openpyxl.Workbook, target_date: date) -> Worksheet
```

- **Source Reference**: [`integrations/google_sheets.py#L184-L195`](../../integrations/google_sheets.py#L184-L195)
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
from integrations.google_sheets import get_month_sheet

# Execute call
result = get_month_sheet(wb=..., target_date=...)
```

---

### `export_attendance_xlsx`
```python
async def export_attendance_xlsx() -> bytes
```

- **Source Reference**: [`integrations/google_sheets.py#L198-L214`](../../integrations/google_sheets.py#L198-L214)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bytes`

#### Overview & Architectural Purpose
Экспортирует Google Таблицу посещаемости целиком в бинарный формат .xlsx.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import export_attendance_xlsx

# Execute call
result = await export_attendance_xlsx()
```

---

### `download_workbook`
```python
async def download_workbook() -> openpyxl.Workbook
```

- **Source Reference**: [`integrations/google_sheets.py#L217-L226`](../../integrations/google_sheets.py#L217-L226)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `openpyxl.Workbook`

#### Overview & Architectural Purpose
Скачивает всю Google Таблицу и преобразует её в книгу openpyxl в памяти.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import download_workbook

# Execute call
result = await download_workbook()
```

---

### `fetch_students_from_google`
```python
async def fetch_students_from_google(target_date: date) -> list[tuple[int, str]]
```

- **Source Reference**: [`integrations/google_sheets.py#L229-L247`](../../integrations/google_sheets.py#L229-L247)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[tuple[int, str]]`

#### Overview & Architectural Purpose
Считывает список студентов академической группы из колонки B месяца.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import fetch_students_from_google

# Execute call
result = await fetch_students_from_google(target_date=...)
```

---

### `find_lesson_column_in_grid`
```python
def find_lesson_column_in_grid( dates_row: list[str], pairs_row: list[str], target_date: date, lesson_num: int ) -> int | None
```

- **Source Reference**: [`integrations/google_sheets.py#L250-L268`](../../integrations/google_sheets.py#L250-L268)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Находит 1-based номер колонки пары по строкам дат и номеров пар из таблицы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `dates_row` | `list[str]` | Yes | Parameter `dates_row` of type `list[str]`. |
| `pairs_row` | `list[str]` | Yes | Parameter `pairs_row` of type `list[str]`. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import find_lesson_column_in_grid

# Execute call
result = find_lesson_column_in_grid(dates_row=..., pairs_row=..., target_date=...)
```

---

### `parse_date_cell`
```python
def parse_date_cell(cell_value: object) -> str | None
```

- **Source Reference**: [`integrations/google_sheets.py#L271-L283`](../../integrations/google_sheets.py#L271-L283)
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
from integrations.google_sheets import parse_date_cell

# Execute call
result = parse_date_cell(cell_value=...)
```

---

### `find_date_column_start`
```python
def find_date_column_start(sheet: Worksheet, target_date: date) -> int | None
```

- **Source Reference**: [`integrations/google_sheets.py#L286-L299`](../../integrations/google_sheets.py#L286-L299)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Находит начальную колонку даты во второй строке листа openpyxl.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import find_date_column_start

# Execute call
result = find_date_column_start(sheet=..., target_date=...)
```

---

### `get_students_list`
```python
def get_students_list(sheet: Worksheet) -> list[tuple[int, str]]
```

- **Source Reference**: [`integrations/google_sheets.py#L302-L318`](../../integrations/google_sheets.py#L302-L318)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[tuple[int, str]]`

#### Overview & Architectural Purpose
Извлекает список студентов группы из колонки B листа openpyxl.

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
from integrations.google_sheets import get_students_list

# Execute call
result = get_students_list(sheet=...)
```

---

### `find_student_row`
```python
def find_student_row(sheet: Worksheet, student_name: str) -> int | None
```

- **Source Reference**: [`integrations/google_sheets.py#L321-L333`](../../integrations/google_sheets.py#L321-L333)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Находит номер строки студента в листе openpyxl по имени или фамилии.

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
from integrations.google_sheets import find_student_row

# Execute call
result = find_student_row(sheet=..., student_name=...)
```

---

### `find_lesson_column`
```python
def find_lesson_column(sheet: Any, target_date: date, lesson_num: int) -> int | None
```

- **Source Reference**: [`integrations/google_sheets.py#L336-L352`](../../integrations/google_sheets.py#L336-L352)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Находит номер колонки пары в openpyxl листе или переданной структуре.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Any` | Yes | Parameter `sheet` of type `Any`. |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import find_lesson_column

# Execute call
result = find_lesson_column(sheet=..., target_date=..., lesson_num=...)
```

---

### `write_student_mark`
```python
def write_student_mark(sheet: Worksheet, row: int, col: int, mark: str) -> None
```

- **Source Reference**: [`integrations/google_sheets.py#L355-L368`](../../integrations/google_sheets.py#L355-L368)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Записывает отметку посещаемости в ячейку листа openpyxl.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `row` | `int` | Yes | Parameter `row` of type `int`. |
| `col` | `int` | Yes | Parameter `col` of type `int`. |
| `mark` | `str` | Yes | Attendance evaluation symbol assigned to the student. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.google_sheets import write_student_mark

# Execute call
result = write_student_mark(sheet=..., row=..., col=...)
```

---

### `_fetch_header_grid`
```python
async def _fetch_header_grid(sheet_name: str, token: str) -> tuple[list[str], list[str]]
```

- **Source Reference**: [`integrations/google_sheets.py#L371-L387`](../../integrations/google_sheets.py#L371-L387)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[list[str], list[str]]`

#### Overview & Architectural Purpose
Считывает строки дат (строка 2) и пар (строка 4) из Google Таблицы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet_name` | `str` | Yes | Parameter `sheet_name` of type `str`. |
| `token` | `str` | Yes | Parameter `token` of type `str`. |

#### Concurrency & Side Effects
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import _fetch_header_grid

# Execute call
result = await _fetch_header_grid(sheet_name=..., token=...)
```

---

### `_build_batch_data`
```python
def _build_batch_data(sheet_name: str, col_letter: str, marks: dict[str, str]) -> list[dict[str, Any]]
```

- **Source Reference**: [`integrations/google_sheets.py#L390-L404`](../../integrations/google_sheets.py#L390-L404)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[dict[str, Any]]`

#### Overview & Architectural Purpose
Формирует массив обновлений ячеек для Google Sheets API batchUpdate.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet_name` | `str` | Yes | Parameter `sheet_name` of type `str`. |
| `col_letter` | `str` | Yes | Parameter `col_letter` of type `str`. |
| `marks` | `dict[str, str]` | Yes | Parameter `marks` of type `dict[str, str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import _build_batch_data

# Execute call
result = _build_batch_data(sheet_name=..., col_letter=..., marks=...)
```

---

### `_send_batch_update`
```python
async def _send_batch_update(token: str, payload: dict[str, Any]) -> None
```

- **Source Reference**: [`integrations/google_sheets.py#L407-L416`](../../integrations/google_sheets.py#L407-L416)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет POST-запрос пакетного обновления batchUpdate в Google Sheets API.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `token` | `str` | Yes | Parameter `token` of type `str`. |
| `payload` | `dict[str, Any]` | Yes | Parameter `payload` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.google_sheets import _send_batch_update

# Execute call
result = await _send_batch_update(token=..., payload=...)
```

---

### `write_lesson_marks`
```python
async def write_lesson_marks(target_date: date, lesson_num: int, marks: dict[str, str]) -> bool
```

- **Source Reference**: [`integrations/google_sheets.py#L419-L441`](../../integrations/google_sheets.py#L419-L441)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Атомарно записывает отметки посещаемости пары в Google Таблицу через batchUpdate.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_date` | `date` | Yes | Target calendar date for schedule or attendance resolution (ISO-8601). |
| `lesson_num` | `int` | Yes | Academic class sequence index (1-based, 1 to 6). |
| `marks` | `dict[str, str]` | Yes | Parameter `marks` of type `dict[str, str]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from integrations.google_sheets import write_lesson_marks

# Execute call
result = await write_lesson_marks(target_date=..., lesson_num=..., marks=...)
```

---
