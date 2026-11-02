# Component Reference: `bot/handlers/admin/gamification.py`
> **File Path**: [`bot/handlers/admin/gamification.py`](../../bot/handlers/admin/gamification.py)
> **Subsystem**: `Admin Gamification Panel`

## 1. Purpose
Хэндлеры раздела «Ачивки и очки» админ-панели (только для ALLOWED_USER_ID).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_render`](#_render) | Function | L28–L34 | `None` | Перерисовывает экран, игнорируя «message is not modifie... |
| [`_load_target`](#_load_target) | Function | L37–L42 | `StudentTarget \| None` | Находит студента по индексу или сообщает, что список ус... |
| [`_show_card`](#_show_card) | Function | L45–L52 | `None` | Показывает карточку студента со свежими XP, очками и бо... |
| [`game_students`](#game_students) | Function | L56–L64 | `None` | Список студентов для управления ачивками и очками :para... |
| [`game_card`](#game_card) | Function | L68–L78 | `None` | Карточка студента (и отмена ввода числа — та же кнопка ... |
| [`game_ask_amount`](#game_ask_amount) | Function | L82–L98 | `None` | Превращает карточку в запрос числа для бонуса XP или оч... |
| [`game_enter_amount`](#game_enter_amount) | Function | L102–L121 | `None` | Применяет вписанное число (N — ровно N, +N/−N — прибави... |
| [`_delete_quietly`](#_delete_quietly) | Function | L124–L129 | `None` | Удаляет введённое старостой сообщение, чтобы в чате ост... |
| [`_edit_panel`](#_edit_panel) | Function | L132–L138 | `None` | Меняет сообщение-панель по id, игнорируя «message is no... |
| [`_apply_amount`](#_apply_amount) | Function | L141–L147 | `None` | Выставляет итоговое значение или прибавляет к нему по р... |
| [`_edit_card`](#_edit_card) | Function | L150–L155 | `None` | Возвращает на место запроса свежую карточку студента. |
| [`game_bonus`](#game_bonus) | Function | L159–L172 | `None` | Начисление или списание бонусных XP / очков гильдии :pa... |
| [`game_reset`](#game_reset) | Function | L176–L188 | `None` | Обнуление бонусов студента :param call: CallbackQuery :... |
| [`game_categories`](#game_categories) | Function | L192–L204 | `None` | Категории ачивок студента :param call: CallbackQuery :p... |
| [`_show_category`](#_show_category) | Function | L207–L213 | `None` | Показывает ачивки категории с отметками выдано / не выд... |
| [`game_category`](#game_category) | Function | L217–L225 | `None` | Ачивки одной категории :param call: CallbackQuery :para... |
| [`game_toggle`](#game_toggle) | Function | L229–L242 | `None` | Выдать или снять ачивку :param call: CallbackQuery :par... |

---

## 3. Comprehensive Function Specifications

### `_render`
```python
async def _render(call: CallbackQuery, text: str, markup: InlineKeyboardMarkup) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L28-L34`](../../bot/handlers/admin/gamification.py#L28-L34)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Перерисовывает экран, игнорируя «message is not modified».

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `markup` | `InlineKeyboardMarkup` | Yes | Parameter `markup` of type `InlineKeyboardMarkup`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import _render

# Execute call
result = await _render(call=..., text=..., markup=...)
```

---

