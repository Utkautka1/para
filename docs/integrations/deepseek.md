# Module Specification: `integrations/deepseek.py`
> **Path**: [`integrations/deepseek.py`](file:///home/u/Рабочий стол/para/integrations/deepseek.py)  
> **Subsystem**: `DeepSeek LLM Integration`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Executes internal domain logic according to service invariants.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_deepseek_client`](#get_deepseek_client) | Function | L24–L32 | `AsyncOpenAI` | Возвращает или инициализирует синглтон-клиент DeepSeek API. |
| [`close_deepseek_client`](#close_deepseek_client) | Function | L35–L40 | `None` | Корректно закрывает HTTP сессию клиента DeepSeek. |
| [`encode_image_bytes`](#encode_image_bytes) | Function | L43–L45 | `str` | Кодирует байты изображения в Base64. |
| [`build_deepseek_messages`](#build_deepseek_messages) | Function | L48–L67 | `list[dict]` | Формирует изолированный список сообщений для отправки в Deep |
| [`solve_homework`](#solve_homework) | Function | L70–L88 | `str` | Отправляет запрос в DeepSeek API и возвращает текст решения. |

---

## 3. Exhaustive Function Specifications

### `get_deepseek_client`
- **Signature**: `def get_deepseek_client() -> AsyncOpenAI`
- **Source Reference**: [integrations/deepseek.py#L24-L32](file:///home/u/Рабочий стол/para/integrations/deepseek.py#L24-L32)
- **Async**: `No`
- **Return Type**: `AsyncOpenAI`

#### Purpose & Architectural Intent
Возвращает или инициализирует синглтон-клиент DeepSeek API.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _deepseek_client`
2. `if _deepseek_client is None:`
3. `return _deepseek_client`

---

### `close_deepseek_client`
- **Signature**: `async def close_deepseek_client() -> None`
- **Source Reference**: [integrations/deepseek.py#L35-L40](file:///home/u/Рабочий стол/para/integrations/deepseek.py#L35-L40)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Корректно закрывает HTTP сессию клиента DeepSeek.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _deepseek_client`
2. `if _deepseek_client is not None:`

---

### `encode_image_bytes`
- **Signature**: `def encode_image_bytes(image_bytes: bytes) -> str`
- **Source Reference**: [integrations/deepseek.py#L43-L45](file:///home/u/Рабочий стол/para/integrations/deepseek.py#L43-L45)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Кодирует байты изображения в Base64.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `image_bytes` | `bytes` | Input parameter |

#### Step-by-Step Logic Execution
1. `return base64.b64encode(image_bytes).decode("utf-8")`

---

### `build_deepseek_messages`
- **Signature**: `def build_deepseek_messages( image_bytes: bytes | None, text_prompt: str | None ) -> list[dict]`
- **Source Reference**: [integrations/deepseek.py#L48-L67](file:///home/u/Рабочий стол/para/integrations/deepseek.py#L48-L67)
- **Async**: `No`
- **Return Type**: `list[dict]`

#### Purpose & Architectural Intent
Формирует изолированный список сообщений для отправки в DeepSeek API.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `image_bytes` | `bytes | None` | Input parameter |
| `text_prompt` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `prompt_val = text_prompt or "Реши все задания с листа."`
2. `content: list[dict] = [{`
3. `if image_bytes:`
4. `return [`

---

### `solve_homework`
- **Signature**: `async def solve_homework( image_bytes: bytes | None = None, text_prompt: str | None = None ) -> str`
- **Source Reference**: [integrations/deepseek.py#L70-L88](file:///home/u/Рабочий стол/para/integrations/deepseek.py#L70-L88)
- **Async**: `Yes`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Отправляет запрос в DeepSeek API и возвращает текст решения.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `image_bytes` | `bytes | None` | Input parameter |
| `text_prompt` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `messages = build_deepseek_messages(image_bytes, text_prompt)`
2. `try:`

---
