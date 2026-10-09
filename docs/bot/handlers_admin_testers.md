# Module Specification: `bot/handlers/admin/testers.py`
> **Path**: [`bot/handlers/admin/testers.py`](file:///home/u/Рабочий стол/para/bot/handlers/admin/testers.py)  
> **Subsystem**: `Tester Management Flow`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Хэндлеры управления списком тестеров Swagger UI и запуск Mini App. Позволяет администратору просматривать, добавлять и удалять Telegram ID пользователей из белого списка тестеров через команды и инлайн-панель.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`cmd_list_testers`](#cmd_list_testers) | Function | L35–L39 | `None` | Отображает список всех зарегистрированных тестеров API. |
| [`cmd_add_tester`](#cmd_add_tester) | Function | L43–L55 | `None` | Добавляет тестера по команде /add_tester <id> с генерацией к |
| [`cmd_del_tester`](#cmd_del_tester) | Function | L59–L68 | `None` | Удаляет тестера по команде /del_tester <id>. |
| [`cmd_open_swagger`](#cmd_open_swagger) | Function | L72–L75 | `None` | Отправляет клавиатуру запуска Swagger UI Mini App. |
| [`cb_admin_testers`](#cb_admin_testers) | Function | L79–L84 | `None` | Открывает меню управления тестерами из админ-панели. |
| [`cb_start_add_tester`](#cb_start_add_tester) | Function | L88–L92 | `None` | Запрашивает Telegram ID для добавления тестера. |
| [`process_tester_id_input`](#process_tester_id_input) | Function | L96–L108 | `None` | Обрабатывает введенный Telegram ID тестера. |
| [`cb_delete_tester`](#cb_delete_tester) | Function | L112–L120 | `None` | Удаляет тестера по клику на кнопку в списке. |

---

## 3. Exhaustive Function Specifications

### `cmd_list_testers`
- **Signature**: `async def cmd_list_testers(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/testers.py#L35-L39](file:///home/u/Рабочий стол/para/bot/handlers/admin/testers.py#L35-L39)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отображает список всех зарегистрированных тестеров API.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `testers = await get_all_testers()`
2. `text = format_testers_text(testers)`
3. `await message.answer(text, reply_markup=get_testers_management_kb(testers))`

---

### `cmd_add_tester`
- **Signature**: `async def cmd_add_tester(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/testers.py#L43-L55](file:///home/u/Рабочий стол/para/bot/handlers/admin/testers.py#L43-L55)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Добавляет тестера по команде /add_tester <id> с генерацией ключа.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `parts = (message.text or "").split()`
2. `if len(parts) < 2 or not parts[1].isdigit():`
3. `uid = int(parts[1])`
4. `await add_tester(uid)`
5. `key = await generate_or_get_tester_key(uid)`
6. `await message.answer(`

---

### `cmd_del_tester`
- **Signature**: `async def cmd_del_tester(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/testers.py#L59-L68](file:///home/u/Рабочий стол/para/bot/handlers/admin/testers.py#L59-L68)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет тестера по команде /del_tester <id>.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `parts = (message.text or "").split()`
2. `if len(parts) < 2 or not parts[1].isdigit():`
3. `uid = int(parts[1])`
4. `ok = await remove_tester(uid)`
5. `msg = f"🗑️ Пользователь <code>{uid}</code> удален." if ok else "⚠️ Нельзя удалить адм`
6. `await message.answer(msg)`

---

### `cmd_open_swagger`
- **Signature**: `async def cmd_open_swagger(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/testers.py#L72-L75](file:///home/u/Рабочий стол/para/bot/handlers/admin/testers.py#L72-L75)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет клавиатуру запуска Swagger UI Mini App.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `testers = await get_all_testers()`
2. `await message.answer("🚀 <b>Swagger UI Портал para-api</b>", reply_markup=get_testers_`

---

### `cb_admin_testers`
- **Signature**: `async def cb_admin_testers(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/testers.py#L79-L84](file:///home/u/Рабочий стол/para/bot/handlers/admin/testers.py#L79-L84)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Открывает меню управления тестерами из админ-панели.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `testers = await get_all_testers()`
2. `text = format_testers_text(testers)`
3. `await callback.message.edit_text(text, reply_markup=get_testers_management_kb(testers`
4. `await callback.answer()`

---

### `cb_start_add_tester`
- **Signature**: `async def cb_start_add_tester(callback: CallbackQuery, state: FSMContext) -> None`
- **Source Reference**: [bot/handlers/admin/testers.py#L88-L92](file:///home/u/Рабочий стол/para/bot/handlers/admin/testers.py#L88-L92)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Запрашивает Telegram ID для добавления тестера.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |
| `state` | `FSMContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `await state.set_state(AddTesterState.waiting_for_user_id)`
2. `await callback.message.answer("✏️ Введите Telegram ID пользователя для добавления в т`
3. `await callback.answer()`

---

### `process_tester_id_input`
- **Signature**: `async def process_tester_id_input(message: Message, state: FSMContext) -> None`
- **Source Reference**: [bot/handlers/admin/testers.py#L96-L108](file:///home/u/Рабочий стол/para/bot/handlers/admin/testers.py#L96-L108)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Обрабатывает введенный Telegram ID тестера.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `state` | `FSMContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `text = (message.text or "").strip()`
2. `if not text.isdigit():`
3. `uid = int(text)`
4. `await add_tester(uid)`
5. `key = await generate_or_get_tester_key(uid)`
6. `await state.clear()`

---

### `cb_delete_tester`
- **Signature**: `async def cb_delete_tester(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/testers.py#L112-L120](file:///home/u/Рабочий стол/para/bot/handlers/admin/testers.py#L112-L120)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет тестера по клику на кнопку в списке.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `raw_id = callback.data.split(":")[-1]`
2. `if raw_id.isdigit():`
3. `testers = await get_all_testers()`
4. `text = format_testers_text(testers)`
5. `await callback.message.edit_text(text, reply_markup=get_testers_management_kb(testers`
6. `await callback.answer("Тестер удален")`

---
