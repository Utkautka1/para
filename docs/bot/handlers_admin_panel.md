# Module Specification: `bot/handlers/admin/panel.py`
> **Path**: [`bot/handlers/admin/panel.py`](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py)  
> **Subsystem**: `Admin Control Panel`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Хэндлеры управления панелью администратора (только для ALLOWED_USER_ID).

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_ack_admin_callback`](#_ack_admin_callback) | Function | L24–L32 | `None` | Мгновенно подтверждает callback в админ-панели с обработкой  |
| [`_safe_edit_admin_message`](#_safe_edit_admin_message) | Function | L35–L47 | `None` | Безопасно обновляет сообщение админки, перехватывая 'not mod |
| [`format_admin_panel_text`](#format_admin_panel_text) | Function | L50–L65 | `str` | Формирует текст главной панели управления. |
| [`cb_admin_menu`](#cb_admin_menu) | Function | L70–L84 | `None` | Отображает главную панель управления с инлайн-кнопками. |
| [`cb_admin_sync`](#cb_admin_sync) | Function | L88–L98 | `None` | Принудительно скачивает расписание КТМУ и таблицу Яндекс Дис |
| [`_get_redis_memory_stat`](#_get_redis_memory_stat) | Function | L101–L111 | `str` | Безопасно извлекает объем используемой оперативной памяти Re |
| [`_collect_health_summary`](#_collect_health_summary) | Function | L114–L136 | `str` | Собирает диагностические метрики всех компонентов системы. |
| [`cb_admin_status`](#cb_admin_status) | Function | L140–L145 | `None` | Показывает подробный дашборд статуса компонентов системы. |
| [`cb_admin_force_topic`](#cb_admin_force_topic) | Function | L149–L155 | `None` | Принудительно публикует или обновляет сообщение в топике. |
| [`cb_admin_recreate_topic`](#cb_admin_recreate_topic) | Function | L159–L166 | `None` | Удаляет текущее сообщение топика и создаёт новое с правильны |
| [`cb_admin_force_exam`](#cb_admin_force_exam) | Function | L170–L177 | `None` | Принудительно обновляет сообщение экзаменов в топике. |
| [`cb_admin_recreate_exam`](#cb_admin_recreate_exam) | Function | L181–L188 | `None` | Удаляет текущее сообщение экзаменов и создаёт новое (сброс M |
| [`cb_admin_force_att_topic`](#cb_admin_force_att_topic) | Function | L192–L199 | `None` | Принудительно обновляет сводный реестр посещаемости в топике |
| [`cb_admin_recreate_att_topic`](#cb_admin_recreate_att_topic) | Function | L203–L210 | `None` | Удаляет старое сообщение реестра и создаёт новое в топике по |
| [`_build_custom_teachers_view`](#_build_custom_teachers_view) | Function | L225–L237 | `tuple[str, list]` | Формирует текст списка кастомных преподавателей и ряды кнопо |
| [`cb_admin_list_custom`](#cb_admin_list_custom) | Function | L241–L253 | `None` | Выводит список кастомных преподавателей с кнопками ред/удал  |
| [`cb_admin_delete_teacher`](#cb_admin_delete_teacher) | Function | L257–L268 | `None` | Удаляет преподавателя и обновляет список. |
| [`cb_admin_edit_teacher`](#cb_admin_edit_teacher) | Function | L272–L293 | `None` | Быстрое редактирование преподавателя. |
| [`cb_admin_start_add_teacher`](#cb_admin_start_add_teacher) | Function | L297–L313 | `None` | Запускает FSM диалог ввода ФИО преподавателя. |
| [`msg_admin_got_teacher_name`](#msg_admin_got_teacher_name) | Function | L317–L332 | `None` | Сохраняет ФИО и запрашивает ссылку на Zoom/Телемост. |
| [`msg_admin_got_teacher_link`](#msg_admin_got_teacher_link) | Function | L336–L358 | `None` | Сохраняет преподавателя в custom_teachers.json и очищает FSM |
| [`_build_unbound_students_kb`](#_build_unbound_students_kb) | Function | L365–L377 | `InlineKeyboardMarkup` | Формирует клавиатуру студентов для привязки Telegram ID. |
| [`cb_admin_list_students_for_binding`](#cb_admin_list_students_for_binding) | Function | L381–L391 | `None` | Отображает список студентов для привязки Telegram ID. |
| [`cb_admin_select_student`](#cb_admin_select_student) | Function | L395–L413 | `None` | Запрашивает ввод Telegram ID для выбранного студента. |
| [`msg_admin_got_student_id`](#msg_admin_got_student_id) | Function | L417–L437 | `None` | Фиксирует Telegram ID студента в реестре и завершает FSM. |

---

## 3. Exhaustive Function Specifications

### `_ack_admin_callback`
- **Signature**: `async def _ack_admin_callback(callback: CallbackQuery, text: str | None = None) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L24-L32](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L24-L32)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Мгновенно подтверждает callback в админ-панели с обработкой устаревания.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |
| `text` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_safe_edit_admin_message`
- **Signature**: `async def _safe_edit_admin_message( message: Message | None, text: str, reply_markup: InlineKeyboardMarkup | None = None ) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L35-L47](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L35-L47)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Безопасно обновляет сообщение админки, перехватывая 'not modified'.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message | None` | Input parameter |
| `text` | `str` | Input parameter |
| `reply_markup` | `InlineKeyboardMarkup | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not message:`
2. `try:`

---

### `format_admin_panel_text`
- **Signature**: `def format_admin_panel_text(status_note: str = "") -> str`
- **Source Reference**: [bot/handlers/admin/panel.py#L50-L65](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L50-L65)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует текст главной панели управления. :param status_note: Дополнительное примечание :return: HTML текст

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `status_note` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `text = (`
2. `if status_note:`
3. `return text`

---

### `cb_admin_menu`
- **Signature**: `async def cb_admin_menu(event: Message | CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L70-L84](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L70-L84)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отображает главную панель управления с инлайн-кнопками. :param event: Message или CallbackQuery

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `event` | `Message | CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.info("Открыто меню админ-панели")`
2. `text = format_admin_panel_text()`
3. `kb = get_admin_main_kb()`
4. `if isinstance(event, CallbackQuery):`

---

### `cb_admin_sync`
- **Signature**: `async def cb_admin_sync(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L88-L98](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L88-L98)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Принудительно скачивает расписание КТМУ и таблицу Яндекс Диска.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `await _ack_admin_callback(callback, "⏳ Синхронизация данных...")`
2. `log.info("Запущена принудительная синхронизация данных из админки")`
3. `res_t = await fetch_teachers(force_refresh=True)`
4. `await fetch_day_schedule(force_refresh=True)`
5. `await sync_topic_main_message()`
6. `count = res_t.get("count", 0)`

---

### `_get_redis_memory_stat`
- **Signature**: `async def _get_redis_memory_stat() -> str`
- **Source Reference**: [bot/handlers/admin/panel.py#L101-L111](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L101-L111)
- **Async**: `Yes`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Безопасно извлекает объем используемой оперативной памяти Redis.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `try:`
2. `return "N/A"`

---

### `_collect_health_summary`
- **Signature**: `async def _collect_health_summary() -> str`
- **Source Reference**: [bot/handlers/admin/panel.py#L114-L136](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L114-L136)
- **Async**: `Yes`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Собирает диагностические метрики всех компонентов системы.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `from db.subscribers import load_subscribers`
2. `from integrations.yandex_docs import get_effective_yandex_cookie`
3. `from services.attendance_topic_updater import load_attendance_topic_state`
4. `from services.classmates_auth import load_classmates_registry`
5. `subs_cnt, class_cnt = len(load_subscribers()), len(load_classmates_registry())`
6. `res_t = await fetch_teachers(force_refresh=False)`

---

### `cb_admin_status`
- **Signature**: `async def cb_admin_status(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L140-L145](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L140-L145)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Показывает подробный дашборд статуса компонентов системы.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `note = await _collect_health_summary()`
2. `text = format_admin_panel_text(note)`
3. `await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())`
4. `await _ack_admin_callback(callback)`

---

### `cb_admin_force_topic`
- **Signature**: `async def cb_admin_force_topic(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L149-L155](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L149-L155)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Принудительно публикует или обновляет сообщение в топике.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `await _ack_admin_callback(callback, "⏳ Обновляю топик...")`
2. `success = await sync_topic_main_message(ignore_time_restriction=True)`
3. `note = "📢 Топик обновлён!" if success else "⚠️ Не удалось обновить топик. Проверьте л`
4. `text = format_admin_panel_text(note)`
5. `await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())`

---

### `cb_admin_recreate_topic`
- **Signature**: `async def cb_admin_recreate_topic(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L159-L166](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L159-L166)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет текущее сообщение топика и создаёт новое с правильным MSG_ID.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `await _ack_admin_callback(callback, "🔁 Пересоздаю сообщение...")`
2. `from services.topic_updater import recreate_topic_message`
3. `success = await recreate_topic_message()`
4. `note = "🔁 Сообщение пересоздано!" if success else "⚠️ Ошибка пересоздания. Проверьте `
5. `text = format_admin_panel_text(note)`
6. `await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())`

---

### `cb_admin_force_exam`
- **Signature**: `async def cb_admin_force_exam(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L170-L177](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L170-L177)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Принудительно обновляет сообщение экзаменов в топике.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `await _ack_admin_callback(callback, "⏳ Обновляю экзамены...")`
2. `from services.exam_topic_updater import sync_exam_topic_message`
3. `success = await sync_exam_topic_message()`
4. `note = "📑 Экзамены обновлены!" if success else "⚠️ Не удалось обновить экзамены."`
5. `text = format_admin_panel_text(note)`
6. `await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())`

---

### `cb_admin_recreate_exam`
- **Signature**: `async def cb_admin_recreate_exam(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L181-L188](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L181-L188)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет текущее сообщение экзаменов и создаёт новое (сброс MSG_ID).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `await _ack_admin_callback(callback, "🔁 Пересоздаю экзамены...")`
2. `from services.exam_topic_updater import recreate_exam_topic_message`
3. `success = await recreate_exam_topic_message()`
4. `note = "🔁 Сообщение экзаменов пересоздано!" if success else "⚠️ Ошибка пересоздания."`
5. `text = format_admin_panel_text(note)`
6. `await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())`

