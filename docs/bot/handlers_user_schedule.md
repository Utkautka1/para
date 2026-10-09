# Module Specification: `bot/handlers/user/schedule.py`
> **Path**: [`bot/handlers/user/schedule.py`](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py)  
> **Subsystem**: `User Schedule Flow`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Хэндлеры команд и Inline-кнопок пользователя. Обрабатывает команды и инлайн-переходы sched:today, sched:tomorrow, sched:week, sched:refresh с редактированием существующего сообщения.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_day_schedule_cached`](#get_day_schedule_cached) | Function | L46–L61 | `tuple[str, list[Lesson]]` | Возвращает отформатированный текст и пары с Redis-кэшировани |
| [`_ack_callback`](#_ack_callback) | Function | L64–L72 | `None` | Мгновенно подтверждает callback в Telegram, гася анимацию ож |
| [`edit_or_answer`](#edit_or_answer) | Function | L75–L94 | `None` | Безопасно обновляет содержимое текущего сообщения с учетом п |
| [`_greet_new_student`](#_greet_new_student) | Function | L97–L105 | `None` | Отправляет персональное приветствие новому зарегистрированно |
| [`_show_access_denied`](#_show_access_denied) | Function | L108–L115 | `None` | Информирует неавторизованного пользователя об отказе в досту |
| [`_show_tester_cabinet`](#_show_tester_cabinet) | Function | L118–L127 | `None` | Отправляет экран личного кабинета тестировщика API со ссылка |
| [`cmd_start`](#cmd_start) | Function | L132–L153 | `None` | Авторизует пользователя, проверяет права тестера и отправляе |
| [`cmd_my_api_key`](#cmd_my_api_key) | Function | L158–L164 | `None` | Показывает персональный API-ключ и кнопки запуска Swagger UI |
| [`cb_show_tester_key`](#cb_show_tester_key) | Function | L168–L172 | `None` | Отправляет всплывающее уведомление с персональным ключом тес |
| [`cb_toggle_notify`](#cb_toggle_notify) | Function | L176–L198 | `None` | Переключает статус подписки на 10-минутные напоминания о пар |
| [`cmd_notice`](#cmd_notice) | Function | L202–L213 | `None` | Отображает экран настроек уведомлений /notice. |
| [`cb_notice_toggle`](#cb_notice_toggle) | Function | L217–L231 | `None` | Переключает статус подписки в меню /notice с обновлением экр |
| [`cb_today`](#cb_today) | Function | L235–L241 | `None` | Заменяет сообщение на расписание на сегодня с Redis-кэширова |
| [`cb_tomorrow`](#cb_tomorrow) | Function | L245–L251 | `None` | Заменяет сообщение на расписание на завтра с Redis-кэширован |
| [`cb_week`](#cb_week) | Function | L255–L271 | `None` | Заменяет сообщение на расписание на текущую неделю с Redis-к |
| [`cb_week_next`](#cb_week_next) | Function | L275–L291 | `None` | Заменяет сообщение на расписание на следующую неделю с Redis |
| [`_refresh_and_format_schedule`](#_refresh_and_format_schedule) | Function | L294–L308 | `tuple[str, list[Lesson], int]` | Сбрасывает UI-кэш представлений и загружает свежее расписани |
| [`cb_refresh`](#cb_refresh) | Function | L312–L323 | `None` | Принудительно скачивает расписание, очищает Redis-кэш и обно |
| [`format_help_text`](#format_help_text) | Function | L326–L340 | `str` | Формирует справочное сообщение со списком команд бота. |
| [`cmd_help`](#cmd_help) | Function | L344–L350 | `None` | Выводит список доступных команд для авторизованного пользова |
| [`handle_user_text_message`](#handle_user_text_message) | Function | L354–L369 | `None` | Отвечает на произвольный текст авторизованного пользователя  |

---

## 3. Exhaustive Function Specifications

### `get_day_schedule_cached`
- **Signature**: `async def get_day_schedule_cached(target_date: date) -> tuple[str, list[Lesson]]`
- **Source Reference**: [bot/handlers/user/schedule.py#L46-L61](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L46-L61)
- **Async**: `Yes`
- **Return Type**: `tuple[str, list[Lesson]]`

#### Purpose & Architectural Intent
Возвращает отформатированный текст и пары с Redis-кэшированием на 180с.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `cache_key = f"sched:day_pack:{target_date.isoformat()}"`
2. `cached = await cache_get(cache_key)`
3. `if cached:`
4. `lessons = await get_api_schedule_for_date(target_date)`
5. `text = format_day_schedule(target_date, lessons)`
6. `payload = json.dumps({"text": text, "lessons": [l.model_dump() for l in lessons]})`

---

### `_ack_callback`
- **Signature**: `async def _ack_callback(callback: CallbackQuery, text: str | None = None) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L64-L72](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L64-L72)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Мгновенно подтверждает callback в Telegram, гася анимацию ожидания.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |
| `text` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `edit_or_answer`
- **Signature**: `async def edit_or_answer( callback: CallbackQuery, text: str, lessons: list[Lesson] | None = None, week_offset: int = 0 ) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L75-L94](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L75-L94)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Безопасно обновляет содержимое текущего сообщения с учетом прав и подписки.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |
| `text` | `str` | Input parameter |
| `lessons` | `list[Lesson] | None` | Input parameter |
| `week_offset` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `uid = callback.from_user.id if callback.from_user else 0`
2. `is_att = bool(uid in ALLOWED_ATTENDANCE_USER_IDS)`
3. `is_test = await is_tester_allowed(uid)`
4. `kb = get_schedule_inline_kb(`
5. `try:`

---

### `_greet_new_student`
- **Signature**: `async def _greet_new_student(message: Message, student: dict) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L97-L105](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L97-L105)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет персональное приветствие новому зарегистрированному студенту.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `student` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `name = student.get("full_name", "Студент")`
2. `await message.answer(`

