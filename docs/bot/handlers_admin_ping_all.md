# Component Reference: `bot/handlers/admin/ping_all.py`
> **File Path**: [`bot/handlers/admin/ping_all.py`](../../bot/handlers/admin/ping_all.py)
> **Subsystem**: `Supergroup Alert Dispatch`

## 1. Purpose
Модуль хэндлера общего пинга одногруппников (/all).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`load_classmates_list`](#load_classmates_list) | Function | L40–L50 | `list[dict[str, Any]]` | Загружает актуальный список одногруппников из файла bir... |
| [`resolve_person_tg_id`](#resolve_person_tg_id) | Function | L53–L68 | `int \| None` | Извлекает Telegram ID из записи студента либо из кэша ю... |
| [`format_mention_tag`](#format_mention_tag) | Function | L71–L92 | `str \| None` | Формирует активный HTML-тег кликабельного упоминания ст... |
| [`is_sender`](#is_sender) | Function | L95–L108 | `bool` | Проверяет, является ли запись студента автором вызванно... |
| [`build_mentions_block`](#build_mentions_block) | Function | L111–L126 | `str` | Формирует единую строку кликабельных упоминаний одногру... |
| [`extract_broadcast_text`](#extract_broadcast_text) | Function | L129–L145 | `str` | Извлекает пользовательский текст сообщения после команд... |
| [`build_broadcast_message`](#build_broadcast_message) | Function | L148–L164 | `str` | Компонует итоговый HTML-текст поста с текстом автора и ... |
| [`safe_delete_command_message`](#safe_delete_command_message) | Function | L167–L185 | `None` | Безопасно удаляет исходное командное сообщение админист... |
| [`send_broadcast_payload`](#send_broadcast_payload) | Function | L188–L214 | `Message` | Отправляет пост от лица бота в целевой топик чата с сох... |
| [`validate_group_chat`](#validate_group_chat) | Function | L217–L231 | `bool` | Проверяет, что команда /all вызвана в группе или суперг... |
| [`compose_broadcast_content`](#compose_broadcast_content) | Function | L234–L249 | `tuple[str, int \| None]` | Формирует итоговый HTML-текст рассылки и извлекает ID с... |
| [`dispatch_broadcast`](#dispatch_broadcast) | Function | L252–L270 | `None` | Отправляет широковещательный пост в чат и удаляет тригг... |
| [`cmd_ping_all`](#cmd_ping_all) | Function | L274–L289 | `None` | Оркестрирует полный сценарий общего пинга группы 1-КПД-... |

---

## 3. Comprehensive Function Specifications

### `load_classmates_list`
```python
async def load_classmates_list() -> list[dict[str, Any]]
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L40-L50`](../../bot/handlers/admin/ping_all.py#L40-L50)
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

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L53-L68`](../../bot/handlers/admin/ping_all.py#L53-L68)
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

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L71-L92`](../../bot/handlers/admin/ping_all.py#L71-L92)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Формирует активный HTML-тег кликабельного упоминания студента.

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

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L95-L108`](../../bot/handlers/admin/ping_all.py#L95-L108)
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

### `build_mentions_block`
```python
def build_mentions_block(classmates: list[dict[str, Any]], sender: User | None) -> str
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L111-L126`](../../bot/handlers/admin/ping_all.py#L111-L126)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует единую строку кликабельных упоминаний одногруппников без автора.

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
from bot.handlers.admin.ping_all import build_mentions_block

# Execute call
result = build_mentions_block(classmates=..., sender=...)
```

---

### `extract_broadcast_text`
```python
def extract_broadcast_text(html_text: str) -> str
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L129-L145`](../../bot/handlers/admin/ping_all.py#L129-L145)
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
def build_broadcast_message(user_html: str, mentions: str, has_reply: bool = False) -> str
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L148-L164`](../../bot/handlers/admin/ping_all.py#L148-L164)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Компонует итоговый HTML-текст поста с текстом автора и пингами внизу.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_html` | `str` | Yes | Parameter `user_html` of type `str`. |
| `mentions` | `str` | Yes | Parameter `mentions` of type `str`. |
| `has_reply` | `bool` | Yes | Parameter `has_reply` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import build_broadcast_message

# Execute call
result = build_broadcast_message(user_html=..., mentions=..., has_reply=...)
```

---

### `safe_delete_command_message`
```python
async def safe_delete_command_message(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L167-L185`](../../bot/handlers/admin/ping_all.py#L167-L185)
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

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L188-L214`](../../bot/handlers/admin/ping_all.py#L188-L214)
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

### `validate_group_chat`
```python
async def validate_group_chat(message: Message) -> bool
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L217-L231`](../../bot/handlers/admin/ping_all.py#L217-L231)
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
def compose_broadcast_content(classmates: list[dict[str, Any]], message: Message) -> tuple[str, int | None]
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L234-L249`](../../bot/handlers/admin/ping_all.py#L234-L249)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, int | None]`

#### Overview & Architectural Purpose
Формирует итоговый HTML-текст рассылки и извлекает ID сообщения для реплая.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `classmates` | `list[dict[str, Any]]` | Yes | Parameter `classmates` of type `list[dict[str, Any]]`. |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.ping_all import compose_broadcast_content

# Execute call
result = compose_broadcast_content(classmates=..., message=...)
```

---

### `dispatch_broadcast`
```python
async def dispatch_broadcast(message: Message, final_text: str, reply_id: int | None) -> None
```

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L252-L270`](../../bot/handlers/admin/ping_all.py#L252-L270)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет широковещательный пост в чат и удаляет триггер-сообщение.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `final_text` | `str` | Yes | Parameter `final_text` of type `str`. |
| `reply_id` | `int | None` | Yes | Parameter `reply_id` of type `int | None`. |

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

- **Source Reference**: [`bot/handlers/admin/ping_all.py#L274-L289`](../../bot/handlers/admin/ping_all.py#L274-L289)
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
