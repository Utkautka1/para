# Module Specification: `utils/mute_parser.py`
> **Path**: [`utils/mute_parser.py`](file:///home/u/Рабочий стол/para/utils/mute_parser.py)  
> **Subsystem**: `Ban Duration Parser`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Утилита парсинга строк времени мута в секунды. Преобразует выражения типа '5с', '10м', '2ч', '1д' в секунды для передачи в Bot.restrict_chat_member.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`parse_duration_to_seconds`](#parse_duration_to_seconds) | Function | L11–L29 | `int | None` | Парсит строку формата '5с', '10м', '2ч', '1д' в интервал в с |

---

## 3. Exhaustive Function Specifications

### `parse_duration_to_seconds`
- **Signature**: `def parse_duration_to_seconds(time_str: str) -> int | None`
- **Source Reference**: [utils/mute_parser.py#L11-L29](file:///home/u/Рабочий стол/para/utils/mute_parser.py#L11-L29)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Парсит строку формата '5с', '10м', '2ч', '1д' в интервал в секундах. :param time_str: Строка с периодом :return: Секунды или None при неверном формате

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `time_str` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `match = re.match(r"^(\d+)\s*([сsмmчhдd])?$", time_str.strip().lower())`
2. `if not match:`
3. `amount = int(match.group(1))`
4. `unit = match.group(2) or "м"`
5. `multipliers = {`
6. `return amount * multipliers.get(unit, 60)`

---
