# Component Reference: `bot/handlers/admin/testers.py`
> **File Path**: [`bot/handlers/admin/testers.py`](../../bot/handlers/admin/testers.py)
> **Subsystem**: `Tester Management Flow`

## 1. Purpose
Хэндлеры управления списком тестеров Swagger UI и запуск Mini App.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_get_admin_key`](#_get_admin_key) | Function | L40–L42 | `str` | Возвращает мастер-ключ для старосты или пустую строку. |
| [`_build_testers_panel`](#_build_testers_panel) | Function | L45–L57 | `tuple[str, InlineKeyboardMarkup]` | Собирает текст и клавиатуру панели тестеров для конкрет... |
| [`cmd_list_testers`](#cmd_list_testers) | Function | L61–L73 | `None` | Отображает список всех авторизованных тестеров Swagger ... |
| [`cmd_add_tester`](#cmd_add_tester) | Function | L77–L99 | `None` | Добавляет пользователя в тестеры по команде /add_tester... |
| [`cmd_del_tester`](#cmd_del_tester) | Function | L103–L122 | `None` | Удаляет пользователя из списка тестеров по команде /del... |
| [`cmd_open_swagger`](#cmd_open_swagger) | Function | L126–L137 | `None` | Отправляет карточку быстрого запуска Swagger UI портала... |
| [`cb_admin_testers`](#cb_admin_testers) | Function | L141–L154 | `None` | Открывает раздел управления тестировщиками из главного ... |
| [`cb_start_add_tester`](#cb_start_add_tester) | Function | L158–L170 | `None` | Переводит диалог в FSM-состояние ожидания ввода ID ново... |
| [`process_tester_id_input`](#process_tester_id_input) | Function | L174–L196 | `None` | Валидирует введенный Telegram ID, добавляет в белый спи... |
| [`cb_delete_tester`](#cb_delete_tester) | Function | L200–L217 | `None` | Удаляет выбранного тестера по клику на кнопку в инлайн-... |

---

## 3. Comprehensive Function Specifications

### `_get_admin_key`
```python
def _get_admin_key(user_id: int) -> str
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L40-L42`](../../bot/handlers/admin/testers.py#L40-L42)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Возвращает мастер-ключ для старосты или пустую строку.

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
from bot.handlers.admin.testers import _get_admin_key

# Execute call
result = _get_admin_key(user_id=...)
```

---

### `_build_testers_panel`
```python
async def _build_testers_panel(user_id: int) -> tuple[str, InlineKeyboardMarkup]
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L45-L57`](../../bot/handlers/admin/testers.py#L45-L57)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `tuple[str, InlineKeyboardMarkup]`

#### Overview & Architectural Purpose
Собирает текст и клавиатуру панели тестеров для конкретного администратора.

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
from bot.handlers.admin.testers import _build_testers_panel

# Execute call
result = await _build_testers_panel(user_id=...)
```

---

### `cmd_list_testers`
```python
async def cmd_list_testers(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L61-L73`](../../bot/handlers/admin/testers.py#L61-L73)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отображает список всех авторизованных тестеров Swagger UI и ссылку на портал.

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
from bot.handlers.admin.testers import cmd_list_testers

# Execute call
result = await cmd_list_testers(message=...)
```

---

### `cmd_add_tester`
```python
async def cmd_add_tester(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L77-L99`](../../bot/handlers/admin/testers.py#L77-L99)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет пользователя в тестеры по команде /add_tester <id> и генерирует ключ.

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
from bot.handlers.admin.testers import cmd_add_tester

# Execute call
result = await cmd_add_tester(message=...)
```

---

### `cmd_del_tester`
```python
async def cmd_del_tester(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L103-L122`](../../bot/handlers/admin/testers.py#L103-L122)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет пользователя из списка тестеров по команде /del_tester <id>.

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
from bot.handlers.admin.testers import cmd_del_tester

# Execute call
result = await cmd_del_tester(message=...)
```

---

### `cmd_open_swagger`
```python
async def cmd_open_swagger(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L126-L137`](../../bot/handlers/admin/testers.py#L126-L137)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Отправляет карточку быстрого запуска Swagger UI портала через Mini App.

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
from bot.handlers.admin.testers import cmd_open_swagger

# Execute call
result = await cmd_open_swagger(message=...)
```

---

### `cb_admin_testers`
```python
async def cb_admin_testers(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L141-L154`](../../bot/handlers/admin/testers.py#L141-L154)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Открывает раздел управления тестировщиками из главного меню панели старосты.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.testers import cb_admin_testers

# Execute call
result = await cb_admin_testers(callback=...)
```

---

### `cb_start_add_tester`
```python
async def cb_start_add_tester(callback: CallbackQuery, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L158-L170`](../../bot/handlers/admin/testers.py#L158-L170)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Переводит диалог в FSM-состояние ожидания ввода ID нового тестера.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.testers import cb_start_add_tester

# Execute call
result = await cb_start_add_tester(callback=..., state=...)
```

---

### `process_tester_id_input`
```python
async def process_tester_id_input(message: Message, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L174-L196`](../../bot/handlers/admin/testers.py#L174-L196)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Валидирует введенный Telegram ID, добавляет в белый список и сбрасывает FSM.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.testers import process_tester_id_input

# Execute call
result = await process_tester_id_input(message=..., state=...)
```

---

### `cb_delete_tester`
```python
async def cb_delete_tester(callback: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/testers.py#L200-L217`](../../bot/handlers/admin/testers.py#L200-L217)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет выбранного тестера по клику на кнопку в инлайн-списке.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Yes | Parameter `callback` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.testers import cb_delete_tester

# Execute call
result = await cb_delete_tester(callback=...)
```

---
