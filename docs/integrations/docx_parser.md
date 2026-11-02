# Component Reference: `integrations/docx_parser.py`
> **File Path**: [`integrations/docx_parser.py`](../../integrations/docx_parser.py)
> **Subsystem**: `Cloud DOCX Parser`

## 1. Purpose
Модуль загрузки и парсинга контактов преподавателей с Yandex Disk.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`fetch_docx_bytes`](#fetch_docx_bytes) | Function | L46–L70 | `bytes \| None` | Загружает бинарные байты docx-файла с Яндекс Диска чере... |
| [`extract_row_texts`](#extract_row_texts) | Function | L73–L89 | `tuple[str, str]` | Извлекает нормализованное ФИО преподавателя и ссылку из... |
| [`parse_docx_teachers`](#parse_docx_teachers) | Function | L92–L113 | `dict[str, TeacherData]` | Распаковывает docx-архив в памяти и парсит таблицу конт... |
| [`_get_docx_lock`](#_get_docx_lock) | Function | L116–L127 | `asyncio.Lock` | Предоставляет лениво созданный мьютекс asyncio.Lock для... |
| [`_is_cache_fresh`](#_is_cache_fresh) | Function | L130–L144 | `bool` | Проверяет валидность локального кэша преподавателей с з... |
| [`_fetch_and_cache_teachers`](#_fetch_and_cache_teachers) | Function | L147–L165 | `dict[str, TeacherData]` | Загружает документ с диска, парсит преподавателей и сли... |
| [`get_teacher_links`](#get_teacher_links) | Function | L168–L184 | `dict[str, TeacherData]` | Предоставляет реестр контактов преподавателей с Singlef... |

---

## 3. Comprehensive Function Specifications

## Class Model: `TeacherData`

Типизированный словарь с контактной информацией преподавателя.

### `fetch_docx_bytes`
```python
async def fetch_docx_bytes() -> bytes | None
```

- **Source Reference**: [`integrations/docx_parser.py#L46-L70`](../../integrations/docx_parser.py#L46-L70)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bytes | None`

#### Overview & Architectural Purpose
Загружает бинарные байты docx-файла с Яндекс Диска через публичный API.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.
- Performs non-blocking network I/O over HTTP or gRPC.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from integrations.docx_parser import fetch_docx_bytes

# Execute call
result = await fetch_docx_bytes()
```

---

### `extract_row_texts`
```python
def extract_row_texts(row_elem: Any) -> tuple[str, str]
```

- **Source Reference**: [`integrations/docx_parser.py#L73-L89`](../../integrations/docx_parser.py#L73-L89)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, str]`

#### Overview & Architectural Purpose
Извлекает нормализованное ФИО преподавателя и ссылку из XML-строки таблицы docx.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `row_elem` | `Any` | Yes | Parameter `row_elem` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.docx_parser import extract_row_texts

# Execute call
result = extract_row_texts(row_elem=...)
```

---

### `parse_docx_teachers`
```python
def parse_docx_teachers(content: bytes) -> dict[str, TeacherData]
```

- **Source Reference**: [`integrations/docx_parser.py#L92-L113`](../../integrations/docx_parser.py#L92-L113)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, TeacherData]`

#### Overview & Architectural Purpose
Распаковывает docx-архив в памяти и парсит таблицу контактов преподавателей.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `content` | `bytes` | Yes | Parameter `content` of type `bytes`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from integrations.docx_parser import parse_docx_teachers

# Execute call
result = parse_docx_teachers(content=...)
```

---

### `_get_docx_lock`
```python
def _get_docx_lock() -> asyncio.Lock
```

- **Source Reference**: [`integrations/docx_parser.py#L116-L127`](../../integrations/docx_parser.py#L116-L127)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `asyncio.Lock`

#### Overview & Architectural Purpose
Предоставляет лениво созданный мьютекс asyncio.Lock для синхронизации запросов.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.docx_parser import _get_docx_lock

# Execute call
result = _get_docx_lock()
```

---

### `_is_cache_fresh`
```python
def _is_cache_fresh(now: float, force_refresh: bool) -> bool
```

- **Source Reference**: [`integrations/docx_parser.py#L130-L144`](../../integrations/docx_parser.py#L130-L144)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет валидность локального кэша преподавателей с защитой от спама.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now` | `float` | Yes | Parameter `now` of type `float`. |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.docx_parser import _is_cache_fresh

# Execute call
result = _is_cache_fresh(now=..., force_refresh=...)
```

---

### `_fetch_and_cache_teachers`
```python
async def _fetch_and_cache_teachers(now: float) -> dict[str, TeacherData]
```

- **Source Reference**: [`integrations/docx_parser.py#L147-L165`](../../integrations/docx_parser.py#L147-L165)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, TeacherData]`

#### Overview & Architectural Purpose
Загружает документ с диска, парсит преподавателей и сливает с кастомным списком.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `now` | `float` | Yes | Parameter `now` of type `float`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.docx_parser import _fetch_and_cache_teachers

# Execute call
result = await _fetch_and_cache_teachers(now=...)
```

---

### `get_teacher_links`
```python
async def get_teacher_links(force_refresh: bool = False) -> dict[str, TeacherData]
```

- **Source Reference**: [`integrations/docx_parser.py#L168-L184`](../../integrations/docx_parser.py#L168-L184)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, TeacherData]`

#### Overview & Architectural Purpose
Предоставляет реестр контактов преподавателей с Singleflight-блокировкой.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.docx_parser import get_teacher_links

# Execute call
result = await get_teacher_links(force_refresh=...)
```

---
