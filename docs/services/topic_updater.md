# Module Specification: `services/topic_updater.py`
> **Path**: [`services/topic_updater.py`](file:///home/u/Рабочий стол/para/services/topic_updater.py)  
> **Subsystem**: `Live Schedule Topic`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль синхронизации и авто-обновления расписания в Telegram-топике группы. Сохраняет состояние _TOPIC_MAIN_MSG_ID в data/topic_state.json для устойчивости к перезапускам. Синхронизирует расписание каждые 60 секунд и отправляет временные 10-минутные уведомления.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`load_topic_state`](#load_topic_state) | Function | L33–L40 | `int | None` | Загружает сохраненный ID главного сообщения из JSON файла. |
| [`save_topic_state`](#save_topic_state) | Function | L43–L49 | `None` | Атомарно сохраняет ID главного сообщения в JSON файл и Redis |
| [`cleanup_expired_messages`](#cleanup_expired_messages) | Function | L52–L66 | `None` | Удаляет просроченные временные сообщения из топика Telegram. |
| [`send_temp_topic_reminder`](#send_temp_topic_reminder) | Function | L69–L86 | `None` | Отправляет уведомление за 10 минут до пары с регистрацией на |
| [`check_and_trigger_reminder`](#check_and_trigger_reminder) | Function | L89–L106 | `None` | Проверяет время до пары и спавнит таску с защитой от дублей  |
| [`get_next_working_day`](#get_next_working_day) | Function | L109–L119 | `date` | Возвращает следующий рабочий день (пропускает воскресенье, с |
| [`resolve_target_date`](#resolve_target_date) | Function | L122–L144 | `date | None` | Вычисляет целевую дату: при завершении всех пар на сегодня п |
| [`is_too_early_to_publish`](#is_too_early_to_publish) | Function | L147–L161 | `bool` | Проверяет, не рано ли публиковать расписание (за 1 час до 1- |
| [`update_topic_message_payload`](#update_topic_message_payload) | Function | L164–L186 | `bool` | Атомарно отправляет новое или редактирует существующее сообщ |
| [`_send_new_topic_message`](#_send_new_topic_message) | Function | L189–L200 | `bool` | Создаёт новое сообщение расписания в топике и закрепляет его |
| [`_pin_silently`](#_pin_silently) | Function | L203–L211 | `None` | Закрепляет сообщение без уведомления участникам. |
| [`recreate_topic_message`](#recreate_topic_message) | Function | L214–L238 | `bool` | Удаляет текущее сообщение и создаёт новое (одноразовый сброс |
| [`_handle_edit_failure`](#_handle_edit_failure) | Function | L241–L259 | `bool` | Обрабатывает ошибку редактирования: "not modified" — штатно, |
| [`should_skip_topic_update`](#should_skip_topic_update) | Function | L262–L271 | `bool` | Проверяет, нужно ли пропустить публикацию расписания из-за р |
| [`process_today_reminders`](#process_today_reminders) | Function | L274–L278 | `None` | Запускает асинхронную проверку напоминаний для пар текущего  |
| [`sync_topic_main_message`](#sync_topic_main_message) | Function | L281–L301 | `bool` | Атомарно обновляет главное сообщение расписания в топике. |
| [`notify_admin_about_api_down`](#notify_admin_about_api_down) | Function | L308–L322 | `None` | Отправляет экстренное уведомление администратору в ЛС при сб |
| [`topic_sync_loop`](#topic_sync_loop) | Function | L325–L346 | `None` | Фоновый цикл синхронизации топика каждые 60 секунд. |

---

## 3. Exhaustive Function Specifications

### `load_topic_state`
- **Signature**: `def load_topic_state() -> int | None`
- **Source Reference**: [services/topic_updater.py#L33-L40](file:///home/u/Рабочий стол/para/services/topic_updater.py#L33-L40)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Загружает сохраненный ID главного сообщения из JSON файла. :return: ID сообщения или None

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `data = sync_load_json(STATE_FILE, default={})`
2. `return data.get("main_msg_id") if isinstance(data, dict) else None`

---

### `save_topic_state`
- **Signature**: `def save_topic_state(msg_id: int | None) -> None`
- **Source Reference**: [services/topic_updater.py#L43-L49](file:///home/u/Рабочий стол/para/services/topic_updater.py#L43-L49)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Атомарно сохраняет ID главного сообщения в JSON файл и Redis.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `msg_id` | `int | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `import asyncio`
2. `sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})`
3. `if msg_id:`

---

### `cleanup_expired_messages`
- **Signature**: `async def cleanup_expired_messages() -> None`
- **Source Reference**: [services/topic_updater.py#L52-L66](file:///home/u/Рабочий стол/para/services/topic_updater.py#L52-L66)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет просроченные временные сообщения из топика Telegram.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `from core.redis_cache import get_expired_messages_for_cleanup`
2. `expired = await get_expired_messages_for_cleanup()`
3. `for chat_id, msg_id in expired:`

---

### `send_temp_topic_reminder`
- **Signature**: `async def send_temp_topic_reminder(lesson: Lesson) -> None`
- **Source Reference**: [services/topic_updater.py#L69-L86](file:///home/u/Рабочий стол/para/services/topic_updater.py#L69-L86)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет уведомление за 10 минут до пары с регистрацией на удаление.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |

#### Step-by-Step Logic Execution
1. `from core.redis_cache import register_message_for_cleanup`
2. `try:`

---

### `check_and_trigger_reminder`
- **Signature**: `async def check_and_trigger_reminder(lesson: Lesson, now_dt: datetime, today: date) -> None`
- **Source Reference**: [services/topic_updater.py#L89-L106](file:///home/u/Рабочий стол/para/services/topic_updater.py#L89-L106)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Проверяет время до пары и спавнит таску с защитой от дублей в Redis.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |
| `now_dt` | `datetime` | Input parameter |
| `today` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `rem_key = f"{today.isoformat()}_{lesson.period}_{lesson.subgroup}_{lesson.subject}"`
2. `if rem_key in _SENT_REMINDERS:`
3. `from core.redis_cache import is_reminder_sent, mark_reminder_sent`
4. `if await is_reminder_sent(rem_key):`
5. `start_t = parse_lesson_start_time(lesson.time_str)`
6. `if not start_t:`

---

### `get_next_working_day`
- **Signature**: `def get_next_working_day(target_date: date) -> date`
- **Source Reference**: [services/topic_updater.py#L109-L119](file:///home/u/Рабочий стол/para/services/topic_updater.py#L109-L119)
- **Async**: `No`
- **Return Type**: `date`

#### Purpose & Architectural Intent
Возвращает следующий рабочий день (пропускает воскресенье, сдвигая на понедельник). :param target_date: Текущая дата :return: Следующая дата без воскресенья

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `next_d = target_date + timedelta(days=1)`
2. `if next_d.weekday() == 6:`
3. `return next_d`

---

### `resolve_target_date`
- **Signature**: `async def resolve_target_date(now_dt: datetime, ignore_restriction: bool) -> date | None`
- **Source Reference**: [services/topic_updater.py#L122-L144](file:///home/u/Рабочий стол/para/services/topic_updater.py#L122-L144)
- **Async**: `Yes`
- **Return Type**: `date | None`

#### Purpose & Architectural Intent
Вычисляет целевую дату: при завершении всех пар на сегодня переключает на следующий день. :param now_dt: Текущее время МСК :param ignore_restriction: Игнорировать ли временные фильтры :return: Дата или None

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `now_dt` | `datetime` | Input parameter |
| `ignore_restriction` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `today = now_dt.date()`
2. `if today.weekday() == 6:`
3. `today_lessons = await get_api_schedule_for_date(today)`
4. `if not today_lessons:`
5. `last_lesson = max(today_lessons, key=lambda x: x.period)`
6. `end_t = parse_lesson_end_time(last_lesson.time_str)`

---

### `is_too_early_to_publish`
- **Signature**: `def is_too_early_to_publish(lessons: list[Lesson], now_dt: datetime, today: date, ignore_restriction: bool) -> bool`
- **Source Reference**: [services/topic_updater.py#L147-L161](file:///home/u/Рабочий стол/para/services/topic_updater.py#L147-L161)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, не рано ли публиковать расписание (за 1 час до 1-й пары). :return: True если еще рано отправлять новое сообщение

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Input parameter |
| `now_dt` | `datetime` | Input parameter |
| `today` | `date` | Input parameter |
| `ignore_restriction` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if today.weekday() == 6 or ignore_restriction or _TOPIC_MAIN_MSG_ID is not None:`
2. `first_lesson = min(lessons, key=lambda x: x.period)`
3. `start_t = parse_lesson_start_time(first_lesson.time_str)`
4. `if start_t:`
5. `return False`

---

### `update_topic_message_payload`
- **Signature**: `async def update_topic_message_payload(text: str, kb: Any, _retry: bool = False) -> bool`
- **Source Reference**: [services/topic_updater.py#L164-L186](file:///home/u/Рабочий стол/para/services/topic_updater.py#L164-L186)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Атомарно отправляет новое или редактирует существующее сообщение топика. При ошибке редактирования (сообщение удалено/недоступно) — пересоздаёт. _retry=True предотвращает бесконечную рекурсию. :return: True если сообщение обновлено/создано, False при ошибке

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |
| `kb` | `Any` | Input parameter |
| `_retry` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_send_new_topic_message`
- **Signature**: `async def _send_new_topic_message(text: str, kb: Any) -> bool`
- **Source Reference**: [services/topic_updater.py#L189-L200](file:///home/u/Рабочий стол/para/services/topic_updater.py#L189-L200)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Создаёт новое сообщение расписания в топике и закрепляет его.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |
| `kb` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _TOPIC_MAIN_MSG_ID`
2. `msg = await bot.send_message(`
3. `_TOPIC_MAIN_MSG_ID = msg.message_id`
4. `save_topic_state(_TOPIC_MAIN_MSG_ID)`
5. `await _pin_silently(TOPIC_CHAT_ID, _TOPIC_MAIN_MSG_ID)`
6. `log.info(f"Главное сообщение создано и закреплено: MSG_ID={_TOPIC_MAIN_MSG_ID}")`

---

### `_pin_silently`
- **Signature**: `async def _pin_silently(chat_id: int, message_id: int) -> None`
- **Source Reference**: [services/topic_updater.py#L203-L211](file:///home/u/Рабочий стол/para/services/topic_updater.py#L203-L211)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Закрепляет сообщение без уведомления участникам.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |
| `message_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `recreate_topic_message`
- **Signature**: `async def recreate_topic_message() -> bool`
- **Source Reference**: [services/topic_updater.py#L214-L238](file:///home/u/Рабочий стол/para/services/topic_updater.py#L214-L238)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Удаляет текущее сообщение и создаёт новое (одноразовый сброс MSG_ID). Используется когда MSG_ID в state указывает на призрачное/невидимое сообщение. После вызова — дальнейшие sync будут редактировать уже правильное сообщение. :return: True если пересоздание прошло

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _TOPIC_MAIN_MSG_ID`
2. `old_id = _TOPIC_MAIN_MSG_ID or load_topic_state()`
3. `if old_id:`
4. `_TOPIC_MAIN_MSG_ID = None`
5. `save_topic_state(None)`
6. `log.info("State сброшен — следующий sync создаст новое сообщение")`

---

### `_handle_edit_failure`
- **Signature**: `async def _handle_edit_failure( e: TelegramBadRequest, text: str, kb: Any, is_retry: bool ) -> bool`
- **Source Reference**: [services/topic_updater.py#L241-L259](file:///home/u/Рабочий стол/para/services/topic_updater.py#L241-L259)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Обрабатывает ошибку редактирования: "not modified" — штатно, остальные — пересоздаёт сообщение (один раз, без рекурсии).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `e` | `TelegramBadRequest` | Input parameter |
| `text` | `str` | Input parameter |
| `kb` | `Any` | Input parameter |
| `is_retry` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _TOPIC_MAIN_MSG_ID`
2. `err = str(e).lower()`
3. `if "not modified" in err:`
4. `if is_retry:`
5. `log.warning(f"⚠️ Ошибка редактирования MSG_ID={_TOPIC_MAIN_MSG_ID} ({e}), пересоздаём`
6. `_TOPIC_MAIN_MSG_ID = None`

---

### `should_skip_topic_update`
- **Signature**: `def should_skip_topic_update( lessons: list, now_dt: datetime, target_date: date, ignore_time_restriction: bool ) -> bool`
- **Source Reference**: [services/topic_updater.py#L262-L271](file:///home/u/Рабочий стол/para/services/topic_updater.py#L262-L271)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, нужно ли пропустить публикацию расписания из-за раннего времени.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lessons` | `list` | Input parameter |
| `now_dt` | `datetime` | Input parameter |
| `target_date` | `date` | Input parameter |
| `ignore_time_restriction` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if lessons and is_too_early_to_publish(lessons, now_dt, target_date, ignore_time_rest`
2. `return False`

---

### `process_today_reminders`
- **Signature**: `async def process_today_reminders(lessons: list, now_dt: datetime, target_date: date) -> None`
- **Source Reference**: [services/topic_updater.py#L274-L278](file:///home/u/Рабочий стол/para/services/topic_updater.py#L274-L278)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Запускает асинхронную проверку напоминаний для пар текущего дня.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lessons` | `list` | Input parameter |
| `now_dt` | `datetime` | Input parameter |
| `target_date` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `if lessons and now_dt.date() == target_date:`

---

### `sync_topic_main_message`
- **Signature**: `async def sync_topic_main_message(ignore_time_restriction: bool = False) -> bool`
- **Source Reference**: [services/topic_updater.py#L281-L301](file:///home/u/Рабочий стол/para/services/topic_updater.py#L281-L301)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Атомарно обновляет главное сообщение расписания в топике.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `ignore_time_restriction` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _TOPIC_MAIN_MSG_ID`
2. `if _TOPIC_MAIN_MSG_ID is None:`
3. `now_dt = datetime.now(TIMEZONE)`
4. `target_date = await resolve_target_date(now_dt, ignore_time_restriction)`
5. `if not target_date:`
6. `lessons = await get_api_schedule_for_date(target_date)`

---

### `notify_admin_about_api_down`
- **Signature**: `async def notify_admin_about_api_down() -> None`
- **Source Reference**: [services/topic_updater.py#L308-L322](file:///home/u/Рабочий стол/para/services/topic_updater.py#L308-L322)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет экстренное уведомление администратору в ЛС при сбое внешних сервисов свыше 30 минут.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _API_ALERT_SENT`
2. `if _API_ALERT_SENT:`
3. `try:`

---

### `topic_sync_loop`
- **Signature**: `async def topic_sync_loop() -> None`
- **Source Reference**: [services/topic_updater.py#L325-L346](file:///home/u/Рабочий стол/para/services/topic_updater.py#L325-L346)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Фоновый цикл синхронизации топика каждые 60 секунд.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _API_FAIL_START_TIME, _API_ALERT_SENT`
2. `log.info("Запущен фоновый сервис авто-обновления расписания в топике Telegram (60 сек`
3. `while True:`

---
