# Component Reference: `integrations/deepseek.py`
> **File Path**: [`integrations/deepseek.py`](../../integrations/deepseek.py)
> **Subsystem**: `DeepSeek LLM Integration`

## 1. Purpose
Интеграция с нейросетевым API DeepSeek (модели Vision/Flash).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_deepseek_client`](#get_deepseek_client) | Function | L27–L35 | `AsyncOpenAI` | Предоставляет синглтон асинхронного клиента для взаимод... |
| [`close_deepseek_client`](#close_deepseek_client) | Function | L38–L43 | `None` | Корректно закрывает сетевую сессию и пул соединений кли... |
| [`encode_image_bytes`](#encode_image_bytes) | Function | L46–L48 | `str` | Кодирует сырые байты изображения задания в строку форма... |
| [`build_deepseek_messages`](#build_deepseek_messages) | Function | L51–L75 | `list[dict[str, Any]]` | Формирует изолированный массив контекстных сообщений с ... |
| [`_call_deepseek_api`](#_call_deepseek_api) | Function | L78–L89 | `str` | Выполняет единичный асинхронный вызов OpenAI SDK для по... |
| [`solve_homework`](#solve_homework) | Function | L92–L110 | `str` | Отправляет мультимодальный запрос в DeepSeek с защитой ... |

---

## 3. Comprehensive Function Specifications

### `get_deepseek_client`
```python
def get_deepseek_client() -> AsyncOpenAI
```

- **Source Reference**: [`integrations/deepseek.py#L27-L35`](../../integrations/deepseek.py#L27-L35)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `AsyncOpenAI`

#### Overview & Architectural Purpose
Предоставляет синглтон асинхронного клиента для взаимодействия с API DeepSeek.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.deepseek import get_deepseek_client

# Execute call
result = get_deepseek_client()
```

---

### `close_deepseek_client`
```python
async def close_deepseek_client() -> None
```

- **Source Reference**: [`integrations/deepseek.py#L38-L43`](../../integrations/deepseek.py#L38-L43)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Корректно закрывает сетевую сессию и пул соединений клиента DeepSeek.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.deepseek import close_deepseek_client

# Execute call
result = await close_deepseek_client()
```

---

### `encode_image_bytes`
```python
def encode_image_bytes(image_bytes: bytes) -> str
```

- **Source Reference**: [`integrations/deepseek.py#L46-L48`](../../integrations/deepseek.py#L46-L48)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Кодирует сырые байты изображения задания в строку формата Base64.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `image_bytes` | `bytes` | Yes | Parameter `image_bytes` of type `bytes`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.deepseek import encode_image_bytes

# Execute call
result = encode_image_bytes(image_bytes=...)
```

---

### `build_deepseek_messages`
```python
def build_deepseek_messages( image_bytes: bytes | None, text_prompt: str | None, ) -> list[dict[str, Any]]
```

- **Source Reference**: [`integrations/deepseek.py#L51-L75`](../../integrations/deepseek.py#L51-L75)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[dict[str, Any]]`

#### Overview & Architectural Purpose
Формирует изолированный массив контекстных сообщений с санитарной очисткой.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `image_bytes` | `bytes | None` | Yes | Parameter `image_bytes` of type `bytes | None`. |
| `text_prompt` | `str | None` | Yes | Parameter `text_prompt` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.deepseek import build_deepseek_messages

# Execute call
result = build_deepseek_messages(image_bytes=..., text_prompt=...)
```

---

### `_call_deepseek_api`
```python
async def _call_deepseek_api(messages: list[dict[str, Any]]) -> str
```

- **Source Reference**: [`integrations/deepseek.py#L78-L89`](../../integrations/deepseek.py#L78-L89)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Выполняет единичный асинхронный вызов OpenAI SDK для получения ответа DeepSeek.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `messages` | `list[dict[str, Any]]` | Yes | Parameter `messages` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from integrations.deepseek import _call_deepseek_api

# Execute call
result = await _call_deepseek_api(messages=...)
```

---

### `solve_homework`
```python
async def solve_homework( image_bytes: bytes | None = None, text_prompt: str | None = None, ) -> str
```

- **Source Reference**: [`integrations/deepseek.py#L92-L110`](../../integrations/deepseek.py#L92-L110)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Отправляет мультимодальный запрос в DeepSeek с защитой Circuit Breaker и retry backoff.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `image_bytes` | `bytes | None` | Yes | Parameter `image_bytes` of type `bytes | None`. |
| `text_prompt` | `str | None` | Yes | Parameter `text_prompt` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from integrations.deepseek import solve_homework

# Execute call
result = await solve_homework(image_bytes=..., text_prompt=...)
```

---
