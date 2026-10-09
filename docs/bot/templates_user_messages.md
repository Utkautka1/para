# Module Specification: `bot/templates/user/messages.py`
> **Path**: [`bot/templates/user/messages.py`](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py)  
> **Subsystem**: `User Message Formatter`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль стильного и информативного форматирования сообщений бота. Формирует расписание с типом пары (Лек/Пр), точным адресом корпуса КТМУ (Цветочная ул., 8 / Вознесенский пр., 44) и реквизитами подключений.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`format_lesson_card`](#format_lesson_card) | Function | L19–L43 | `str` | Формирует подробную карточку пары с безопасным HTML-экраниро |
| [`format_minutes`](#format_minutes) | Function | L47–L60 | `str` | Преобразует общее количество минут в читаемую строку (часы и |
| [`_parse_time_interval_minutes`](#_parse_time_interval_minutes) | Function | L63–L71 | `tuple[int, int] | None` | Извлекает время начала и конца пары в минутах от начала суто |
| [`_check_single_lesson_status`](#_check_single_lesson_status) | Function | L74–L92 | `tuple[bool, str]` | Проверяет статус одной пары относительно текущего времени в  |
| [`get_lesson_status_banner`](#get_lesson_status_banner) | Function | L95–L115 | `str` | Рассчитывает и формирует статусный баннер пары для текущего  |
| [`format_day_schedule`](#format_day_schedule) | Function | L118–L136 | `str` | Собирает расписание на день в чистый HTML-блок. |
| [`format_week_lesson_loc`](#format_week_lesson_loc) | Function | L139–L144 | `str` | Формирует компактную строку локации для недельного обзора. |
| [`format_week_lesson_card`](#format_week_lesson_card) | Function | L147–L159 | `str` | Формирует отдельную карточку пары в цитате с HTML-экранирова |
| [`format_week_day_block`](#format_week_day_block) | Function | L163–L171 | `str` | Формирует блок одного учебного дня для недельного расписания |
| [`format_week_schedule`](#format_week_schedule) | Function | L174–L178 | `str` | Формирует аккуратное, структурированное расписание на неделю |
| [`format_reminder_text`](#format_reminder_text) | Function | L181–L189 | `str` | Формирует сдержанное и точное сообщение-напоминание. |
| [`format_notice_settings_text`](#format_notice_settings_text) | Function | L192–L212 | `str` | Формирует информативный текст экрана настроек уведомлений. |

---

## 3. Exhaustive Function Specifications

### `format_lesson_card`
- **Signature**: `def format_lesson_card(lesson: Lesson) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L19-L43](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L19-L43)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует подробную карточку пары с безопасным HTML-экранированием.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |

#### Step-by-Step Logic Execution
1. `subj = html.escape(lesson.subject)`
2. `teacher = html.escape(lesson.teacher)`
3. `l_type = f" ({html.escape(lesson.lesson_type)})" if lesson.lesson_type else ""`
4. `stream = " • 🔗 <b>поток</b>" if lesson.is_stream else ""`
5. `sg = f" • 👥 <b>Подгруппа {lesson.subgroup}</b>" if lesson.subgroup > 0 else ""`
6. `addr = html.escape(lesson.address)`

---

### `format_minutes`
- **Signature**: `def format_minutes(total_minutes: int) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L47-L60](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L47-L60)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Преобразует общее количество минут в читаемую строку (часы и минуты). :param total_minutes: Количество минут :return: Форматированная строка

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `total_minutes` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `hours = total_minutes // 60`
2. `mins = total_minutes % 60`
3. `if hours > 0 and mins > 0:`
4. `if hours > 0:`
5. `return f"{mins} мин"`

---

### `_parse_time_interval_minutes`
- **Signature**: `def _parse_time_interval_minutes(time_str: str) -> tuple[int, int] | None`
- **Source Reference**: [bot/templates/user/messages.py#L63-L71](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L63-L71)
- **Async**: `No`
- **Return Type**: `tuple[int, int] | None`

#### Purpose & Architectural Intent
Извлекает время начала и конца пары в минутах от начала суток.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `time_str` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `import re`
2. `matches = re.findall(r"(\d{1,2})[:\.](\d{2})", time_str)`
3. `if len(matches) >= 2:`
4. `return None`

---

### `_check_single_lesson_status`
- **Signature**: `def _check_single_lesson_status(lesson: Lesson, n_min: int) -> tuple[bool, str]`
- **Source Reference**: [bot/templates/user/messages.py#L74-L92](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L74-L92)
- **Async**: `No`
- **Return Type**: `tuple[bool, str]`

#### Purpose & Architectural Intent
Проверяет статус одной пары относительно текущего времени в минутах. :param lesson: Объект пары :param n_min: Текущее время в минутах от начала суток :return: Кортеж (найдено_ли_состояние, HTML_баннер)

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |
| `n_min` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `interval = _parse_time_interval_minutes(lesson.time_str)`
2. `if not interval:`
3. `s_min, e_min = interval`
4. `if s_min <= n_min <= e_min:`
5. `if n_min < s_min:`
6. `return False, ""`

---

### `get_lesson_status_banner`
- **Signature**: `def get_lesson_status_banner(lessons: list[Lesson], target_date: date) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L95-L115](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L95-L115)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Рассчитывает и формирует статусный баннер пары для текущего дня. :param lessons: Список пар на день :param target_date: Дата :return: HTML фрагмент со статусом пары или пустая строка

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lessons` | `list[Lesson]` | Input parameter |
| `target_date` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `from datetime import datetime`
2. `from config import TIMEZONE`
3. `now_dt = datetime.now(TIMEZONE)`
4. `if target_date != now_dt.date() or not lessons:`
5. `n_min = now_dt.time().hour * 60 + now_dt.time().minute`
6. `for l in lessons:`

---

### `format_day_schedule`
- **Signature**: `def format_day_schedule(target_date: date, lessons: list[Lesson]) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L118-L136](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L118-L136)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Собирает расписание на день в чистый HTML-блок. :param target_date: Целевая дата :param lessons: Список пар :return: Итоговый HTML текст

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date` | Input parameter |
| `lessons` | `list[Lesson]` | Input parameter |

#### Step-by-Step Logic Execution
1. `weekday_str = WEEKDAYS_RU[target_date.weekday()]`
2. `date_str = target_date.strftime("%d.%m")`
3. `header = f"<b>{GROUP_NAME} • {weekday_str}, {date_str}</b>\n"`
4. `banner = get_lesson_status_banner(lessons, target_date)`
5. `header += banner`
6. `if not lessons:`

---

### `format_week_lesson_loc`
- **Signature**: `def format_week_lesson_loc(lesson: Lesson) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L139-L144](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L139-L144)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует компактную строку локации для недельного обзора.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |

#### Step-by-Step Logic Execution
1. `if lesson.is_remote:`
2. `campus = "Вознесенский" if "вознесен" in lesson.address.lower() else "Цветочная"`
3. `return f"📍 Каб. {html.escape(lesson.room)} ({campus})"`

---

### `format_week_lesson_card`
- **Signature**: `def format_week_lesson_card(lesson: Lesson) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L147-L159](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L147-L159)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует отдельную карточку пары в цитате с HTML-экранированием.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |

#### Step-by-Step Logic Execution
1. `subj = html.escape(lesson.subject)`
2. `teacher = html.escape(lesson.teacher)`
3. `type_suffix = f" ({html.escape(lesson.lesson_type)})" if lesson.lesson_type else ""`
4. `stream_badge = " • 🔗 поток" if lesson.is_stream else ""`
5. `sg_badge = f" • 👥 {lesson.subgroup} п/г" if lesson.subgroup > 0 else ""`
6. `loc = format_week_lesson_loc(lesson)`

---

### `format_week_day_block`
- **Signature**: `def format_week_day_block(day_date: date, lessons: list[Lesson]) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L163-L171](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L163-L171)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует блок одного учебного дня для недельного расписания.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `day_date` | `date` | Input parameter |
| `lessons` | `list[Lesson]` | Input parameter |

#### Step-by-Step Logic Execution
1. `w_str = WEEKDAYS_RU[day_date.weekday()]`
2. `d_str = day_date.strftime("%d.%m")`
3. `header = f"🗓 <b>{w_str}, {d_str}</b>\n"`
4. `if not lessons:`
5. `cards = [format_week_lesson_card(l) for l in lessons]`
6. `return f"{header}" + "\n".join(cards)`

---

### `format_week_schedule`
- **Signature**: `def format_week_schedule(days_data: list[tuple[date, list[Lesson]]]) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L174-L178](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L174-L178)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует аккуратное, структурированное расписание на неделю.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `days_data` | `list[tuple[date, list[Lesson]]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `header = f"🎓 <b>РАСПИСАНИЕ НА НЕДЕЛЮ ({GROUP_NAME})</b>\n────────────────────────────`
2. `day_blocks = [format_week_day_block(d, l) for d, l in days_data]`
3. `return header + "\n\n".join(day_blocks)`

---

### `format_reminder_text`
- **Signature**: `def format_reminder_text(lesson: Lesson) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L181-L189](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L181-L189)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует сдержанное и точное сообщение-напоминание. :param lesson: Предстоящее занятие :return: HTML текст напоминания

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `lesson` | `Lesson` | Input parameter |

#### Step-by-Step Logic Execution
1. `card = format_lesson_card(lesson)`
2. `return f"⏰ <b>Через 10 минут начинается пара!</b>\n\n{card}"`

---

### `format_notice_settings_text`
- **Signature**: `def format_notice_settings_text(is_subscribed: bool) -> str`
- **Source Reference**: [bot/templates/user/messages.py#L192-L212](file:///home/u/Рабочий стол/para/bot/templates/user/messages.py#L192-L212)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует информативный текст экрана настроек уведомлений. :param is_subscribed: Статус подписки на напоминания :return: HTML-сообщение

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `is_subscribed` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `status_icon = "🔔" if is_subscribed else "🔕"`
2. `status_text = "<b>ВКЛЮЧЕНЫ</b>" if is_subscribed else "<b>ОТКЛЮЧЕНЫ</b>"`
3. `desc = (`
4. `return (`

---
