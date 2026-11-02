# Component Reference: `bot/templates/admin/testers.py`
> **File Path**: [`bot/templates/admin/testers.py`](../../bot/templates/admin/testers.py)
> **Subsystem**: `Tester Keyboards & States`

## 1. Purpose
Тексты, стейты и клавиатуры для управления тестерами и Swagger UI Mini App.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`format_testers_text`](#format_testers_text) | Function | L20–L41 | `str` | Формирует информационный текст экрана управления доступ... |
| [`get_swagger_buttons`](#get_swagger_buttons) | Function | L44–L61 | `list[InlineKeyboardButton]` | Формирует инлайн-кнопки для перехода в Mini App и прямо... |
| [`get_testers_management_kb`](#get_testers_management_kb) | Function | L64–L94 | `InlineKeyboardMarkup` | Генерирует клавиатуру управления списком тестеров Swagg... |

---

## 3. Comprehensive Function Specifications

## Class Model: `AddTesterState`

FSM-стейт ожидания ввода Telegram ID для добавления тестера.

### `format_testers_text`
```python
def format_testers_text(testers: list[int], admin_key: str = "") -> str
```

- **Source Reference**: [`bot/templates/admin/testers.py#L20-L41`](../../bot/templates/admin/testers.py#L20-L41)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Формирует информационный текст экрана управления доступом к Swagger UI.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `testers` | `list[int]` | Yes | Parameter `testers` of type `list[int]`. |
| `admin_key` | `str` | Yes | Parameter `admin_key` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.testers import format_testers_text

# Execute call
result = format_testers_text(testers=..., admin_key=...)
```

---

### `get_swagger_buttons`
```python
def get_swagger_buttons(login_url: str | None = None) -> list[InlineKeyboardButton]
```

- **Source Reference**: [`bot/templates/admin/testers.py#L44-L61`](../../bot/templates/admin/testers.py#L44-L61)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[InlineKeyboardButton]`

#### Overview & Architectural Purpose
Формирует инлайн-кнопки для перехода в Mini App и прямого открытия Swagger UI.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `login_url` | `str | None` | Yes | Parameter `login_url` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.testers import get_swagger_buttons

# Execute call
result = get_swagger_buttons(login_url=...)
```

---

### `get_testers_management_kb`
```python
def get_testers_management_kb(testers: list[int], login_url: str | None = None) -> InlineKeyboardMarkup
```

- **Source Reference**: [`bot/templates/admin/testers.py#L64-L94`](../../bot/templates/admin/testers.py#L64-L94)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `InlineKeyboardMarkup`

#### Overview & Architectural Purpose
Генерирует клавиатуру управления списком тестеров Swagger UI.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `testers` | `list[int]` | Yes | Parameter `testers` of type `list[int]`. |
| `login_url` | `str | None` | Yes | Parameter `login_url` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from bot.templates.admin.testers import get_testers_management_kb

# Execute call
result = get_testers_management_kb(testers=..., login_url=...)
```

---
