# Component Reference: `services/solver/payload_extractor.py`
> **File Path**: [`services/solver/payload_extractor.py`](../../services/solver/payload_extractor.py)
> **Subsystem**: `Solver Payload Ingestion`

## 1. Purpose
Модуль извлечения и парсинга полезной нагрузки задач ДЗ.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`download_file_bytes`](#download_file_bytes) | Function | L21–L45 | `bytes \| None` | Безопасно скачивает байты файла из Telegram с контролем... |
| [`_extract_docx_images`](#_extract_docx_images) | Function | L48–L64 | `list[bytes]` | Извлекает бинарные данные встроенных изображений из стр... |
| [`extract_docx_data`](#extract_docx_data) | Function | L67–L86 | `tuple[str, list[bytes]]` | Извлекает весь текстовый контент и встроенные изображен... |
| [`extract_pdf_data`](#extract_pdf_data) | Function | L89–L106 | `str` | Извлекает текстовые слои со всех страниц переданного PD... |
| [`_read_code_file_payload`](#_read_code_file_payload) | Function | L109–L122 | `str` | Декодирует текстовый файл исходного кода с контролем ма... |
| [`parse_file_payload`](#parse_file_payload) | Function | L125–L150 | `tuple[bytes \| None, str \| None]` | Разбирает байты файла (изображение, docx, pdf, текст) в... |
| [`resolve_task_payload`](#resolve_task_payload) | Function | L153–L175 | `tuple[bytes \| None, str \| None]` | Скачивает и подготавливает медиа/текст задания для пере... |

---

## 3. Comprehensive Function Specifications

### `download_file_bytes`
```python
async def download_file_bytes(tg_bot: Bot, file_id: str, file_size: int) -> bytes | None
```

- **Source Reference**: [`services/solver/payload_extractor.py#L21-L45`](../../services/solver/payload_extractor.py#L21-L45)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bytes | None`

#### Overview & Architectural Purpose
Безопасно скачивает байты файла из Telegram с контролем лимита размера.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `tg_bot` | `Bot` | Yes | Parameter `tg_bot` of type `Bot`. |
| `file_id` | `str` | Yes | Parameter `file_id` of type `str`. |
| `file_size` | `int` | Yes | Size of the audio file in bytes. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.solver.payload_extractor import download_file_bytes

# Execute call
result = await download_file_bytes(tg_bot=..., file_id=..., file_size=...)
```

---

### `_extract_docx_images`
```python
def _extract_docx_images(doc) -> list[bytes]
```

- **Source Reference**: [`services/solver/payload_extractor.py#L48-L64`](../../services/solver/payload_extractor.py#L48-L64)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[bytes]`

#### Overview & Architectural Purpose
Извлекает бинарные данные встроенных изображений из структуры docx.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Any` | Yes | Parameter `doc` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.solver.payload_extractor import _extract_docx_images

# Execute call
result = _extract_docx_images(doc=...)
```

---

### `extract_docx_data`
```python
def extract_docx_data(doc_bytes: bytes) -> tuple[str, list[bytes]]
```

- **Source Reference**: [`services/solver/payload_extractor.py#L67-L86`](../../services/solver/payload_extractor.py#L67-L86)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, list[bytes]]`

#### Overview & Architectural Purpose
Извлекает весь текстовый контент и встроенные изображения из .docx документа.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc_bytes` | `bytes` | Yes | Parameter `doc_bytes` of type `bytes`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.solver.payload_extractor import extract_docx_data

# Execute call
result = extract_docx_data(doc_bytes=...)
```

---

### `extract_pdf_data`
```python
def extract_pdf_data(doc_bytes: bytes) -> str
```

- **Source Reference**: [`services/solver/payload_extractor.py#L89-L106`](../../services/solver/payload_extractor.py#L89-L106)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Извлекает текстовые слои со всех страниц переданного PDF-документа.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc_bytes` | `bytes` | Yes | Parameter `doc_bytes` of type `bytes`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.solver.payload_extractor import extract_pdf_data

# Execute call
result = extract_pdf_data(doc_bytes=...)
```

---

### `_read_code_file_payload`
```python
def _read_code_file_payload(doc_bytes: bytes, file_name: str, prompt: str) -> str
```

- **Source Reference**: [`services/solver/payload_extractor.py#L109-L122`](../../services/solver/payload_extractor.py#L109-L122)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Декодирует текстовый файл исходного кода с контролем максимальной длины.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc_bytes` | `bytes` | Yes | Parameter `doc_bytes` of type `bytes`. |
| `file_name` | `str` | Yes | Parameter `file_name` of type `str`. |
| `prompt` | `str` | Yes | Parameter `prompt` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.solver.payload_extractor import _read_code_file_payload

# Execute call
result = _read_code_file_payload(doc_bytes=..., file_name=..., prompt=...)
```

---

### `parse_file_payload`
```python
def parse_file_payload( doc_bytes: bytes, file_name: str, mime: str | None, prompt: str ) -> tuple[bytes | None, str | None]
```

- **Source Reference**: [`services/solver/payload_extractor.py#L125-L150`](../../services/solver/payload_extractor.py#L125-L150)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[bytes | None, str | None]`

#### Overview & Architectural Purpose
Разбирает байты файла (изображение, docx, pdf, текст) в формат для DeepSeek.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc_bytes` | `bytes` | Yes | Parameter `doc_bytes` of type `bytes`. |
| `file_name` | `str` | Yes | Parameter `file_name` of type `str`. |
| `mime` | `str | None` | Yes | Parameter `mime` of type `str | None`. |
| `prompt` | `str` | Yes | Parameter `prompt` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.solver.payload_extractor import parse_file_payload

# Execute call
result = parse_file_payload(doc_bytes=..., file_name=..., mime=...)
```

---

### `resolve_task_payload`
```python
async def resolve_task_payload(tg_bot: Bot, task: dict) -> tuple[bytes | None, str | None]
```

- **Source Reference**: [`services/solver/payload_extractor.py#L153-L175`](../../services/solver/payload_extractor.py#L153-L175)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[bytes | None, str | None]`

#### Overview & Architectural Purpose
Скачивает и подготавливает медиа/текст задания для передачи в нейросеть.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `tg_bot` | `Bot` | Yes | Parameter `tg_bot` of type `Bot`. |
| `task` | `dict` | Yes | Parameter `task` of type `dict`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.solver.payload_extractor import resolve_task_payload

# Execute call
result = await resolve_task_payload(tg_bot=..., task=...)
```

---