---

### `cb_admin_force_att_topic`
- **Signature**: `async def cb_admin_force_att_topic(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L192-L199](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L192-L199)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Принудительно обновляет сводный реестр посещаемости в топике.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `await _ack_admin_callback(callback, "⏳ Обновляю реестр посещаемости...")`
2. `from services.attendance_topic_updater import sync_attendance_topic_message`
3. `success = await sync_attendance_topic_message(force_refresh=True)`
4. `note = "📊 Реестр посещаемости обновлён!" if success else "⚠️ Не удалось обновить реес`
5. `text = format_admin_panel_text(note)`
6. `await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())`

---

### `cb_admin_recreate_att_topic`
- **Signature**: `async def cb_admin_recreate_att_topic(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L203-L210](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L203-L210)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет старое сообщение реестра и создаёт новое в топике посещаемости.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `await _ack_admin_callback(callback, "🔁 Пересоздаю сообщение посещаемости...")`
2. `from services.attendance_topic_updater import recreate_attendance_topic_message`
3. `success = await recreate_attendance_topic_message()`
4. `note = "🔁 Реестр посещаемости пересоздан!" if success else "⚠️ Ошибка пересоздания."`
5. `text = format_admin_panel_text(note)`
6. `await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())`

---

## Class: `AddTeacherState`
Executes internal domain logic according to service invariants.

### `_build_custom_teachers_view`
- **Signature**: `def _build_custom_teachers_view(custom: dict) -> tuple[str, list]`
- **Source Reference**: [bot/handlers/admin/panel.py#L225-L237](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L225-L237)
- **Async**: `No`
- **Return Type**: `tuple[str, list]`

#### Purpose & Architectural Intent
Формирует текст списка кастомных преподавателей и ряды кнопок.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `custom` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not custom:`
2. `text = "👨‍🏫 <b>Добавленные вручную контакты:</b>\n\n"`
3. `kb_rows = []`
4. `for key, val in custom.items():`
5. `return text, kb_rows`

