# Module Specification: `integrations/yandex_docs.py`
> **Path**: [`integrations/yandex_docs.py`](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py)  
> **Subsystem**: `WOPI Cloud Service`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Сервис интеграции с Яндекс Документами через протокол WOPI. Обеспечивает чтение и запись посещаемости в таблицу .xlsx на Яндекс Диске. Поскольку прямая публичная веб-ссылка docs.yandex.ru защищена капчей, сессионный токен доступа WOPI извлекается через headless Chromium. Запись в файл выполняется по стандарту WOPI (HTTP POST с X-WOPI-Override: PUT) с соблюдением активной блокировки X-WOPI-Lock.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`WopiSession.__init__`](#wopisession__init__) | Method | L40–L46 | `Any` | Method |
| [`extract_client_config`](#extract_client_config) | Function | L49–L61 | `dict` | Извлекает JSON конфигурации редактора из HTML страницы. |
| [`merge_cookie_header`](#merge_cookie_header) | Function | L64–L73 | `str` | Объединяет текущие Cookie с обновленными значениями из ответ |
| [`get_yandex_cookie_header`](#get_yandex_cookie_header) | Function | L76–L83 | `str` | Формирует fallback строку заголовка Cookie из конфигурации . |
| [`get_effective_yandex_cookie`](#get_effective_yandex_cookie) | Function | L86–L97 | `str` | Возвращает актуальные Cookie из Redis, либо fallback из .env |
| [`save_effective_yandex_cookie`](#save_effective_yandex_cookie) | Function | L100–L109 | `None` | Атомарно сохраняет актуальную строку Cookie в Redis с TTL. |
| [`update_cookies_from_response`](#update_cookies_from_response) | Function | L112–L119 | `None` | Извлекает Set-Cookie из ответа и при наличии обновлений сохр |
| [`fetch_page_dom`](#fetch_page_dom) | Function | L122–L145 | `str` | Загружает HTML страницы редактора через HTTP с актуальной се |
| [`get_active_wopi_lock`](#get_active_wopi_lock) | Function | L148–L160 | `str` | Определяет активный идентификатор блокировки файла. |
| [`init_wopi_session`](#init_wopi_session) | Function | L163–L179 | `WopiSession` | Инициализирует WOPI-сессию для чтения и сохранения таблицы. |
| [`load_workbook_from_bytes`](#load_workbook_from_bytes) | Function | L182–L187 | `openpyxl.Workbook` | Синхронно парсит байты книги openpyxl в отдельном потоке без |
| [`compute_sheet_summary_counts`](#compute_sheet_summary_counts) | Function | L190–L205 | `dict[tuple[str, int], int]` | Подсчитывает количество отметок О, У, Н для каждой строки ст |
| [`patch_sheet_xml_counts`](#patch_sheet_xml_counts) | Function | L208–L226 | `str` | Заменяет пустые значения <v></v> на вычисленные количества в |
| [`ensure_all_summary_headers`](#ensure_all_summary_headers) | Function | L229–L252 | `None` | Гарантирует заголовки, коды и COUNTIF формулы во всех листах |
| [`inject_summary_cache`](#inject_summary_cache) | Function | L255–L268 | `bytes` | Инжектирует кэшированные значения формул COUNTIF в zip-архив |
| [`save_workbook_to_bytes`](#save_workbook_to_bytes) | Function | L271–L279 | `bytes` | Синхронно сохраняет книгу openpyxl в байты с инжекцией кэша  |
| [`download_workbook`](#download_workbook) | Function | L282–L295 | `openpyxl.Workbook` | Скачивает бинарный контент таблицы и загружает в openpyxl. |
| [`acquire_wopi_lock`](#acquire_wopi_lock) | Function | L298–L303 | `bool` | Блокирует файл в WOPI перед записью (HTTP 200). |
| [`release_wopi_lock`](#release_wopi_lock) | Function | L306–L311 | `bool` | Снимает блокировку с файла после записи (HTTP 200). |
| [`put_wopi_contents`](#put_wopi_contents) | Function | L314–L330 | `httpx.Response` | Отправляет бинарные данные таблицы методом PUT по протоколу  |
| [`_try_put_with_lock`](#_try_put_with_lock) | Function | L333–L348 | `bool` | Пробует записать файл сначала с текущим lock, затем с новым. |
| [`upload_workbook`](#upload_workbook) | Function | L351–L359 | `bool` | Сохраняет книгу и выгружает на сервер с управлением блокиров |
| [`verify_upload`](#verify_upload) | Function | L362–L379 | `bool` | Выполняет легковесную валидацию сохранения через скачивание  |
| [`_download_raw_bytes`](#_download_raw_bytes) | Function | L382–L390 | `bytes` | Скачивает бинарный контент таблицы без парсинга openpyxl. |
| [`_find_sheet_rid`](#_find_sheet_rid) | Function | L393–L410 | `str | None` | Находит relationship ID (r:id) листа по его имени в workbook |
| [`_resolve_sheet_target_path`](#_resolve_sheet_target_path) | Function | L413–L429 | `str | None` | Определяет относительный путь к XML листа в архиве по его r: |
| [`_extract_sheet_xml`](#_extract_sheet_xml) | Function | L432–L454 | `str | None` | Извлекает XML нужного листа по имени из xlsx zip-архива. |
| [`_cell_has_expected_mark`](#_cell_has_expected_mark) | Function | L457–L466 | `bool` | Проверяет совпадение отметки посещаемости в ячейке XML. |
| [`_marks_found_in_xml`](#_marks_found_in_xml) | Function | L469–L490 | `bool` | Проверяет наличие ожидаемых отметок посещаемости в XML листа |
| [`_verify_marks_in_raw`](#_verify_marks_in_raw) | Function | L493–L512 | `bool` | Проверяет наличие отметок в бинарном содержимом таблицы. |
| [`get_month_sheet`](#get_month_sheet) | Function | L515–L524 | `Worksheet` | Находит рабочий лист для указанной даты по номеру месяца. |
| [`parse_date_cell`](#parse_date_cell) | Function | L527–L533 | `str | None` | Приводит значение ячейки даты к строковому формату ДД.ММ. |
| [`find_date_column_start`](#find_date_column_start) | Function | L536–L548 | `int | None` | Ищет начальную колонку даты во 2-й строке таблицы. |
| [`find_lesson_column`](#find_lesson_column) | Function | L551–L567 | `int | None` | Определяет точную колонку для указанной даты и номера пары. |
| [`normalize_fio`](#normalize_fio) | Function | L570–L572 | `str` | Очищает строку ФИО от неразрывных пробелов и лишних знаков. |
| [`get_students_list`](#get_students_list) | Function | L575–L589 | `list[tuple[int, str]]` | Извлекает список студентов из колонки B, начиная с 5-й строк |
| [`find_student_row`](#find_student_row) | Function | L592–L602 | `int | None` | Находит номер строки студента в колонке B по ФИО. |
| [`write_student_mark`](#write_student_mark) | Function | L605–L622 | `None` | Записывает символ посещаемости (П, О, У, Н) в ячейку таблицы |

---

## 3. Exhaustive Function Specifications

## Class: `WopiSession`
Сессия авторизованного доступа к документу по протоколу WOPI.

### `WopiSession.__init__`
- **Signature**: `def __init__(self, resource_url: str, access_token: str, lock_id: str)`
- **Source Reference**: [integrations/yandex_docs.py#L40-L46](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L40-L46)
- **Async**: `No`
- **Return Type**: `Any`

#### Purpose & Architectural Intent
Executes internal domain logic according to service invariants.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `self` | `Any` | Input parameter |
| `resource_url` | `str` | Input parameter |
| `access_token` | `str` | Input parameter |
| `lock_id` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `self.resource_url = resource_url`
2. `self.access_token = access_token`
3. `self.lock_id = lock_id`

---

### `extract_client_config`
- **Signature**: `def extract_client_config(html_content: str) -> dict`
- **Source Reference**: [integrations/yandex_docs.py#L49-L61](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L49-L61)
- **Async**: `No`
- **Return Type**: `dict`

#### Purpose & Architectural Intent
Извлекает JSON конфигурации редактора из HTML страницы. В валидной сессии параметры зашиты в тег <script id="client-config">. При его отсутствии проверяем, не истекла ли сессия (экран логина).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `html_content` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `match = re.search(r'<script[^>]*id="client-config"[^>]*>(.*?)</script>', html_content`
2. `if match:`
3. `if "<title>Авторизация</title>" in html_content or "passp-bg" in html_content:`
4. `raise ValueError("Тег client-config не найден в DOM Яндекс Документов")`

---

### `merge_cookie_header`
- **Signature**: `def merge_cookie_header(current_cookie: str, new_cookies: dict[str, str]) -> str`
- **Source Reference**: [integrations/yandex_docs.py#L64-L73](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L64-L73)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Объединяет текущие Cookie с обновленными значениями из ответа сервера.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `current_cookie` | `str` | Input parameter |
| `new_cookies` | `dict[str, str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `cookie_map = {}`
2. `for part in current_cookie.split(";"):`
3. `for k, v in new_cookies.items():`
4. `return "; ".join(f"{k}={v}" for k, v in cookie_map.items())`

---

### `get_yandex_cookie_header`
- **Signature**: `def get_yandex_cookie_header() -> str`
- **Source Reference**: [integrations/yandex_docs.py#L76-L83](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L76-L83)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует fallback строку заголовка Cookie из конфигурации .env.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `from config import YANDEX_COOKIE, YANDEX_SESSION_ID`
2. `if YANDEX_COOKIE:`
3. `if YANDEX_SESSION_ID:`
4. `return ""`

---

### `get_effective_yandex_cookie`
- **Signature**: `async def get_effective_yandex_cookie() -> str`
- **Source Reference**: [integrations/yandex_docs.py#L86-L97](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L86-L97)
- **Async**: `Yes`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Возвращает актуальные Cookie из Redis, либо fallback из .env.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `try:`
2. `return get_yandex_cookie_header()`

---

### `save_effective_yandex_cookie`
- **Signature**: `async def save_effective_yandex_cookie(cookie_str: str) -> None`
- **Source Reference**: [integrations/yandex_docs.py#L100-L109](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L100-L109)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Атомарно сохраняет актуальную строку Cookie в Redis с TTL.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cookie_str` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `update_cookies_from_response`
- **Signature**: `async def update_cookies_from_response(res: httpx.Response, current_cookie: str) -> None`
- **Source Reference**: [integrations/yandex_docs.py#L112-L119](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L112-L119)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Извлекает Set-Cookie из ответа и при наличии обновлений сохраняет в Redis.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `res` | `httpx.Response` | Input parameter |
| `current_cookie` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not res.cookies:`
2. `new_cookies = dict(res.cookies)`
3. `merged = merge_cookie_header(current_cookie, new_cookies)`
4. `if merged != current_cookie:`

---

### `fetch_page_dom`
- **Signature**: `async def fetch_page_dom(doc_url: str) -> str`
- **Source Reference**: [integrations/yandex_docs.py#L122-L145](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L122-L145)
- **Async**: `Yes`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Загружает HTML страницы редактора через HTTP с актуальной сессией. Используем HTTP с Cookie из Redis/.env, автоматически обновляя Set-Cookie при получении свежих заголовков от сервера.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc_url` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `cookie_hdr = await get_effective_yandex_cookie()`
2. `headers = {`
3. `if cookie_hdr:`
4. `async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:`

---

### `get_active_wopi_lock`
- **Signature**: `async def get_active_wopi_lock(resource_url: str, token: str) -> str`
- **Source Reference**: [integrations/yandex_docs.py#L148-L160](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L148-L160)
- **Async**: `Yes`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Определяет активный идентификатор блокировки файла. Отправляет пустой PUT-запрос, чтобы сервер вернул 409 с заголовком x-wopi-lock.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `resource_url` | `str` | Input parameter |
| `token` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `url = f"{resource_url}/contents?access_token={token}"`
2. `headers = {"X-WOPI-Override": "PUT", "Content-Type": "application/octet-stream"}`
3. `async with httpx.AsyncClient(timeout=15.0) as client:`

---

### `init_wopi_session`
- **Signature**: `async def init_wopi_session(doc_url: str = ATTENDANCE_DOC_URL) -> WopiSession`
- **Source Reference**: [integrations/yandex_docs.py#L163-L179](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L163-L179)
- **Async**: `Yes`
- **Return Type**: `WopiSession`

#### Purpose & Architectural Intent
Инициализирует WOPI-сессию для чтения и сохранения таблицы. Возвращает объект WopiSession с валидным токеном и блокировкой.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc_url` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `log.debug("Инициализация WOPI сессии через Chromium...")`
2. `html = await fetch_page_dom(doc_url)`
3. `config = extract_client_config(html)`
4. `action_data = config.get("officeActionData", {})`
5. `res_url = action_data.get("resource_url")`
6. `token = action_data.get("access_token")`

---

### `load_workbook_from_bytes`
- **Signature**: `def load_workbook_from_bytes(content: bytes) -> openpyxl.Workbook`
- **Source Reference**: [integrations/yandex_docs.py#L182-L187](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L182-L187)
- **Async**: `No`
- **Return Type**: `openpyxl.Workbook`

#### Purpose & Architectural Intent
Синхронно парсит байты книги openpyxl в отдельном потоке без логов предупреждений.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `content` | `bytes` | Input parameter |

#### Step-by-Step Logic Execution
1. `import warnings`
2. `with warnings.catch_warnings():`

---

### `compute_sheet_summary_counts`
- **Signature**: `def compute_sheet_summary_counts(sheet: Worksheet) -> dict[tuple[str, int], int]`
- **Source Reference**: [integrations/yandex_docs.py#L190-L205](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L190-L205)
- **Async**: `No`
- **Return Type**: `dict[tuple[str, int], int]`

#### Purpose & Architectural Intent
Подсчитывает количество отметок О, У, Н для каждой строки студента.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Worksheet` | Input parameter |

#### Step-by-Step Logic Execution
1. `mc = sheet.max_column`
2. `if mc < 4:`
3. `c_o, c_u, c_n = mc - 2, mc - 1, mc`
4. `l_o = openpyxl.utils.get_column_letter(c_o)`
5. `l_u = openpyxl.utils.get_column_letter(c_u)`
6. `l_n = openpyxl.utils.get_column_letter(c_n)`

---

### `patch_sheet_xml_counts`
- **Signature**: `def patch_sheet_xml_counts(xml_text: str, counts: dict[tuple[str, int], int]) -> str`
- **Source Reference**: [integrations/yandex_docs.py#L208-L226](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L208-L226)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Заменяет пустые значения <v></v> на вычисленные количества в XML листа.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `xml_text` | `str` | Input parameter |
| `counts` | `dict[tuple[str, int], int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `def repl(m):`
2. `pattern = (`
3. `return re.sub(pattern, repl, xml_text)`

---

### `ensure_all_summary_headers`
- **Signature**: `def ensure_all_summary_headers(wb: openpyxl.Workbook) -> None`
- **Source Reference**: [integrations/yandex_docs.py#L229-L252](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L229-L252)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Гарантирует заголовки, коды и COUNTIF формулы во всех листах месяцев.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `wb` | `openpyxl.Workbook` | Input parameter |

#### Step-by-Step Logic Execution
1. `for name in wb.sheetnames:`

---

### `inject_summary_cache`
- **Signature**: `def inject_summary_cache(raw_bytes: bytes, wb: openpyxl.Workbook) -> bytes`
- **Source Reference**: [integrations/yandex_docs.py#L255-L268](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L255-L268)
- **Async**: `No`
- **Return Type**: `bytes`

#### Purpose & Architectural Intent
Инжектирует кэшированные значения формул COUNTIF в zip-архив xlsx.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw_bytes` | `bytes` | Input parameter |
| `wb` | `openpyxl.Workbook` | Input parameter |

#### Step-by-Step Logic Execution
1. `sheet_map = {f"xl/worksheets/sheet{i+1}.xml": name for i, name in enumerate(wb.sheetn`
2. `in_zip = zipfile.ZipFile(io.BytesIO(raw_bytes))`
3. `out_buf = io.BytesIO()`
4. `with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as out_zip:`
5. `return out_buf.getvalue()`

---

### `save_workbook_to_bytes`
- **Signature**: `def save_workbook_to_bytes(wb: openpyxl.Workbook) -> bytes`
- **Source Reference**: [integrations/yandex_docs.py#L271-L279](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L271-L279)
- **Async**: `No`
- **Return Type**: `bytes`

#### Purpose & Architectural Intent
Синхронно сохраняет книгу openpyxl в байты с инжекцией кэша формул.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `wb` | `openpyxl.Workbook` | Input parameter |

#### Step-by-Step Logic Execution
1. `ensure_all_summary_headers(wb)`
2. `wb.calculation.calcMode = "auto"`
3. `wb.calculation.fullCalcOnLoad = True`
4. `wb.calculation.forceFullCalc = True`
5. `buf = io.BytesIO()`
6. `wb.save(buf)`

---

### `download_workbook`
- **Signature**: `async def download_workbook(session: WopiSession) -> openpyxl.Workbook`
- **Source Reference**: [integrations/yandex_docs.py#L282-L295](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L282-L295)
- **Async**: `Yes`
- **Return Type**: `openpyxl.Workbook`

#### Purpose & Architectural Intent
Скачивает бинарный контент таблицы и загружает в openpyxl. Возвращает объект книги Excel с сохранением валидаций данных.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `WopiSession` | Input parameter |

#### Step-by-Step Logic Execution
1. `url = f"{session.resource_url}/contents?access_token={session.access_token}"`
2. `async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:`

---

### `acquire_wopi_lock`
- **Signature**: `async def acquire_wopi_lock(session: WopiSession, client: httpx.AsyncClient, lock_id: str) -> bool`
- **Source Reference**: [integrations/yandex_docs.py#L298-L303](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L298-L303)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Блокирует файл в WOPI перед записью (HTTP 200).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `WopiSession` | Input parameter |
| `client` | `httpx.AsyncClient` | Input parameter |
| `lock_id` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `url = f"{session.resource_url}?access_token={session.access_token}"`
2. `hdr = {"X-WOPI-Override": "LOCK", "X-WOPI-Lock": lock_id}`
3. `res = await client.post(url, headers=hdr)`
4. `return res.status_code == 200`

---

### `release_wopi_lock`
- **Signature**: `async def release_wopi_lock(session: WopiSession, client: httpx.AsyncClient, lock_id: str) -> bool`
- **Source Reference**: [integrations/yandex_docs.py#L306-L311](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L306-L311)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Снимает блокировку с файла после записи (HTTP 200).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `WopiSession` | Input parameter |
| `client` | `httpx.AsyncClient` | Input parameter |
| `lock_id` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `url = f"{session.resource_url}?access_token={session.access_token}"`
2. `hdr = {"X-WOPI-Override": "UNLOCK", "X-WOPI-Lock": lock_id}`
3. `res = await client.post(url, headers=hdr)`
4. `return res.status_code == 200`

---

### `put_wopi_contents`
- **Signature**: `async def put_wopi_contents( session: WopiSession, client: httpx.AsyncClient, data: bytes, lock_id: str ) -> httpx.Response`
- **Source Reference**: [integrations/yandex_docs.py#L314-L330](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L314-L330)
- **Async**: `Yes`
- **Return Type**: `httpx.Response`

#### Purpose & Architectural Intent
Отправляет бинарные данные таблицы методом PUT по протоколу WOPI.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `WopiSession` | Input parameter |
| `client` | `httpx.AsyncClient` | Input parameter |
| `data` | `bytes` | Input parameter |
| `lock_id` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `url = f"{session.resource_url}/contents?access_token={session.access_token}"`
2. `hdr = {`
3. `res = await client.post(url, headers=hdr, content=data)`
4. `log.debug(f"WOPI PUT: HTTP {res.status_code}, lock={lock_id[:16]}...")`
5. `if res.status_code != 200:`
6. `return res`

---

### `_try_put_with_lock`
- **Signature**: `async def _try_put_with_lock( session: WopiSession, client: httpx.AsyncClient, data: bytes ) -> bool`
- **Source Reference**: [integrations/yandex_docs.py#L333-L348](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L333-L348)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Пробует записать файл сначала с текущим lock, затем с новым.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `WopiSession` | Input parameter |
| `client` | `httpx.AsyncClient` | Input parameter |
| `data` | `bytes` | Input parameter |

#### Step-by-Step Logic Execution
1. `if session.lock_id:`
2. `new_lock = str(uuid.uuid4())`
3. `if not await acquire_wopi_lock(session, client, new_lock):`
4. `res = await put_wopi_contents(session, client, data, new_lock)`
5. `await release_wopi_lock(session, client, new_lock)`
6. `return res.status_code == 200`

---

### `upload_workbook`
- **Signature**: `async def upload_workbook(session: WopiSession, wb: openpyxl.Workbook) -> bool`
- **Source Reference**: [integrations/yandex_docs.py#L351-L359](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L351-L359)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Сохраняет книгу и выгружает на сервер с управлением блокировками.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `WopiSession` | Input parameter |
| `wb` | `openpyxl.Workbook` | Input parameter |

#### Step-by-Step Logic Execution
1. `data = await asyncio.to_thread(save_workbook_to_bytes, wb)`
2. `async with httpx.AsyncClient(timeout=30.0) as client:`
3. `log.error("❌ Ошибка загрузки таблицы в WOPI")`
4. `return False`

---

### `verify_upload`
- **Signature**: `async def verify_upload( session: WopiSession, target_date: date, lesson_num: int, expected_marks: dict[str, str], ) -> bool`
- **Source Reference**: [integrations/yandex_docs.py#L362-L379](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L362-L379)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Выполняет легковесную валидацию сохранения через скачивание raw-байтов. Извлекает только XML нужного листа без создания дерева openpyxl (~2MB RAM). Возвращает True при подтверждении отметок на сервере.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `WopiSession` | Input parameter |
| `target_date` | `date` | Input parameter |
| `lesson_num` | `int` | Input parameter |
| `expected_marks` | `dict[str, str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_download_raw_bytes`
- **Signature**: `async def _download_raw_bytes(session: WopiSession) -> bytes`
- **Source Reference**: [integrations/yandex_docs.py#L382-L390](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L382-L390)
- **Async**: `Yes`
- **Return Type**: `bytes`

#### Purpose & Architectural Intent
Скачивает бинарный контент таблицы без парсинга openpyxl.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `session` | `WopiSession` | Input parameter |

#### Step-by-Step Logic Execution
1. `url = f"{session.resource_url}/contents?access_token={session.access_token}"`
2. `async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:`

---

### `_find_sheet_rid`
- **Signature**: `def _find_sheet_rid(wb_xml: str, sheet_name: str) -> str | None`
- **Source Reference**: [integrations/yandex_docs.py#L393-L410](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L393-L410)
- **Async**: `No`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Находит relationship ID (r:id) листа по его имени в workbook.xml. Используем ElementTree вместо хрупких регулярных выражений. Возвращает строку вида 'rId1' или None.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `wb_xml` | `str` | Input parameter |
| `sheet_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_resolve_sheet_target_path`
- **Signature**: `def _resolve_sheet_target_path(rels_xml: str, rid: str) -> str | None`
- **Source Reference**: [integrations/yandex_docs.py#L413-L429](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L413-L429)
- **Async**: `No`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Определяет относительный путь к XML листа в архиве по его r:id. Нормализует префикс 'xl/' и ведущие слэши из rels-манифеста. Возвращает путь в zip-архиве, например 'xl/worksheets/sheet1.xml'.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `rels_xml` | `str` | Input parameter |
| `rid` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_extract_sheet_xml`
- **Signature**: `def _extract_sheet_xml(raw: bytes, sheet_name: str) -> str | None`
- **Source Reference**: [integrations/yandex_docs.py#L432-L454](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L432-L454)
- **Async**: `No`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Извлекает XML нужного листа по имени из xlsx zip-архива. Использует связку workbook.xml -> workbook.xml.rels без загрузки openpyxl. Возвращает XML-текст листа или None.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw` | `bytes` | Input parameter |
| `sheet_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_cell_has_expected_mark`
- **Signature**: `def _cell_has_expected_mark(cell_xml: str, mark: str) -> bool`
- **Source Reference**: [integrations/yandex_docs.py#L457-L466](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L457-L466)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет совпадение отметки посещаемости в ячейке XML. Распознает значения в <t> и <v>, декодируя HTML-сущности (например, &#1055;). Возвращает True, если значение ячейки совпадает с ожидаемой отметкой.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cell_xml` | `str` | Input parameter |
| `mark` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `unescaped = html.unescape(cell_xml)`
2. `match = re.search(r"<(?:\w+:)?(?:t|v)[^>]*>([^<]*)</(?:\w+:)?(?:t|v)>", unescaped)`
3. `return bool(match and match.group(1).strip().upper() == mark)`

---

### `_marks_found_in_xml`
- **Signature**: `def _marks_found_in_xml( xml_text: str, check_marks: dict[str, str] ) -> bool`
- **Source Reference**: [integrations/yandex_docs.py#L469-L490](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L469-L490)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет наличие ожидаемых отметок посещаемости в XML листа. Ищет ячейки соответствующих строк и проверяет совпадение меток. Возвращает True, если все проверяемые отметки найдены.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `xml_text` | `str` | Input parameter |
| `check_marks` | `dict[str, str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `found = 0`
2. `for row_str, mark in check_marks.items():`
3. `ok = found == len(check_marks)`
4. `if not ok:`
5. `return ok`

---

### `_verify_marks_in_raw`
- **Signature**: `def _verify_marks_in_raw( raw: bytes, target_date: date, expected_marks: dict[str, str] ) -> bool`
- **Source Reference**: [integrations/yandex_docs.py#L493-L512](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L493-L512)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет наличие отметок в бинарном содержимом таблицы. Выбирает лист месяца, извлекает его XML и валидирует метки. Возвращает True при успешном подтверждении.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw` | `bytes` | Input parameter |
| `target_date` | `date` | Input parameter |
| `expected_marks` | `dict[str, str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `sheet_name = MONTH_SHEET_MAP.get(target_date.month)`
2. `if not sheet_name:`
3. `check_marks = {r: m for r, m in expected_marks.items() if m in {"О", "У", "Н"}}`
4. `if not check_marks:`
5. `xml_text = _extract_sheet_xml(raw, sheet_name)`
6. `if not xml_text:`

---

### `get_month_sheet`
- **Signature**: `def get_month_sheet(wb: openpyxl.Workbook, target_date: date) -> Worksheet`
- **Source Reference**: [integrations/yandex_docs.py#L515-L524](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L515-L524)
- **Async**: `No`
- **Return Type**: `Worksheet`

#### Purpose & Architectural Intent
Находит рабочий лист для указанной даты по номеру месяца. Выбрасывает ValueError, если вкладка отсутствует в таблице.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `wb` | `openpyxl.Workbook` | Input parameter |
| `target_date` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `sheet_name = MONTH_SHEET_MAP.get(target_date.month)`
2. `if not sheet_name or sheet_name not in wb.sheetnames:`
3. `return wb[sheet_name]`

---

### `parse_date_cell`
- **Signature**: `def parse_date_cell(cell_value: object) -> str | None`
- **Source Reference**: [integrations/yandex_docs.py#L527-L533](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L527-L533)
- **Async**: `No`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Приводит значение ячейки даты к строковому формату ДД.ММ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cell_value` | `object` | Input parameter |

#### Step-by-Step Logic Execution
1. `if isinstance(cell_value, (datetime, date)):`
2. `if cell_value:`
3. `return None`

---

### `find_date_column_start`
- **Signature**: `def find_date_column_start(sheet: Worksheet, target_date: date) -> int | None`
- **Source Reference**: [integrations/yandex_docs.py#L536-L548](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L536-L548)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Ищет начальную колонку даты во 2-й строке таблицы. Возвращает 1-based индекс первой колонки дня или None.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Worksheet` | Input parameter |
| `target_date` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `target_str = target_date.strftime("%d.%m")`
2. `for col in range(1, sheet.max_column + 1):`
3. `return None`

---

### `find_lesson_column`
- **Signature**: `def find_lesson_column(sheet: Worksheet, target_date: date, lesson_num: int) -> int | None`
- **Source Reference**: [integrations/yandex_docs.py#L551-L567](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L551-L567)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Определяет точную колонку для указанной даты и номера пары. Ищет дату во 2-й строке, затем номер пары (1-6) в 4-й строке.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Worksheet` | Input parameter |
| `target_date` | `date` | Input parameter |
| `lesson_num` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `start_col = find_date_column_start(sheet, target_date)`
2. `if not start_col:`
3. `for offset in range(6):`
4. `return None`

---

### `normalize_fio`
- **Signature**: `def normalize_fio(name: str) -> str`
- **Source Reference**: [integrations/yandex_docs.py#L570-L572](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L570-L572)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Очищает строку ФИО от неразрывных пробелов и лишних знаков.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `return name.replace("\xa0", " ").strip()`

---

### `get_students_list`
- **Signature**: `def get_students_list(sheet: Worksheet) -> list[tuple[int, str]]`
- **Source Reference**: [integrations/yandex_docs.py#L575-L589](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L575-L589)
- **Async**: `No`
- **Return Type**: `list[tuple[int, str]]`

#### Purpose & Architectural Intent
Извлекает список студентов из колонки B, начиная с 5-й строки. Возвращает список кортежей (номер_строки, ФИО).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Worksheet` | Input parameter |

#### Step-by-Step Logic Execution
1. `students: list[tuple[int, str]] = []`
2. `for row in range(5, sheet.max_row + 1):`
3. `return students`

---

### `find_student_row`
- **Signature**: `def find_student_row(sheet: Worksheet, student_name: str) -> int | None`
- **Source Reference**: [integrations/yandex_docs.py#L592-L602](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L592-L602)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Находит номер строки студента в колонке B по ФИО. Использует частичное совпадение фамилии и имени для надёжности.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Worksheet` | Input parameter |
| `student_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `target = normalize_fio(student_name).lower()`
2. `for row, name in get_students_list(sheet):`
3. `return None`

---

### `write_student_mark`
- **Signature**: `def write_student_mark( sheet: Worksheet, row: int, col: int, mark: str ) -> None`
- **Source Reference**: [integrations/yandex_docs.py#L605-L622](file:///home/u/Рабочий стол/para/integrations/yandex_docs.py#L605-L622)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Записывает символ посещаемости (П, О, У, Н) в ячейку таблицы. Проверяет валидность символа перед записью.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `sheet` | `Worksheet` | Input parameter |
| `row` | `int` | Input parameter |
| `col` | `int` | Input parameter |
| `mark` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `valid_marks = {"П", "О", "У", "Н", ""}`
2. `clean_mark = mark.strip().upper()`
3. `if clean_mark not in valid_marks:`
4. `cell = sheet.cell(row, col)`
5. `cell.value = clean_mark if clean_mark else None`
6. `log.debug(f"Записана отметка '{clean_mark}' в ячейку R{row}C{col}")`

---