---

### `_show_access_denied`
- **Signature**: `async def _show_access_denied(message: Message, uid: int) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L108-L115](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L108-L115)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Информирует неавторизованного пользователя об отказе в доступе.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `uid` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `await message.answer(`

---

### `_show_tester_cabinet`
- **Signature**: `async def _show_tester_cabinet(message: Message, uid: int) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L118-L127](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L118-L127)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет экран личного кабинета тестировщика API со ссылками.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `uid` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `key = await generate_or_get_tester_key(uid)`
2. `text = (`
3. `await message.answer(text, reply_markup=get_tester_cabinet_kb())`

---

### `cmd_start`
- **Signature**: `async def cmd_start(message: Message) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L132-L153](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L132-L153)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Авторизует пользователя, проверяет права тестера и отправляет меню.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `is_auth, is_just_reg, student = process_user_auth(message.from_user)`
2. `uid = message.from_user.id if message.from_user else 0`
3. `is_tester = await is_tester_allowed(uid)`
4. `if not is_auth and not is_tester:`
5. `if not is_auth and is_tester:`
6. `if is_just_reg and student:`

---

### `cmd_my_api_key`
- **Signature**: `async def cmd_my_api_key(message: Message) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L158-L164](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L158-L164)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Показывает персональный API-ключ и кнопки запуска Swagger UI.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `uid = message.from_user.id if message.from_user else 0`
2. `if not await is_tester_allowed(uid):`
3. `await _show_tester_cabinet(message, uid)`

---

### `cb_show_tester_key`
- **Signature**: `async def cb_show_tester_key(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L168-L172](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L168-L172)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет всплывающее уведомление с персональным ключом тестера.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `uid = callback.from_user.id if callback.from_user else 0`
2. `key = await generate_or_get_tester_key(uid)`
3. `await callback.answer(f"Ваш ключ: {key}", show_alert=True)`

---

### `cb_toggle_notify`
- **Signature**: `async def cb_toggle_notify(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L176-L198](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L176-L198)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Переключает статус подписки на 10-минутные напоминания о парах в ЛС.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `uid = callback.from_user.id if callback.from_user else 0`
2. `new_sub = toggle_subscriber(uid)`
3. `ans_text = "🔔 Напоминания за 10 мин включены!" if new_sub else "🔕 Напоминания отключе`
4. `await _ack_callback(callback, ans_text)`
5. `now = datetime.now(TIMEZONE).date()`
6. `_, lessons = await get_day_schedule_cached(now)`

---

### `cmd_notice`
- **Signature**: `async def cmd_notice(message: Message) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L202-L213](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L202-L213)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отображает экран настроек уведомлений /notice.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not is_authorized_user(message.from_user):`
2. `uid = message.from_user.id if message.from_user else 0`
3. `is_sub = is_subscribed(uid)`
4. `text = format_notice_settings_text(is_sub)`
5. `await message.answer(text, reply_markup=get_notice_settings_kb(is_sub))`

---

