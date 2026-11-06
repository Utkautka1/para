# Component Reference: `bot/handlers/admin/mute.py`
> **File Path**: [`bot/handlers/admin/mute.py`](../../bot/handlers/admin/mute.py)
> **Subsystem**: `Moderation Ban Engine`

## 1. Purpose
Хэндлеры команд модерации и ограничения отправки сообщений (Мут в топиках).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`cache_user_from_message`](#cache_user_from_message) | Function | L22–L43 | `None` | Сохраняет username и user_id авторов сообщений и реплае... |
| [`_find_in_admins`](#_find_in_admins) | Function | L46–L65 | `tuple[int, str] \| None` | Ищет пользователя по юзернейму в списке администраторов... |
| [`_find_in_registry`](#_find_in_registry) | Function | L68–L86 | `tuple[int, str] \| None` | Ищет студента в локальном реестре одногруппников по юзе... |
| [`resolve_user_id_by_username`](#resolve_user_id_by_username) | Function | L89–L108 | `tuple[int, str] \| None` | Выполняет каскадный поиск Telegram ID по строковому юзе... |
| [`_resolve_from_entities`](#_resolve_from_entities) | Function | L111–L128 | `tuple[int, str] \| None` | Извлекает Telegram ID из скрытых сущностей text_mention... |
| [`resolve_target_identity`](#resolve_target_identity) | Function | L131–L154 | `tuple[int \| None, str]` | Определяет идентификатор и имя цели из текстовых аргуме... |
| [`_strip_mute_prefix`](#_strip_mute_prefix) | Function | L157–L172 | `str` | Отрезает команду мута (.закрыть рот, .закрой рот) от на... |
| [`parse_reply_mute_args`](#parse_reply_mute_args) | Function | L175–L195 | `tuple[str, str]` | Извлекает длительность и причину мута при ответе на чуж... |
| [`parse_standalone_mute_args`](#parse_standalone_mute_args) | Function | L198–L219 | `tuple[int \| None, str, str, str]` | Парсит аргументы команды мута без реплая (с явным ID/@u... |
| [`extract_target_id_and_args`](#extract_target_id_and_args) | Function | L222–L237 | `tuple[int \| None, str, str, str]` | Унифицированно извлекает параметры цели мута из реплая ... |
| [`apply_user_restriction`](#apply_user_restriction) | Function | L240–L254 | `None` | Накладывает ограничение на отправку сообщений пользоват... |
| [`_apply_unmute_permissions`](#_apply_unmute_permissions) | Function | L257–L277 | `None` | Восстанавливает стандартные права пользователя на отпра... |
| [`send_mute_notification`](#send_mute_notification) | Function | L280–L294 | `None` | Отправляет публичный или приватный отчет о наложении ли... |
| [`_safe_delete_message`](#_safe_delete_message) | Function | L297–L316 | `None` | Безопасно удаляет командное сообщение в супергруппе без... |
| [`_build_mute_report`](#_build_mute_report) | Function | L319–L334 | `str` | Формирует стильный HTML-текст карточки уведомления о бл... |
| [`is_mute_command`](#is_mute_command) | Function | L337–L352 | `bool` | Проверяет, соответствует ли входящий текст команде нало... |
| [`is_unmute_command`](#is_unmute_command) | Function | L355–L370 | `bool` | Проверяет, соответствует ли входящий текст команде доср... |
| [`_execute_mute`](#_execute_mute) | Function | L373–L383 | `None` | Применяет мут к пользователю в чате и отправляет отчет. |
| [`cmd_mute_user`](#cmd_mute_user) | Function | L387–L403 | `None` | Исполняет команду ограничения отправки сообщений наруши... |
| [`_execute_unmute`](#_execute_unmute) | Function | L406–L416 | `None` | Снимает мут с пользователя в чате и отправляет отчет. |
| [`cmd_unmute_user`](#cmd_unmute_user) | Function | L420–L435 | `None` | Снимает ограничения на отправку сообщений с ранее забло... |

---

## 3. Comprehensive Function Specifications

### `cache_user_from_message`
```python
def cache_user_from_message(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L22-L43`](../../bot/handlers/admin/mute.py#L22-L43)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сохраняет username и user_id авторов сообщений и реплаев в Redis-кэш.

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
from bot.handlers.admin.mute import cache_user_from_message

# Execute call
result = cache_user_from_message(message=...)
```

---

### `_find_in_admins`
```python
async def _find_in_admins(bot, chat_id: int, clean: str) -> tuple[int, str] | None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L46-L65`](../../bot/handlers/admin/mute.py#L46-L65)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[int, str] | None`

#### Overview & Architectural Purpose
Ищет пользователя по юзернейму в списке администраторов группы Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `clean` | `str` | Yes | Parameter `clean` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.mute import _find_in_admins

# Execute call
result = await _find_in_admins(bot=..., chat_id=..., clean=...)
```

---

### `_find_in_registry`
```python
def _find_in_registry(clean: str) -> tuple[int, str] | None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L68-L86`](../../bot/handlers/admin/mute.py#L68-L86)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[int, str] | None`

#### Overview & Architectural Purpose
Ищет студента в локальном реестре одногруппников по юзернейму.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `clean` | `str` | Yes | Parameter `clean` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.mute import _find_in_registry

# Execute call
result = _find_in_registry(clean=...)
```

---

### `resolve_user_id_by_username`
```python
async def resolve_user_id_by_username(bot, chat_id: int, username: str) -> tuple[int, str] | None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L89-L108`](../../bot/handlers/admin/mute.py#L89-L108)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[int, str] | None`

#### Overview & Architectural Purpose
Выполняет каскадный поиск Telegram ID по строковому юзернейму.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `username` | `str` | Yes | Parameter `username` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.mute import resolve_user_id_by_username

# Execute call
result = await resolve_user_id_by_username(bot=..., chat_id=..., username=...)
```

---

### `_resolve_from_entities`
```python
def _resolve_from_entities(message: Message) -> tuple[int, str] | None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L111-L128`](../../bot/handlers/admin/mute.py#L111-L128)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[int, str] | None`

#### Overview & Architectural Purpose
Извлекает Telegram ID из скрытых сущностей text_mention в сообщении.

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
from bot.handlers.admin.mute import _resolve_from_entities

# Execute call
result = _resolve_from_entities(message=...)
```

---

### `resolve_target_identity`
```python
async def resolve_target_identity(message: Message, target_raw: str) -> tuple[int | None, str]
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L131-L154`](../../bot/handlers/admin/mute.py#L131-L154)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[int | None, str]`

#### Overview & Architectural Purpose
Определяет идентификатор и имя цели из текстовых аргументов модератора.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `target_raw` | `str` | Yes | Parameter `target_raw` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.mute import resolve_target_identity

# Execute call
result = await resolve_target_identity(message=..., target_raw=...)
```

---

### `_strip_mute_prefix`
```python
def _strip_mute_prefix(text: str) -> str
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L157-L172`](../../bot/handlers/admin/mute.py#L157-L172)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Отрезает команду мута (.закрыть рот, .закрой рот) от начала строки.

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
from bot.handlers.admin.mute import _strip_mute_prefix

# Execute call
result = _strip_mute_prefix(text=...)
```

---

### `parse_reply_mute_args`
```python
def parse_reply_mute_args(text: str) -> tuple[str, str]
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L175-L195`](../../bot/handlers/admin/mute.py#L175-L195)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str, str]`

#### Overview & Architectural Purpose
Извлекает длительность и причину мута при ответе на чужое сообщение (reply).

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
from bot.handlers.admin.mute import parse_reply_mute_args

# Execute call
result = parse_reply_mute_args(text=...)
```

---

### `parse_standalone_mute_args`
```python
async def parse_standalone_mute_args(message: Message) -> tuple[int | None, str, str, str]
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L198-L219`](../../bot/handlers/admin/mute.py#L198-L219)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[int | None, str, str, str]`

#### Overview & Architectural Purpose
Парсит аргументы команды мута без реплая (с явным ID/@username).

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
from bot.handlers.admin.mute import parse_standalone_mute_args

# Execute call
result = await parse_standalone_mute_args(message=...)
```

---

### `extract_target_id_and_args`
```python
async def extract_target_id_and_args(message: Message) -> tuple[int | None, str, str, str]
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L222-L237`](../../bot/handlers/admin/mute.py#L222-L237)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[int | None, str, str, str]`

#### Overview & Architectural Purpose
Унифицированно извлекает параметры цели мута из реплая или текста команды.

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
from bot.handlers.admin.mute import extract_target_id_and_args

# Execute call
result = await extract_target_id_and_args(message=...)
```

---

### `apply_user_restriction`
```python
async def apply_user_restriction(bot, chat_id: int, user_id: int, duration_sec: int) -> None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L240-L254`](../../bot/handlers/admin/mute.py#L240-L254)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Накладывает ограничение на отправку сообщений пользователю через Bot API.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `duration_sec` | `int` | Yes | Audio duration in seconds for message formatting. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.mute import apply_user_restriction

# Execute call
result = await apply_user_restriction(bot=..., chat_id=..., user_id=...)
```

---

### `_apply_unmute_permissions`
```python
async def _apply_unmute_permissions(bot, chat_id: int, user_id: int) -> None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L257-L277`](../../bot/handlers/admin/mute.py#L257-L277)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Восстанавливает стандартные права пользователя на отправку всех типов сообщений.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Any` | Yes | Parameter `bot` of type `Any`. |
| `chat_id` | `int` | Yes | Unique 64-bit Telegram chat or supergroup identifier. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.mute import _apply_unmute_permissions

# Execute call
result = await _apply_unmute_permissions(bot=..., chat_id=..., user_id=...)
```

---

### `send_mute_notification`
```python
async def send_mute_notification(message: Message, res_text: str) -> None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L280-L294`](../../bot/handlers/admin/mute.py#L280-L294)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет публичный или приватный отчет о наложении либо снятии мута.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `res_text` | `str` | Yes | Parameter `res_text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.mute import send_mute_notification

# Execute call
result = await send_mute_notification(message=..., res_text=...)
```

---

### `_safe_delete_message`
```python
async def _safe_delete_message(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L297-L316`](../../bot/handlers/admin/mute.py#L297-L316)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Безопасно удаляет командное сообщение в супергруппе без падения от ошибок.

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
from bot.handlers.admin.mute import _safe_delete_message

# Execute call
result = await _safe_delete_message(message=...)
```

---

### `_build_mute_report`
```python
def _build_mute_report(target_name: str, time_raw: str, reason: str) -> str
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L319-L334`](../../bot/handlers/admin/mute.py#L319-L334)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует стильный HTML-текст карточки уведомления о блокировке пользователя.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_name` | `str` | Yes | Parameter `target_name` of type `str`. |
| `time_raw` | `str` | Yes | Parameter `time_raw` of type `str`. |
| `reason` | `str` | Yes | Parameter `reason` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.mute import _build_mute_report

# Execute call
result = _build_mute_report(target_name=..., time_raw=..., reason=...)
```

---

### `is_mute_command`
```python
def is_mute_command(text: str | None) -> bool
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L337-L352`](../../bot/handlers/admin/mute.py#L337-L352)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, соответствует ли входящий текст команде наложения мута.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str | None` | Yes | Parameter `text` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.mute import is_mute_command

# Execute call
result = is_mute_command(text=...)
```

---

### `is_unmute_command`
```python
def is_unmute_command(text: str | None) -> bool
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L355-L370`](../../bot/handlers/admin/mute.py#L355-L370)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, соответствует ли входящий текст команде досрочного размута.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str | None` | Yes | Parameter `text` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.mute import is_unmute_command

# Execute call
result = is_unmute_command(text=...)
```

---

### `_execute_mute`
```python
async def _execute_mute(message: Message, target_id: int, target_name: str, time_raw: str, reason: str | None) -> None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L373-L383`](../../bot/handlers/admin/mute.py#L373-L383)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Применяет мут к пользователю в чате и отправляет отчет.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `target_id` | `int` | Yes | Parameter `target_id` of type `int`. |
| `target_name` | `str` | Yes | Parameter `target_name` of type `str`. |
| `time_raw` | `str` | Yes | Parameter `time_raw` of type `str`. |
| `reason` | `str | None` | Yes | Parameter `reason` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.mute import _execute_mute

# Execute call
result = await _execute_mute(message=..., target_id=..., target_name=...)
```

---

### `cmd_mute_user`
```python
async def cmd_mute_user(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L387-L403`](../../bot/handlers/admin/mute.py#L387-L403)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Исполняет команду ограничения отправки сообщений нарушителю в чате группы.

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
from bot.handlers.admin.mute import cmd_mute_user

# Execute call
result = await cmd_mute_user(message=...)
```

---

### `_execute_unmute`
```python
async def _execute_unmute(message: Message, target_id: int, target_name: str) -> None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L406-L416`](../../bot/handlers/admin/mute.py#L406-L416)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Снимает мут с пользователя в чате и отправляет отчет.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `target_id` | `int` | Yes | Parameter `target_id` of type `int`. |
| `target_name` | `str` | Yes | Parameter `target_name` of type `str`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.mute import _execute_unmute

# Execute call
result = await _execute_unmute(message=..., target_id=..., target_name=...)
```

---

### `cmd_unmute_user`
```python
async def cmd_unmute_user(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/mute.py#L420-L435`](../../bot/handlers/admin/mute.py#L420-L435)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Снимает ограничения на отправку сообщений с ранее заблокированного участника.

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
from bot.handlers.admin.mute import cmd_unmute_user

# Execute call
result = await cmd_unmute_user(message=...)
```

---