### `_load_target`
```python
async def _load_target(call: CallbackQuery, idx: int) -> StudentTarget | None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L37-L42`](../../bot/handlers/admin/gamification.py#L37-L42)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `StudentTarget | None`

#### Overview & Architectural Purpose
Находит студента по индексу или сообщает, что список устарел.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `idx` | `int` | Yes | Parameter `idx` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import _load_target

# Execute call
result = await _load_target(call=..., idx=...)
```

---

### `_show_card`
```python
async def _show_card(call: CallbackQuery, idx: int) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L45-L52`](../../bot/handlers/admin/gamification.py#L45-L52)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Показывает карточку студента со свежими XP, очками и бонусами.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `idx` | `int` | Yes | Parameter `idx` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import _show_card

# Execute call
result = await _show_card(call=..., idx=...)
```

---

### `game_students`
```python
async def game_students(call: CallbackQuery) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L56-L64`](../../bot/handlers/admin/gamification.py#L56-L64)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Список студентов для управления ачивками и очками :param call: CallbackQuery :return:

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import game_students

# Execute call
result = await game_students(call=...)
```

---

### `game_card`
```python
async def game_card(call: CallbackQuery, callback_data: tgame.GameAdminCallback, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L68-L78`](../../bot/handlers/admin/gamification.py#L68-L78)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Карточка студента (и отмена ввода числа — та же кнопка «Назад») :param call: CallbackQuery :param callback_data: индекс студента :param state: FSMContext :return:

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `callback_data` | `tgame.GameAdminCallback` | Yes | Parameter `callback_data` of type `tgame.GameAdminCallback`. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import game_card

# Execute call
result = await game_card(call=..., callback_data=..., state=...)
```

---

### `game_ask_amount`
```python
async def game_ask_amount(call: CallbackQuery, callback_data: tgame.GameAdminCallback, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L82-L98`](../../bot/handlers/admin/gamification.py#L82-L98)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Превращает карточку в запрос числа для бонуса XP или очков гильдии :param call: CallbackQuery :param callback_data: индекс студента и вид бонуса ('xp' / 'guild') :param state: FSMContext :return:

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `callback_data` | `tgame.GameAdminCallback` | Yes | Parameter `callback_data` of type `tgame.GameAdminCallback`. |
| `state` | `FSMContext` | Yes | Aiogram FSM context manager for dialog state persistence. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import game_ask_amount

# Execute call
result = await game_ask_amount(call=..., callback_data=..., state=...)
```

---

### `game_enter_amount`
```python
async def game_enter_amount(message: Message, state: FSMContext) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L102-L121`](../../bot/handlers/admin/gamification.py#L102-L121)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Применяет вписанное число (N — ровно N, +N/−N — прибавить/отнять) и возвращает карточку :param message: Message :param state: FSMContext :return:

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
from bot.handlers.admin.gamification import game_enter_amount

# Execute call
result = await game_enter_amount(message=..., state=...)
```

---

### `_delete_quietly`
```python
async def _delete_quietly(message: Message) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L124-L129`](../../bot/handlers/admin/gamification.py#L124-L129)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Удаляет введённое старостой сообщение, чтобы в чате оставалась только панель.

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
from bot.handlers.admin.gamification import _delete_quietly

# Execute call
result = await _delete_quietly(message=...)
```

---

### `_edit_panel`
```python
async def _edit_panel(message: Message, panel_id: int, text: str, markup: InlineKeyboardMarkup | None) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L132-L138`](../../bot/handlers/admin/gamification.py#L132-L138)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Меняет сообщение-панель по id, игнорируя «message is not modified».

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `panel_id` | `int` | Yes | Parameter `panel_id` of type `int`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `markup` | `InlineKeyboardMarkup | None` | Yes | Parameter `markup` of type `InlineKeyboardMarkup | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import _edit_panel

# Execute call
result = await _edit_panel(message=..., panel_id=..., text=...)
```

---

### `_apply_amount`
```python
async def _apply_amount(message: Message, target: StudentTarget, kind: str, parsed: tuple[bool, int]) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L141-L147`](../../bot/handlers/admin/gamification.py#L141-L147)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Выставляет итоговое значение или прибавляет к нему по разобранному вводу.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `target` | `StudentTarget` | Yes | Parameter `target` of type `StudentTarget`. |
| `kind` | `str` | Yes | Parameter `kind` of type `str`. |
| `parsed` | `tuple[bool, int]` | Yes | Parameter `parsed` of type `tuple[bool, int]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import _apply_amount

# Execute call
result = await _apply_amount(message=..., target=..., kind=...)
```

---

### `_edit_card`
```python
async def _edit_card(message: Message, panel_id: int, idx: int) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L150-L155`](../../bot/handlers/admin/gamification.py#L150-L155)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Возвращает на место запроса свежую карточку студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `Message` | Yes | Aiogram Message event object encapsulating inbound user payload. |
| `panel_id` | `int` | Yes | Parameter `panel_id` of type `int`. |
| `idx` | `int` | Yes | Parameter `idx` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import _edit_card

# Execute call
result = await _edit_card(message=..., panel_id=..., idx=...)
```

---

### `game_bonus`
```python
async def game_bonus(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L159-L172`](../../bot/handlers/admin/gamification.py#L159-L172)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Начисление или списание бонусных XP / очков гильдии :param call: CallbackQuery :param callback_data: индекс студента и 'xp|100' / 'guild|-10' :return:

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `callback_data` | `tgame.GameAdminCallback` | Yes | Parameter `callback_data` of type `tgame.GameAdminCallback`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import game_bonus

# Execute call
result = await game_bonus(call=..., callback_data=...)
```

---

### `game_reset`
```python
async def game_reset(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L176-L188`](../../bot/handlers/admin/gamification.py#L176-L188)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Обнуление бонусов студента :param call: CallbackQuery :param callback_data: индекс студента :return:

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `callback_data` | `tgame.GameAdminCallback` | Yes | Parameter `callback_data` of type `tgame.GameAdminCallback`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import game_reset

# Execute call
result = await game_reset(call=..., callback_data=...)
```

---

### `game_categories`
```python
async def game_categories(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L192-L204`](../../bot/handlers/admin/gamification.py#L192-L204)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Категории ачивок студента :param call: CallbackQuery :param callback_data: индекс студента :return:

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `callback_data` | `tgame.GameAdminCallback` | Yes | Parameter `callback_data` of type `tgame.GameAdminCallback`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import game_categories

# Execute call
result = await game_categories(call=..., callback_data=...)
```

---

### `_show_category`
```python
async def _show_category(call: CallbackQuery, idx: int, category: str) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L207-L213`](../../bot/handlers/admin/gamification.py#L207-L213)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Показывает ачивки категории с отметками выдано / не выдано.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `idx` | `int` | Yes | Parameter `idx` of type `int`. |
| `category` | `str` | Yes | Parameter `category` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import _show_category

# Execute call
result = await _show_category(call=..., idx=..., category=...)
```

---

### `game_category`
```python
async def game_category(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L217-L225`](../../bot/handlers/admin/gamification.py#L217-L225)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Ачивки одной категории :param call: CallbackQuery :param callback_data: индекс студента и категория :return:

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `callback_data` | `tgame.GameAdminCallback` | Yes | Parameter `callback_data` of type `tgame.GameAdminCallback`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import game_category

# Execute call
result = await game_category(call=..., callback_data=...)
```

---

### `game_toggle`
```python
async def game_toggle(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None
```

- **Source Reference**: [`bot/handlers/admin/gamification.py#L229-L242`](../../bot/handlers/admin/gamification.py#L229-L242)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Выдать или снять ачивку :param call: CallbackQuery :param callback_data: индекс студента и 'категория|id_ачивки' :return:

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `call` | `CallbackQuery` | Yes | Parameter `call` of type `CallbackQuery`. |
| `callback_data` | `tgame.GameAdminCallback` | Yes | Parameter `callback_data` of type `tgame.GameAdminCallback`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.handlers.admin.gamification import game_toggle

# Execute call
result = await game_toggle(call=..., callback_data=...)
```

---
