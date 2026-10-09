# Module Specification: `bot/templates/admin/keyboards.py`
> **Path**: [`bot/templates/admin/keyboards.py`](file:///home/u/Рабочий стол/para/bot/templates/admin/keyboards.py)  
> **Subsystem**: `Admin Panel Keyboards`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль аккуратных Inline-клавиатур личной Панели Администратора. Содержит клавиатуры для управления синхронизацией, топиками, а также списком тестировщиков и запуском Swagger UI Mini App.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_build_topic_action_rows`](#_build_topic_action_rows) | Function | L14–L30 | `list` | Формирует кнопки принудительного обновления и пересоздания т |
| [`_build_action_rows`](#_build_action_rows) | Function | L33–L46 | `list` | Формирует основные кнопки управления топиками и синхронизаци |
| [`get_admin_main_kb`](#get_admin_main_kb) | Function | L49–L51 | `InlineKeyboardMarkup` | Генерирует инлайн-клавиатуру главного экрана админки со стил |
| [`get_swagger_launch_btn`](#get_swagger_launch_btn) | Function | L54–L58 | `InlineKeyboardButton` | Формирует кнопку запуска Mini App или информационную ссылку. |
| [`get_testers_management_kb`](#get_testers_management_kb) | Function | L61–L74 | `InlineKeyboardMarkup` | Генерирует клавиатуру управления списком тестеров Swagger UI |

---

## 3. Exhaustive Function Specifications

### `_build_topic_action_rows`
- **Signature**: `def _build_topic_action_rows() -> list`
- **Source Reference**: [bot/templates/admin/keyboards.py#L14-L30](file:///home/u/Рабочий стол/para/bot/templates/admin/keyboards.py#L14-L30)
- **Async**: `No`
- **Return Type**: `list`

#### Purpose & Architectural Intent
Формирует кнопки принудительного обновления и пересоздания топиков.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return [`

---

### `_build_action_rows`
- **Signature**: `def _build_action_rows() -> list`
- **Source Reference**: [bot/templates/admin/keyboards.py#L33-L46](file:///home/u/Рабочий стол/para/bot/templates/admin/keyboards.py#L33-L46)
- **Async**: `No`
- **Return Type**: `list`

#### Purpose & Architectural Intent
Формирует основные кнопки управления топиками и синхронизацией со стилями.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `rows = [`
2. `rows.extend(_build_topic_action_rows())`
3. `return rows`

---

### `get_admin_main_kb`
- **Signature**: `def get_admin_main_kb() -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/admin/keyboards.py#L49-L51](file:///home/u/Рабочий стол/para/bot/templates/admin/keyboards.py#L49-L51)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Генерирует инлайн-клавиатуру главного экрана админки со стилями кнопок.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return InlineKeyboardMarkup(inline_keyboard=_build_action_rows())`

---

### `get_swagger_launch_btn`
- **Signature**: `def get_swagger_launch_btn() -> InlineKeyboardButton`
- **Source Reference**: [bot/templates/admin/keyboards.py#L54-L58](file:///home/u/Рабочий стол/para/bot/templates/admin/keyboards.py#L54-L58)
- **Async**: `No`
- **Return Type**: `InlineKeyboardButton`

#### Purpose & Architectural Intent
Формирует кнопку запуска Mini App или информационную ссылку.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `if MINIAPP_URL.startswith("https://"):`
2. `return InlineKeyboardButton(text="🚀 Ссылка на Swagger UI", callback_data="admin:show_`

---

### `get_testers_management_kb`
- **Signature**: `def get_testers_management_kb(testers: list[int]) -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/admin/keyboards.py#L61-L74](file:///home/u/Рабочий стол/para/bot/templates/admin/keyboards.py#L61-L74)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Генерирует клавиатуру управления списком тестеров Swagger UI.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `testers` | `list[int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `rows: list = [[get_swagger_launch_btn()]]`
2. `rows.append([`
3. `for uid in testers[:6]:`
4. `rows.append([InlineKeyboardButton(text="◀️ Назад в админку", callback_data="admin:men`
5. `return InlineKeyboardMarkup(inline_keyboard=rows)`

---
