# Module Specification: `bot/templates/user/keyboards.py`
> **Path**: [`bot/templates/user/keyboards.py`](file:///home/u/Рабочий стол/para/bot/templates/user/keyboards.py)  
> **Subsystem**: `User Inline Keyboards`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль аккуратных Inline-клавиатур навигации. Создает компактные кнопки управления и ссылки для подключения к парам. Ссылки группируются максимум по 2 в ряд для аккуратного отображения в топике.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`format_lesson_button_text`](#format_lesson_button_text) | Function | L15–L23 | `str` | Формирует лаконичный текст кнопки подключения к дистанционно |
| [`chunk_link_buttons`](#chunk_link_buttons) | Function | L26–L43 | `list[list[InlineKeyboardButton]]` | Разбивает кнопки ссылок на дистанционные пары по 2 кнопки в  |
| [`_build_admin_nav_rows`](#_build_admin_nav_rows) | Function | L46–L53 | `list[list[InlineKeyboardButton]]` | Формирует кнопки администратора и старосты для навигации. |
| [`_build_nav_rows`](#_build_nav_rows) | Function | L56–L74 | `list[list[InlineKeyboardButton]]` | Формирует основные кнопки навигации по календарю и неделям с |
| [`get_schedule_inline_kb`](#get_schedule_inline_kb) | Function | L77–L93 | `InlineKeyboardMarkup` | Генерирует продвинутую инлайн-клавиатуру навигации с тумблер |
| [`get_tester_cabinet_kb`](#get_tester_cabinet_kb) | Function | L96–L104 | `InlineKeyboardMarkup` | Клавиатура персонального кабинета авторизованного тестировщи |
| [`get_topic_inline_kb`](#get_topic_inline_kb) | Function | L107–L119 | `InlineKeyboardMarkup | None` | Генерирует чистую инлайн-клавиатуру исключительно для топика |
| [`get_notice_settings_kb`](#get_notice_settings_kb) | Function | L122–L135 | `InlineKeyboardMarkup` | Генерирует инлайн-клавиатуру для меню управления уведомления |

---

## 3. Exhaustive Function Specifications

### `format_lesson_button_text`
- **Signature**: `def format_lesson_button_text(lesson: Lesson) -> str`
- **Source Reference**: [bot/templates/user/keyboards.py#L15-L23](file:///home/u/Рабочий стол/para/bot/templates/user/keyboards.py#L15-L23)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует лаконичный текст кнопки подключения к дистанционной паре. :param lesson: Объект занятия :return: Текст для Inline-кнопки

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |

#### Step-by-Step Logic Execution
1. `sg = f" (П/Г {lesson.subgroup})" if lesson.subgroup > 0 else ""`
2. `return f"🔗 {lesson.period + 1}-я пара{sg}"`

---

### `chunk_link_buttons`
- **Signature**: `def chunk_link_buttons(lessons: list[Lesson]) -> list[list[InlineKeyboardButton]]`
- **Source Reference**: [bot/templates/user/keyboards.py#L26-L43](file:///home/u/Рабочий стол/para/bot/templates/user/keyboards.py#L26-L43)
- **Async**: `No`
- **Return Type**: `list[list[InlineKeyboardButton]]`

#### Purpose & Architectural Intent
Разбивает кнопки ссылок на дистанционные пары по 2 кнопки в ряд. :param lessons: Список предметов :return: Двумерный список кнопок

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Input parameter |

#### Step-by-Step Logic Execution
1. `btns = []`
2. `for l in lessons:`
3. `return [btns[i:i + 2] for i in range(0, len(btns), 2)]`

---

### `_build_admin_nav_rows`
- **Signature**: `def _build_admin_nav_rows(is_admin: bool, is_attendance_admin: bool) -> list[list[InlineKeyboardButton]]`
- **Source Reference**: [bot/templates/user/keyboards.py#L46-L53](file:///home/u/Рабочий стол/para/bot/templates/user/keyboards.py#L46-L53)
- **Async**: `No`
- **Return Type**: `list[list[InlineKeyboardButton]]`

#### Purpose & Architectural Intent
Формирует кнопки администратора и старосты для навигации.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `is_admin` | `bool` | Input parameter |
| `is_attendance_admin` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `rows = []`
2. `if is_attendance_admin or is_admin:`
3. `if is_admin:`
4. `return rows`

---

### `_build_nav_rows`
- **Signature**: `def _build_nav_rows( week_offset: int, is_admin: bool = False, is_subscribed: bool = True, is_attendance_admin: bool = False, is_tester: bool = False, ) -> list[list[InlineKeyboardButton]]`
- **Source Reference**: [bot/templates/user/keyboards.py#L56-L74](file:///home/u/Рабочий стол/para/bot/templates/user/keyboards.py#L56-L74)
- **Async**: `No`
- **Return Type**: `list[list[InlineKeyboardButton]]`

#### Purpose & Architectural Intent
Формирует основные кнопки навигации по календарю и неделям со стилями.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `week_offset` | `int` | Input parameter |
| `is_admin` | `bool` | Input parameter |
| `is_subscribed` | `bool` | Input parameter |
| `is_attendance_admin` | `bool` | Input parameter |
| `is_tester` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `w_text = "⏭ Неделя (След.)" if week_offset == 0 else "⏮ Неделя (Тек.)"`
2. `w_data = "sched:week_next" if week_offset == 0 else "sched:week"`
3. `n_text = "🔔 Напоминания: Вкл" if is_subscribed else "🔕 Напоминания: Выкл"`
4. `rows = [`
5. `if is_tester:`
6. `rows.extend(_build_admin_nav_rows(is_admin, is_attendance_admin))`

---

### `get_schedule_inline_kb`
- **Signature**: `def get_schedule_inline_kb( lessons: list[Lesson] | None = None, week_offset: int = 0, is_admin: bool = False, is_subscribed: bool = True, is_attendance_admin: bool = False, is_tester: bool = False, ) -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/user/keyboards.py#L77-L93](file:///home/u/Рабочий стол/para/bot/templates/user/keyboards.py#L77-L93)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Генерирует продвинутую инлайн-клавиатуру навигации с тумблером напоминаний.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lessons` | `list[Lesson] | None` | Input parameter |
| `week_offset` | `int` | Input parameter |
| `is_admin` | `bool` | Input parameter |
| `is_subscribed` | `bool` | Input parameter |
| `is_attendance_admin` | `bool` | Input parameter |
| `is_tester` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `rows = []`
2. `if lessons:`
3. `rows.extend(_build_nav_rows(`
4. `return InlineKeyboardMarkup(inline_keyboard=rows)`

---

### `get_tester_cabinet_kb`
- **Signature**: `def get_tester_cabinet_kb() -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/user/keyboards.py#L96-L104](file:///home/u/Рабочий стол/para/bot/templates/user/keyboards.py#L96-L104)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Клавиатура персонального кабинета авторизованного тестировщика.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return InlineKeyboardMarkup(`

---

### `get_topic_inline_kb`
- **Signature**: `def get_topic_inline_kb(lessons: list[Lesson] | None = None) -> InlineKeyboardMarkup | None`
- **Source Reference**: [bot/templates/user/keyboards.py#L107-L119](file:///home/u/Рабочий стол/para/bot/templates/user/keyboards.py#L107-L119)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup | None`

#### Purpose & Architectural Intent
Генерирует чистую инлайн-клавиатуру исключительно для топика группы. Содержит только ссылки на дистанционные пары без громоздких кнопок копирования. :param lessons: Список пар на день :return: InlineKeyboardMarkup или None

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lessons` | `list[Lesson] | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not lessons:`
2. `rows = chunk_link_buttons(lessons)`
3. `return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None`

---

### `get_notice_settings_kb`
- **Signature**: `def get_notice_settings_kb(is_subscribed: bool) -> InlineKeyboardMarkup`
- **Source Reference**: [bot/templates/user/keyboards.py#L122-L135](file:///home/u/Рабочий стол/para/bot/templates/user/keyboards.py#L122-L135)
- **Async**: `No`
- **Return Type**: `InlineKeyboardMarkup`

#### Purpose & Architectural Intent
Генерирует инлайн-клавиатуру для меню управления уведомлениями /notice. :param is_subscribed: Текущий статус подписки :return: InlineKeyboardMarkup с динамическим тумблером

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `is_subscribed` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `toggle_text = "🔕 Отключить уведомления" if is_subscribed else "🔔 Включить уведомления`
2. `toggle_style = "danger" if is_subscribed else "success"`
3. `rows = [`
4. `return InlineKeyboardMarkup(inline_keyboard=rows)`

---
