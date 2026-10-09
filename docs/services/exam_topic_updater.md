# Module Specification: `services/exam_topic_updater.py`
> **Path**: [`services/exam_topic_updater.py`](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py)  
> **Subsystem**: `Examination Topic`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль синхронизации и авто-обновления сообщения в топике 'Экзамены'. Сохраняет состояние EXAM_MAIN_MSG_ID в data/exam_topic_state.json. Автоматически формирует реестр экзаменов с точным расчётом дат проведения.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`get_default_semester_start`](#get_default_semester_start) | Function | L31–L35 | `date` | Вычисляет 1 сентября текущего учебного года при недоступност |
| [`get_effective_semester_start`](#get_effective_semester_start) | Function | L41–L52 | `date` | Определяет актуальную дату старта семестра из расписания КТМ |
| [`load_exam_topic_state`](#load_exam_topic_state) | Function | L55–L58 | `int | None` | Загружает ID главного сообщения топика экзаменов. |
| [`save_exam_topic_state`](#save_exam_topic_state) | Function | L61–L63 | `None` | Атомарно сохраняет ID главного сообщения топика экзаменов. |
| [`get_week_date_range_str`](#get_week_date_range_str) | Function | L66–L75 | `str` | Вычисляет диапазон дат для порядкового номера учебной недели |
| [`format_exam_card`](#format_exam_card) | Function | L78–L97 | `str` | Формирует карточку аттестации/экзамена с HTML-экранированием |
| [`format_exams_schedule_message`](#format_exams_schedule_message) | Function | L101–L111 | `str` | Форматирует расписание экзаменов и аттестаций в чистый HTML. |
| [`_pin_exam_silently`](#_pin_exam_silently) | Function | L114–L122 | `None` | Закрепляет сообщение экзаменов без уведомления. |
| [`create_exam_message`](#create_exam_message) | Function | L125–L135 | `int` | Создает и закрепляет главное сообщение в топике экзаменов. |
| [`handle_exam_edit_error`](#handle_exam_edit_error) | Function | L138–L152 | `bool` | Обрабатывает ошибку редактирования сообщения топика экзамено |
| [`send_or_edit_exam_msg`](#send_or_edit_exam_msg) | Function | L155–L173 | `bool` | Отправляет или редактирует главное сообщение в топике экзаме |
| [`recreate_exam_topic_message`](#recreate_exam_topic_message) | Function | L176–L192 | `bool` | Удаляет текущее сообщение экзаменов и создаёт новое (сброс M |
| [`sync_exam_topic_message`](#sync_exam_topic_message) | Function | L195–L212 | `bool` | Атомарно публикует или обновляет расписание экзаменов в топи |
| [`exam_topic_sync_loop`](#exam_topic_sync_loop) | Function | L215–L225 | `None` | Фоновый цикл авто-обновления топика Экзамены раз в 10 минут. |

---

## 3. Exhaustive Function Specifications

### `get_default_semester_start`
- **Signature**: `def get_default_semester_start() -> date`
- **Source Reference**: [services/exam_topic_updater.py#L31-L35](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L31-L35)
- **Async**: `No`
- **Return Type**: `date`

#### Purpose & Architectural Intent
Вычисляет 1 сентября текущего учебного года при недоступности API.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `today = datetime.now(TIMEZONE).date()`
2. `start_year = today.year if today.month >= 8 else today.year - 1`
3. `return date(start_year, 9, 1)`

---

### `get_effective_semester_start`
- **Signature**: `async def get_effective_semester_start() -> date`
- **Source Reference**: [services/exam_topic_updater.py#L41-L52](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L41-L52)
- **Async**: `Yes`
- **Return Type**: `date`

#### Purpose & Architectural Intent
Определяет актуальную дату старта семестра из расписания КТМУ.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `try:`
2. `return get_default_semester_start()`

---

### `load_exam_topic_state`
- **Signature**: `def load_exam_topic_state() -> int | None`
- **Source Reference**: [services/exam_topic_updater.py#L55-L58](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L55-L58)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Загружает ID главного сообщения топика экзаменов.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `data = sync_load_json(STATE_FILE, default={})`
2. `return data.get("main_msg_id") if isinstance(data, dict) else None`

---

### `save_exam_topic_state`
- **Signature**: `def save_exam_topic_state(msg_id: int | None) -> None`
- **Source Reference**: [services/exam_topic_updater.py#L61-L63](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L61-L63)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Атомарно сохраняет ID главного сообщения топика экзаменов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `msg_id` | `int | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})`

---

### `get_week_date_range_str`
- **Signature**: `def get_week_date_range_str(week_num: int, semester_start: date | None = None) -> str`
- **Source Reference**: [services/exam_topic_updater.py#L66-L75](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L66-L75)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Вычисляет диапазон дат для порядкового номера учебной недели.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `week_num` | `int` | Input parameter |
| `semester_start` | `date | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `start_d = semester_start or get_default_semester_start()`
2. `start_sunday = start_d + timedelta(days=(6 - start_d.weekday()))`
3. `if week_num == 1:`
4. `mon = start_sunday + timedelta(days=1) + timedelta(weeks=week_num - 2)`
5. `sun = mon + timedelta(days=6)`
6. `return f"{mon.strftime('%d.%m')}–{sun.strftime('%d.%m.%Y')}"`

---

### `format_exam_card`
- **Signature**: `def format_exam_card(ex: ExamItem, semester_start: date | None = None) -> str`
- **Source Reference**: [services/exam_topic_updater.py#L78-L97](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L78-L97)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует карточку аттестации/экзамена с HTML-экранированием.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `ex` | `ExamItem` | Input parameter |
| `semester_start` | `date | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if ex.weeks:`
2. `sg_str = f" • 👥 Подгруппа {ex.subgroup}" if ex.subgroup > 0 else ""`
3. `subj = html.escape(ex.subject)`
4. `e_type = html.escape(ex.exam_type)`
5. `teacher = html.escape(ex.teacher)`
6. `addr = html.escape(ex.address)`

---

### `format_exams_schedule_message`
- **Signature**: `def format_exams_schedule_message(exams: list[ExamItem], semester_start: date | None = None) -> str`
- **Source Reference**: [services/exam_topic_updater.py#L101-L111](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L101-L111)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Форматирует расписание экзаменов и аттестаций в чистый HTML.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `exams` | `list[ExamItem]` | Input parameter |
| `semester_start` | `date | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `header = (`
2. `if not exams:`
3. `blocks = [format_exam_card(ex, semester_start) for ex in exams]`
4. `return header + "\n\n".join(blocks)`

---

### `_pin_exam_silently`
- **Signature**: `async def _pin_exam_silently(message_id: int) -> None`
- **Source Reference**: [services/exam_topic_updater.py#L114-L122](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L114-L122)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Закрепляет сообщение экзаменов без уведомления.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `create_exam_message`
- **Signature**: `async def create_exam_message(text: str) -> int`
- **Source Reference**: [services/exam_topic_updater.py#L125-L135](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L125-L135)
- **Async**: `Yes`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Создает и закрепляет главное сообщение в топике экзаменов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `msg = await bot.send_message(`
2. `save_exam_topic_state(msg.message_id)`
3. `await _pin_exam_silently(msg.message_id)`
4. `log.info(f"Сообщение экзаменов создано и закреплено: MSG_ID={msg.message_id}")`
5. `return msg.message_id`

---

### `handle_exam_edit_error`
- **Signature**: `async def handle_exam_edit_error(text: str, err_str: str, retry: bool) -> bool`
- **Source Reference**: [services/exam_topic_updater.py#L138-L152](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L138-L152)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Обрабатывает ошибку редактирования сообщения топика экзаменов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |
| `err_str` | `str` | Input parameter |
| `retry` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _EXAM_MAIN_MSG_ID`
2. `if "not modified" in err_str:`
3. `if retry:`
4. `log.warning(f"⚠️ Ошибка редактирования exam MSG_ID={_EXAM_MAIN_MSG_ID}, пересоздаём..`
5. `_EXAM_MAIN_MSG_ID = None`
6. `save_exam_topic_state(None)`

---

### `send_or_edit_exam_msg`
- **Signature**: `async def send_or_edit_exam_msg(text: str, _retry: bool = False) -> bool`
- **Source Reference**: [services/exam_topic_updater.py#L155-L173](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L155-L173)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Отправляет или редактирует главное сообщение в топике экзаменов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |
| `_retry` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _EXAM_MAIN_MSG_ID`
2. `try:`

---

### `recreate_exam_topic_message`
- **Signature**: `async def recreate_exam_topic_message() -> bool`
- **Source Reference**: [services/exam_topic_updater.py#L176-L192](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L176-L192)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Удаляет текущее сообщение экзаменов и создаёт новое (сброс MSG_ID). :return: True если пересоздание прошло

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _EXAM_MAIN_MSG_ID`
2. `old_id = _EXAM_MAIN_MSG_ID or load_exam_topic_state()`
3. `if old_id:`
4. `_EXAM_MAIN_MSG_ID = None`
5. `save_exam_topic_state(None)`
6. `return await sync_exam_topic_message()`

---

### `sync_exam_topic_message`
- **Signature**: `async def sync_exam_topic_message() -> bool`
- **Source Reference**: [services/exam_topic_updater.py#L195-L212](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L195-L212)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Атомарно публикует или обновляет расписание экзаменов в топике. :return: True если обновлено

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _EXAM_MAIN_MSG_ID`
2. `if _EXAM_MAIN_MSG_ID is None:`
3. `exams = await get_api_exams()`
4. `sem_start = await get_effective_semester_start()`
5. `text = format_exams_schedule_message(exams, sem_start)`
6. `try:`

---

### `exam_topic_sync_loop`
- **Signature**: `async def exam_topic_sync_loop() -> None`
- **Source Reference**: [services/exam_topic_updater.py#L215-L225](file:///home/u/Рабочий стол/para/services/exam_topic_updater.py#L215-L225)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Фоновый цикл авто-обновления топика Экзамены раз в 10 минут.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `log.info("Запущен фоновый сервис авто-обновления топика Экзамены (10 мин)")`
2. `while True:`

---