---

### `cb_admin_list_custom`
- **Signature**: `async def cb_admin_list_custom(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L241-L253](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L241-L253)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Выводит список кастомных преподавателей с кнопками ред/удал и навигацией. :param callback: CallbackQuery

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `custom = load_custom_teachers()`
2. `text, kb_rows = _build_custom_teachers_view(custom)`
3. `kb_rows.append([InlineKeyboardButton(text="➕ Добавить нового", callback_data="admin:a`
4. `kb_rows.append([InlineKeyboardButton(text="◀️ В главную панель", callback_data="admin`
5. `kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)`
6. `await _safe_edit_admin_message(callback.message, text, kb)`

---

### `cb_admin_delete_teacher`
- **Signature**: `async def cb_admin_delete_teacher(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L257-L268](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L257-L268)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет преподавателя и обновляет список. :param callback: CallbackQuery

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `from services.custom_teachers import delete_custom_teacher`
2. `last_name = callback.data.split(":")[-1]`
3. `delete_custom_teacher(last_name)`
4. `await fetch_teachers(force_refresh=True)`
5. `await callback.answer("❌ Запись удалена!")`
6. `await cb_admin_list_custom(callback)`

---

### `cb_admin_edit_teacher`
- **Signature**: `async def cb_admin_edit_teacher(callback: CallbackQuery, state: FSMContext) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L272-L293](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L272-L293)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Быстрое редактирование преподавателя. :param callback: CallbackQuery :param state: FSMContext

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |
| `state` | `FSMContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `last_name = callback.data.split(":")[-1]`
2. `custom = load_custom_teachers()`
3. `t_info = custom.get(last_name, {})`
4. `full_name = t_info.get("full_name", last_name.capitalize())`
5. `await state.set_state(AddTeacherState.waiting_for_link_info)`
6. `await state.update_data(full_name=full_name, suggested_key=last_name)`

---

### `cb_admin_start_add_teacher`
- **Signature**: `async def cb_admin_start_add_teacher(callback: CallbackQuery, state: FSMContext) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L297-L313](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L297-L313)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Запускает FSM диалог ввода ФИО преподавателя. :param callback: CallbackQuery :param state: FSMContext

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |
| `state` | `FSMContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `suggested_key = callback.data.split(":")[-1]`
2. `await state.set_state(AddTeacherState.waiting_for_full_name)`
3. `await state.update_data(suggested_key=suggested_key)`
4. `prompt = (`
5. `await _safe_edit_admin_message(callback.message, prompt)`
6. `await callback.answer()`

---

### `msg_admin_got_teacher_name`
- **Signature**: `async def msg_admin_got_teacher_name(message: Message, state: FSMContext) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L317-L332](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L317-L332)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет ФИО и запрашивает ссылку на Zoom/Телемост. :param message: Message :param state: FSMContext

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `state` | `FSMContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `full_name = message.text.strip() if message.text else ""`
2. `await state.update_data(full_name=full_name)`
3. `await state.set_state(AddTeacherState.waiting_for_link_info)`
4. `prompt = (`
5. `await message.answer(prompt)`

---

### `msg_admin_got_teacher_link`
- **Signature**: `async def msg_admin_got_teacher_link(message: Message, state: FSMContext) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L336-L358](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L336-L358)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет преподавателя в custom_teachers.json и очищает FSM. :param message: Message :param state: FSMContext

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `state` | `FSMContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = await state.get_data()`
2. `full_name = data.get("full_name", "")`
3. `link_info = message.text.strip() if message.text else ""`
4. `last_name = full_name.split()[0].lower() if full_name else data.get("suggested_key", `
5. `save_custom_teacher(last_name, full_name, link_info)`
6. `await fetch_teachers(force_refresh=True)`

---

## Class: `BindStudentState`
Executes internal domain logic according to service invariants.

### `_build_unbound_students_kb`
- **Signature**: `def _build_unbound_students_kb() -> InlineKeyboardMarkup`
- **Source Reference**: [bot/handlers/admin/panel.py#L365-L377](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L365-L377)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Формирует клавиатуру студентов для привязки Telegram ID.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `from services.classmates_auth import load_classmates_registry`
2. `registry = load_classmates_registry()`
3. `kb_rows = []`
4. `for idx, student in enumerate(registry):`
5. `kb_rows.append([InlineKeyboardButton(text="◀️ В главную панель", callback_data="admin`
6. `return InlineKeyboardMarkup(inline_keyboard=kb_rows)`

---

### `cb_admin_list_students_for_binding`
- **Signature**: `async def cb_admin_list_students_for_binding(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L381-L391](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L381-L391)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отображает список студентов для привязки Telegram ID.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `text = (`
2. `kb = _build_unbound_students_kb()`
3. `await _safe_edit_admin_message(callback.message, text, kb)`
4. `await callback.answer()`

---

### `cb_admin_select_student`
- **Signature**: `async def cb_admin_select_student(callback: CallbackQuery, state: FSMContext) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L395-L413](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L395-L413)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Запрашивает ввод Telegram ID для выбранного студента.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |
| `state` | `FSMContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `from services.classmates_auth import load_classmates_registry`
2. `idx = int(callback.data.split(":")[-1])`
3. `registry = load_classmates_registry()`
4. `if idx >= len(registry):`
5. `student = registry[idx]`
6. `fio = student.get("full_name", "")`

---

### `msg_admin_got_student_id`
- **Signature**: `async def msg_admin_got_student_id(message: Message, state: FSMContext) -> None`
- **Source Reference**: [bot/handlers/admin/panel.py#L417-L437](file:///home/u/Рабочий стол/para/bot/handlers/admin/panel.py#L417-L437)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Фиксирует Telegram ID студента в реестре и завершает FSM.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `state` | `FSMContext` | Input parameter |

#### Step-by-Step Logic Execution
1. `raw_id = (message.text or "").strip()`
2. `if not raw_id.isdigit():`
3. `data = await state.get_data()`
4. `fio = data.get("student_name", "")`
5. `from services.classmates_auth import bind_student_tg_id`
6. `updated = bind_student_tg_id(fio, int(raw_id))`

---
