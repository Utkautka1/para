# Module Specification: `services/attendance_stats.py`
> **Path**: [`services/attendance_stats.py`](file:///home/u/Рабочий стол/para/services/attendance_stats.py)  
> **Subsystem**: `Spreadsheet Analytics`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Сервис агрегации сквозной статистики посещаемости студентов. Отвечает за: 1. Выгрузку и обход всех доступных месяцев (СЕНТ, ОКТ, ...) в таблице Яндекс Документов 2. Подсчёт суммарных отметок (П, О, У, Н) по каждому студенту за всё время 3. Кэширование агрегированных данных в Redis для мгновенного отклика UI и топика 4. Формирование персонализированной аналитики для команды /my_attendance

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_init_student_stat`](#_init_student_stat) | Function | L33–L39 | `dict[str, Any]` | Инициализирует структуру счетчиков посещаемости студента. |
| [`_count_row_marks`](#_count_row_marks) | Function | L42–L52 | `dict[str, int]` | Подсчитывает отметки посещаемости студента в строке конкретн |
| [`_aggregate_sheet_stats`](#_aggregate_sheet_stats) | Function | L55–L72 | `None` | Обрабатывает один лист месяца и накапливает отметки в общий  |
| [`parse_workbook_attendance`](#parse_workbook_attendance) | Function | L75–L84 | `dict[str, dict[str, Any]]` | Извлекает отметки всех студентов по всем месяцам из книги op |
| [`_load_from_redis_cache`](#_load_from_redis_cache) | Function | L87–L96 | `dict[str, dict[str, Any]] | None` | Считывает закэшированную статистику из Redis. |
| [`_save_to_redis_cache`](#_save_to_redis_cache) | Function | L99–L106 | `None` | Сохраняет структуру статистики в Redis с TTL 1 час. |
| [`invalidate_attendance_stats_cache`](#invalidate_attendance_stats_cache) | Function | L109–L112 | `None` | Принудительно сбрасывает кэш сквозной статистики посещаемост |
| [`fetch_all_time_attendance`](#fetch_all_time_attendance) | Function | L115–L128 | `dict[str, dict[str, Any]]` | Возвращает сквозную статистику посещаемости с Redis-кэширова |
| [`find_student_attendance`](#find_student_attendance) | Function | L131–L146 | `dict[str, Any] | None` | Находит статистику студента по точному или частичному совпад |
| [`_adjust_student_counts`](#_adjust_student_counts) | Function | L149–L155 | `None` | Корректирует счетчики студента с учетом замены старой отметк |
| [`_get_saved_lesson_marks`](#_get_saved_lesson_marks) | Function | L158–L166 | `dict[str, str]` | Считывает ранее сохраненный срез отметок пары из Redis. |
| [`_save_lesson_marks`](#_save_lesson_marks) | Function | L169–L172 | `None` | Сохраняет срез отметок пары в Redis с настроенным TTL для за |
| [`apply_session_optimistic_update`](#apply_session_optimistic_update) | Function | L175–L190 | `dict[str, dict[str, Any]]` | Мгновенно обновляет кэш статистики в Redis на основе отметок |

---

## 3. Exhaustive Function Specifications

### `_init_student_stat`
- **Signature**: `def _init_student_stat(fio: str) -> dict[str, Any]`
- **Source Reference**: [services/attendance_stats.py#L33-L39](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L33-L39)
- **Async**: `No`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Инициализирует структуру счетчиков посещаемости студента.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `fio` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `return {`

---

### `_count_row_marks`
- **Signature**: `def _count_row_marks(sheet: Worksheet, row: int, mc: int) -> dict[str, int]`
- **Source Reference**: [services/attendance_stats.py#L42-L52](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L42-L52)
- **Async**: `No`
- **Return Type**: `dict[str, int]`

#### Purpose & Architectural Intent
Подсчитывает отметки посещаемости студента в строке конкретного месяца.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Worksheet` | Input parameter |
| `row` | `int` | Input parameter |
| `mc` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `row_counts = {"П": 0, "О": 0, "У": 0, "Н": 0}`
2. `for col in range(3, mc + 1):`
3. `return row_counts`

---

### `_aggregate_sheet_stats`
- **Signature**: `def _aggregate_sheet_stats( sheet: Worksheet, s_name: str, stats: dict[str, dict[str, Any]] ) -> None`
- **Source Reference**: [services/attendance_stats.py#L55-L72](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L55-L72)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Обрабатывает один лист месяца и накапливает отметки в общий реестр.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Worksheet` | Input parameter |
| `s_name` | `str` | Input parameter |
| `stats` | `dict[str, dict[str, Any]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `mc = sheet.max_column`
2. `for r in range(5, 45):`

---

### `parse_workbook_attendance`
- **Signature**: `def parse_workbook_attendance(wb: openpyxl.Workbook) -> dict[str, dict[str, Any]]`
- **Source Reference**: [services/attendance_stats.py#L75-L84](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L75-L84)
- **Async**: `No`
- **Return Type**: `dict[str, dict[str, Any]]`

#### Purpose & Architectural Intent
Извлекает отметки всех студентов по всем месяцам из книги openpyxl.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `wb` | `openpyxl.Workbook` | Input parameter |

#### Step-by-Step Logic Execution
1. `stats: dict[str, dict[str, Any]] = {}`
2. `valid_months = set(MONTH_SHEET_MAP.values())`
3. `for s_name in wb.sheetnames:`
4. `log.info(f"Собрана статистика посещаемости для {len(stats)} студентов")`
5. `return stats`

---

### `_load_from_redis_cache`
- **Signature**: `async def _load_from_redis_cache() -> dict[str, dict[str, Any]] | None`
- **Source Reference**: [services/attendance_stats.py#L87-L96](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L87-L96)
- **Async**: `Yes`
- **Return Type**: `dict[str, dict[str, Any]] | None`

#### Purpose & Architectural Intent
Считывает закэшированную статистику из Redis.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `cached = await cache_get(REDIS_STATS_KEY)`
2. `if not cached:`
3. `try:`

---

### `_save_to_redis_cache`
- **Signature**: `async def _save_to_redis_cache(stats: dict[str, dict[str, Any]]) -> None`
- **Source Reference**: [services/attendance_stats.py#L99-L106](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L99-L106)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет структуру статистики в Redis с TTL 1 час.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `stats` | `dict[str, dict[str, Any]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `invalidate_attendance_stats_cache`
- **Signature**: `async def invalidate_attendance_stats_cache() -> None`
- **Source Reference**: [services/attendance_stats.py#L109-L112](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L109-L112)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Принудительно сбрасывает кэш сквозной статистики посещаемости.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `await cache_flush(f"{REDIS_STATS_KEY}*")`
2. `log.info("Кэш сквозной статистики посещаемости сброшен")`

---

### `fetch_all_time_attendance`
- **Signature**: `async def fetch_all_time_attendance( force_refresh: bool = False ) -> dict[str, dict[str, Any]]`
- **Source Reference**: [services/attendance_stats.py#L115-L128](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L115-L128)
- **Async**: `Yes`
- **Return Type**: `dict[str, dict[str, Any]]`

#### Purpose & Architectural Intent
Возвращает сквозную статистику посещаемости с Redis-кэшированием.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not force_refresh:`
2. `log.info("Загрузка и пересчёт статистики посещаемости из Яндекс Документов...")`
3. `wopi = await init_wopi_session()`
4. `wb = await download_workbook(wopi)`
5. `stats = await asyncio.to_thread(parse_workbook_attendance, wb)`
6. `await _save_to_redis_cache(stats)`

---

### `find_student_attendance`
- **Signature**: `def find_student_attendance( stats: dict[str, dict[str, Any]], target_name: str ) -> dict[str, Any] | None`
- **Source Reference**: [services/attendance_stats.py#L131-L146](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L131-L146)
- **Async**: `No`
- **Return Type**: `dict[str, Any] | None`

#### Purpose & Architectural Intent
Находит статистику студента по точному или частичному совпадению ФИО.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `stats` | `dict[str, dict[str, Any]]` | Input parameter |
| `target_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `target_clean = normalize_fio(target_name).lower()`
2. `for fio, data in stats.items():`
3. `parts = target_clean.split()`
4. `if parts:`
5. `return None`

---

### `_adjust_student_counts`
- **Signature**: `def _adjust_student_counts(stat: dict[str, Any], old_mark: str | None, new_mark: str) -> None`
- **Source Reference**: [services/attendance_stats.py#L149-L155](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L149-L155)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Корректирует счетчики студента с учетом замены старой отметки на новую.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `stat` | `dict[str, Any]` | Input parameter |
| `old_mark` | `str | None` | Input parameter |
| `new_mark` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `tot = stat.setdefault("total", {"П": 0, "О": 0, "У": 0, "Н": 0})`
2. `if old_mark and old_mark in tot and tot[old_mark] > 0:`
3. `if new_mark in tot:`

---

### `_get_saved_lesson_marks`
- **Signature**: `async def _get_saved_lesson_marks(t_date: str, l_num: int) -> dict[str, str]`
- **Source Reference**: [services/attendance_stats.py#L158-L166](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L158-L166)
- **Async**: `Yes`
- **Return Type**: `dict[str, str]`

#### Purpose & Architectural Intent
Считывает ранее сохраненный срез отметок пары из Redis.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `t_date` | `str` | Input parameter |
| `l_num` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `raw = await cache_get(f"{REDIS_MARKS_CACHE_PREFIX}:{t_date}:{l_num}")`
2. `if not raw:`
3. `try:`

---

### `_save_lesson_marks`
- **Signature**: `async def _save_lesson_marks(t_date: str, l_num: int, marks: dict[str, str]) -> None`
- **Source Reference**: [services/attendance_stats.py#L169-L172](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L169-L172)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет срез отметок пары в Redis с настроенным TTL для защиты от задвоений.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `t_date` | `str` | Input parameter |
| `l_num` | `int` | Input parameter |
| `marks` | `dict[str, str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `payload = json.dumps(marks, ensure_ascii=False)`
2. `await cache_set(f"{REDIS_MARKS_CACHE_PREFIX}:{t_date}:{l_num}", payload, ttl=MARKS_CA`

---

### `apply_session_optimistic_update`
- **Signature**: `async def apply_session_optimistic_update(session: Any) -> dict[str, dict[str, Any]]`
- **Source Reference**: [services/attendance_stats.py#L175-L190](file:///home/u/Рабочий стол/para/services/attendance_stats.py#L175-L190)
- **Async**: `Yes`
- **Return Type**: `dict[str, dict[str, Any]]`

#### Purpose & Architectural Intent
Мгновенно обновляет кэш статистики в Redis на основе отметок сессии.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `stats = await fetch_all_time_attendance(force_refresh=False)`
2. `saved_marks = await _get_saved_lesson_marks(session.target_date, session.lesson_num)`
3. `new_saved_marks = dict(saved_marks)`
4. `for row_idx, fio in session.students:`
5. `await _save_lesson_marks(session.target_date, session.lesson_num, new_saved_marks)`
6. `await _save_to_redis_cache(stats)`

---
