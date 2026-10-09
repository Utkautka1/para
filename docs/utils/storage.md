# Module Specification: `utils/storage.py`
> **Path**: [`utils/storage.py`](file:///home/u/Рабочий стол/para/utils/storage.py)  
> **Subsystem**: `Atomic Storage Engine`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль атомарного и безопасного ввода-вывода JSON-файлов. Гарантирует сохранность состояния при рестартах и сбоях: запись производится через временный файл с последующим os.replace. Асинхронные обертки используют asyncio.to_thread для предотвращения блокировки Event Loop.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`sync_load_json`](#sync_load_json) | Function | L20–L35 | `Any` | Синхронно считывает данные из JSON файла. |
| [`_write_temp_and_replace`](#_write_temp_and_replace) | Function | L38–L55 | `bool` | Записывает данные во временный файл и атомарно заменяет целе |
| [`sync_atomic_save_json`](#sync_atomic_save_json) | Function | L58–L66 | `bool` | Синхронно и атомарно сохраняет данные в JSON файл. |
| [`load_json`](#load_json) | Function | L69–L77 | `Any` | Асинхронно считывает JSON в пуле потоков без блокировки цикл |
| [`save_json`](#save_json) | Function | L80–L88 | `bool` | Асинхронно и атомарно сохраняет JSON в пуле потоков. |

---

## 3. Exhaustive Function Specifications

### `sync_load_json`
- **Signature**: `def sync_load_json(file_path: str, default: Any = None) -> Any`
- **Source Reference**: [utils/storage.py#L20-L35](file:///home/u/Рабочий стол/para/utils/storage.py#L20-L35)
- **Async**: `No`
- **Return Type**: `Any`

#### Purpose & Architectural Intent
Синхронно считывает данные из JSON файла. :param file_path: Путь к файлу :param default: Значение по умолчанию при отсутствии или ошибке :return: Распарсенные данные или default

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `file_path` | `str` | Input parameter |
| `default` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not os.path.exists(file_path):`
2. `try:`

---

### `_write_temp_and_replace`
- **Signature**: `def _write_temp_and_replace(file_path: str, data: Any) -> bool`
- **Source Reference**: [utils/storage.py#L38-L55](file:///home/u/Рабочий стол/para/utils/storage.py#L38-L55)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Записывает данные во временный файл и атомарно заменяет целевой файл.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `file_path` | `str` | Input parameter |
| `data` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `dir_name = os.path.dirname(os.path.abspath(file_path))`
2. `os.makedirs(dir_name, exist_ok=True)`
3. `temp_path = None`
4. `try:`

---

### `sync_atomic_save_json`
- **Signature**: `def sync_atomic_save_json(file_path: str, data: Any) -> bool`
- **Source Reference**: [utils/storage.py#L58-L66](file:///home/u/Рабочий стол/para/utils/storage.py#L58-L66)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Синхронно и атомарно сохраняет данные в JSON файл. :param file_path: Путь к целевому файлу :param data: Данные для сериализации :return: True при успехе, иначе False

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `file_path` | `str` | Input parameter |
| `data` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `return _write_temp_and_replace(file_path, data)`

---

### `load_json`
- **Signature**: `async def load_json(file_path: str, default: Any = None) -> Any`
- **Source Reference**: [utils/storage.py#L69-L77](file:///home/u/Рабочий стол/para/utils/storage.py#L69-L77)
- **Async**: `Yes`
- **Return Type**: `Any`

#### Purpose & Architectural Intent
Асинхронно считывает JSON в пуле потоков без блокировки цикла событий. :param file_path: Путь к файлу :param default: Значение по умолчанию :return: Распарсенные данные

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `file_path` | `str` | Input parameter |
| `default` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `return await asyncio.to_thread(sync_load_json, file_path, default)`

---

### `save_json`
- **Signature**: `async def save_json(file_path: str, data: Any) -> bool`
- **Source Reference**: [utils/storage.py#L80-L88](file:///home/u/Рабочий стол/para/utils/storage.py#L80-L88)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Асинхронно и атомарно сохраняет JSON в пуле потоков. :param file_path: Путь к файлу :param data: Данные для сохранения :return: True при успехе

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `file_path` | `str` | Input parameter |
| `data` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `return await asyncio.to_thread(sync_atomic_save_json, file_path, data)`

---
