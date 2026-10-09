# Module Specification: `services/notifier.py`
> **Path**: [`services/notifier.py`](file:///home/u/Рабочий стол/para/services/notifier.py)  
> **Subsystem**: `Notification Dispatcher`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Сервис рассылки уведомлений и динамических напоминаний. Использует AsyncIOScheduler для отправки ежедневного расписания в 06:00 МСК и планирования индивидуальных напоминаний за 10 минут до каждой пары.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`build_missing_teacher_alert`](#build_missing_teacher_alert) | Function | L40–L55 | `tuple[str, InlineKeyboardMarkup]` | Формирует текст и клавиатуру предупреждения об отсутствии пр |
| [`notify_missing_teacher`](#notify_missing_teacher) | Function | L58–L68 | `None` | Уведомляет администратора в ЛС, если преподаватель дистанцио |
| [`send_to_user`](#send_to_user) | Function | L71–L82 | `None` | Отправляет сообщение разрешенному пользователю ALLOWED_USER_ |
| [`parse_lesson_start_time`](#parse_lesson_start_time) | Function | L85–L100 | `dtime | None` | Парсит время начала пары из строки любого формата ('08:30–09 |
| [`parse_lesson_end_time`](#parse_lesson_end_time) | Function | L103–L118 | `dtime | None` | Парсит время окончания пары из строки любого формата ('08:30 |
| [`_send_reminder_to_chat`](#_send_reminder_to_chat) | Function | L121–L130 | `None` | Отправляет персональное напоминание одному подписчику под ко |
| [`send_single_reminder`](#send_single_reminder) | Function | L133–L143 | `None` | Отправляет 10-минутное напоминание о паре всем активным подп |
| [`schedule_lesson_reminder`](#schedule_lesson_reminder) | Function | L146–L165 | `None` | Планирует таймер напоминания за 10 минут до пары. |
| [`_send_attendance_to_admin`](#_send_attendance_to_admin) | Function | L168–L177 | `None` | Отправляет запрос подтверждения пары старосте или замстарост |
| [`send_attendance_prompt`](#send_attendance_prompt) | Function | L180–L186 | `None` | Отправляет запрос подтверждения проведения пары старосте и з |
| [`auto_close_attendance_session`](#auto_close_attendance_session) | Function | L189–L198 | `None` | Автоматически закрывает неактивную сессию отметки по окончан |
| [`schedule_attendance_poll`](#schedule_attendance_poll) | Function | L201–L215 | `None` | Планирует опрос через 30 минут от старта пары и автозавершен |
| [`daily_schedule_dispatch`](#daily_schedule_dispatch) | Function | L218–L231 | `None` | Ежедневный воркер расчёта таймеров (пропускает воскресенье). |
| [`setup_scheduler`](#setup_scheduler) | Function | L234–L247 | `AsyncIOScheduler` | Инициализирует и запускает планировщик задач. |

---

## 3. Exhaustive Function Specifications

### `build_missing_teacher_alert`
- **Signature**: `def build_missing_teacher_alert(raw_teacher: str, subj_name: str) -> tuple[str, InlineKeyboardMarkup]`
- **Source Reference**: [services/notifier.py#L40-L55](file:///home/u/Рабочий стол/para/services/notifier.py#L40-L55)
- **Async**: `No`
- **Return Type**: `tuple[str, InlineKeyboardMarkup]`

#### Purpose & Architectural Intent
Формирует текст и клавиатуру предупреждения об отсутствии преподавателя.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw_teacher` | `str` | Input parameter |
| `subj_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `text = (`
2. `last_name = raw_teacher.split()[0].lower()`
3. `kb = InlineKeyboardMarkup(inline_keyboard=[[`
4. `return text, kb`

---

### `notify_missing_teacher`
- **Signature**: `async def notify_missing_teacher(raw_teacher: str, subj_name: str) -> None`
- **Source Reference**: [services/notifier.py#L58-L68](file:///home/u/Рабочий стол/para/services/notifier.py#L58-L68)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Уведомляет администратора в ЛС, если преподаватель дистанционной пары не найден.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw_teacher` | `str` | Input parameter |
| `subj_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not raw_teacher or raw_teacher in _NOTIFIED_MISSING_TEACHERS:`
2. `_NOTIFIED_MISSING_TEACHERS.add(raw_teacher)`
3. `text, kb = build_missing_teacher_alert(raw_teacher, subj_name)`
4. `log.warning(f"Уведомление админа об отсутствующем преподавателе: {raw_teacher}")`
5. `await send_to_user(text, reply_markup=kb)`

---

### `send_to_user`
- **Signature**: `async def send_to_user(text: str, reply_markup=None) -> None`
- **Source Reference**: [services/notifier.py#L71-L82](file:///home/u/Рабочий стол/para/services/notifier.py#L71-L82)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет сообщение разрешенному пользователю ALLOWED_USER_ID. :param text: Текст HTML сообщения :param reply_markup: Опциональная клавиатура

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |
| `reply_markup` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `parse_lesson_start_time`
- **Signature**: `def parse_lesson_start_time(time_str: str) -> dtime | None`
- **Source Reference**: [services/notifier.py#L85-L100](file:///home/u/Рабочий стол/para/services/notifier.py#L85-L100)
- **Async**: `No`
- **Return Type**: `dtime | None`

#### Purpose & Architectural Intent
Парсит время начала пары из строки любого формата ('08:30–09:55', '8:30-09:55'). :param time_str: Строка времени :return: Объект time или None при ошибке

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `time_str` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`
2. `return None`

---

### `parse_lesson_end_time`
- **Signature**: `def parse_lesson_end_time(time_str: str) -> dtime | None`
- **Source Reference**: [services/notifier.py#L103-L118](file:///home/u/Рабочий стол/para/services/notifier.py#L103-L118)
- **Async**: `No`
- **Return Type**: `dtime | None`

#### Purpose & Architectural Intent
Парсит время окончания пары из строки любого формата ('08:30–09:55'). :param time_str: Строка времени :return: Объект time или None при ошибке

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `time_str` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`
2. `return None`

---

### `_send_reminder_to_chat`
- **Signature**: `async def _send_reminder_to_chat( chat_id: int, text: str, lesson: Lesson, sem: asyncio.Semaphore ) -> None`
- **Source Reference**: [services/notifier.py#L121-L130](file:///home/u/Рабочий стол/para/services/notifier.py#L121-L130)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет персональное напоминание одному подписчику под контролем семафора.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |
| `text` | `str` | Input parameter |
| `lesson` | `Lesson` | Input parameter |
| `sem` | `asyncio.Semaphore` | Input parameter |

#### Step-by-Step Logic Execution
1. `kb = get_schedule_inline_kb([lesson], is_admin=(chat_id == ALLOWED_USER_ID), is_subsc`
2. `async with sem:`

---

### `send_single_reminder`
- **Signature**: `async def send_single_reminder(lesson: Lesson) -> None`
- **Source Reference**: [services/notifier.py#L133-L143](file:///home/u/Рабочий стол/para/services/notifier.py#L133-L143)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет 10-минутное напоминание о паре всем активным подписчикам конкурентно.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.info(f"Отправка напоминания для пары {lesson.period + 1}: {lesson.subject}")`
2. `text = format_reminder_text(lesson)`
3. `from db.subscribers import load_subscribers`
4. `targets = load_subscribers()`
5. `if not targets:`
6. `sem = asyncio.Semaphore(10)`

---

### `schedule_lesson_reminder`
- **Signature**: `def schedule_lesson_reminder(today: date, lesson: Lesson, now_dt: datetime) -> None`
- **Source Reference**: [services/notifier.py#L146-L165](file:///home/u/Рабочий стол/para/services/notifier.py#L146-L165)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Планирует таймер напоминания за 10 минут до пары. :param today: Дата сегодняшнего дня :param lesson: Объект пары :param now_dt: Текущее время с часовым поясом

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `today` | `date` | Input parameter |
| `lesson` | `Lesson` | Input parameter |
| `now_dt` | `datetime` | Input parameter |

#### Step-by-Step Logic Execution
1. `start_t = parse_lesson_start_time(lesson.time_str)`
2. `if not start_t:`
3. `pair_dt = datetime.combine(today, start_t, tzinfo=TIMEZONE)`
4. `remind_dt = pair_dt - timedelta(minutes=REMINDER_OFFSET_MINUTES)`
5. `if remind_dt > now_dt:`

---

### `_send_attendance_to_admin`
- **Signature**: `async def _send_attendance_to_admin( user_id: int, text: str, kb: Any, sem: asyncio.Semaphore ) -> None`
- **Source Reference**: [services/notifier.py#L168-L177](file:///home/u/Рабочий стол/para/services/notifier.py#L168-L177)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет запрос подтверждения пары старосте или замстаросты.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |
| `text` | `str` | Input parameter |
| `kb` | `Any` | Input parameter |
| `sem` | `asyncio.Semaphore` | Input parameter |

#### Step-by-Step Logic Execution
1. `async with sem:`

---

### `send_attendance_prompt`
- **Signature**: `async def send_attendance_prompt(lesson: Lesson) -> None`
- **Source Reference**: [services/notifier.py#L180-L186](file:///home/u/Рабочий стол/para/services/notifier.py#L180-L186)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет запрос подтверждения проведения пары старосте и замстаросты параллельно.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |

#### Step-by-Step Logic Execution
1. `text = format_confirm_text(lesson.number, lesson.subject, lesson.teacher or "Не указа`
2. `kb = get_lesson_confirm_kb(lesson.number)`
3. `sem = asyncio.Semaphore(5)`
4. `tasks = [_send_attendance_to_admin(uid, text, kb, sem) for uid in ALLOWED_ATTENDANCE_`
5. `await asyncio.gather(*tasks, return_exceptions=True)`

---

### `auto_close_attendance_session`
- **Signature**: `async def auto_close_attendance_session(lesson_num: int) -> None`
- **Source Reference**: [services/notifier.py#L189-L198](file:///home/u/Рабочий стол/para/services/notifier.py#L189-L198)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Автоматически закрывает неактивную сессию отметки по окончании пары.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson_num` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `if not session or session.lesson_num != lesson_num:`
3. `if session.current_idx > 0:`
4. `await clear_session()`
5. `log.info(f"Сессия посещаемости пары {lesson_num} закрыта по окончании пары")`

---

### `schedule_attendance_poll`
- **Signature**: `def schedule_attendance_poll(today: date, lesson: Lesson, now_dt: datetime) -> None`
- **Source Reference**: [services/notifier.py#L201-L215](file:///home/u/Рабочий стол/para/services/notifier.py#L201-L215)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Планирует опрос через 30 минут от старта пары и автозавершение в конце.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `today` | `date` | Input parameter |
| `lesson` | `Lesson` | Input parameter |
| `now_dt` | `datetime` | Input parameter |

#### Step-by-Step Logic Execution
1. `start_t = parse_lesson_start_time(lesson.time_str)`
2. `end_t = parse_lesson_end_time(lesson.time_str)`
3. `if not start_t or not end_t:`
4. `poll_dt = datetime.combine(today, start_t, tzinfo=TIMEZONE) + timedelta(minutes=30)`
5. `end_dt = datetime.combine(today, end_t, tzinfo=TIMEZONE)`
6. `if poll_dt > now_dt:`

---

### `daily_schedule_dispatch`
- **Signature**: `async def daily_schedule_dispatch() -> None`
- **Source Reference**: [services/notifier.py#L218-L231](file:///home/u/Рабочий стол/para/services/notifier.py#L218-L231)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Ежедневный воркер расчёта таймеров (пропускает воскресенье).

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `now_dt = datetime.now(TIMEZONE)`
2. `today = now_dt.date()`
3. `if today.weekday() == 6:`
4. `log.info(f"=== ЕЖЕДНЕВНЫЙ ФОНОВЫЙ РАСЧЁТ ТАЙМЕРОВ ({today}) ===")`
5. `lessons = await get_api_schedule_for_date(today, force_refresh=True)`
6. `for lesson in lessons:`

---

### `setup_scheduler`
- **Signature**: `def setup_scheduler() -> AsyncIOScheduler`
- **Source Reference**: [services/notifier.py#L234-L247](file:///home/u/Рабочий стол/para/services/notifier.py#L234-L247)
- **Async**: `No`
- **Return Type**: `AsyncIOScheduler`

#### Purpose & Architectural Intent
Инициализирует и запускает планировщик задач. :return: AsyncIOScheduler

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `scheduler.add_job(`
2. `scheduler.start()`
3. `log.info(f"Планировщик запущен. Ежедневная рассылка в {DAILY_NOTIFY_HOUR:02d}:{DAILY_`
4. `return scheduler`

---
