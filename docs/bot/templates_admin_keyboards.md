# Component Reference: `bot/templates/admin/keyboards.py`
> **File Path**: [`bot/templates/admin/keyboards.py`](../../bot/templates/admin/keyboards.py)
> **Subsystem**: `Admin Panel Keyboards`

## 1. Purpose
Модуль аккуратных Inline-клавиатур личной Панели Администратора.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_build_topic_action_rows`](#_build_topic_action_rows) | Function | L14–L38 | `list` | Формирует ряды кнопок принудительного обновления и пере... |
| [`_build_action_rows`](#_build_action_rows) | Function | L41–L68 | `list` | Формирует основную матрицу кнопок панели управления адм... |
| [`get_admin_main_kb`](#get_admin_main_kb) | Function | L71–L81 | `InlineKeyboardMarkup` | Генерирует главную инлайн-клавиатуру панели управления ... |
| [`get_swagger_launch_btn`](#get_swagger_launch_btn) | Function | L84–L97 | `InlineKeyboardButton` | Формирует кнопку запуска Telegram Mini App с порталом S... |
| [`get_testers_management_kb`](#get_testers_management_kb) | Function | L100–L126 | `InlineKeyboardMarkup` | Генерирует клавиатуру управления списком разрешенных те... |

---

## 3. Comprehensive Function Specifications

### `_build_topic_action_rows`
```python
def _build_topic_action_rows() -> list
```

- **Source Reference**: [`bot/templates/admin/keyboards.py#L14-L38`](../../bot/templates/admin/keyboards.py#L14-L38)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list`

#### Overview & Architectural Purpose
Формирует ряды кнопок принудительного обновления и пересоздания топиков супергруппы.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.keyboards import _build_topic_action_rows

# Execute call
result = _build_topic_action_rows()
```

---

### `_build_action_rows`
```python
def _build_action_rows() -> list
```

- **Source Reference**: [`bot/templates/admin/keyboards.py#L41-L68`](../../bot/templates/admin/keyboards.py#L41-L68)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list`

#### Overview & Architectural Purpose
Формирует основную матрицу кнопок панели управления администратора.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.keyboards import _build_action_rows

# Execute call
result = _build_action_rows()
```

---

### `get_admin_main_kb`
```python
def get_admin_main_kb() -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/keyboards.py#L71-L81`](../../bot/templates/admin/keyboards.py#L71-L81)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует главную инлайн-клавиатуру панели управления старосты.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.keyboards import get_admin_main_kb

# Execute call
result = get_admin_main_kb()
```

---

### `get_swagger_launch_btn`
```python
def get_swagger_launch_btn() -> InlineKeyboardButton
```

- **Source Reference**: [`bot/templates/admin/keyboards.py#L84-L97`](../../bot/templates/admin/keyboards.py#L84-L97)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardButton`

#### Overview & Architectural Purpose
Формирует кнопку запуска Telegram Mini App с порталом Swagger UI.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.keyboards import get_swagger_launch_btn

# Execute call
result = get_swagger_launch_btn()
```

---

### `get_testers_management_kb`
```python
def get_testers_management_kb(testers: list[int]) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/keyboards.py#L100-L126`](../../bot/templates/admin/keyboards.py#L100-L126)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует клавиатуру управления списком разрешенных тестеров API.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `testers` | `list[int]` | Yes | Parameter `testers` of type `list[int]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.keyboards import get_testers_management_kb

# Execute call
result = get_testers_management_kb(testers=...)
```

---
