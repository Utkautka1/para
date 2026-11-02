# Component Reference: `core/prompt_sanitizer.py`
> **File Path**: [`core/prompt_sanitizer.py`](../../core/prompt_sanitizer.py)
> **Subsystem**: `AI Prompt Sanitization`

## 1. Purpose
Санитайзер и валидатор входных пользовательских промптов для нейросетевых моделей.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`remove_invisible_control_chars`](#remove_invisible_control_chars) | Function | L40–L43 | `str` | Удаляет нулевые байты и невидимые управляющие символы. |
| [`escape_context_delimiters`](#escape_context_delimiters) | Function | L46–L53 | `str` | Экранирует теги XML и угловые скобки для изоляции конте... |
| [`detect_injection_indicators`](#detect_injection_indicators) | Function | L56–L62 | `list[str]` | Сканирует текст на наличие сигнатур prompt injection и ... |
| [`sanitize_prompt`](#sanitize_prompt) | Function | L65–L83 | `SanitizeResult` | Санирует пользовательский запрос перед встраиванием в ш... |

---

## 3. Comprehensive Function Specifications

## Class Model: `SanitizeResult`

Результат санитарной обработки пользовательского промпта.

### `remove_invisible_control_chars`
```python
def remove_invisible_control_chars(text: str) -> str
```

- **Source Reference**: [`core/prompt_sanitizer.py#L40-L43`](../../core/prompt_sanitizer.py#L40-L43)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Удаляет нулевые байты и невидимые управляющие символы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.prompt_sanitizer import remove_invisible_control_chars

# Execute call
result = remove_invisible_control_chars(text=...)
```

---

### `escape_context_delimiters`
```python
def escape_context_delimiters(text: str) -> str
```

- **Source Reference**: [`core/prompt_sanitizer.py#L46-L53`](../../core/prompt_sanitizer.py#L46-L53)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Экранирует теги XML и угловые скобки для изоляции контекста.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.prompt_sanitizer import escape_context_delimiters

# Execute call
result = escape_context_delimiters(text=...)
```

---

### `detect_injection_indicators`
```python
def detect_injection_indicators(text: str) -> list[str]
```

- **Source Reference**: [`core/prompt_sanitizer.py#L56-L62`](../../core/prompt_sanitizer.py#L56-L62)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[str]`

#### Overview & Architectural Purpose
Сканирует текст на наличие сигнатур prompt injection и jailbreak.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.prompt_sanitizer import detect_injection_indicators

# Execute call
result = detect_injection_indicators(text=...)
```

---

### `sanitize_prompt`
```python
def sanitize_prompt(raw_text: str | None, max_length: int = 15000) -> SanitizeResult
```

- **Source Reference**: [`core/prompt_sanitizer.py#L65-L83`](../../core/prompt_sanitizer.py#L65-L83)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `SanitizeResult`

#### Overview & Architectural Purpose
Санирует пользовательский запрос перед встраиванием в шаблон LLM.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `raw_text` | `str | None` | Yes | Parameter `raw_text` of type `str | None`. |
| `max_length` | `int` | Yes | Parameter `max_length` of type `int`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.prompt_sanitizer import sanitize_prompt

# Execute call
result = sanitize_prompt(raw_text=..., max_length=...)
```

---
