# Component Reference: `bot/handlers/admin/ping_all.py`
> **File Path**: [`bot/handlers/admin/ping_all.py`](../../bot/handlers/admin/ping_all.py)
> **Subsystem**: `Supergroup Alert Dispatch`

## 1. Purpose
Модуль хэндлера общего пинга одногруппников (/all).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`load_classmates_list`](#load_classmates_list) | Function | L42–L51 | `list[dict[str, Any]]` | Загружает актуальный список одногруппников из файла bir... |
| [`resolve_person_tg_id`](#resolve_person_tg_id) | Function | L54–L67 | `int \| None` | Извлекает Telegram ID из записи студента либо из кэша ю... |
| [`format_mention_tag`](#format_mention_tag) | Function | L70–L88 | `str \| None` | Формирует видимый кликабельный тег студента для push-ув... |
| [`is_sender`](#is_sender) | Function | L91–L103 | `bool` | Проверяет, является ли запись студента автором вызванно... |
| [`filter_classmates_to_ping`](#filter_classmates_to_ping) | Function | L106–L116 | `list[dict[str, Any]]` | Отбирает одногруппников для пинга, исключая автора кома... |
| [`chunk_classmates`](#chunk_classmates) | Function | L119–L133 | `list[list[dict[str, Any]]]` | Разбивает список студентов на пачки фиксированного разм... |
| [`format_chunk_message`](#format_chunk_message) | Function | L136–L146 | `str` | Форматирует одну пачку упоминаний в строку сервисного о... |
| [`extract_broadcast_text`](#extract_broadcast_text) | Function | L149–L164 | `str` | Извлекает пользовательский текст сообщения после команд... |
| [`build_broadcast_message`](#build_broadcast_message) | Function | L167–L182 | `str` | Компонует основной чистый текст поста без единого никне... |
| [`safe_delete_command_message`](#safe_delete_command_message) | Function | L185–L202 | `None` | Безопасно удаляет исходное командное сообщение админист... |
| [`send_broadcast_payload`](#send_broadcast_payload) | Function | L205–L223 | `Message` | Отправляет пост от лица бота в целевой топик чата с сох... |
| [`send_mention_batch`](#send_mention_batch) | Function | L226–L249 | `None` | Отправляет одну пачку упоминаний как реплай на основной... |
| [`dispatch_mention_batches`](#dispatch_mention_batches) | Function | L252–L272 | `None` | Последовательно отправляет пачки упоминаний с микропауз... |
| [`validate_group_chat`](#validate_group_chat) | Function | L275–L288 | `bool` | Проверяет, что команда /all вызвана в группе или суперг... |
| [`compose_broadcast_content`](#compose_broadcast_content) | Function | L291–L304 | `tuple[str, int \| None]` | Формирует чистый текст поста и извлекает ID сообщения д... |
| [`run_broadcast_pipeline`](#run_broadcast_pipeline) | Function | L307–L320 | `None` | Выполняет отправку главного поста и пакетов упоминаний. |
| [`dispatch_broadcast`](#dispatch_broadcast) | Function | L323–L334 | `None` | Запускает рассылку с перехватом ошибок и уведомлением а... |
| [`cmd_ping_all`](#cmd_ping_all) | Function | L338–L352 | `None` | Оркестрирует полный сценарий общего пинга группы 1-КПД-... |

---

## 3. Comprehensive Function Specifications

### `load_classmates_list`
```python
async def load_classmates_list() -> list[dict[str, Any]]
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L42-L51`](../../bot/handlers/admin/ping_all.py#L42-L51)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `list[dict[str, Any]]`

#### Overview & Architectural Purpose
Загружает актуальный список одногруппников из файла birthdays.json.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import load_classmates_list

# Execute call
result = await load_classmates_list()
```

---

### `resolve_person_tg_id`
```python
def resolve_person_tg_id(person: dict[str, Any]) -> int | None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L54-L67`](../../bot/handlers/admin/ping_all.py#L54-L67)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `int | None`

#### Overview & Architectural Purpose
Извлекает Telegram ID из записи студента либо из кэша юзернеймов Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `person` | `dict[str, Any]` | Yes | Parameter `person` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import resolve_person_tg_id

# Execute call
result = resolve_person_tg_id(person=...)
```

---

### `format_mention_tag`
```python
def format_mention_tag(person: dict[str, Any]) -> str | None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L70-L88`](../../bot/handlers/admin/ping_all.py#L70-L88)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Формирует видимый кликабельный тег студента для push-уведомления.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `person` | `dict[str, Any]` | Yes | Parameter `person` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import format_mention_tag

# Execute call
result = format_mention_tag(person=...)
```

---

### `is_sender`
```python
def is_sender(person: dict[str, Any], sender_id: int | None, sender_username: str | None) -> bool
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L91-L103`](../../bot/handlers/admin/ping_all.py#L91-L103)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, является ли запись студента автором вызванной команды.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `person` | `dict[str, Any]` | Yes | Parameter `person` of type `dict[str, Any]`. |
| `sender_id` | `int | None` | Yes | Parameter `sender_id` of type `int | None`. |
| `sender_username` | `str | None` | Yes | Parameter `sender_username` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import is_sender

# Execute call
result = is_sender(person=..., sender_id=..., sender_username=...)
```

---

### `filter_classmates_to_ping`
```python
def filter_classmates_to_ping(classmates: list[dict[str, Any]], sender: User | None) -> list[dict[str, Any]]
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L106-L116`](../../bot/handlers/admin/ping_all.py#L106-L116)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[dict[str, Any]]`

#### Overview & Architectural Purpose
Отбирает одногруппников для пинга, исключая автора команды.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `classmates` | `list[dict[str, Any]]` | Yes | Parameter `classmates` of type `list[dict[str, Any]]`. |
| `sender` | `User | None` | Yes | Display name of the user who sent the audio message. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import filter_classmates_to_ping

# Execute call
result = filter_classmates_to_ping(classmates=..., sender=...)
```

---

### `chunk_classmates`
```python
def chunk_classmates( classmates: list[dict[str, Any]], chunk_size: int = PING_ALL_CHUNK_SIZE, ) -> list[list[dict[str, Any]]]
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L119-L133`](../../bot/handlers/admin/ping_all.py#L119-L133)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[list[dict[str, Any]]]`

#### Overview & Architectural Purpose
Разбивает список студентов на пачки фиксированного размера.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `classmates` | `list[dict[str, Any]]` | Yes | Parameter `classmates` of type `list[dict[str, Any]]`. |
| `chunk_size` | `int` | Yes | Parameter `chunk_size` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import chunk_classmates

# Execute call
result = chunk_classmates(classmates=..., chunk_size=...)
```

---

### `format_chunk_message`
```python
def format_chunk_message(chunk: list[dict[str, Any]]) -> str
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L136-L146`](../../bot/handlers/admin/ping_all.py#L136-L146)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Форматирует одну пачку упоминаний в строку сервисного ответа.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `chunk` | `list[dict[str, Any]]` | Yes | Parameter `chunk` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import format_chunk_message

# Execute call
result = format_chunk_message(chunk=...)
```

---

### `extract_broadcast_text`
```python
def extract_broadcast_text(html_text: str) -> str
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L149-L164`](../../bot/handlers/admin/ping_all.py#L149-L164)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Извлекает пользовательский текст сообщения после команды /all или .all.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `html_text` | `str` | Yes | Parameter `html_text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import extract_broadcast_text

# Execute call
result = extract_broadcast_text(html_text=...)
```

---

### `build_broadcast_message`
```python
def build_broadcast_message(user_html: str, has_reply: bool = False) -> str
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L167-L182`](../../bot/handlers/admin/ping_all.py#L167-L182)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Компонует основной чистый текст поста без единого никнейма.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_html` | `str` | Yes | Parameter `user_html` of type `str`. |
| `has_reply` | `bool` | Yes | Parameter `has_reply` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import build_broadcast_message

# Execute call
result = build_broadcast_message(user_html=..., has_reply=...)
```

---

### `safe_delete_command_message`
```python
async def safe_delete_command_message(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L185-L202`](../../bot/handlers/admin/ping_all.py#L185-L202)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Безопасно удаляет исходное командное сообщение администратора.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import safe_delete_command_message

# Execute call
result = await safe_delete_command_message(message=...)
```

---

### `send_broadcast_payload`
```python
async def send_broadcast_payload(message: Message, final_html: str, reply_to_id: int | None) -> Message
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L205-L223`](../../bot/handlers/admin/ping_all.py#L205-L223)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Message`

#### Overview & Architectural Purpose
Отправляет пост от лица бота в целевой топик чата с сохранением вложений.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `final_html` | `str` | Yes | Parameter `final_html` of type `str`. |
| `reply_to_id` | `int | None` | Yes | Parameter `reply_to_id` of type `int | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import send_broadcast_payload

# Execute call
result = await send_broadcast_payload(message=..., final_html=..., reply_to_id=...)
```

---

### `send_mention_batch`
```python
async def send_mention_batch( message: Message, chat_id: int, thread_id: int | None, reply_to_id: int, batch_text: str, ) -> None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L226-L249`](../../bot/handlers/admin/ping_all.py#L226-L249)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет одну пачку упоминаний как реплай на основной пост.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `thread_id` | `int | None` | Yes | Parameter `thread_id` of type `int | None`. |
| `reply_to_id` | `int` | Yes | Parameter `reply_to_id` of type `int`. |
| `batch_text` | `str` | Yes | Parameter `batch_text` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import send_mention_batch

# Execute call
result = await send_mention_batch(message=..., chat_id=..., thread_id=...)
```

---

### `dispatch_mention_batches`
```python
async def dispatch_mention_batches( message: Message, main_msg_id: int, chunks: list[list[dict[str, Any]]], ) -> None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L252-L272`](../../bot/handlers/admin/ping_all.py#L252-L272)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Последовательно отправляет пачки упоминаний с микропаузой.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `main_msg_id` | `int` | Yes | Parameter `main_msg_id` of type `int`. |
| `chunks` | `list[list[dict[str, Any]]]` | Yes | Parameter `chunks` of type `list[list[dict[str, Any]]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import dispatch_mention_batches

# Execute call
result = await dispatch_mention_batches(message=..., main_msg_id=..., chunks=...)
```

---

### `validate_group_chat`
```python
async def validate_group_chat(message: Message) -> bool
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L275-L288`](../../bot/handlers/admin/ping_all.py#L275-L288)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, что команда /all вызвана в группе или супергруппе колледжа.

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
from bot.handlers.admin.ping_all import validate_group_chat

# Execute call
result = await validate_group_chat(message=...)
```

---

### `compose_broadcast_content`
```python
def compose_broadcast_content(message: Message) -> tuple[str, int | None]
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L291-L304`](../../bot/handlers/admin/ping_all.py#L291-L304)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, int | None]`

#### Overview & Architectural Purpose
Формирует чистый текст поста и извлекает ID сообщения для реплая.

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
from bot.handlers.admin.ping_all import compose_broadcast_content

# Execute call
result = compose_broadcast_content(message=...)
```

---

### `run_broadcast_pipeline`
```python
async def run_broadcast_pipeline( message: Message, final_text: str, reply_id: int | None, classmates: list[dict[str, Any]], ) -> None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L307-L320`](../../bot/handlers/admin/ping_all.py#L307-L320)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Выполняет отправку главного поста и пакетов упоминаний.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `final_text` | `str` | Yes | Parameter `final_text` of type `str`. |
| `reply_id` | `int | None` | Yes | Parameter `reply_id` of type `int | None`. |
| `classmates` | `list[dict[str, Any]]` | Yes | Parameter `classmates` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import run_broadcast_pipeline

# Execute call
result = await run_broadcast_pipeline(message=..., final_text=..., reply_id=...)
```

---

### `dispatch_broadcast`
```python
async def dispatch_broadcast( message: Message, final_text: str, reply_id: int | None, classmates: list[dict[str, Any]], ) -> None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L323-L334`](../../bot/handlers/admin/ping_all.py#L323-L334)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Запускает рассылку с перехватом ошибок и уведомлением администратора.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `final_text` | `str` | Yes | Parameter `final_text` of type `str`. |
| `reply_id` | `int | None` | Yes | Parameter `reply_id` of type `int | None`. |
| `classmates` | `list[dict[str, Any]]` | Yes | Parameter `classmates` of type `list[dict[str, Any]]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import dispatch_broadcast

# Execute call
result = await dispatch_broadcast(message=..., final_text=..., reply_id=...)
```

---

### `cmd_ping_all`
```python
async def cmd_ping_all(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L338-L352`](../../bot/handlers/admin/ping_all.py#L338-L352)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Оркестрирует полный сценарий общего пинга группы 1-КПД-3 по команде /all.

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
from bot.handlers.admin.ping_all import cmd_ping_all

# Execute call
result = await cmd_ping_all(message=...)
```

---
