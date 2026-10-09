# Module Specification: `services/attendance_topic_updater.py`
> **Path**: [`services/attendance_topic_updater.py`](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py)  
> **Subsystem**: `Telemetry Topic`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль синхронизации и авто-обновления сообщения в топике 'Посещаемость'. Отвечает за: 1. Публикацию и закрепление академического рейтинга группы по лигам 2. Визуализацию прогресс-баров посещаемости и сквозного пульса группы 3. Сохранение идентификатора сообщения в data/attendance_topic_state.json 4. Фоновый цикл авто-обновления без лишних интерактивных кнопок в чате

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`load_attendance_topic_state`](#load_attendance_topic_state) | Function | L36–L39 | `int | None` | Загружает сохраненный ID главного сообщения топика посещаемо |
| [`save_attendance_topic_state`](#save_attendance_topic_state) | Function | L42–L44 | `None` | Атомарно сохраняет ID главного сообщения топика посещаемости |
| [`make_progress_bar`](#make_progress_bar) | Function | L47–L50 | `str` | Формирует аккуратную 4-символьную шкалу прогресса посещаемос |
| [`_format_compact_marks`](#_format_compact_marks) | Function | L53–L61 | `str` | Формирует понятные отметки, исключая оптическую иллюзию 1О - |
| [`extract_short_fio`](#extract_short_fio) | Function | L64–L69 | `str` | Извлекает Фамилию и Имя без отчества для исключения переносо |
| [`_build_student_item`](#_build_student_item) | Function | L72–L85 | `dict[str, Any]` | Преобразует сырые данные студента в структурированный элемен |
| [`_build_compact_topic_header`](#_build_compact_topic_header) | Function | L88–L96 | `str` | Формирует презентабельную компактную шапку дашборда группы. |
| [`_decline_absence`](#_decline_absence) | Function | L99–L108 | `str` | Склоняет слово 'прогул' по грамматическим правилам русского  |
| [`_format_debt_details`](#_format_debt_details) | Function | L111–L120 | `str` | Формирует понятный список причин (прогулы, опоздания, справк |
| [`_format_debt_student`](#_format_debt_student) | Function | L123–L133 | `str` | Формирует строку студента, имеющего пропуски или опоздания. |
| [`_format_perfect_student`](#_format_perfect_student) | Function | L136–L141 | `str` | Формирует аккуратную строку отличника без лишнего визуальног |
| [`_build_topic_footer`](#_build_topic_footer) | Function | L144–L151 | `str` | Формирует подвал сообщения со ссылкой на ЛС и временем обнов |
| [`format_attendance_topic_message`](#format_attendance_topic_message) | Function | L154–L172 | `str` | Формирует дашборд с компактным блоком отличников и журналом  |
| [`_pin_attendance_silently`](#_pin_attendance_silently) | Function | L175–L183 | `None` | Закрепляет главное сообщение реестра в топике без звукового  |
| [`create_attendance_message`](#create_attendance_message) | Function | L186–L196 | `int` | Создает и закрепляет главное сообщение в топике посещаемости |
| [`handle_attendance_edit_error`](#handle_attendance_edit_error) | Function | L199–L211 | `bool` | Обрабатывает ошибки обновления сообщения в топике (not modif |
| [`send_or_edit_attendance_msg`](#send_or_edit_attendance_msg) | Function | L214–L232 | `bool` | Отправляет или обновляет главное сообщение в топике посещаем |
| [`recreate_attendance_topic_message`](#recreate_attendance_topic_message) | Function | L235–L247 | `bool` | Удаляет старое сообщение топика посещаемости и создаёт новое |
| [`sync_attendance_topic_message`](#sync_attendance_topic_message) | Function | L250–L265 | `bool` | Синхронизирует данные из таблицы и обновляет сообщение в топ |
| [`_get_attendance_sync_sleep_seconds`](#_get_attendance_sync_sleep_seconds) | Function | L268–L273 | `int` | Определяет интервал: 3 мин в учебные часы (08-19), иначе 15  |
| [`attendance_topic_sync_loop`](#attendance_topic_sync_loop) | Function | L276–L285 | `None` | Фоновый цикл авто-обновления топика с адаптивным интервалом. |

---

## 3. Exhaustive Function Specifications

### `load_attendance_topic_state`
- **Signature**: `def load_attendance_topic_state() -> int | None`
- **Source Reference**: [services/attendance_topic_updater.py#L36-L39](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L36-L39)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Загружает сохраненный ID главного сообщения топика посещаемости.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `data = sync_load_json(STATE_FILE, default={})`
2. `return data.get("main_msg_id") if isinstance(data, dict) else None`

---

### `save_attendance_topic_state`
- **Signature**: `def save_attendance_topic_state(msg_id: int | None) -> None`
- **Source Reference**: [services/attendance_topic_updater.py#L42-L44](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L42-L44)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Атомарно сохраняет ID главного сообщения топика посещаемости.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `msg_id` | `int | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})`

---

### `make_progress_bar`
- **Signature**: `def make_progress_bar(pct: float) -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L47-L50](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L47-L50)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует аккуратную 4-символьную шкалу прогресса посещаемости.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `pct` | `float` | Input parameter |

#### Step-by-Step Logic Execution
1. `filled = max(0, min(4, round(pct / 25.0)))`
2. `return "▰" * filled + "▱" * (4 - filled)`

---

### `_format_compact_marks`
- **Signature**: `def _format_compact_marks(p: int, o: int, u: int, n: int) -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L53-L61](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L53-L61)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует понятные отметки, исключая оптическую иллюзию 1О -> 10.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `p` | `int` | Input parameter |
| `o` | `int` | Input parameter |
| `u` | `int` | Input parameter |
| `n` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `parts = [f"{p}П"]`
2. `if o > 0:`
3. `if u > 0:`
4. `parts.append(f"{n}Н")`
5. `return " · ".join(parts)`

---

### `extract_short_fio`
- **Signature**: `def extract_short_fio(fio: str) -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L64-L69](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L64-L69)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Извлекает Фамилию и Имя без отчества для исключения переносов строк.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `fio` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `parts = fio.split()`
2. `if len(parts) >= 2:`
3. `return fio`

---

### `_build_student_item`
- **Signature**: `def _build_student_item(fio: str, data: dict[str, Any]) -> dict[str, Any]`
- **Source Reference**: [services/attendance_topic_updater.py#L72-L85](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L72-L85)
- **Async**: `No`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Преобразует сырые данные студента в структурированный элемент рейтинга.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `fio` | `str` | Input parameter |
| `data` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `tot = data.get("total", {})`
2. `p, o = tot.get("П", 0), tot.get("О", 0)`
3. `u, n = tot.get("У", 0), tot.get("Н", 0)`
4. `total_classes = p + o + u + n`
5. `valid_classes = p + o + u`
6. `pct = (valid_classes / total_classes * 100.0) if total_classes > 0 else 100.0`

---

### `_build_compact_topic_header`
- **Signature**: `def _build_compact_topic_header(pulse: float, total: int, p_cnt: int, d_cnt: int) -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L88-L96](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L88-L96)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует презентабельную компактную шапку дашборда группы.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `pulse` | `float` | Input parameter |
| `total` | `int` | Input parameter |
| `p_cnt` | `int` | Input parameter |
| `d_cnt` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `return (`

---

### `_decline_absence`
- **Signature**: `def _decline_absence(n: int) -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L99-L108](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L99-L108)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Склоняет слово 'прогул' по грамматическим правилам русского языка.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `n` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if 11 <= (n % 100) <= 14:`
2. `rem = n % 10`
3. `if rem == 1:`
4. `if 2 <= rem <= 4:`
5. `return f"{n} прогулов"`

---

### `_format_debt_details`
- **Signature**: `def _format_debt_details(s: dict[str, Any]) -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L111-L120](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L111-L120)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует понятный список причин (прогулы, опоздания, справки).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `s` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `parts = []`
2. `if s["n"] > 0:`
3. `if s["o"] > 0:`
4. `if s["u"] > 0:`
5. `return ", ".join(parts) if parts else "без замечаний"`

---

### `_format_debt_student`
- **Signature**: `def _format_debt_student(s: dict[str, Any]) -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L123-L133](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L123-L133)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует строку студента, имеющего пропуски или опоздания.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `s` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `details = _format_debt_details(s)`
2. `clean_fio = html.escape(s["fio"])`
3. `if s["pct"] == 0 or s["n"] >= 12:`
4. `return f"{icon} <b>{clean_fio}</b> — <b>{s['pct']:.0f}%</b> ({details})"`

---

### `_format_perfect_student`
- **Signature**: `def _format_perfect_student(s: dict[str, Any]) -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L136-L141](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L136-L141)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует аккуратную строку отличника без лишнего визуального шума.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `s` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `clean_fio = html.escape(s["fio"])`
2. `if s["u"] > 0:`
3. `return f"• <b>{clean_fio}</b>"`

---

### `_build_topic_footer`
- **Signature**: `def _build_topic_footer() -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L144-L151](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L144-L151)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует подвал сообщения со ссылкой на ЛС и временем обновления.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `now_str = datetime.now(TIMEZONE).strftime("%H:%M")`
2. `return (`

---

### `format_attendance_topic_message`
- **Signature**: `def format_attendance_topic_message(stats: dict[str, dict[str, Any]]) -> str`
- **Source Reference**: [services/attendance_topic_updater.py#L154-L172](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L154-L172)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует дашборд с компактным блоком отличников и журналом долгов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `stats` | `dict[str, dict[str, Any]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not stats:`
2. `items = [_build_student_item(fio, d) for fio, d in stats.items()]`
3. `perfect = [s for s in items if s["n"] == 0 and s["o"] == 0]`
4. `debts = [s for s in items if s["n"] > 0 or s["o"] > 0]`
5. `perfect.sort(key=lambda s: s["fio"])`
6. `debts.sort(key=lambda s: (-s["pct"], -s["n"], s["fio"]))`

---

### `_pin_attendance_silently`
- **Signature**: `async def _pin_attendance_silently(message_id: int) -> None`
- **Source Reference**: [services/attendance_topic_updater.py#L175-L183](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L175-L183)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Закрепляет главное сообщение реестра в топике без звукового уведомления.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `create_attendance_message`
- **Signature**: `async def create_attendance_message(text: str) -> int`
- **Source Reference**: [services/attendance_topic_updater.py#L186-L196](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L186-L196)
- **Async**: `Yes`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Создает и закрепляет главное сообщение в топике посещаемости.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `msg = await bot.send_message(`
2. `save_attendance_topic_state(msg.message_id)`
3. `await _pin_attendance_silently(msg.message_id)`
4. `log.info(f"Сообщение реестра посещаемости создано: MSG_ID={msg.message_id}")`
5. `return msg.message_id`

---

### `handle_attendance_edit_error`
- **Signature**: `async def handle_attendance_edit_error(text: str, err_str: str, retry: bool) -> bool`
- **Source Reference**: [services/attendance_topic_updater.py#L199-L211](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L199-L211)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Обрабатывает ошибки обновления сообщения в топике (not modified / удалено).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |
| `err_str` | `str` | Input parameter |
| `retry` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _ATT_MAIN_MSG_ID`
2. `if "not modified" in err_str:`
3. `if retry:`
4. `log.warning(f"⚠️ Ошибка редактирования attendance MSG_ID={_ATT_MAIN_MSG_ID}, пересозд`
5. `_ATT_MAIN_MSG_ID = None`
6. `save_attendance_topic_state(None)`

---

### `send_or_edit_attendance_msg`
- **Signature**: `async def send_or_edit_attendance_msg(text: str, _retry: bool = False) -> bool`
- **Source Reference**: [services/attendance_topic_updater.py#L214-L232](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L214-L232)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Отправляет или обновляет главное сообщение в топике посещаемости.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |
| `_retry` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _ATT_MAIN_MSG_ID`
2. `try:`

---

### `recreate_attendance_topic_message`
- **Signature**: `async def recreate_attendance_topic_message() -> bool`
- **Source Reference**: [services/attendance_topic_updater.py#L235-L247](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L235-L247)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Удаляет старое сообщение топика посещаемости и создаёт новое.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _ATT_MAIN_MSG_ID`
2. `old_id = _ATT_MAIN_MSG_ID or load_attendance_topic_state()`
3. `if old_id:`
4. `_ATT_MAIN_MSG_ID = None`
5. `save_attendance_topic_state(None)`
6. `return await sync_attendance_topic_message(force_refresh=True)`

---

### `sync_attendance_topic_message`
- **Signature**: `async def sync_attendance_topic_message(force_refresh: bool = False) -> bool`
- **Source Reference**: [services/attendance_topic_updater.py#L250-L265](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L250-L265)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Синхронизирует данные из таблицы и обновляет сообщение в топике с локом.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _ATT_MAIN_MSG_ID`
2. `if _ATT_MAIN_MSG_ID is None:`
3. `async with redis_lock("att:lock:topic_sync", ttl=20) as acquired:`

---

### `_get_attendance_sync_sleep_seconds`
- **Signature**: `def _get_attendance_sync_sleep_seconds() -> int`
- **Source Reference**: [services/attendance_topic_updater.py#L268-L273](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L268-L273)
- **Async**: `No`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Определяет интервал: 3 мин в учебные часы (08-19), иначе 15 мин.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `now = datetime.now(TIMEZONE)`
2. `if 8 <= now.hour < 19 and now.weekday() < 6:`
3. `return ATTENDANCE_SYNC_NIGHT_INTERVAL_SECONDS`

---

### `attendance_topic_sync_loop`
- **Signature**: `async def attendance_topic_sync_loop() -> None`
- **Source Reference**: [services/attendance_topic_updater.py#L276-L285](file:///home/u/Рабочий стол/para/services/attendance_topic_updater.py#L276-L285)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Фоновый цикл авто-обновления топика с адаптивным интервалом.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `log.info("Запущен адаптивный фоновый сервис авто-обновления топика Посещаемость")`
2. `while True:`

---
