# Module Specification: `bot/templates/admin/testers.py`
> **Path**: [`bot/templates/admin/testers.py`](file:///home/u/Рабочий стол/para/bot/templates/admin/testers.py)  
> **Subsystem**: `Tester Keyboards & States`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Тексты, стейты и клавиатуры для управления тестерами и Swagger UI Mini App. Изолирует шаблоны отображения и разметку интерфейса от логики хэндлеров в соответствии с канонической структурой проекта.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`format_testers_text`](#format_testers_text) | Function | L20–L30 | `str` | Формирует HTML-текст со списком текущих тестировщиков. |
| [`get_swagger_buttons`](#get_swagger_buttons) | Function | L33–L40 | `list[InlineKeyboardButton]` | Формирует кнопки запуска веб-интерфейса Swagger UI и Mini Ap |
| [`get_testers_management_kb`](#get_testers_management_kb) | Function | L43–L59 | `InlineKeyboardMarkup` | Генерирует клавиатуру управления списком тестеров Swagger UI |

---

## 3. Exhaustive Function Specifications

## Class: `AddTesterState`
FSM-стейт ожидания ввода Telegram ID для добавления тестера.

### `format_testers_text`
- **Signature**: `def format_testers_text(testers: list[int]) -> str`
- **Source Reference**: [bot/templates/admin/testers.py#L20-L30](file:///home/u/Рабочий стол/para/bot/templates/admin/testers.py#L20-L30)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует HTML-текст со списком текущих тестировщиков.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `testers` | `list[int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `items = "\n".join(f"  • <code>{uid}</code>" for uid in testers) or "  <i>(Список пуст`
2. `web_url = f"<code>{SWAGGER_URL}</code>" if SWAGGER_URL else "<i>(Не задан)</i>"`
3. `return (`

---

### `get_swagger_buttons`
- **Signature**: `def get_swagger_buttons() -> list[InlineKeyboardButton]`
- **Source Reference**: [bot/templates/admin/testers.py#L33-L40](file:///home/u/Рабочий стол/para/bot/templates/admin/testers.py#L33-L40)
- **Async**: `No`
- **Return Type**: `list[InlineKeyboardButton]`

#### Purpose & Architectural Intent
Формирует кнопки запуска веб-интерфейса Swagger UI и Mini App.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `btns = []`
2. `if SWAGGER_URL:`
3. `if MINIAPP_URL.startswith("https://"):`
4. `return btns`

---

### `get_testers_management_kb`
- **Signature**: `def get_testers_management_kb(testers: list[int]) -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/admin/testers.py#L43-L59](file:///home/u/Рабочий стол/para/bot/templates/admin/testers.py#L43-L59)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Генерирует клавиатуру управления списком тестеров Swagger UI.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `testers` | `list[int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `rows: list = []`
2. `top_btns = get_swagger_buttons()`
3. `if top_btns:`
4. `rows.append([`
5. `for uid in testers[:6]:`
6. `rows.append([InlineKeyboardButton(text="◀️ Назад в админку", callback_data="admin:men`

---
