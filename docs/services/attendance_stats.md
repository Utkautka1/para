# Component Reference: `services/attendance_stats.py`
> **File Path**: [`services/attendance_stats.py`](../../services/attendance_stats.py)
> **Subsystem**: `Spreadsheet Analytics`

## 1. Purpose
Сервис агрегации сквозной статистики посещаемости студентов.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_init_student_stat`](#_init_student_stat) | Function | L39–L52 | `dict[str, Any]` | Инициализирует базовую структуру счетчиков посещаемости... |
| [`_count_row_marks`](#_count_row_marks) | Function | L55–L72 | `dict[str, int]` | Подсчитывает отметки посещаемости студента в строке кон... |
| [`_process_student_row`](#_process_student_row) | Function | L75–L95 | `None` | Извлекает и суммирует отметки одного студента из конкре... |
| [`_aggregate_sheet_stats`](#_aggregate_sheet_stats) | Function | L98–L109 | `None` | Обрабатывает один лист месяца и накапливает отметки в о... |
| [`parse_workbook_attendance`](#parse_workbook_attendance) | Function | L112–L128 | `dict[str, dict[str, Any]]` | Извлекает отметки всех студентов по всем месяцам из кни... |
| [`_load_from_redis_cache`](#_load_from_redis_cache) | Function | L131–L147 | `dict[str, dict[str, Any]] \| None` | Считывает закэшированную сквозную статистику посещаемос... |
| [`_save_to_redis_cache`](#_save_to_redis_cache) | Function | L150–L164 | `None` | Сохраняет структуру статистики в Redis с настроенным вр... |
| [`invalidate_attendance_stats_cache`](#invalidate_attendance_stats_cache) | Function | L167–L178 | `None` | Принудительно инвалидирует кэш сквозной статистики и ли... |
| [`_build_snapshot_record`](#_build_snapshot_record) | Function | L181–L195 | `dict[str, Any]` | Формирует нормализованную запись посещаемости для сохра... |
| [`_save_sqlite_snapshot`](#_save_sqlite_snapshot) | Function | L198–L210 | `None` | Сохраняет срез посещаемости в SQLite и локальный дисков... |
| [`_extract_snapshot_dict`](#_extract_snapshot_dict) | Function | L213–L225 | `dict[str, dict[str, Any]]` | Преобразует объекты AttendanceSnapshot в словарь сквозн... |
| [`_load_sqlite_snapshot`](#_load_sqlite_snapshot) | Function | L228–L242 | `dict[str, dict[str, Any]] \| None` | Восстанавливает срез посещаемости из локального кэша ил... |
| [`_download_and_cache_fresh_stats`](#_download_and_cache_fresh_stats) | Function | L248–L261 | `dict[str, dict[str, Any]]` | Загружает актуальный XLSX-файл из Яндекса и кэширует в ... |
| [`_trigger_background_attendance_refresh`](#_trigger_background_attendance_refresh) | Function | L264–L276 | `None` | Запускает обновление посещаемости в фоновом режиме без ... |
| [`_fetch_with_sync_lock`](#_fetch_with_sync_lock) | Function | L279–L292 | `dict[str, dict[str, Any]]` | Синхронизированная загрузка актуальной посещаемости с з... |
| [`fetch_all_time_attendance`](#fetch_all_time_attendance) | Function | L295–L309 | `dict[str, dict[str, Any]]` | Возвращает сквозную статистику посещаемости по стратеги... |
| [`find_student_attendance`](#find_student_attendance) | Function | L312–L332 | `dict[str, Any] \| None` | Находит статистику студента по точному или частичному с... |
| [`_adjust_student_counts`](#_adjust_student_counts) | Function | L335–L348 | `None` | Корректирует счетчики студента с учетом замены старой о... |
| [`_get_saved_lesson_marks`](#_get_saved_lesson_marks) | Function | L351–L365 | `dict[str, str]` | Считывает ранее сохраненный срез отметок пары из Redis. |
| [`_save_lesson_marks`](#_save_lesson_marks) | Function | L368–L377 | `None` | Сохраняет срез отметок пары в Redis с настроенным TTL д... |
| [`_update_session_marks_in_stats`](#_update_session_marks_in_stats) | Function | L380–L398 | `dict[str, str]` | Применяет новые отметки студентов из интерактивной сесс... |
| [`apply_session_optimistic_update`](#apply_session_optimistic_update) | Function | L401–L416 | `dict[str, dict[str, Any]]` | Мгновенно обновляет кэш статистики в Redis на основе от... |

---

## 3. Comprehensive Function Specifications

### `_init_student_stat`
```python
def _init_student_stat(fio: str) -> dict[str, Any]
```

- **Source Reference**: [`services/attendance_stats.py#L39-L52`](../../services/attendance_stats.py#L39-L52)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Инициализирует базовую структуру счетчиков посещаемости для одного студента.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _init_student_stat