### `cb_notice_toggle`
- **Signature**: `async def cb_notice_toggle(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L217-L231](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L217-L231)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Переключает статус подписки в меню /notice с обновлением экрана.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `uid = callback.from_user.id if callback.from_user else 0`
2. `new_sub = toggle_subscriber(uid)`
3. `ans = "🔔 Уведомления включены!" if new_sub else "🔕 Уведомления отключены."`
4. `await _ack_callback(callback, ans)`
5. `text = format_notice_settings_text(new_sub)`
6. `try:`

---

### `cb_today`
- **Signature**: `async def cb_today(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L235-L241](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L235-L241)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Заменяет сообщение на расписание на сегодня с Redis-кэшированием.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.info("Нажата инлайн-кнопка: Сегодня")`
2. `await _ack_callback(callback)`
3. `now = datetime.now(TIMEZONE).date()`
4. `text, lessons = await get_day_schedule_cached(now)`
5. `await edit_or_answer(callback, text, lessons)`

---

### `cb_tomorrow`
- **Signature**: `async def cb_tomorrow(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L245-L251](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L245-L251)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Заменяет сообщение на расписание на завтра с Redis-кэшированием.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.info("Нажата инлайн-кнопка: Завтра")`
2. `await _ack_callback(callback)`
3. `tomorrow = datetime.now(TIMEZONE).date() + timedelta(days=1)`
4. `text, lessons = await get_day_schedule_cached(tomorrow)`
5. `await edit_or_answer(callback, text, lessons)`

---

### `cb_week`
- **Signature**: `async def cb_week(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L255-L271](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L255-L271)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Заменяет сообщение на расписание на текущую неделю с Redis-кэшированием.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.info("Нажата инлайн-кнопка: Эта неделя")`
2. `await _ack_callback(callback)`
3. `today = datetime.now(TIMEZONE).date()`
4. `monday = today - timedelta(days=today.weekday())`
5. `cache_key = f"sched:week:{monday.isoformat()}"`
6. `cached_text = await cache_get(cache_key)`

---

### `cb_week_next`
- **Signature**: `async def cb_week_next(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L275-L291](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L275-L291)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Заменяет сообщение на расписание на следующую неделю с Redis-кэшированием.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.info("Нажата инлайн-кнопка: Следующая неделя")`
2. `await _ack_callback(callback)`
3. `today = datetime.now(TIMEZONE).date()`
4. `next_monday = today - timedelta(days=today.weekday()) + timedelta(weeks=1)`
5. `cache_key = f"sched:week_next:{next_monday.isoformat()}"`
6. `cached_text = await cache_get(cache_key)`

---

### `_refresh_and_format_schedule`
- **Signature**: `async def _refresh_and_format_schedule(now: date) -> tuple[str, list[Lesson], int]`
- **Source Reference**: [bot/handlers/user/schedule.py#L294-L308](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L294-L308)
- **Async**: `Yes`
- **Return Type**: `tuple[str, list[Lesson], int]`

#### Purpose & Architectural Intent
Сбрасывает UI-кэш представлений и загружает свежее расписание из API.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `now` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `await cache_flush("sched:day_pack*")`
2. `await cache_flush("sched:week*")`
3. `teachers_res = await fetch_teachers(force_refresh=False)`
4. `count = teachers_res.get("count", 0)`
5. `try:`
6. `text = format_day_schedule(now, lessons)`

---

### `cb_refresh`
- **Signature**: `async def cb_refresh(callback: CallbackQuery) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L312-L323](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L312-L323)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Принудительно скачивает расписание, очищает Redis-кэш и обновляет экран. :param callback: CallbackQuery

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `callback` | `CallbackQuery` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.info("Нажата инлайн-кнопка: Обновить расписание (Сброс Redis)")`
2. `await _ack_callback(callback, "Синхронизация с API КТМУ...")`
3. `now = datetime.now(TIMEZONE).date()`
4. `text, lessons, count = await _refresh_and_format_schedule(now)`
5. `text += f"\n\n<i>✅ Расписание КТМУ и контакты ({count}) сверены, Redis обновлен!</i>"`
6. `await edit_or_answer(callback, text, lessons)`

---

### `format_help_text`
- **Signature**: `def format_help_text(is_admin: bool) -> str`
- **Source Reference**: [bot/handlers/user/schedule.py#L326-L340](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L326-L340)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует справочное сообщение со списком команд бота.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `is_admin` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `base = (`
2. `if is_admin:`
3. `base += "\n<i>Для навигации по расписанию используйте кнопки под сообщением.</i>"`
4. `return base`

---

### `cmd_help`
- **Signature**: `async def cmd_help(message: Message) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L344-L350](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L344-L350)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Выводит список доступных команд для авторизованного пользователя.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not is_authorized_user(message.from_user):`
2. `uid = message.from_user.id if message.from_user else 0`
3. `text = format_help_text(is_admin=(uid == ALLOWED_USER_ID))`
4. `await message.answer(text)`

---

### `handle_user_text_message`
- **Signature**: `async def handle_user_text_message(message: Message) -> None`
- **Source Reference**: [bot/handlers/user/schedule.py#L354-L369](file:///home/u/Рабочий стол/para/bot/handlers/user/schedule.py#L354-L369)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отвечает на произвольный текст авторизованного пользователя меню помощи.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not is_authorized_user(message.from_user):`
2. `uid = message.from_user.id if message.from_user else 0`
3. `text = format_help_text(is_admin=(uid == ALLOWED_USER_ID))`
4. `now = datetime.now(TIMEZONE).date()`
5. `_, lessons = await get_day_schedule_cached(now)`
6. `is_att = bool(uid in ALLOWED_ATTENDANCE_USER_IDS)`

---
