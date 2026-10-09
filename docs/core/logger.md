# Module Specification: `core/logger.py`
> **Path**: [`core/logger.py`](file:///home/u/Рабочий стол/para/core/logger.py)  
> **Subsystem**: `Telemetry Logging`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Единый модуль логирования проекта. Предоставляет настроенный логгер с выводом в консоль и ротируемый файл logs/bot.log. Использует RotatingFileHandler (до 10 МБ на файл, 5 бэкапов) для защиты диска от переполнения.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_create_formatter`](#_create_formatter) | Function | L18–L23 | `logging.Formatter` | Создает единый форматтер сообщений для консоли и файла. |
| [`_create_stream_handler`](#_create_stream_handler) | Function | L26–L31 | `logging.StreamHandler` | Создает консольный хэндлер со стандартным потоком вывода. |
| [`_create_rotating_file_handler`](#_create_rotating_file_handler) | Function | L34–L49 | `RotatingFileHandler` | Создает ротируемый файловый хэндлер UTF-8 с лимитом размера. |
| [`get_logger`](#get_logger) | Function | L52–L67 | `logging.Logger` | Создает и настраивает логгер для заданной подсистемы. |

---

## 3. Exhaustive Function Specifications

### `_create_formatter`
- **Signature**: `def _create_formatter() -> logging.Formatter`
- **Source Reference**: [core/logger.py#L18-L23](file:///home/u/Рабочий стол/para/core/logger.py#L18-L23)
- **Async**: `No`
- **Return Type**: `logging.Formatter`

#### Purpose & Architectural Intent
Создает единый форматтер сообщений для консоли и файла.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return logging.Formatter(`

---

### `_create_stream_handler`
- **Signature**: `def _create_stream_handler(formatter: logging.Formatter) -> logging.StreamHandler`
- **Source Reference**: [core/logger.py#L26-L31](file:///home/u/Рабочий стол/para/core/logger.py#L26-L31)
- **Async**: `No`
- **Return Type**: `logging.StreamHandler`

#### Purpose & Architectural Intent
Создает консольный хэндлер со стандартным потоком вывода.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `formatter` | `logging.Formatter` | Input parameter |

#### Step-by-Step Logic Execution
1. `handler = logging.StreamHandler(sys.stdout)`
2. `handler.setFormatter(formatter)`
3. `handler.setLevel(logging.INFO)`
4. `return handler`

---

### `_create_rotating_file_handler`
- **Signature**: `def _create_rotating_file_handler(formatter: logging.Formatter) -> RotatingFileHandler`
- **Source Reference**: [core/logger.py#L34-L49](file:///home/u/Рабочий стол/para/core/logger.py#L34-L49)
- **Async**: `No`
- **Return Type**: `RotatingFileHandler`

#### Purpose & Architectural Intent
Создает ротируемый файловый хэндлер UTF-8 с лимитом размера. Защищает диск сервера от бесконтрольного роста логов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `formatter` | `logging.Formatter` | Input parameter |

#### Step-by-Step Logic Execution
1. `os.makedirs("logs", exist_ok=True)`
2. `handler = RotatingFileHandler(`
3. `handler.setFormatter(formatter)`
4. `handler.setLevel(logging.DEBUG)`
5. `return handler`

---

### `get_logger`
- **Signature**: `def get_logger(name: str) -> logging.Logger`
- **Source Reference**: [core/logger.py#L52-L67](file:///home/u/Рабочий стол/para/core/logger.py#L52-L67)
- **Async**: `No`
- **Return Type**: `logging.Logger`

#### Purpose & Architectural Intent
Создает и настраивает логгер для заданной подсистемы. :param name: Смысловое название компонента (напр. 'schedule_parser') :return: Экземпляр logging.Logger

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `logger = logging.getLogger(name)`
2. `if logger.handlers:`
3. `logger.setLevel(logging.DEBUG)`
4. `formatter = _create_formatter()`
5. `logger.addHandler(_create_stream_handler(formatter))`
6. `logger.addHandler(_create_rotating_file_handler(formatter))`

---
