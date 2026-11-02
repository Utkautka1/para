# Component Reference: `bot/templates/user/voice.py`
> **File Path**: [`bot/templates/user/voice.py`](../../bot/templates/user/voice.py)
> **Subsystem**: `Voice Message Templates`
> **Architecture Layer**: `Presentation Markup & Sanitization`
> **Concurrency Model**: `Synchronous Pure Function Rendering`
> **Persistence Backend**: `Stateless HTML Escape & Telegram Formatter`
> **Service Level Objective**: `Sub-1µs Render Latency`

## 1. Purpose
Шаблоны сообщений для расшифровки голосовых и видеосообщений в Telegram.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`format_transcription_status`](#format_transcription_status) | Function | L12–L22 | `str` | Возвращает текст временного статуса начала распознавани... |
| [`format_duration_str`](#format_duration_str) | Function | L25–L41 | `str` | Форматирует хронометраж аудиосообщения в формат (минуты... |
| [`format_transcription_result`](#format_transcription_result) | Function | L44–L58 | `str` | Формирует красивое итоговое сообщение с расшифрованным ... |
| [`format_transcription_empty`](#format_transcription_empty) | Function | L61–L74 | `str` | Формирует уведомление о неразборчивой или тихой аудиоза... |
| [`format_transcription_error`](#format_transcription_error) | Function | L77–L87 | `str` | Возвращает сообщение о техническом сбое при обработке а... |
| [`format_too_long_error`](#format_too_long_error) | Function | L90–L102 | `str` | Возвращает предупреждение о превышении допустимого хрон... |
| [`format_too_big_error`](#format_too_big_error) | Function | L105–L115 | `str` | Возвращает предупреждение о превышении максимального ра... |
| [`format_rate_limit_error`](#format_rate_limit_error) | Function | L118–L128 | `str` | Возвращает сообщение о троттлинге параллельных запросов... |
| [`format_queue_status`](#format_queue_status) | Function | L131–L141 | `str` | Возвращает текст статуса нахождения аудиосообщения в оч... |

---

## 3. Comprehensive Function Specifications

### `format_transcription_status`
```python
def format_transcription_status() -> str
```

- **Source Reference**: [`bot/templates/user/voice.py#L12-L22`](../../bot/templates/user/voice.py#L12-L22)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает текст временного статуса начала распознавания аудиосообщения.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.voice import format_transcription_status

# Execute call
result = format_transcription_status()
```

---

### `format_duration_str`
```python
def format_duration_str(duration_seconds: int) -> str
```

- **Source Reference**: [`bot/templates/user/voice.py#L25-L41`](../../bot/templates/user/voice.py#L25-L41)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Форматирует хронометраж аудиосообщения в формат (минуты:секунды).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `duration_seconds` | `int` | Yes | Parameter `duration_seconds` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.voice import format_duration_str

# Execute call
result = format_duration_str(duration_seconds=...)
```

---

### `format_transcription_result`
```python
def format_transcription_result(sender_name: str, duration_sec: int, transcription_text: str) -> str
```

- **Source Reference**: [`bot/templates/user/voice.py#L44-L58`](../../bot/templates/user/voice.py#L44-L58)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует красивое итоговое сообщение с расшифрованным текстом речи.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sender_name` | `str` | Yes | Display name of the sender for message formatting. |
| `duration_sec` | `int` | Yes | Audio duration in seconds for message formatting. |
| `transcription_text` | `str` | Yes | Transcribed raw text recognized by Whisper engine. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.voice import format_transcription_result

# Execute call
result = format_transcription_result(sender_name=..., duration_sec=..., transcription_text=...)
```

---

### `format_transcription_empty`
```python
def format_transcription_empty(sender_name: str, duration_sec: int) -> str
```

- **Source Reference**: [`bot/templates/user/voice.py#L61-L74`](../../bot/templates/user/voice.py#L61-L74)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует уведомление о неразборчивой или тихой аудиозаписи.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sender_name` | `str` | Yes | Display name of the sender for message formatting. |
| `duration_sec` | `int` | Yes | Audio duration in seconds for message formatting. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.voice import format_transcription_empty

# Execute call
result = format_transcription_empty(sender_name=..., duration_sec=...)
```

---

### `format_transcription_error`
```python
def format_transcription_error() -> str
```

- **Source Reference**: [`bot/templates/user/voice.py#L77-L87`](../../bot/templates/user/voice.py#L77-L87)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает сообщение о техническом сбое при обработке аудиофайла.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.voice import format_transcription_error

# Execute call
result = format_transcription_error()
```

---

### `format_too_long_error`
```python
def format_too_long_error(max_seconds: int = 300) -> str
```

- **Source Reference**: [`bot/templates/user/voice.py#L90-L102`](../../bot/templates/user/voice.py#L90-L102)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает предупреждение о превышении допустимого хронометража аудио.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `max_seconds` | `int` | Yes | Maximum allowed audio duration limit in seconds. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.voice import format_too_long_error

# Execute call
result = format_too_long_error(max_seconds=...)
```

---

### `format_too_big_error`
```python
def format_too_big_error(max_mb: int = 20) -> str
```

- **Source Reference**: [`bot/templates/user/voice.py#L105-L115`](../../bot/templates/user/voice.py#L105-L115)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает предупреждение о превышении максимального размера файла.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `max_mb` | `int` | Yes | Maximum allowed audio file size limit in megabytes. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.voice import format_too_big_error

# Execute call
result = format_too_big_error(max_mb=...)
```

---

### `format_rate_limit_error`
```python
def format_rate_limit_error() -> str
```

- **Source Reference**: [`bot/templates/user/voice.py#L118-L128`](../../bot/templates/user/voice.py#L118-L128)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает сообщение о троттлинге параллельных запросов одного пользователя.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.voice import format_rate_limit_error

# Execute call
result = format_rate_limit_error()
```

---

### `format_queue_status`
```python
def format_queue_status(queue_pos: int) -> str
```

- **Source Reference**: [`bot/templates/user/voice.py#L131-L141`](../../bot/templates/user/voice.py#L131-L141)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает текст статуса нахождения аудиосообщения в очереди на GPU.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `queue_pos` | `int` | Yes | 1-based queue index indicating position waiting for GPU semaphore. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.user.voice import format_queue_status

# Execute call
result = format_queue_status(queue_pos=...)
```

---
