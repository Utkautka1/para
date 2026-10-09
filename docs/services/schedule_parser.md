# Module Specification: `services/schedule_parser.py`
> **Path**: [`services/schedule_parser.py`](file:///home/u/Рабочий стол/para/services/schedule_parser.py)  
> **Subsystem**: `KTMU Timetable Engine`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль парсинга API расписания КТМУ с расчетом звонков по четности недели. Определяет точное время звонков с учетом измененных расписаний (dayPeriodTimesByParity), вычисляет дату, предмет, тип пары (Лек/Пр), адреса корпусов и кэширует данные.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`clear_resolved_day_cache`](#clear_resolved_day_cache) | Function | L40–L42 | `None` | Сбрасывает L1 in-memory кэш предрассчитанных занятий при обн |
| [`resolve_room_address`](#resolve_room_address) | Function | L46–L52 | `str` | Определяет адрес корпуса КТМУ по номеру кабинета из настроек |
| [`extract_zoom_creds`](#extract_zoom_creds) | Function | L55–L71 | `tuple[str | None, str | None, str | None]` | Извлекает URL, ID конференции и пароль Zoom/Телемоста. |
| [`clean_subject_title`](#clean_subject_title) | Function | L74–L84 | `str` | Очищает дублирующиеся названия предметов. |
| [`calculate_week_number`](#calculate_week_number) | Function | L87–L100 | `int` | Вычисляет порядковый номер учебной недели. |
| [`is_instance_active_for_week`](#is_instance_active_for_week) | Function | L103–L118 | `bool` | Проверяет проведение пары на неделе. |
| [`is_item_for_group`](#is_item_for_group) | Function | L121–L136 | `bool` | Проверяет принадлежность занятия или нагрузки к целевой груп |
| [`is_stream_lesson`](#is_stream_lesson) | Function | L139–L152 | `bool` | Определяет, является ли занятие потоковым (объединяет нескол |
| [`extract_subgroup`](#extract_subgroup) | Function | L155–L170 | `int` | Извлекает номер подгруппы для целевой группы с учетом участи |
| [`_lookup_period_time`](#_lookup_period_time) | Function | L173–L177 | `str | None` | Извлекает время пары по индексу, если оно задано в списке зв |
| [`get_period_time_str`](#get_period_time_str) | Function | L180–L199 | `str` | Определяет интервал времени пары строго из API КТМУ. |
| [`get_http_client`](#get_http_client) | Function | L209–L227 | `httpx.AsyncClient` | Возвращает персистентный HTTP клиент с пулом соединений и ув |
| [`update_cache_headers`](#update_cache_headers) | Function | L230–L238 | `None` | Обновляет локальные ETag и Last-Modified заголовки. |
| [`filter_snapshot_for_target_group`](#filter_snapshot_for_target_group) | Function | L241–L258 | `dict[str, Any]` | Очищает сырой 40 МБ JSON от чужих групп с сохранением потоко |
| [`_parse_and_clean_payload`](#_parse_and_clean_payload) | Function | L261–L272 | `tuple[str | None, dict[str, Any]]` | Синхронно в пуле потоков парсит 50 МБ JSON и фильтрует целев |
| [`_persist_snapshot_to_redis`](#_persist_snapshot_to_redis) | Function | L275–L279 | `None` | В фоновом режиме сохраняет снимок и ETag в Redis. |
| [`process_api_response`](#process_api_response) | Function | L282–L306 | `dict[str, Any] | None` | Обрабатывает ответ API КТМУ (304 или 200) без блокировки осн |
| [`_fetch_remote_schedule`](#_fetch_remote_schedule) | Function | L312–L320 | `httpx.Response` | Выполняет HTTP-запрос к расписанию КТМУ с заголовками кэширо |
| [`refresh_schedule_in_background`](#refresh_schedule_in_background) | Function | L323–L342 | `None` | Асинхронно обновляет расписание КТМУ с защитой от частых сбо |
| [`init_schedule_cache_from_redis`](#init_schedule_cache_from_redis) | Function | L345–L358 | `bool` | Загружает срез расписания и метаданные из Redis для мгновенн |
| [`fetch_schedule_data`](#fetch_schedule_data) | Function | L361–L383 | `dict[str, Any] | None` | Отдаёт расписание из памяти/Redis или обновляет данные с уче |
| [`extract_entity_maps`](#extract_entity_maps) | Function | L386–L398 | `tuple[dict, dict, dict, dict, dict]` | Извлекает маппинги предмет/учитель/кабинет/группа/типы пар. |
| [`resolve_teacher_contact_info`](#resolve_teacher_contact_info) | Function | L401–L423 | `tuple[str, str | None, str | None, str | None]` | Получает актуальные ФИО преподавателя и ссылки на видеоконфе |
| [`resolve_room_name`](#resolve_room_name) | Function | L426–L431 | `str` | Определяет наименование аудитории или бейдж дистанта. |
| [`build_lesson_object`](#build_lesson_object) | Function | L434–L451 | `Lesson` | Собирает объект Lesson с точным расписанием звонков и призна |
| [`is_placed_lesson_active`](#is_placed_lesson_active) | Function | L454–L458 | `bool` | Проверяет, размещено ли занятие в сетке на указанный день и  |
| [`_extract_lessons_for_day`](#_extract_lessons_for_day) | Function | L461–L476 | `list[Lesson]` | Извлекает и упорядочивает список занятий для группы на указа |
| [`get_schedule_for_date`](#get_schedule_for_date) | Function | L479–L495 | `list[Lesson]` | Формирует список пар для группы на дату с двухуровневым L1/L |
| [`get_week_schedule`](#get_week_schedule) | Function | L498–L510 | `list[tuple[date, list[Lesson]]]` | Быстро формирует недельное расписание с сохранением L1-кэша  |

---

## 3. Exhaustive Function Specifications

### `clear_resolved_day_cache`
- **Signature**: `def clear_resolved_day_cache() -> None`
- **Source Reference**: [services/schedule_parser.py#L40-L42](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L40-L42)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сбрасывает L1 in-memory кэш предрассчитанных занятий при обновлении данных.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `_RESOLVED_DAY_CACHE.clear()`

---

### `resolve_room_address`
- **Signature**: `def resolve_room_address(room_name: str, is_remote: bool) -> str`
- **Source Reference**: [services/schedule_parser.py#L46-L52](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L46-L52)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Определяет адрес корпуса КТМУ по номеру кабинета из настроек config.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `room_name` | `str` | Input parameter |
| `is_remote` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if is_remote:`
2. `if room_name.lower().startswith("в-"):`
3. `return CAMPUS_ADDRESS_TSVETOCHNAYA`

---

### `extract_zoom_creds`
- **Signature**: `def extract_zoom_creds(text: str) -> tuple[str | None, str | None, str | None]`
- **Source Reference**: [services/schedule_parser.py#L55-L71](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L55-L71)
- **Async**: `No`
- **Return Type**: `tuple[str | None, str | None, str | None]`

#### Purpose & Architectural Intent
Извлекает URL, ID конференции и пароль Zoom/Телемоста. :param text: Текст из таблицы преподавателя :return: Кортеж (url, meeting_id, passcode)

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not text:`
2. `clean_text = re.sub(r"https?\s+://|http\s+s://", "https://", text, flags=re.IGNORECAS`
3. `url_m = re.search(r"https?://[^\s<>\"\'\`]+", clean_text)`
4. `id_m = re.search(r"(?:Идентификатор(?:\s+конференции)?|Meeting\s+ID)[:\s]+([0-9\s]{8,`
5. `pass_m = re.search(r"(?:Код(?:\s+доступа)?|Passcode)[:\s]+([A-Za-z0-9]+)", text, re.I`
6. `url = url_m.group(0) if url_m else None`

---

### `clean_subject_title`
- **Signature**: `def clean_subject_title(subject: str) -> str`
- **Source Reference**: [services/schedule_parser.py#L74-L84](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L74-L84)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Очищает дублирующиеся названия предметов. :param subject: Название предмета :return: Чистое название

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `subject` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `parts = [p.strip() for p in subject.split("/") if p.strip()]`
2. `if len(parts) == 2 and parts[0].lower() in parts[1].lower():`
3. `return subject`

---

### `calculate_week_number`
- **Signature**: `def calculate_week_number(target_date: date, semester_start_str: str) -> int`
- **Source Reference**: [services/schedule_parser.py#L87-L100](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L87-L100)
- **Async**: `No`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Вычисляет порядковый номер учебной недели. :param target_date: Целевая дата :param semester_start_str: Старт семестра :return: Номер недели

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date` | Input parameter |
| `semester_start_str` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `start_date = date.fromisoformat(semester_start_str)`
2. `start_monday = start_date - timedelta(days=start_date.weekday())`
3. `days_diff = (target_date - start_monday).days`
4. `if days_diff < 0:`
5. `return (days_diff // 7) + 1`

---

### `is_instance_active_for_week`
- **Signature**: `def is_instance_active_for_week(inst: dict[str, Any], week_num: int) -> bool`
- **Source Reference**: [services/schedule_parser.py#L103-L118](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L103-L118)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет проведение пары на неделе. :param inst: Занятие :param week_num: Номер недели :return: True, если проводится

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `inst` | `dict[str, Any]` | Input parameter |
| `week_num` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `pattern = inst.get("weekPattern", "all")`
2. `if pattern == "custom":`
3. `if pattern == "even":`
4. `if pattern == "odd":`
5. `return True`

---

### `is_item_for_group`
- **Signature**: `def is_item_for_group(item: dict[str, Any], group_id: str) -> bool`
- **Source Reference**: [services/schedule_parser.py#L121-L136](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L121-L136)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет принадлежность занятия или нагрузки к целевой группе, включая потоки. :param item: Словарь занятия или нагрузки :param group_id: ID целевой группы :return: True если занятие предназначено для группы

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Input parameter |
| `group_id` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not isinstance(item, dict):`
2. `if item.get("groupId") == group_id or group_id in item.get("groupIds", []):`
3. `if group_id in item.get("streamGroupIds", []):`
4. `participants = item.get("streamParticipants", [])`
5. `return any(p.get("groupId") == group_id for p in participants if isinstance(p, dict))`

---

### `is_stream_lesson`
- **Signature**: `def is_stream_lesson(inst: dict[str, Any]) -> bool`
- **Source Reference**: [services/schedule_parser.py#L139-L152](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L139-L152)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Определяет, является ли занятие потоковым (объединяет несколько групп). :param inst: Экземпляр занятия :return: True если пара потоковая

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `inst` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not isinstance(inst, dict):`
2. `if len(inst.get("streamGroupIds", [])) > 0:`
3. `if len(inst.get("streamParticipants", [])) > 0:`
4. `return bool(inst.get("streamId"))`

---

### `extract_subgroup`
- **Signature**: `def extract_subgroup(inst: dict[str, Any], group_id: str) -> int`
- **Source Reference**: [services/schedule_parser.py#L155-L170](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L155-L170)
- **Async**: `No`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Извлекает номер подгруппы для целевой группы с учетом участия в потоке. :param inst: Экземпляр занятия :param group_id: ID целевой группы :return: Номер подгруппы (0 если общая)

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `inst` | `dict[str, Any]` | Input parameter |
| `group_id` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not isinstance(inst, dict):`
2. `if inst.get("groupId") == group_id:`
3. `for sp in inst.get("streamParticipants", []):`
4. `return int(inst.get("subgroup", 0) or 0)`

---

### `_lookup_period_time`
- **Signature**: `def _lookup_period_time(times_list: list[str], period_idx: int) -> str | None`
- **Source Reference**: [services/schedule_parser.py#L173-L177](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L173-L177)
- **Async**: `No`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Извлекает время пары по индексу, если оно задано в списке звонков.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `times_list` | `list[str]` | Input parameter |
| `period_idx` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if period_idx < len(times_list) and times_list[period_idx]:`
2. `return None`

---

### `get_period_time_str`
- **Signature**: `def get_period_time_str( group_data: dict[str, Any], day_idx: int, period_idx: int, week_num: int, global_config: dict[str, Any] | None = None ) -> str`
- **Source Reference**: [services/schedule_parser.py#L180-L199](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L180-L199)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Определяет интервал времени пары строго из API КТМУ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `group_data` | `dict[str, Any]` | Input parameter |
| `day_idx` | `int` | Input parameter |
| `period_idx` | `int` | Input parameter |
| `week_num` | `int` | Input parameter |
| `global_config` | `dict[str, Any] | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `parity = "even" if week_num % 2 == 0 else "odd"`
2. `by_parity = group_data.get("dayPeriodTimesByParity", {}).get(parity, {}).get(str(day_`
3. `res = _lookup_period_time(by_parity, period_idx) or _lookup_period_time(`
4. `if res:`
5. `if global_config:`
6. `return "Время уточняется"`

---

### `get_http_client`
- **Signature**: `def get_http_client() -> httpx.AsyncClient`
- **Source Reference**: [services/schedule_parser.py#L209-L227](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L209-L227)
- **Async**: `No`
- **Return Type**: `httpx.AsyncClient`

#### Purpose & Architectural Intent
Возвращает персистентный HTTP клиент с пулом соединений и увеличенным таймаутом.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _HTTP_CLIENT`
2. `if _HTTP_CLIENT is None or _HTTP_CLIENT.is_closed:`
3. `return _HTTP_CLIENT`

---

### `update_cache_headers`
- **Signature**: `def update_cache_headers(headers: httpx.Headers) -> None`
- **Source Reference**: [services/schedule_parser.py#L230-L238](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L230-L238)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Обновляет локальные ETag и Last-Modified заголовки.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `headers` | `httpx.Headers` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _LAST_ETAG, _LAST_MODIFIED`
2. `if "etag" in headers:`
3. `if "last-modified" in headers:`

---

### `filter_snapshot_for_target_group`
- **Signature**: `def filter_snapshot_for_target_group(snapshot: dict[str, Any]) -> dict[str, Any]`
- **Source Reference**: [services/schedule_parser.py#L241-L258](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L241-L258)
- **Async**: `No`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Очищает сырой 40 МБ JSON от чужих групп с сохранением потоковых пар.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `snapshot` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `sched = snapshot.get("schedule", {})`
2. `group_insts = [i for i in sched.get("instances", []) if is_item_for_group(i, GROUP_ID`
3. `group_ids = {i["instId"] for i in group_insts if "instId" in i}`
4. `group_assigns = {k: v for k, v in sched.get("assignment", {}).items() if k in group_i`
5. `group_loads = [l for l in snapshot.get("loads", []) if is_item_for_group(l, GROUP_ID)`
6. `return {`

---

### `_parse_and_clean_payload`
- **Signature**: `def _parse_and_clean_payload(content: bytes) -> tuple[str | None, dict[str, Any]]`
- **Source Reference**: [services/schedule_parser.py#L261-L272](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L261-L272)
- **Async**: `No`
- **Return Type**: `tuple[str | None, dict[str, Any]]`

#### Purpose & Architectural Intent
Синхронно в пуле потоков парсит 50 МБ JSON и фильтрует целевую группу. Используется в asyncio.to_thread, чтобы не блокировать event loop FastAPI. Возвращает (published_at, cleaned_snapshot).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `content` | `bytes` | Input parameter |

#### Step-by-Step Logic Execution
1. `val = json.loads(content).get("value", {})`
2. `snapshot = val.get("publishedSnapshot") or val`
3. `pub_at = snapshot.get("publishedAt")`
4. `cleaned = filter_snapshot_for_target_group(snapshot)`
5. `return pub_at, cleaned`

---

### `_persist_snapshot_to_redis`
- **Signature**: `def _persist_snapshot_to_redis(snapshot: dict[str, Any]) -> None`
- **Source Reference**: [services/schedule_parser.py#L275-L279](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L275-L279)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
В фоновом режиме сохраняет снимок и ETag в Redis.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `snapshot` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `from core.redis_cache import save_schedule_snapshot`
2. `meta = {"etag": _LAST_ETAG, "last_modified": _LAST_MODIFIED, "published_at": _LAST_PU`
3. `asyncio.create_task(save_schedule_snapshot(snapshot, meta))`

---

### `process_api_response`
- **Signature**: `async def process_api_response(res: httpx.Response, now: float) -> dict[str, Any] | None`
- **Source Reference**: [services/schedule_parser.py#L282-L306](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L282-L306)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any] | None`

#### Purpose & Architectural Intent
Обрабатывает ответ API КТМУ (304 или 200) без блокировки основного потока. Возвращает очищенный срез расписания или текущий кэш при ошибке.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `res` | `httpx.Response` | Input parameter |
| `now` | `float` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _DATA_CACHE, _LAST_PUBLISHED_AT, _COOLDOWN_UNTIL`
2. `if res.status_code == 304:`
3. `if res.status_code != 200:`
4. `update_cache_headers(res.headers)`
5. `pub_at, cleaned = await asyncio.to_thread(_parse_and_clean_payload, res.content)`
6. `if pub_at and pub_at != _LAST_PUBLISHED_AT:`

---

### `_fetch_remote_schedule`
- **Signature**: `async def _fetch_remote_schedule() -> httpx.Response`
- **Source Reference**: [services/schedule_parser.py#L312-L320](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L312-L320)
- **Async**: `Yes`
- **Return Type**: `httpx.Response`

#### Purpose & Architectural Intent
Выполняет HTTP-запрос к расписанию КТМУ с заголовками кэширования.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `client = get_http_client()`
2. `headers = {}`
3. `if _LAST_ETAG:`
4. `if _LAST_MODIFIED:`
5. `return await client.get(SCHEDULE_API_URL, headers=headers)`

---

### `refresh_schedule_in_background`
- **Signature**: `async def refresh_schedule_in_background(force: bool = False) -> None`
- **Source Reference**: [services/schedule_parser.py#L323-L342](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L323-L342)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Асинхронно обновляет расписание КТМУ с защитой от частых сбоев. При ошибке сети включает 5-минутный кулдаун для предотвращения спама.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _IS_REFRESHING, _COOLDOWN_UNTIL`
2. `now = time.time()`
3. `if _IS_REFRESHING or (now < _COOLDOWN_UNTIL and not force):`
4. `_IS_REFRESHING = True`
5. `try:`

---

### `init_schedule_cache_from_redis`
- **Signature**: `async def init_schedule_cache_from_redis(now: float) -> bool`
- **Source Reference**: [services/schedule_parser.py#L345-L358](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L345-L358)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Загружает срез расписания и метаданные из Redis для мгновенного холодного старта.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `now` | `float` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _DATA_CACHE, _LAST_ETAG, _LAST_MODIFIED, _LAST_PUBLISHED_AT`
2. `from core.redis_cache import load_schedule_snapshot`
3. `snap, meta = await load_schedule_snapshot()`
4. `if snap and meta:`
5. `return False`

---

### `fetch_schedule_data`
- **Signature**: `async def fetch_schedule_data(force_refresh: bool = False) -> dict[str, Any] | None`
- **Source Reference**: [services/schedule_parser.py#L361-L383](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L361-L383)
- **Async**: `Yes`
- **Return Type**: `dict[str, Any] | None`

#### Purpose & Architectural Intent
Отдаёт расписание из памяти/Redis или обновляет данные с учетом кулдауна. Предотвращает цикличные зависания и обеспечивает мгновенный холодный старт.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `now = time.time()`
2. `if force_refresh:`
3. `if _DATA_CACHE[1] is None and await init_schedule_cache_from_redis(now):`
4. `cache_valid = (now - _DATA_CACHE[0] < SCHEDULE_CACHE_TTL_SECONDS)`
5. `if _DATA_CACHE[1] is not None:`
6. `await refresh_schedule_in_background()`

---

### `extract_entity_maps`
- **Signature**: `def extract_entity_maps(data: dict[str, Any]) -> tuple[dict, dict, dict, dict, dict]`
- **Source Reference**: [services/schedule_parser.py#L386-L398](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L386-L398)
- **Async**: `No`
- **Return Type**: `tuple[dict, dict, dict, dict, dict]`

#### Purpose & Architectural Intent
Извлекает маппинги предмет/учитель/кабинет/группа/типы пар. :param data: JSON данные :return: Кортеж словарей

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `data` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `subjs = {s["id"]: s.get("name", "") for s in data.get("subjects", []) if isinstance(s`
2. `teachs = {t["id"]: t.get("name", "") for t in data.get("teachers", []) if isinstance(`
3. `rms = {r["id"]: r.get("name", "") for r in data.get("rooms", []) if isinstance(r, dic`
4. `groups = {g["id"]: g for g in data.get("groups", []) if isinstance(g, dict)}`
5. `l_types = {l["id"]: l.get("name", "") for l in data.get("lessonTypes", []) if isinsta`
6. `return (subjs, teachs, rms, groups.get(GROUP_ID, {}), l_types)`

---

### `resolve_teacher_contact_info`
- **Signature**: `def resolve_teacher_contact_info( raw_teacher: str, teacher_data_map: dict[str, TeacherData], is_remote: bool, subj_name: str ) -> tuple[str, str | None, str | None, str | None]`
- **Source Reference**: [services/schedule_parser.py#L401-L423](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L401-L423)
- **Async**: `No`
- **Return Type**: `tuple[str, str | None, str | None, str | None]`

#### Purpose & Architectural Intent
Получает актуальные ФИО преподавателя и ссылки на видеоконференцию.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw_teacher` | `str` | Input parameter |
| `teacher_data_map` | `dict[str, TeacherData]` | Input parameter |
| `is_remote` | `bool` | Input parameter |
| `subj_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not raw_teacher:`
2. `last_name = raw_teacher.split()[0].lower()`
3. `t_info = teacher_data_map.get(last_name)`
4. `if t_info:`
5. `if is_remote:`
6. `return raw_teacher, None, None, None`

---

### `resolve_room_name`
- **Signature**: `def resolve_room_name(asgn: dict[str, Any], inst: dict[str, Any], rms: dict[str, str], is_remote: bool) -> str`
- **Source Reference**: [services/schedule_parser.py#L426-L431](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L426-L431)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Определяет наименование аудитории или бейдж дистанта.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `asgn` | `dict[str, Any]` | Input parameter |
| `inst` | `dict[str, Any]` | Input parameter |
| `rms` | `dict[str, str]` | Input parameter |
| `is_remote` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if is_remote:`
2. `room_id = asgn.get("roomId") or (inst.get("preferredRoomIds") or [""])[0]`
3. `return rms.get(room_id, room_id)`

---

### `build_lesson_object`
- **Signature**: `def build_lesson_object( inst: dict[str, Any], asgn: dict[str, Any], maps: tuple[dict, dict, dict, dict, dict], day_idx: int, week_num: int, teacher_map: dict[str, TeacherData], cfg: dict[str, Any] | None = None ) -> Lesson`
- **Source Reference**: [services/schedule_parser.py#L434-L451](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L434-L451)
- **Async**: `No`
- **Return Type**: `Lesson`

#### Purpose & Architectural Intent
Собирает объект Lesson с точным расписанием звонков и признаком потока.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `inst` | `dict[str, Any]` | Input parameter |
| `asgn` | `dict[str, Any]` | Input parameter |
| `maps` | `tuple[dict, dict, dict, dict, dict]` | Input parameter |
| `day_idx` | `int` | Input parameter |
| `week_num` | `int` | Input parameter |
| `teacher_map` | `dict[str, TeacherData]` | Input parameter |
| `cfg` | `dict[str, Any] | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `subjs, teachs, rms, group_data, l_types = maps`
2. `period = asgn.get("period", 0)`
3. `time_str = get_period_time_str(group_data, day_idx, period, week_num, cfg)`
4. `subj_name = clean_subject_title(subjs.get(inst.get("subjectId"), "Занятие"))`
5. `is_remote = inst.get("format") == "remote"`
6. `r_name = resolve_room_name(asgn, inst, rms, is_remote)`

---

### `is_placed_lesson_active`
- **Signature**: `def is_placed_lesson_active(inst: dict[str, Any], asgn: dict[str, Any] | None, day_idx: int, week_num: int) -> bool`
- **Source Reference**: [services/schedule_parser.py#L454-L458](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L454-L458)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, размещено ли занятие в сетке на указанный день и неделю.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `inst` | `dict[str, Any]` | Input parameter |
| `asgn` | `dict[str, Any] | None` | Input parameter |
| `day_idx` | `int` | Input parameter |
| `week_num` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not asgn:`
2. `return asgn.get("day") == day_idx and is_instance_active_for_week(inst, week_num)`

---

### `_extract_lessons_for_day`
- **Signature**: `def _extract_lessons_for_day( data: dict[str, Any], day_idx: int, week_num: int, links: dict[str, TeacherData] ) -> list[Lesson]`
- **Source Reference**: [services/schedule_parser.py#L461-L476](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L461-L476)
- **Async**: `No`
- **Return Type**: `list[Lesson]`

#### Purpose & Architectural Intent
Извлекает и упорядочивает список занятий для группы на указанный день недели.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `data` | `dict[str, Any]` | Input parameter |
| `day_idx` | `int` | Input parameter |
| `week_num` | `int` | Input parameter |
| `links` | `dict[str, TeacherData]` | Input parameter |

#### Step-by-Step Logic Execution
1. `sched = data.get("schedule", {})`
2. `insts, asgns = sched.get("instances", []), sched.get("assignment", {})`
3. `maps, cfg = extract_entity_maps(data), data.get("config", {})`
4. `lessons: list[Lesson] = []`
5. `for inst in insts:`
6. `lessons.sort(key=lambda x: x.period)`

---

### `get_schedule_for_date`
- **Signature**: `async def get_schedule_for_date(target_date: date, force_refresh: bool = False) -> list[Lesson]`
- **Source Reference**: [services/schedule_parser.py#L479-L495](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L479-L495)
- **Async**: `Yes`
- **Return Type**: `list[Lesson]`

#### Purpose & Architectural Intent
Формирует список пар для группы на дату с двухуровневым L1/L2 кэшированием. При повторном запросе отдает уже собранные модели за 0.01 мс без повторного парсинга.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_date` | `date` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not force_refresh and target_date in _RESOLVED_DAY_CACHE:`
2. `data = await fetch_schedule_data(force_refresh=force_refresh)`
3. `if not data:`
4. `sem_start = data.get("config", {}).get("semesterStart", "2026-09-01")`
5. `week_num, day_idx = calculate_week_number(target_date, sem_start), target_date.weekda`
6. `links = await get_teacher_links(force_refresh=False)`

---

### `get_week_schedule`
- **Signature**: `async def get_week_schedule(monday_date: date, force_refresh: bool = False) -> list[tuple[date, list[Lesson]]]`
- **Source Reference**: [services/schedule_parser.py#L498-L510](file:///home/u/Рабочий стол/para/services/schedule_parser.py#L498-L510)
- **Async**: `Yes`
- **Return Type**: `list[tuple[date, list[Lesson]]]`

#### Purpose & Architectural Intent
Быстро формирует недельное расписание с сохранением L1-кэша каждого дня.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `monday_date` | `date` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if force_refresh:`
2. `result: list[tuple[date, list[Lesson]]] = []`
3. `for i in range(6):`
4. `return result`

---
