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
| [`_build_core_action_rows`](#_build_core_action_rows) | Function | L41–L62 | `list` | Формирует основные кнопки сервисных действий админки. |
| [`_build_action_rows`](#_build_action_rows) | Function | L65–L75 | `list` | Формирует полную матрицу кнопок панели управления админ... |
| [`get_admin_main_kb`](#get_admin_main_kb) | Function | L78–L88 | `InlineKeyboardMarkup` | Генерирует главную инлайн-клавиатуру панели управления ... |
| [`get_swagger_launch_btn`](#get_swagger_launch_btn) | Function | L91–L104 | `InlineKeyboardButton` | Формирует кнопку запуска Telegram Mini App с порталом S... |
| [`_build_tester_rows`](#_build_tester_rows) | Function | L107–L115 | `list` | Формирует ряды кнопок для отображения списка тестеров с... |
| [`get_testers_management_kb`](#get_testers_management_kb) | Function | L118–L135 | `InlineKeyboardMarkup` | Генерирует клавиатуру управления списком разрешенных те... |

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

### `_build_core_action_rows`
```python
def _build_core_action_rows() -> list
```

- **Source Reference**: [`bot/templates/admin/keyboards.py#L41-L62`](../../bot/templates/admin/keyboards.py#L41-L62)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list`

#### Overview & Architectural Purpose
Формирует основные кнопки сервисных действий админки.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.keyboards import _build_core_action_rows

# Execute call
result = _build_core_action_rows()
```

---

### `_build_action_rows`
```python
def _build_action_rows() -> list
```

- **Source Reference**: [`bot/templates/admin/keyboards.py#L65-L75`](../../bot/templates/admin/keyboards.py#L65-L75)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list`

#### Overview & Architectural Purpose
Формирует полную матрицу кнопок панели управления администратора.

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

- **Source Reference**: [`bot/templates/admin/keyboards.py#L78-L88`](../../bot/templates/admin/keyboards.py#L78-L88)
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

- **Source Reference**: [`bot/templates/admin/keyboards.py#L91-L104`](../../bot/templates/admin/keyboards.py#L91-L104)
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

### `_build_tester_rows`
```python
def _build_tester_rows(testers: list[int]) -> list
```

- **Source Reference**: [`bot/templates/admin/keyboards.py#L107-L115`](../../bot/templates/admin/keyboards.py#L107-L115)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list`

#### Overview & Architectural Purpose
Формирует ряды кнопок для отображения списка тестеров с удалением.

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
from bot.templates.admin.keyboards import _build_tester_rows

# Execute call
result = _build_tester_rows(testers=...)
```

---

### `get_testers_management_kb`
```python
def get_testers_management_kb(testers: list[int]) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/keyboards.py#L118-L135`](../../bot/templates/admin/keyboards.py#L118-L135)
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