# Execute call
result = _init_student_stat(fio=...)
```

---

### `_count_row_marks`
```python
def _count_row_marks(sheet: Worksheet, row: int, mc: int) -> dict[str, int]
```

- **Source Reference**: [`services/attendance_stats.py#L55-L72`](../../services/attendance_stats.py#L55-L72)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, int]`

#### Overview & Architectural Purpose
Подсчитывает отметки посещаемости студента в строке конкретного месяца.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `row` | `int` | Yes | Parameter `row` of type `int`. |
| `mc` | `int` | Yes | Parameter `mc` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _count_row_marks

# Execute call
result = _count_row_marks(sheet=..., row=..., mc=...)
```

---

### `_process_student_row`
```python
def _process_student_row(sheet: Worksheet, r: int, mc: int, s_name: str, stats: dict[str, dict[str, Any]]) -> None
```

- **Source Reference**: [`services/attendance_stats.py#L75-L95`](../../services/attendance_stats.py#L75-L95)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Извлекает и суммирует отметки одного студента из конкретной строки таблицы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `r` | `int` | Yes | Parameter `r` of type `int`. |
| `mc` | `int` | Yes | Parameter `mc` of type `int`. |
| `s_name` | `str` | Yes | Parameter `s_name` of type `str`. |
| `stats` | `dict[str, dict[str, Any]]` | Yes | Parameter `stats` of type `dict[str, dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _process_student_row

# Execute call
result = _process_student_row(sheet=..., r=..., mc=...)
```

---

### `_aggregate_sheet_stats`
```python
def _aggregate_sheet_stats(sheet: Worksheet, s_name: str, stats: dict[str, dict[str, Any]]) -> None
```

