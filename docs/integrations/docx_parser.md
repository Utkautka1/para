# Module Specification: `integrations/docx_parser.py`
> **Path**: [`integrations/docx_parser.py`](file:///home/u/Рабочий стол/para/integrations/docx_parser.py)  
> **Subsystem**: `Cloud DOCX Parser`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль загрузки и парсинга контактов преподавателей с Yandex Disk. Скачивает файл .docx с Yandex Disk через публичный REST API Яндекс Диска, извлекает из таблицы ФИО преподавателей и их персональные Zoom/Телемост ссылки.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`fetch_docx_bytes`](#fetch_docx_bytes) | Function | L35–L56 | `bytes | None` | Загружает сырые байты docx файла с Yandex Disk через публичн |
| [`extract_row_texts`](#extract_row_texts) | Function | L59–L73 | `tuple[str, str]` | Извлекает полное имя преподавателя и строку ссылок из таблиц |
| [`parse_docx_teachers`](#parse_docx_teachers) | Function | L76–L91 | `dict[str, TeacherData]` | Распаковывает docx и парсит таблицу контактов преподавателей |
| [`_get_docx_lock`](#_get_docx_lock) | Function | L98–L103 | `asyncio.Lock` | Возвращает лениво инициализированный asyncio.Lock для текуще |
| [`_is_cache_fresh`](#_is_cache_fresh) | Function | L106–L113 | `bool` | Проверяет актуальность кэша преподавателей с защитой от част |
| [`_fetch_and_cache_teachers`](#_fetch_and_cache_teachers) | Function | L116–L126 | `dict[str, TeacherData]` | Скачивает docx с Яндекс Диска, парсит преподавателей и обнов |
| [`get_teacher_links`](#get_teacher_links) | Function | L129–L138 | `dict[str, TeacherData]` | Возвращает карту контактов преподавателей с Singleflight бло |

---

## 3. Exhaustive Function Specifications

## Class: `TeacherData`
Тип данных элемента преподавателя.

### `fetch_docx_bytes`
- **Signature**: `async def fetch_docx_bytes() -> bytes | None`
- **Source Reference**: [integrations/docx_parser.py#L35-L56](file:///home/u/Рабочий стол/para/integrations/docx_parser.py#L35-L56)
- **Async**: `Yes`
- **Return Type**: `bytes | None`

#### Purpose & Architectural Intent
Загружает сырые байты docx файла с Yandex Disk через публичный API. :return: Байты файла docx или None при ошибке

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `api_url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={YANDEX_`
2. `try:`

---

### `extract_row_texts`
- **Signature**: `def extract_row_texts(row_elem: Any) -> tuple[str, str]`
- **Source Reference**: [integrations/docx_parser.py#L59-L73](file:///home/u/Рабочий стол/para/integrations/docx_parser.py#L59-L73)
- **Async**: `No`
- **Return Type**: `tuple[str, str]`

#### Purpose & Architectural Intent
Извлекает полное имя преподавателя и строку ссылок из таблицы docx. :param row_elem: XML элемент w:tr :return: Кортеж (ФИО, Ссылка_и_данные)

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `row_elem` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `cells = row_elem.findall(".//w:tc", NS)`
2. `if len(cells) < 3:`
3. `name_texts = [t.text for t in cells[0].findall(".//w:t", NS) if t.text]`
4. `name = " ".join(" ".join(name_texts).split()).strip()`
5. `link_texts = [t.text for t in cells[2].findall(".//w:t", NS) if t.text]`
6. `link_info = " ".join(link_texts).strip()`

---

### `parse_docx_teachers`
- **Signature**: `def parse_docx_teachers(content: bytes) -> dict[str, TeacherData]`
- **Source Reference**: [integrations/docx_parser.py#L76-L91](file:///home/u/Рабочий стол/para/integrations/docx_parser.py#L76-L91)
- **Async**: `No`
- **Return Type**: `dict[str, TeacherData]`

#### Purpose & Architectural Intent
Распаковывает docx и парсит таблицу контактов преподавателей.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `content` | `bytes` | Input parameter |

#### Step-by-Step Logic Execution
1. `teachers_map: dict[str, TeacherData] = {}`
2. `try:`
3. `return teachers_map`

---

### `_get_docx_lock`
- **Signature**: `def _get_docx_lock() -> asyncio.Lock`
- **Source Reference**: [integrations/docx_parser.py#L98-L103](file:///home/u/Рабочий стол/para/integrations/docx_parser.py#L98-L103)
- **Async**: `No`
- **Return Type**: `asyncio.Lock`

#### Purpose & Architectural Intent
Возвращает лениво инициализированный asyncio.Lock для текущего event loop.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `global _DOCX_LOCK`
2. `if _DOCX_LOCK is None:`
3. `return _DOCX_LOCK`

---

### `_is_cache_fresh`
- **Signature**: `def _is_cache_fresh(now: float, force_refresh: bool) -> bool`
- **Source Reference**: [integrations/docx_parser.py#L106-L113](file:///home/u/Рабочий стол/para/integrations/docx_parser.py#L106-L113)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет актуальность кэша преподавателей с защитой от частых сетевых запросов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `now` | `float` | Input parameter |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not _CACHE[1]:`
2. `age = now - _CACHE[0]`
3. `if not force_refresh:`
4. `return age < MIN_DOCX_REFRESH_INTERVAL_SECONDS`

---

### `_fetch_and_cache_teachers`
- **Signature**: `async def _fetch_and_cache_teachers(now: float) -> dict[str, TeacherData]`
- **Source Reference**: [integrations/docx_parser.py#L116-L126](file:///home/u/Рабочий стол/para/integrations/docx_parser.py#L116-L126)
- **Async**: `Yes`
- **Return Type**: `dict[str, TeacherData]`

#### Purpose & Architectural Intent
Скачивает docx с Яндекс Диска, парсит преподавателей и обновляет кэш в памяти.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `now` | `float` | Input parameter |

#### Step-by-Step Logic Execution
1. `global _CACHE`
2. `from services.custom_teachers import load_custom_teachers`
3. `log.info("Загрузка свежих данных с Яндекс Диска...")`
4. `content = await fetch_docx_bytes()`
5. `parsed = (await asyncio.to_thread(parse_docx_teachers, content)) if content else _CAC`
6. `custom = load_custom_teachers()`

---

### `get_teacher_links`
- **Signature**: `async def get_teacher_links(force_refresh: bool = False) -> dict[str, TeacherData]`
- **Source Reference**: [integrations/docx_parser.py#L129-L138](file:///home/u/Рабочий стол/para/integrations/docx_parser.py#L129-L138)
- **Async**: `Yes`
- **Return Type**: `dict[str, TeacherData]`

#### Purpose & Architectural Intent
Возвращает карту контактов преподавателей с Singleflight блокировкой.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `now = time.time()`
2. `if _is_cache_fresh(now, force_refresh):`
3. `async with _get_docx_lock():`

---
