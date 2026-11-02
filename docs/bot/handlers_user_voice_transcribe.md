# Component Reference: `bot/handlers/user/voice_transcribe.py`
> **File Path**: [`bot/handlers/user/voice_transcribe.py`](../../bot/handlers/user/voice_transcribe.py)
> **Subsystem**: `Voice Transcription Handler`
> **Architecture Layer**: `Telegram User Media Ingress`
> **Concurrency Model**: `Aiogram 3 Async Inbound Event Loop + Per-User Rate Limiting`
> **Persistence Backend**: `Stateless Telegram Ingress & Memory In-Flight State`
> **Service Level Objective**: `Sub-100ms Telegram Message Ingress & Auto-Splitting`

## 1. Purpose
Хэндлер автоматической расшифровки голосовых и видеосообщений в топиках чата.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`AudioMeta.__init__`](#audiometa__init__) | Method | L51–L78 | `Any` | Инициализирует контейнер метаданных входящего голосовог... |
| [`AudioMeta.__iter__`](#audiometa__iter__) | Method | L80–L90 | `Any` | Обеспечивает распаковку основных полей: file_id, durati... |
| [`is_allowed_chat`](#is_allowed_chat) | Function | L93–L103 | `bool` | Проверяет, разрешена ли обработка голосовых сообщений в... |
| [`is_voice_request_allowed`](#is_voice_request_allowed) | Function | L106–L125 | `bool` | Проверяет, можно ли тратить GPU-очередь STT на это сооб... |
| [`extract_audio_meta`](#extract_audio_meta) | Function | L128–L154 | `AudioMeta` | Извлекает нормализованные метаданные аудио- или видеосо... |
| [`acquire_user_slot`](#acquire_user_slot) | Function | L157–L176 | `bool` | Атомарно проверяет и резервирует слот параллельной обра... |
| [`release_user_slot`](#release_user_slot) | Function | L179–L192 | `None` | Освобождает занятый слот пользователя после завершения ... |
| [`validate_audio_limits`](#validate_audio_limits) | Function | L195–L214 | `str \| None` | Проверяет длительность и размер файла на соответствие л... |
| [`log_voice_request`](#log_voice_request) | Function | L217–L232 | `None` | Логирует структурированную информацию о входящем аудиос... |
| [`_determine_audio_extension`](#_determine_audio_extension) | Function | L235–L248 | `str` | Извлекает расширение исходного медиафайла Telegram из е... |
| [`download_temp_audio`](#download_temp_audio) | Function | L251–L276 | `str` | Скачивает медиафайл из Telegram в общий с сервисом stt ... |
| [`cleanup_temp_file`](#cleanup_temp_file) | Function | L279–L293 | `None` | Удаляет временный аудиофайл с диска с безопасным подавл... |
| [`send_overflow_chunks`](#send_overflow_chunks) | Function | L296–L308 | `None` | Отправляет последующие части длинного сообщения с экран... |
| [`deliver_transcription`](#deliver_transcription) | Function | L311–L335 | `None` | Отправляет результат распознавания текста пользователю ... |
| [`_download_and_transcribe`](#_download_and_transcribe) | Function | L338–L354 | `str` | Выполняет полный цикл скачивания и распознавания речи с... |
| [`process_audio_pipeline`](#process_audio_pipeline) | Function | L357–L388 | `None` | Координирует сквозной процесс транскрибации от скачиван... |
| [`_check_and_acquire_voice`](#_check_and_acquire_voice) | Function | L391–L412 | `bool` | Проверяет лимиты аудиосообщения и резервирует слот поль... |
| [`handle_voice_or_video_note`](#handle_voice_or_video_note) | Function | L416–L437 | `None` | Точка входа для голосовых сообщений и видео-кружочков в... |

---

## 3. Comprehensive Function Specifications

## Class Model: `AudioMeta`

Контейнер нормализованных метаданных аудиосообщения Telegram.

### `AudioMeta.__init__`
```python
def __init__( self, file_id: str, duration: int, sender: str, file_size: int = 0, user_id: int = 0, username: str = "",
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L51-L78`](../../bot/handlers/user/voice_transcribe.py#L51-L78)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Инициализирует контейнер метаданных входящего голосового или видеосообщения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file_id` | `str` | Yes | Parameter `file_id` of type `str`. |
| `duration` | `int` | Yes | Audio duration in seconds. |
| `sender` | `str` | Yes | Display name of the user who sent the audio message. |
| `file_size` | `int` | Yes | Size of the audio file in bytes. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `username` | `str` | Yes | Parameter `username` of type `str`. |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `thread_id` | `int | None` | Yes | Parameter `thread_id` of type `int | None`. |
| `media_type` | `str` | Yes | Parameter `media_type` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import __init__

# Execute call
result = __init__(file_id=..., duration=..., sender=...)
```

---

### `AudioMeta.__iter__`
```python
def __iter__(self)
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L80-L90`](../../bot/handlers/user/voice_transcribe.py#L80-L90)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Обеспечивает распаковку основных полей: file_id, duration, sender.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import __iter__

# Execute call
result = __iter__()
```

---

### `is_allowed_chat`
```python
def is_allowed_chat(chat_id: int, chat_type: str) -> bool
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L93-L103`](../../bot/handlers/user/voice_transcribe.py#L93-L103)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, разрешена ли обработка голосовых сообщений в данном чате.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `chat_type` | `str` | Yes | Parameter `chat_type` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import is_allowed_chat

# Execute call
result = is_allowed_chat(chat_id=..., chat_type=...)
```

---

### `is_voice_request_allowed`
```python
async def is_voice_request_allowed(message: Message) -> bool
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L106-L125`](../../bot/handlers/user/voice_transcribe.py#L106-L125)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, можно ли тратить GPU-очередь STT на это сообщение.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import is_voice_request_allowed

# Execute call
result = await is_voice_request_allowed(message=...)
```

---

### `extract_audio_meta`
```python
def extract_audio_meta(message: Message) -> AudioMeta
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L128-L154`](../../bot/handlers/user/voice_transcribe.py#L128-L154)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `AudioMeta`

#### Overview & Architectural Purpose
Извлекает нормализованные метаданные аудио- или видеосообщения Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import extract_audio_meta

# Execute call
result = extract_audio_meta(message=...)
```

---

### `acquire_user_slot`
```python
def acquire_user_slot(user_id: int) -> bool
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L157-L176`](../../bot/handlers/user/voice_transcribe.py#L157-L176)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Атомарно проверяет и резервирует слот параллельной обработки для пользователя.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import acquire_user_slot

# Execute call
result = acquire_user_slot(user_id=...)
```

---

### `release_user_slot`
```python
def release_user_slot(user_id: int) -> None
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L179-L192`](../../bot/handlers/user/voice_transcribe.py#L179-L192)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Освобождает занятый слот пользователя после завершения транскрибации.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import release_user_slot

# Execute call
result = release_user_slot(user_id=...)
```

---

### `validate_audio_limits`
```python
def validate_audio_limits(duration: int, file_size: int, sender: str) -> str | None
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L195-L214`](../../bot/handlers/user/voice_transcribe.py#L195-L214)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Проверяет длительность и размер файла на соответствие лимитам Telegram и модели.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `duration` | `int` | Yes | Audio duration in seconds. |
| `file_size` | `int` | Yes | Size of the audio file in bytes. |
| `sender` | `str` | Yes | Display name of the user who sent the audio message. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import validate_audio_limits

# Execute call
result = validate_audio_limits(duration=..., file_size=..., sender=...)
```

---

### `log_voice_request`
```python
def log_voice_request(meta: AudioMeta) -> None
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L217-L232`](../../bot/handlers/user/voice_transcribe.py#L217-L232)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Логирует структурированную информацию о входящем аудиосообщении.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `meta` | `AudioMeta` | Yes | Parameter `meta` of type `AudioMeta`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import log_voice_request

# Execute call
result = log_voice_request(meta=...)
```

---

### `_determine_audio_extension`
```python
def _determine_audio_extension(file_path: str | None) -> str
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L235-L248`](../../bot/handlers/user/voice_transcribe.py#L235-L248)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Извлекает расширение исходного медиафайла Telegram из его пути.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file_path` | `str | None` | Yes | Parameter `file_path` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import _determine_audio_extension

# Execute call
result = _determine_audio_extension(file_path=...)
```

---

### `download_temp_audio`
```python
async def download_temp_audio(file_id: str) -> str
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L251-L276`](../../bot/handlers/user/voice_transcribe.py#L251-L276)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Скачивает медиафайл из Telegram в общий с сервисом stt tmpfs-том.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file_id` | `str` | Yes | Parameter `file_id` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import download_temp_audio

# Execute call
result = await download_temp_audio(file_id=...)
```

---

### `cleanup_temp_file`
```python
def cleanup_temp_file(path: str) -> None
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L279-L293`](../../bot/handlers/user/voice_transcribe.py#L279-L293)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет временный аудиофайл с диска с безопасным подавлением ошибок.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `path` | `str` | Yes | Parameter `path` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import cleanup_temp_file

# Execute call
result = cleanup_temp_file(path=...)
```

---

### `send_overflow_chunks`
```python
async def send_overflow_chunks(message: Message, chunks: list[str]) -> None
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L296-L308`](../../bot/handlers/user/voice_transcribe.py#L296-L308)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет последующие части длинного сообщения с экранированием HTML.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `chunks` | `list[str]` | Yes | Parameter `chunks` of type `list[str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import send_overflow_chunks

# Execute call
result = await send_overflow_chunks(message=..., chunks=...)
```

---

### `deliver_transcription`
```python
async def deliver_transcription( message: Message, status_msg: Message, sender_name: str, duration: int, text: str, ) -> None
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L311-L335`](../../bot/handlers/user/voice_transcribe.py#L311-L335)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет результат распознавания текста пользователю или в топик.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `status_msg` | `Message` | Yes | Aiogram Message instance displaying transient progress status. |
| `sender_name` | `str` | Yes | Display name of the sender for message formatting. |
| `duration` | `int` | Yes | Audio duration in seconds. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import deliver_transcription

# Execute call
result = await deliver_transcription(message=..., status_msg=..., sender_name=...)
```

---

### `_download_and_transcribe`
```python
async def _download_and_transcribe(file_id: str) -> str
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L338-L354`](../../bot/handlers/user/voice_transcribe.py#L338-L354)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Выполняет полный цикл скачивания и распознавания речи с контролем таймаута.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file_id` | `str` | Yes | Parameter `file_id` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import _download_and_transcribe

# Execute call
result = await _download_and_transcribe(file_id=...)
```

---

### `process_audio_pipeline`
```python
async def process_audio_pipeline( file_id: str, sender: str, duration: int, message: Message, status_msg: Message, user_id: int = 0, ) -> None
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L357-L388`](../../bot/handlers/user/voice_transcribe.py#L357-L388)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Координирует сквозной процесс транскрибации от скачивания до отправки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file_id` | `str` | Yes | Parameter `file_id` of type `str`. |
| `sender` | `str` | Yes | Display name of the user who sent the audio message. |
| `duration` | `int` | Yes | Audio duration in seconds. |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `status_msg` | `Message` | Yes | Aiogram Message instance displaying transient progress status. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import process_audio_pipeline

# Execute call
result = await process_audio_pipeline(file_id=..., sender=..., duration=...)
```

---

### `_check_and_acquire_voice`
```python
async def _check_and_acquire_voice(message: Message, meta: AudioMeta) -> bool
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L391-L412`](../../bot/handlers/user/voice_transcribe.py#L391-L412)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет лимиты аудиосообщения и резервирует слот пользователя.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `meta` | `AudioMeta` | Yes | Parameter `meta` of type `AudioMeta`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import _check_and_acquire_voice

# Execute call
result = await _check_and_acquire_voice(message=..., meta=...)
```

---

### `handle_voice_or_video_note`
```python
async def handle_voice_or_video_note(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/voice_transcribe.py#L416-L437`](../../bot/handlers/user/voice_transcribe.py#L416-L437)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Точка входа для голосовых сообщений и видео-кружочков во всех топиках.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.voice_transcribe import handle_voice_or_video_note

# Execute call
result = await handle_voice_or_video_note(message=...)
```

---
