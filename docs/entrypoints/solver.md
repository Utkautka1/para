# Module Specification: `solver.py`
> **Path**: [`solver.py`](file:///home/u/Рабочий стол/para/solver.py)  
> **Subsystem**: `AI Queue Consumer`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Сервис-воркер решения домашних заданий через DeepSeek. Работает в бесконечном цикле: 1. Извлекает задачу из Redis-очереди hw:tasks:queue (BLPOP) 2. Скачивает и парсит прикреплённый файл (изображение, docx, pdf) 3. Отправляет запрос в DeepSeek API (stateless) 4. Формирует .docx файл с решением по ГОСТ 5. Отправляет документ в топик «Готовое ДЗ» (ID 3951)

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`build_post_link`](#build_post_link) | Function | L38–L41 | `str` | Формирует прямую ссылку на оригинальное сообщение задания в  |
| [`download_file_bytes`](#download_file_bytes) | Function | L44–L57 | `bytes | None` | Безопасно скачивает байты файла Telegram с лимитом размера 2 |
| [`extract_docx_data`](#extract_docx_data) | Function | L60–L76 | `tuple[str, list[bytes]]` | Извлекает весь текст и встроенные картинки из .docx документ |
| [`extract_pdf_data`](#extract_pdf_data) | Function | L79–L88 | `str` | Извлекает текст со всех страниц PDF документа. |
| [`parse_file_payload`](#parse_file_payload) | Function | L91–L109 | `tuple[bytes | None, str | None]` | Разбирает байты файла (изображение, docx, pdf, текст) в форм |
| [`resolve_task_payload`](#resolve_task_payload) | Function | L112–L124 | `tuple[bytes | None, str | None]` | Скачивает и подготавливает медиа/текст задания для передачи  |
| [`send_solution_to_telegram`](#send_solution_to_telegram) | Function | L127–L140 | `None` | Отправляет готовый .docx файл решения в топик готовых ДЗ. |
| [`notify_task_error`](#notify_task_error) | Function | L143–L157 | `None` | Отправляет уведомление об ошибке решения в чат пользователя. |
| [`execute_single_task`](#execute_single_task) | Function | L160–L179 | `None` | Обрабатывает одну задачу: решает ДЗ в DeepSeek и отправляет  |
| [`_guarded_execute_task`](#_guarded_execute_task) | Function | L185–L188 | `None` | Исполняет задачу под семафором параллелизма для защиты от пе |
| [`run_solver_loop`](#run_solver_loop) | Function | L191–L214 | `None` | Бесконечный цикл чтения очереди задач и параллельного запуск |
| [`main`](#main) | Function | L218–L235 | `None` | Инициализация ресурсов и запуск сервиса para-solver. |

---

## 3. Exhaustive Function Specifications

### `build_post_link`
- **Signature**: `def build_post_link(chat_id: int, message_id: int) -> str`
- **Source Reference**: [solver.py#L38-L41](file:///home/u/Рабочий стол/para/solver.py#L38-L41)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует прямую ссылку на оригинальное сообщение задания в Telegram.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `chat_id` | `int` | Input parameter |
| `message_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `clean_id = str(chat_id).replace("-100", "")`
2. `return f"https://t.me/c/{clean_id}/{message_id}"`

---

### `download_file_bytes`
- **Signature**: `async def download_file_bytes(tg_bot: Bot, file_id: str, file_size: int) -> bytes | None`
- **Source Reference**: [solver.py#L44-L57](file:///home/u/Рабочий стол/para/solver.py#L44-L57)
- **Async**: `Yes`
- **Return Type**: `bytes | None`

#### Purpose & Architectural Intent
Безопасно скачивает байты файла Telegram с лимитом размера 20 МБ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `tg_bot` | `Bot` | Input parameter |
| `file_id` | `str` | Input parameter |
| `file_size` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if file_size > MAX_FILE_SIZE:`
2. `try:`

---

### `extract_docx_data`
- **Signature**: `def extract_docx_data(doc_bytes: bytes) -> tuple[str, list[bytes]]`
- **Source Reference**: [solver.py#L60-L76](file:///home/u/Рабочий стол/para/solver.py#L60-L76)
- **Async**: `No`
- **Return Type**: `tuple[str, list[bytes]]`

#### Purpose & Architectural Intent
Извлекает весь текст и встроенные картинки из .docx документа.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc_bytes` | `bytes` | Input parameter |

#### Step-by-Step Logic Execution
1. `import docx`
2. `doc = docx.Document(io.BytesIO(doc_bytes))`
3. `paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]`
4. `for table in doc.tables:`
5. `images = []`
6. `for rel in doc.part.rels.values():`

---

### `extract_pdf_data`
- **Signature**: `def extract_pdf_data(doc_bytes: bytes) -> str`
- **Source Reference**: [solver.py#L79-L88](file:///home/u/Рабочий стол/para/solver.py#L79-L88)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Извлекает текст со всех страниц PDF документа.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc_bytes` | `bytes` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `parse_file_payload`
- **Signature**: `def parse_file_payload(doc_bytes: bytes, file_name: str, mime: str | None, prompt: str) -> tuple[bytes | None, str | None]`
- **Source Reference**: [solver.py#L91-L109](file:///home/u/Рабочий стол/para/solver.py#L91-L109)
- **Async**: `No`
- **Return Type**: `tuple[bytes | None, str | None]`

#### Purpose & Architectural Intent
Разбирает байты файла (изображение, docx, pdf, текст) в формат для DeepSeek.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc_bytes` | `bytes` | Input parameter |
| `file_name` | `str` | Input parameter |
| `mime` | `str | None` | Input parameter |
| `prompt` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `fn = file_name.lower()`
2. `if (mime and mime.startswith("image")) or fn.endswith((".png", ".jpg", ".jpeg", ".web`
3. `if fn.endswith(".docx"):`
4. `if fn.endswith(".pdf"):`
5. `if fn.endswith((".txt", ".md", ".py", ".json", ".csv", ".c", ".cpp", ".js", ".java"))`
6. `return None, prompt or None`

---

### `resolve_task_payload`
- **Signature**: `async def resolve_task_payload(tg_bot: Bot, task: dict) -> tuple[bytes | None, str | None]`
- **Source Reference**: [solver.py#L112-L124](file:///home/u/Рабочий стол/para/solver.py#L112-L124)
- **Async**: `Yes`
- **Return Type**: `tuple[bytes | None, str | None]`

#### Purpose & Architectural Intent
Скачивает и подготавливает медиа/текст задания для передачи в нейросеть.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `tg_bot` | `Bot` | Input parameter |
| `task` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `file_id = task.get("file_id")`
2. `prompt = task.get("prompt") or ""`
3. `if not file_id:`
4. `f_size = task.get("file_size") or 0`
5. `raw_bytes = await download_file_bytes(tg_bot, file_id, f_size)`
6. `if not raw_bytes:`

---

### `send_solution_to_telegram`
- **Signature**: `async def send_solution_to_telegram(tg_bot: Bot, task: dict, doc_path: str) -> None`
- **Source Reference**: [solver.py#L127-L140](file:///home/u/Рабочий стол/para/solver.py#L127-L140)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет готовый .docx файл решения в топик готовых ДЗ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `tg_bot` | `Bot` | Input parameter |
| `task` | `dict` | Input parameter |
| `doc_path` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `chat_id = task.get("chat_id", config.TOPIC_CHAT_ID)`
2. `msg_id = task.get("message_id", 0)`
3. `orig_link = build_post_link(chat_id, msg_id)`
4. `caption = f"✅ <b>Готовое решение ДЗ</b>\n\n📌 Ссылка на задание: {orig_link}"`
5. `doc_file = FSInputFile(doc_path, filename=f"Решение_ДЗ_{msg_id}.docx")`
6. `await tg_bot.send_document(`

---

### `notify_task_error`
- **Signature**: `async def notify_task_error(tg_bot: Bot, task: dict) -> None`
- **Source Reference**: [solver.py#L143-L157](file:///home/u/Рабочий стол/para/solver.py#L143-L157)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет уведомление об ошибке решения в чат пользователя.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `tg_bot` | `Bot` | Input parameter |
| `task` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `execute_single_task`
- **Signature**: `async def execute_single_task(tg_bot: Bot, task: dict) -> None`
- **Source Reference**: [solver.py#L160-L179](file:///home/u/Рабочий стол/para/solver.py#L160-L179)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Обрабатывает одну задачу: решает ДЗ в DeepSeek и отправляет документ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `tg_bot` | `Bot` | Input parameter |
| `task` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `msg_id = task.get("message_id", 0)`
2. `filename = f"solution_{uuid.uuid4().hex[:8]}_{msg_id}.docx"`
3. `doc_path = os.path.join(tempfile.gettempdir(), filename)`
4. `try:`

---

### `_guarded_execute_task`
- **Signature**: `async def _guarded_execute_task(tg_bot: Bot, task: dict) -> None`
- **Source Reference**: [solver.py#L185-L188](file:///home/u/Рабочий стол/para/solver.py#L185-L188)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Исполняет задачу под семафором параллелизма для защиты от перегрузки.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `tg_bot` | `Bot` | Input parameter |
| `task` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `async with _SOLVER_SEMAPHORE:`

---

### `run_solver_loop`
- **Signature**: `async def run_solver_loop() -> None`
- **Source Reference**: [solver.py#L191-L214](file:///home/u/Рабочий стол/para/solver.py#L191-L214)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Бесконечный цикл чтения очереди задач и параллельного запуска решений.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `log.info("Запущен рабочий цикл очереди решений para-solver...")`
2. `active_tasks: set[asyncio.Task] = set()`
3. `while True:`

---

### `main`
- **Signature**: `async def main() -> None`
- **Source Reference**: [solver.py#L218-L235](file:///home/u/Рабочий стол/para/solver.py#L218-L235)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Инициализация ресурсов и запуск сервиса para-solver.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `log.info("=" * 60)`
2. `log.info("ЗАПУСК Сервиса AI-Решения ДЗ (para-solver)")`
3. `log.info(f"  Модель DeepSeek: {config.DEEPSEEK_MODEL_NAME}")`
4. `log.info(f"  Топик приема: {config.HW_INPUT_TOPIC_THREAD_ID}")`
5. `log.info(f"  Топик решений: {config.HW_OUTPUT_TOPIC_THREAD_ID}")`
6. `log.info("=" * 60)`

---
