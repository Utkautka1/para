# Component Reference: `bot/handlers/user/hw_solver.py`
> **File Path**: [`bot/handlers/user/hw_solver.py`](../../bot/handlers/user/hw_solver.py)
> **Subsystem**: `AI Homework Flow`

## 1. Purpose
Хэндлер перехвата новых ДЗ в целевом топике (ID 405).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`combine_prompt_and_instructions`](#combine_prompt_and_instructions) | Function | L62–L78 | `str` | Объединяет инструкцию из подписи/текста реплая и основн... |
| [`is_valid_homework_prompt`](#is_valid_homework_prompt) | Function | L81–L95 | `bool` | Проверяет, содержит ли сообщение запрос на решение учеб... |
| [`extract_media_meta`](#extract_media_meta) | Function | L98–L118 | `tuple[str \| None, str \| None, str \| None, str \| None, int]` | Извлекает идентификаторы и метаданные медиафайла (фото ... |
| [`_describe_task`](#_describe_task) | Function | L121–L129 | `HomeworkTask` | Описывает принятое сообщение для ачивок топика ДЗ. |
| [`_sender_name`](#_sender_name) | Function | L132–L134 | `str \| None` | Имя автора сообщения для fallback-ФИО ачивок. |
| [`compute_content_hash`](#compute_content_hash) | Function | L137–L154 | `str` | Вычисляет SHA256 хэш промпта и уникального ID файла для... |
| [`is_hw_allowed`](#is_hw_allowed) | Function | L157–L181 | `bool` | Комплексно проверяет право пользователя и валидность за... |
| [`acknowledge_hw_task`](#acknowledge_hw_task) | Function | L184–L201 | `None` | Ставит реакцию 👀 на сообщение студента для мгновенной о... |
| [`build_hw_task`](#build_hw_task) | Function | L204–L230 | `dict` | Собирает payload задания для очереди solver. |
| [`dispatch_hw_task`](#dispatch_hw_task) | Function | L233–L248 | `None` | Ставит задание в очередь и подтверждает приём реакцией. |
| [`is_own_task_reply`](#is_own_task_reply) | Function | L251–L262 | `bool` | Проверяет, что сообщение — реплай автора на его же прин... |
| [`merge_into_pending`](#merge_into_pending) | Function | L265–L281 | `bool` | Дописывает уточнение к заданию, которое ещё ждёт в окне... |
| [`validate_hw_file_size`](#validate_hw_file_size) | Function | L284–L307 | `bool` | Проверяет размер медиафайла для защиты сервиса от исчер... |
| [`handle_new_homework`](#handle_new_homework) | Function | L311–L329 | `None` | Перехватывает сообщение с ДЗ в топике и передает в очер... |
| [`_accept_new_task`](#_accept_new_task) | Function | L332–L349 | `bool` | Проверяет файл и дубликаты и ставит задание (или исправ... |

---

## 3. Comprehensive Function Specifications

### `combine_prompt_and_instructions`
```python
def combine_prompt_and_instructions(msg: Message, target: Message) -> str
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L62-L78`](../../bot/handlers/user/hw_solver.py#L62-L78)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Объединяет инструкцию из подписи/текста реплая и основное задание.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `target` | `Message` | Yes | Parameter `target` of type `Message`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import combine_prompt_and_instructions

# Execute call
result = combine_prompt_and_instructions(msg=..., target=...)
```

---

### `is_valid_homework_prompt`
```python
def is_valid_homework_prompt(text: str | None, has_media: bool) -> bool
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L81-L95`](../../bot/handlers/user/hw_solver.py#L81-L95)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, содержит ли сообщение запрос на решение учебной задачи.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str | None` | Yes | Parameter `text` of type `str | None`. |
| `has_media` | `bool` | Yes | Parameter `has_media` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import is_valid_homework_prompt

# Execute call
result = is_valid_homework_prompt(text=..., has_media=...)
```

---

### `extract_media_meta`
```python
def extract_media_meta(msg: Message, target: Message) -> tuple[str | None, str | None, str | None, str | None, int]
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L98-L118`](../../bot/handlers/user/hw_solver.py#L98-L118)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[str | None, str | None, str | None, str | None, int]`

#### Overview & Architectural Purpose
Извлекает идентификаторы и метаданные медиафайла (фото или документа).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `target` | `Message` | Yes | Parameter `target` of type `Message`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import extract_media_meta

# Execute call
result = extract_media_meta(msg=..., target=...)
```

---

### `_describe_task`
```python
def _describe_task(msg: Message, target: Message, prompt: str, is_followup: bool) -> HomeworkTask
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L121-L129`](../../bot/handlers/user/hw_solver.py#L121-L129)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `HomeworkTask`

#### Overview & Architectural Purpose
Описывает принятое сообщение для ачивок топика ДЗ.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `target` | `Message` | Yes | Parameter `target` of type `Message`. |
| `prompt` | `str` | Yes | Parameter `prompt` of type `str`. |
| `is_followup` | `bool` | Yes | Parameter `is_followup` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import _describe_task

# Execute call
result = _describe_task(msg=..., target=..., prompt=...)
```

---

### `_sender_name`
```python
def _sender_name(msg: Message) -> str | None
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L132-L134`](../../bot/handlers/user/hw_solver.py#L132-L134)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str | None`

#### Overview & Architectural Purpose
Имя автора сообщения для fallback-ФИО ачивок.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import _sender_name

# Execute call
result = _sender_name(msg=...)
```

---

### `compute_content_hash`
```python
def compute_content_hash(text: str | None, unique_id: str | None) -> str
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L137-L154`](../../bot/handlers/user/hw_solver.py#L137-L154)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Вычисляет SHA256 хэш промпта и уникального ID файла для дедупликации.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str | None` | Yes | Parameter `text` of type `str | None`. |
| `unique_id` | `str | None` | Yes | Parameter `unique_id` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import compute_content_hash

# Execute call
result = compute_content_hash(text=..., unique_id=...)
```

---

### `is_hw_allowed`
```python
async def is_hw_allowed(msg: Message, target: Message, user_id: int) -> bool
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L157-L181`](../../bot/handlers/user/hw_solver.py#L157-L181)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Комплексно проверяет право пользователя и валидность задачи на решение.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `target` | `Message` | Yes | Parameter `target` of type `Message`. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import is_hw_allowed

# Execute call
result = await is_hw_allowed(msg=..., target=..., user_id=...)
```

---

### `acknowledge_hw_task`
```python
async def acknowledge_hw_task(bot: Bot, msg: Message) -> None
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L184-L201`](../../bot/handlers/user/hw_solver.py#L184-L201)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Ставит реакцию 👀 на сообщение студента для мгновенной обратной связи.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Bot` | Yes | Parameter `bot` of type `Bot`. |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import acknowledge_hw_task

# Execute call
result = await acknowledge_hw_task(bot=..., msg=...)
```

---

### `build_hw_task`
```python
def build_hw_task( msg: Message, user_id: int, prompt: str, meta: tuple[str | None, str | None, str | None, int], revision_of: int | None = None, ) -> dict
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L204-L230`](../../bot/handlers/user/hw_solver.py#L204-L230)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict`

#### Overview & Architectural Purpose
Собирает payload задания для очереди solver.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `prompt` | `str` | Yes | Parameter `prompt` of type `str`. |
| `meta` | `tuple[str | None, str | None, str | None, int]` | Yes | Parameter `meta` of type `tuple[str | None, str | None, str | None, int]`. |
| `revision_of` | `int | None` | Yes | Parameter `revision_of` of type `int | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import build_hw_task

# Execute call
result = build_hw_task(msg=..., user_id=..., prompt=...)
```

---

### `dispatch_hw_task`
```python
async def dispatch_hw_task(bot: Bot, msg: Message, task: dict, c_hash: str) -> None
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L233-L248`](../../bot/handlers/user/hw_solver.py#L233-L248)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Ставит задание в очередь и подтверждает приём реакцией.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Bot` | Yes | Parameter `bot` of type `Bot`. |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `task` | `dict` | Yes | Parameter `task` of type `dict`. |
| `c_hash` | `str` | Yes | Parameter `c_hash` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import dispatch_hw_task

# Execute call
result = await dispatch_hw_task(bot=..., msg=..., task=...)
```

---

### `is_own_task_reply`
```python
async def is_own_task_reply(msg: Message, target: Message, user_id: int) -> bool
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L251-L262`](../../bot/handlers/user/hw_solver.py#L251-L262)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет, что сообщение — реплай автора на его же принятое задание.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `target` | `Message` | Yes | Parameter `target` of type `Message`. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import is_own_task_reply

# Execute call
result = await is_own_task_reply(msg=..., target=..., user_id=...)
```

---

### `merge_into_pending`
```python
async def merge_into_pending(bot: Bot, msg: Message, target: Message) -> bool
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L265-L281`](../../bot/handlers/user/hw_solver.py#L265-L281)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Дописывает уточнение к заданию, которое ещё ждёт в окне уточнений.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Bot` | Yes | Parameter `bot` of type `Bot`. |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `target` | `Message` | Yes | Parameter `target` of type `Message`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import merge_into_pending

# Execute call
result = await merge_into_pending(bot=..., msg=..., target=...)
```

---

### `validate_hw_file_size`
```python
async def validate_hw_file_size(bot: Bot, msg: Message, f_size: int, f_name: str | None) -> bool
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L284-L307`](../../bot/handlers/user/hw_solver.py#L284-L307)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет размер медиафайла для защиты сервиса от исчерпания памяти.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Bot` | Yes | Parameter `bot` of type `Bot`. |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `f_size` | `int` | Yes | Parameter `f_size` of type `int`. |
| `f_name` | `str | None` | Yes | Parameter `f_name` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import validate_hw_file_size

# Execute call
result = await validate_hw_file_size(bot=..., msg=..., f_size=...)
```

---

### `handle_new_homework`
```python
async def handle_new_homework(msg: Message, bot: Bot) -> None
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L311-L329`](../../bot/handlers/user/hw_solver.py#L311-L329)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Перехватывает сообщение с ДЗ в топике и передает в очередь solver.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `bot` | `Bot` | Yes | Parameter `bot` of type `Bot`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import handle_new_homework

# Execute call
result = await handle_new_homework(msg=..., bot=...)
```

---

### `_accept_new_task`
```python
async def _accept_new_task(bot: Bot, msg: Message, target: Message, user_id: int, own_reply: bool) -> bool
```

- **Source Reference**: [`bot/handlers/user/hw_solver.py#L332-L349`](../../bot/handlers/user/hw_solver.py#L332-L349)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет файл и дубликаты и ставит задание (или исправление) в очередь.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `bot` | `Bot` | Yes | Parameter `bot` of type `Bot`. |
| `msg` | `Message` | Yes | Parameter `msg` of type `Message`. |
| `target` | `Message` | Yes | Parameter `target` of type `Message`. |
| `user_id` | `int` | Yes | Unique 64-bit Telegram user identifier. |
| `own_reply` | `bool` | Yes | Parameter `own_reply` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.user.hw_solver import _accept_new_task

# Execute call
result = await _accept_new_task(bot=..., msg=..., target=...)
```

---
