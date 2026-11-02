# Component Reference: `core/logger.py`
> **File Path**: [`core/logger.py`](../../core/logger.py)
> **Subsystem**: `Telemetry Logging`

## 1. Purpose
Единый модуль логирования платформы с поддержкой распределенного трейсинга.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`set_trace_id`](#set_trace_id) | Function | L33–L41 | `None` | Устанавливает идентификатор распределенного трейсинга в... |
| [`get_trace_id`](#get_trace_id) | Function | L44–L50 | `str` | Возвращает активный идентификатор трейсинга из текущего... |
| [`_TraceIdFilter.filter`](#_traceidfilterfilter) | Method | L56–L60 | `bool` | Добавляет форматированный префикс trace_id в объект Log... |
| [`_create_formatter`](#_create_formatter) | Function | L63–L74 | `logging.Formatter` | Создает унифицированный форматтер строковых записей с п... |
| [`_create_stream_handler`](#_create_stream_handler) | Function | L77–L89 | `logging.StreamHandler` | Создает потоковый обработчик для вывода сообщений в std... |
| [`_resolve_log_file`](#_resolve_log_file) | Function | L92–L102 | `str` | Определяет лог-файл текущего сервиса. |
| [`_create_rotating_file_handler`](#_create_rotating_file_handler) | Function | L105–L129 | `RotatingFileHandler \| None` | Создает ротируемый файловый обработчик журналов с огран... |
| [`_get_shared_handlers`](#_get_shared_handlers) | Function | L132–L146 | `list[logging.Handler]` | Возвращает хэндлеры процесса (stdout + файл сервиса), с... |
| [`get_logger`](#get_logger) | Function | L149–L164 | `logging.Logger` | Возвращает синглтон-экземпляр логгера для указанной под... |

---

## 3. Comprehensive Function Specifications

### `set_trace_id`
```python
def set_trace_id(trace_id: str) -> None
```

- **Source Reference**: [`core/logger.py#L33-L41`](../../core/logger.py#L33-L41)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Устанавливает идентификатор распределенного трейсинга в текущий контекст asyncio.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `trace_id` | `str` | Yes | Parameter `trace_id` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.logger import set_trace_id

# Execute call
result = set_trace_id(trace_id=...)
```

---

### `get_trace_id`
```python
def get_trace_id() -> str
```

- **Source Reference**: [`core/logger.py#L44-L50`](../../core/logger.py#L44-L50)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает активный идентификатор трейсинга из текущего контекста.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.logger import get_trace_id

# Execute call
result = get_trace_id()
```

---

## Class Model: `_TraceIdFilter`

Инжектирует контекстный trace_id в каждую запись лога.

### `_TraceIdFilter.filter`
```python
def filter(self, record: logging.LogRecord) -> bool
```

- **Source Reference**: [`core/logger.py#L56-L60`](../../core/logger.py#L56-L60)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Добавляет форматированный префикс trace_id в объект LogRecord.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `record` | `logging.LogRecord` | Yes | Parameter `record` of type `logging.LogRecord`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.logger import filter

# Execute call
result = filter(record=...)
```

---

### `_create_formatter`
```python
def _create_formatter() -> logging.Formatter
```

- **Source Reference**: [`core/logger.py#L63-L74`](../../core/logger.py#L63-L74)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `logging.Formatter`

#### Overview & Architectural Purpose
Создает унифицированный форматтер строковых записей с поддержкой trace_id.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.logger import _create_formatter

# Execute call
result = _create_formatter()
```

---

### `_create_stream_handler`
```python
def _create_stream_handler(formatter: logging.Formatter) -> logging.StreamHandler
```

- **Source Reference**: [`core/logger.py#L77-L89`](../../core/logger.py#L77-L89)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `logging.StreamHandler`

#### Overview & Architectural Purpose
Создает потоковый обработчик для вывода сообщений в stdout.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `formatter` | `logging.Formatter` | Yes | Parameter `formatter` of type `logging.Formatter`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.logger import _create_stream_handler

# Execute call
result = _create_stream_handler(formatter=...)
```

---

### `_resolve_log_file`
```python
def _resolve_log_file() -> str
```

- **Source Reference**: [`core/logger.py#L92-L102`](../../core/logger.py#L92-L102)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Определяет лог-файл текущего сервиса.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.logger import _resolve_log_file

# Execute call
result = _resolve_log_file()
```

---

### `_create_rotating_file_handler`
```python
def _create_rotating_file_handler(formatter: logging.Formatter) -> RotatingFileHandler | None
```

- **Source Reference**: [`core/logger.py#L105-L129`](../../core/logger.py#L105-L129)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `RotatingFileHandler | None`

#### Overview & Architectural Purpose
Создает ротируемый файловый обработчик журналов с ограничением размера.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `formatter` | `logging.Formatter` | Yes | Parameter `formatter` of type `logging.Formatter`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.logger import _create_rotating_file_handler

# Execute call
result = _create_rotating_file_handler(formatter=...)
```

---

### `_get_shared_handlers`
```python
def _get_shared_handlers() -> list[logging.Handler]
```

- **Source Reference**: [`core/logger.py#L132-L146`](../../core/logger.py#L132-L146)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[logging.Handler]`

#### Overview & Architectural Purpose
Возвращает хэндлеры процесса (stdout + файл сервиса), создавая их один раз.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.logger import _get_shared_handlers

# Execute call
result = _get_shared_handlers()
```

---

### `get_logger`
```python
def get_logger(name: str) -> logging.Logger
```

- **Source Reference**: [`core/logger.py#L149-L164`](../../core/logger.py#L149-L164)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `logging.Logger`

#### Overview & Architectural Purpose
Возвращает синглтон-экземпляр логгера для указанной подсистемы.

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
from core.logger import get_logger

# Execute call
result = get_logger(name=...)
```

---