- **Source Reference**: [`services/attendance_stats.py#L98-L109`](../../services/attendance_stats.py#L98-L109)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Обрабатывает один лист месяца и накапливает отметки в общий реестр.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sheet` | `Worksheet` | Yes | Parameter `sheet` of type `Worksheet`. |
| `s_name` | `str` | Yes | Parameter `s_name` of type `str`. |
| `stats` | `dict[str, dict[str, Any]]` | Yes | Parameter `stats` of type `dict[str, dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _aggregate_sheet_stats

# Execute call
result = _aggregate_sheet_stats(sheet=..., s_name=..., stats=...)
```

---

### `parse_workbook_attendance`
```python
def parse_workbook_attendance(wb: openpyxl.Workbook) -> dict[str, dict[str, Any]]
```

- **Source Reference**: [`services/attendance_stats.py#L112-L128`](../../services/attendance_stats.py#L112-L128)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, dict[str, Any]]`

#### Overview & Architectural Purpose
Извлекает отметки всех студентов по всем месяцам из книги openpyxl.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `wb` | `openpyxl.Workbook` | Yes | Openpyxl workbook instance containing academic attendance sheets. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import parse_workbook_attendance

# Execute call
result = parse_workbook_attendance(wb=...)
```

---

### `_load_from_redis_cache`
```python
async def _load_from_redis_cache() -> dict[str, dict[str, Any]] | None
```

- **Source Reference**: [`services/attendance_stats.py#L131-L147`](../../services/attendance_stats.py#L131-L147)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, dict[str, Any]] | None`

#### Overview & Architectural Purpose
Считывает закэшированную сквозную статистику посещаемости из Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_stats import _load_from_redis_cache

# Execute call
result = await _load_from_redis_cache()
```

---

### `_save_to_redis_cache`
```python
async def _save_to_redis_cache(stats: dict[str, dict[str, Any]]) -> None
```

- **Source Reference**: [`services/attendance_stats.py#L150-L164`](../../services/attendance_stats.py#L150-L164)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сохраняет структуру статистики в Redis с настроенным временем жизни TTL.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `stats` | `dict[str, dict[str, Any]]` | Yes | Parameter `stats` of type `dict[str, dict[str, Any]]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_stats import _save_to_redis_cache

# Execute call
result = await _save_to_redis_cache(stats=...)
```

---

### `invalidate_attendance_stats_cache`
```python
async def invalidate_attendance_stats_cache() -> None
```

- **Source Reference**: [`services/attendance_stats.py#L167-L178`](../../services/attendance_stats.py#L167-L178)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Принудительно инвалидирует кэш сквозной статистики и лидерборда в Redis.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import invalidate_attendance_stats_cache

# Execute call
result = await invalidate_attendance_stats_cache()
```

---

### `_build_snapshot_record`
```python
def _build_snapshot_record(name: str, data: dict[str, Any]) -> dict[str, Any]
```

- **Source Reference**: [`services/attendance_stats.py#L181-L195`](../../services/attendance_stats.py#L181-L195)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any]`

#### Overview & Architectural Purpose
Формирует нормализованную запись посещаемости для сохранения в БД.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` | Yes | Parameter `name` of type `str`. |
| `data` | `dict[str, Any]` | Yes | Parameter `data` of type `dict[str, Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _build_snapshot_record

# Execute call
result = _build_snapshot_record(name=..., data=...)
```

---

### `_save_sqlite_snapshot`
```python
async def _save_sqlite_snapshot(stats: dict[str, dict[str, Any]]) -> None
```

- **Source Reference**: [`services/attendance_stats.py#L198-L210`](../../services/attendance_stats.py#L198-L210)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сохраняет срез посещаемости в SQLite и локальный дисковый кэш.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `stats` | `dict[str, dict[str, Any]]` | Yes | Parameter `stats` of type `dict[str, dict[str, Any]]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_stats import _save_sqlite_snapshot

# Execute call
result = await _save_sqlite_snapshot(stats=...)
```

---

### `_extract_snapshot_dict`
```python
def _extract_snapshot_dict(snapshots: list[Any]) -> dict[str, dict[str, Any]]
```

- **Source Reference**: [`services/attendance_stats.py#L213-L225`](../../services/attendance_stats.py#L213-L225)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, dict[str, Any]]`

#### Overview & Architectural Purpose
Преобразует объекты AttendanceSnapshot в словарь сквозной посещаемости.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `snapshots` | `list[Any]` | Yes | Parameter `snapshots` of type `list[Any]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _extract_snapshot_dict

# Execute call
result = _extract_snapshot_dict(snapshots=...)
```

---

### `_load_sqlite_snapshot`
```python
async def _load_sqlite_snapshot() -> dict[str, dict[str, Any]] | None
```

- **Source Reference**: [`services/attendance_stats.py#L228-L242`](../../services/attendance_stats.py#L228-L242)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, dict[str, Any]] | None`

#### Overview & Architectural Purpose
Восстанавливает срез посещаемости из локального кэша или SQLite при недоступности Яндекса.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_stats import _load_sqlite_snapshot

# Execute call
result = await _load_sqlite_snapshot()
```

---

### `_download_and_cache_fresh_stats`
```python
async def _download_and_cache_fresh_stats() -> dict[str, dict[str, Any]]
```

- **Source Reference**: [`services/attendance_stats.py#L248-L261`](../../services/attendance_stats.py#L248-L261)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, dict[str, Any]]`

#### Overview & Architectural Purpose
Загружает актуальный XLSX-файл из Яндекса и кэширует в Redis и SQLite.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _download_and_cache_fresh_stats

# Execute call
result = await _download_and_cache_fresh_stats()
```

---

### `_trigger_background_attendance_refresh`
```python
async def _trigger_background_attendance_refresh() -> None
```

- **Source Reference**: [`services/attendance_stats.py#L264-L276`](../../services/attendance_stats.py#L264-L276)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Запускает обновление посещаемости в фоновом режиме без блокировки вызывающего потока.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_stats import _trigger_background_attendance_refresh

# Execute call
result = await _trigger_background_attendance_refresh()
```

---

### `_fetch_with_sync_lock`
```python
async def _fetch_with_sync_lock(force_refresh: bool) -> dict[str, dict[str, Any]]
```

- **Source Reference**: [`services/attendance_stats.py#L279-L292`](../../services/attendance_stats.py#L279-L292)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, dict[str, Any]]`

#### Overview & Architectural Purpose
Синхронизированная загрузка актуальной посещаемости с защитой от лавины запросов.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from services.attendance_stats import _fetch_with_sync_lock

# Execute call
result = await _fetch_with_sync_lock(force_refresh=...)
```

---

### `fetch_all_time_attendance`
```python
async def fetch_all_time_attendance(force_refresh: bool = False) -> dict[str, dict[str, Any]]
```

- **Source Reference**: [`services/attendance_stats.py#L295-L309`](../../services/attendance_stats.py#L295-L309)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, dict[str, Any]]`

#### Overview & Architectural Purpose
Возвращает сквозную статистику посещаемости по стратегии Stale-While-Revalidate.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import fetch_all_time_attendance

# Execute call
result = await fetch_all_time_attendance(force_refresh=...)
```

---

### `find_student_attendance`
```python
def find_student_attendance(stats: dict[str, dict[str, Any]], target_name: str) -> dict[str, Any] | None
```

- **Source Reference**: [`services/attendance_stats.py#L312-L332`](../../services/attendance_stats.py#L312-L332)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, Any] | None`

#### Overview & Architectural Purpose
Находит статистику студента по точному или частичному совпадению ФИО.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `stats` | `dict[str, dict[str, Any]]` | Yes | Parameter `stats` of type `dict[str, dict[str, Any]]`. |
| `target_name` | `str` | Yes | Parameter `target_name` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import find_student_attendance

# Execute call
result = find_student_attendance(stats=..., target_name=...)
```

---

### `_adjust_student_counts`
```python
def _adjust_student_counts(stat: dict[str, Any], old_mark: str | None, new_mark: str) -> None
```

- **Source Reference**: [`services/attendance_stats.py#L335-L348`](../../services/attendance_stats.py#L335-L348)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Корректирует счетчики студента с учетом замены старой отметки на новую.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `stat` | `dict[str, Any]` | Yes | Parameter `stat` of type `dict[str, Any]`. |
| `old_mark` | `str | None` | Yes | Parameter `old_mark` of type `str | None`. |
| `new_mark` | `str` | Yes | Parameter `new_mark` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _adjust_student_counts

# Execute call
result = _adjust_student_counts(stat=..., old_mark=..., new_mark=...)
```

---

### `_get_saved_lesson_marks`
```python
async def _get_saved_lesson_marks(t_date: str, l_num: int) -> dict[str, str]
```

- **Source Reference**: [`services/attendance_stats.py#L351-L365`](../../services/attendance_stats.py#L351-L365)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, str]`

#### Overview & Architectural Purpose
Считывает ранее сохраненный срез отметок пары из Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `t_date` | `str` | Yes | Parameter `t_date` of type `str`. |
| `l_num` | `int` | Yes | Parameter `l_num` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.attendance_stats import _get_saved_lesson_marks

# Execute call
result = await _get_saved_lesson_marks(t_date=..., l_num=...)
```

---

### `_save_lesson_marks`
```python
async def _save_lesson_marks(t_date: str, l_num: int, marks: dict[str, str]) -> None
```

- **Source Reference**: [`services/attendance_stats.py#L368-L377`](../../services/attendance_stats.py#L368-L377)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сохраняет срез отметок пары в Redis с настроенным TTL для защиты от задвоений.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `t_date` | `str` | Yes | Parameter `t_date` of type `str`. |
| `l_num` | `int` | Yes | Parameter `l_num` of type `int`. |
| `marks` | `dict[str, str]` | Yes | Parameter `marks` of type `dict[str, str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _save_lesson_marks

# Execute call
result = await _save_lesson_marks(t_date=..., l_num=..., marks=...)
```

---

### `_update_session_marks_in_stats`
```python
def _update_session_marks_in_stats( session: Any, saved_marks: dict[str, str], stats: dict[str, dict[str, Any]] ) -> dict[str, str]
```

- **Source Reference**: [`services/attendance_stats.py#L380-L398`](../../services/attendance_stats.py#L380-L398)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `dict[str, str]`

#### Overview & Architectural Purpose
Применяет новые отметки студентов из интерактивной сессии к агрегированной статистике.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `Any` | Yes | Active domain session instance containing current student index and marks. |
| `saved_marks` | `dict[str, str]` | Yes | Parameter `saved_marks` of type `dict[str, str]`. |
| `stats` | `dict[str, dict[str, Any]]` | Yes | Parameter `stats` of type `dict[str, dict[str, Any]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import _update_session_marks_in_stats

# Execute call
result = _update_session_marks_in_stats(session=..., saved_marks=..., stats=...)
```

---

### `apply_session_optimistic_update`
```python
async def apply_session_optimistic_update(session: Any) -> dict[str, dict[str, Any]]
```

- **Source Reference**: [`services/attendance_stats.py#L401-L416`](../../services/attendance_stats.py#L401-L416)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `dict[str, dict[str, Any]]`

#### Overview & Architectural Purpose
Мгновенно обновляет кэш статистики в Redis на основе отметок активной сессии.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `session` | `Any` | Yes | Active domain session instance containing current student index and marks. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.attendance_stats import apply_session_optimistic_update

# Execute call
result = await apply_session_optimistic_update(session=...)
```

---
