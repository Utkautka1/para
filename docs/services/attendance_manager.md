# Module Specification: `services/attendance_manager.py`
> **Path**: [`services/attendance_manager.py`](file:///home/u/Рабочий стол/para/services/attendance_manager.py)  
> **Subsystem**: `Attendance Operations`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Менеджер интерактивной сессии отметки посещаемости. Управляет состоянием опроса старосты в Redis: 1. Создаёт сессию при начале опроса пары 2. Фиксирует выбор статусов студентов (П, О, У, Н) 3. Поддерживает шаг назад и пакетную отметку оставшихся (П) 4. Сохраняет итоговые данные в Яндекс Документы через yandex_docs

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`save_session_to_redis`](#save_session_to_redis) | Function | L52–L60 | `None` | Сохраняет состояние сессии в Redis с установленным TTL. |
| [`get_active_session`](#get_active_session) | Function | L63–L77 | `AttendanceSession | None` | Извлекает активную сессию посещаемости из Redis. |
| [`clear_session`](#clear_session) | Function | L80–L85 | `None` | Удаляет активную сессию посещаемости из Redis. |
| [`_fetch_students_from_wopi`](#_fetch_students_from_wopi) | Function | L88–L96 | `list[tuple[int, str]]` | Скачивает таблицу через WOPI и считывает список студентов. |
| [`fetch_target_students`](#fetch_target_students) | Function | L99–L112 | `list[tuple[int, str]]` | Возвращает список студентов с кэшированием в Redis для мгнов |
| [`create_attendance_session`](#create_attendance_session) | Function | L116–L136 | `AttendanceSession` | Инициализирует новую сессию опроса и сохраняет в Redis. |
| [`record_student_mark`](#record_student_mark) | Function | L139–L152 | `AttendanceSession | None` | Записывает отметку для текущего студента и сдвигает указател |
| [`step_back`](#step_back) | Function | L155–L168 | `AttendanceSession | None` | Возвращает сессию на шаг назад для исправления предыдущей от |
| [`mark_all_remaining_present`](#mark_all_remaining_present) | Function | L171–L186 | `AttendanceSession | None` | Массово проставляет отметку 'П' всем оставшимся студентам. |
| [`ensure_summary_headers`](#ensure_summary_headers) | Function | L189–L203 | `None` | Гарантирует сохранение текстовых заголовков и кодов в сводны |
| [`apply_marks_to_sheet`](#apply_marks_to_sheet) | Function | L206–L209 | `None` | Применяет все собранные отметки сессии к рабочему листу open |
| [`_prepare_updated_workbook`](#_prepare_updated_workbook) | Function | L212–L223 | `Any` | Скачивает книгу и проставляет отметки сессии в колонку пары. |
| [`_try_commit_once`](#_try_commit_once) | Function | L226–L240 | `bool` | Одна попытка записи: скачать → применить отметки → загрузить |
| [`_post_commit_sync`](#_post_commit_sync) | Function | L243–L253 | `None` | Контрольная сверка реестра с Яндекс Документами после сохран |
| [`commit_session_to_table`](#commit_session_to_table) | Function | L256–L278 | `bool` | Выгружает все зафиксированные отметки сессии в Яндекс Докуме |
| [`calculate_summary_stats`](#calculate_summary_stats) | Function | L281–L287 | `dict[str, int]` | Подсчитывает итоговые количества отметок по категориям (П, О |

---

## 3. Exhaustive Function Specifications

## Class: `AttendanceSession`
Модель активной сессии отметки посещаемости пары.

### `save_session_to_redis`
- **Signature**: `async def save_session_to_redis(session: AttendanceSession) -> None`
- **Source Reference**: [services/attendance_manager.py#L52-L60](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L52-L60)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет состояние сессии в Redis с установленным TTL.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `AttendanceSession` | Input parameter |

#### Step-by-Step Logic Execution
1. `client = await get_redis()`
2. `if not client:`
3. `data = session.model_dump_json()`
4. `await client.set(REDIS_SESSION_KEY, data, ex=SESSION_TTL_SECONDS)`
5. `log.info(f"Сессия посещаемости сохранена в Redis (пара {session.lesson_num}, студент `

---

### `get_active_session`
- **Signature**: `async def get_active_session() -> AttendanceSession | None`
- **Source Reference**: [services/attendance_manager.py#L63-L77](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L63-L77)
- **Async**: `Yes`
- **Return Type**: `AttendanceSession | None`

#### Purpose & Architectural Intent
Извлекает активную сессию посещаемости из Redis.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `client = await get_redis()`
2. `if not client:`
3. `data = await client.get(REDIS_SESSION_KEY)`
4. `if not data:`
5. `try:`

---

### `clear_session`
- **Signature**: `async def clear_session() -> None`
- **Source Reference**: [services/attendance_manager.py#L80-L85](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L80-L85)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет активную сессию посещаемости из Redis.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `client = await get_redis()`
2. `if client:`

---

### `_fetch_students_from_wopi`
- **Signature**: `async def _fetch_students_from_wopi(target_date: date) -> list[tuple[int, str]]`
- **Source Reference**: [services/attendance_manager.py#L88-L96](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L88-L96)
- **Async**: `Yes`
- **Return Type**: `list[tuple[int, str]]`

#### Purpose & Architectural Intent
Скачивает таблицу через WOPI и считывает список студентов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `wopi = await init_wopi_session()`
2. `wb = await download_workbook(wopi)`
3. `sheet = get_month_sheet(wb, target_date)`
4. `students = get_students_list(sheet)`
5. `if not students:`
6. `return students`

---

### `fetch_target_students`
- **Signature**: `async def fetch_target_students(target_date: date) -> list[tuple[int, str]]`
- **Source Reference**: [services/attendance_manager.py#L99-L112](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L99-L112)
- **Async**: `Yes`
- **Return Type**: `list[tuple[int, str]]`

#### Purpose & Architectural Intent
Возвращает список студентов с кэшированием в Redis для мгновенного отклика.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `client = await get_redis()`
2. `if client:`
3. `students = await _fetch_students_from_wopi(target_date)`
4. `if client and students:`
5. `return students`

---

### `create_attendance_session`
- **Signature**: `async def create_attendance_session( target_date: date, lesson_num: int, lesson_title: str, initiator_id: int ) -> AttendanceSession`
- **Source Reference**: [services/attendance_manager.py#L116-L136](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L116-L136)
- **Async**: `Yes`
- **Return Type**: `AttendanceSession`

#### Purpose & Architectural Intent
Инициализирует новую сессию опроса и сохраняет в Redis.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date` | Input parameter |
| `lesson_num` | `int` | Input parameter |
| `lesson_title` | `str` | Input parameter |
| `initiator_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `active = await get_active_session()`
2. `if active and active.initiator_id != initiator_id:`
3. `students = await fetch_target_students(target_date)`
4. `session = AttendanceSession(`
5. `await save_session_to_redis(session)`
6. `log.info(f"Создана сессия для пары {lesson_num} ({len(students)} студентов)")`

---

### `record_student_mark`
- **Signature**: `async def record_student_mark(mark: str) -> AttendanceSession | None`
- **Source Reference**: [services/attendance_manager.py#L139-L152](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L139-L152)
- **Async**: `Yes`
- **Return Type**: `AttendanceSession | None`

#### Purpose & Architectural Intent
Записывает отметку для текущего студента и сдвигает указатель на следующего. Возвращает обновленную сессию или None, если сессия не найдена.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `mark` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `if not session or session.current_idx >= len(session.students):`
3. `row_idx, _ = session.students[session.current_idx]`
4. `session.marks[str(row_idx)] = mark`
5. `session.current_idx += 1`
6. `await save_session_to_redis(session)`

---

### `step_back`
- **Signature**: `async def step_back() -> AttendanceSession | None`
- **Source Reference**: [services/attendance_manager.py#L155-L168](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L155-L168)
- **Async**: `Yes`
- **Return Type**: `AttendanceSession | None`

#### Purpose & Architectural Intent
Возвращает сессию на шаг назад для исправления предыдущей отметки. Уменьшает индекс текущего студента на 1, если он больше 0.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `if not session or session.current_idx == 0:`
3. `session.current_idx -= 1`
4. `prev_row, _ = session.students[session.current_idx]`
5. `session.marks.pop(str(prev_row), None)`
6. `await save_session_to_redis(session)`

---

### `mark_all_remaining_present`
- **Signature**: `async def mark_all_remaining_present() -> AttendanceSession | None`
- **Source Reference**: [services/attendance_manager.py#L171-L186](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L171-L186)
- **Async**: `Yes`
- **Return Type**: `AttendanceSession | None`

#### Purpose & Architectural Intent
Массово проставляет отметку 'П' всем оставшимся студентам. Устанавливает указатель в конец списка для перехода к сохранению.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `session = await get_active_session()`
2. `if not session:`
3. `for idx in range(session.current_idx, len(session.students)):`
4. `session.current_idx = len(session.students)`
5. `await save_session_to_redis(session)`
6. `log.info(f"Оставшиеся студенты отмечены как 'П' (всего {len(session.marks)})")`

---

### `ensure_summary_headers`
- **Signature**: `def ensure_summary_headers(sheet) -> None`
- **Source Reference**: [services/attendance_manager.py#L189-L203](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L189-L203)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Гарантирует сохранение текстовых заголовков и кодов в сводных колонках. Предотвращает сброс формул кросс-листовых ссылок в пустые строки openpyxl.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `mc = sheet.max_column`
2. `if mc < 4:`
3. `sheet.cell(2, mc - 2, "Опоздавшие")`
4. `sheet.cell(3, mc - 2, "О")`
5. `sheet.cell(2, mc - 1, "отсутствие по уважительной причине")`
6. `sheet.cell(3, mc - 1, "У")`

---

### `apply_marks_to_sheet`
- **Signature**: `def apply_marks_to_sheet(sheet, session: AttendanceSession, col: int) -> None`
- **Source Reference**: [services/attendance_manager.py#L206-L209](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L206-L209)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Применяет все собранные отметки сессии к рабочему листу openpyxl.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Any` | Input parameter |
| `session` | `AttendanceSession` | Input parameter |
| `col` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `for row_str, mark in session.marks.items():`

---

### `_prepare_updated_workbook`
- **Signature**: `async def _prepare_updated_workbook( wopi, t_date: date, session: AttendanceSession )`
- **Source Reference**: [services/attendance_manager.py#L212-L223](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L212-L223)
- **Async**: `Yes`
- **Return Type**: `Any`

#### Purpose & Architectural Intent
Скачивает книгу и проставляет отметки сессии в колонку пары.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `wopi` | `Any` | Input parameter |
| `t_date` | `date` | Input parameter |
| `session` | `AttendanceSession` | Input parameter |

#### Step-by-Step Logic Execution
1. `wb = await download_workbook(wopi)`
2. `sheet = get_month_sheet(wb, t_date)`
3. `col = find_lesson_column(sheet, t_date, session.lesson_num)`
4. `if not col:`
5. `apply_marks_to_sheet(sheet, session, col)`
6. `ensure_summary_headers(sheet)`

---

### `_try_commit_once`
- **Signature**: `async def _try_commit_once(session: AttendanceSession, t_date: date) -> bool`
- **Source Reference**: [services/attendance_manager.py#L226-L240](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L226-L240)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Одна попытка записи: скачать → применить отметки → загрузить → верифицировать.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `AttendanceSession` | Input parameter |
| `t_date` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `wopi = await init_wopi_session()`
2. `wb = await _prepare_updated_workbook(wopi, t_date, session)`
3. `upload_ok = await upload_workbook(wopi, wb)`
4. `del wb`
5. `gc.collect()`
6. `if not upload_ok:`

---

### `_post_commit_sync`
- **Signature**: `async def _post_commit_sync() -> None`
- **Source Reference**: [services/attendance_manager.py#L243-L253](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L243-L253)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Контрольная сверка реестра с Яндекс Документами после сохранения.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `try:`

---

### `commit_session_to_table`
- **Signature**: `async def commit_session_to_table(session: AttendanceSession) -> bool`
- **Source Reference**: [services/attendance_manager.py#L256-L278](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L256-L278)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Выгружает все зафиксированные отметки сессии в Яндекс Документы. До MAX_COMMIT_RETRIES попыток с пересозданием WOPI-сессии. После подтвержденного сохранения сбрасывает сессию и обновляет топик.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `AttendanceSession` | Input parameter |

#### Step-by-Step Logic Execution
1. `t_date = date.fromisoformat(session.target_date)`
2. `for attempt in range(1, MAX_COMMIT_RETRIES + 1):`
3. `log.error(f"❌ Все {MAX_COMMIT_RETRIES} попытки записи пары {session.lesson_num} прова`
4. `return False`

---

### `calculate_summary_stats`
- **Signature**: `def calculate_summary_stats(marks: dict[str, str]) -> dict[str, int]`
- **Source Reference**: [services/attendance_manager.py#L281-L287](file:///home/u/Рабочий стол/para/services/attendance_manager.py#L281-L287)
- **Async**: `No`
- **Return Type**: `dict[str, int]`

#### Purpose & Architectural Intent
Подсчитывает итоговые количества отметок по категориям (П, О, У, Н).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `marks` | `dict[str, str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `stats = {"П": 0, "О": 0, "У": 0, "Н": 0}`
2. `for m in marks.values():`
3. `return stats`

---
