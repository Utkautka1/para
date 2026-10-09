# Module Specification: `config.py`
> **Path**: [`config.py`](file:///home/u/Рабочий стол/para/config.py)  
> **Subsystem**: `System Configuration`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль конфигурации бота расписания КТМУ. Считывает все параметры исключительно из файла .env без хардкод-значений. При отсутствии любой из обязательных переменных выбрасывает исключение ValueError.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_required_env`](#get_required_env) | Function | L17–L27 | `str` | Извлекает обязательную переменную из .env или вызывает Value |

---

## 3. Exhaustive Function Specifications

### `get_required_env`
- **Signature**: `def get_required_env(key: str) -> str`
- **Source Reference**: [config.py#L17-L27](file:///home/u/Рабочий стол/para/config.py#L17-L27)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Извлекает обязательную переменную из .env или вызывает ValueError. :param key: Название ключа переменной :return: Значение переменной из окружения

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `key` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `val = os.getenv(key)`
2. `if not val:`
3. `return val`

---
