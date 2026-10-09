# Module Specification: `bot/handlers/user/hw_solver.py`
> **Path**: [`bot/handlers/user/hw_solver.py`](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py)  
> **Subsystem**: `AI Homework Flow`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Хэндлер перехвата новых ДЗ в целевом топике (ID 405). Отлавливает фото, документы (.docx, .pdf, .txt, код) и текстовые задачи, валидирует их, проверяет антиспам и ставит задачу в очередь Redis (hw:tasks:queue) для фонового воркера para-solver.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`combine_prompt_and_instructions`](#combine_prompt_and_instructions) | Function | L32–L38 | `str` | Объединяет инструкцию из подписи/текста реплая и основное за |
| [`is_valid_homework_prompt`](#is_valid_homework_prompt) | Function | L41–L58 | `bool` | Проверяет, содержит ли сообщение запрос на решение учебной з |
| [`extract_media_meta`](#extract_media_meta) | Function | L61–L70 | `tuple[str | None, str | None, str | None, str | None, int]` | Извлекает идентификаторы и метаданные медиафайла (фото или д |
| [`compute_content_hash`](#compute_content_hash) | Function | L73–L80 | `str` | Вычисляет SHA256 хэш промпта и уникального ID файла для защи |
| [`is_hw_allowed`](#is_hw_allowed) | Function | L83–L96 | `bool` | Проверяет лимиты пользователя, статус обработки и наличие уч |
| [`acknowledge_hw_task`](#acknowledge_hw_task) | Function | L99–L108 | `None` | Ставит реакцию-подтверждение о принятии задачи в очередь ней |
| [`dispatch_hw_task`](#dispatch_hw_task) | Function | L111–L132 | `None` | Формирует payload и отправляет задачу в очередь воркера para |
| [`validate_hw_file_size`](#validate_hw_file_size) | Function | L135–L148 | `bool` | Проверяет размер медиафайла (не более 20 МБ) для предотвраще |
| [`handle_new_homework`](#handle_new_homework) | Function | L155–L175 | `None` | Перехватывает сообщение с ДЗ и отправляет в очередь воркера  |

---

## 3. Exhaustive Function Specifications

### `combine_prompt_and_instructions`
- **Signature**: `def combine_prompt_and_instructions(msg: Message, target: Message) -> str`
- **Source Reference**: [bot/handlers/user/hw_solver.py#L32-L38](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py#L32-L38)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Объединяет инструкцию из подписи/текста реплая и основное задание.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `msg` | `Message` | Input parameter |
| `target` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `u_text = msg.text or msg.caption or ""`
2. `t_text = target.caption or target.text or ""`
3. `if u_text and t_text and u_text != t_text:`
4. `return u_text or t_text or ""`

---

### `is_valid_homework_prompt`
- **Signature**: `def is_valid_homework_prompt(text: str | None, has_media: bool) -> bool`
- **Source Reference**: [bot/handlers/user/hw_solver.py#L41-L58](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py#L41-L58)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, содержит ли сообщение запрос на решение учебной задачи. 'Голые' медиафайлы без промпта не берутся в обработку, чтобы бот не трогал учебные материалы и конспекты, загружаемые в топик.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str | None` | Input parameter |
| `has_media` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not text:`
2. `t = text.lower().strip()`
3. `flood_words = {"привет", "хай", "как дела", "спасибо", "спасбо", "спсибо", "ок", "пон`
4. `if t in flood_words or len(t) < 4:`
5. `kw_list = [`
6. `return any(kw in t for kw in kw_list) or len(t) >= 25`

---

### `extract_media_meta`
- **Signature**: `def extract_media_meta(msg: Message, target: Message) -> tuple[str | None, str | None, str | None, str | None, int]`
- **Source Reference**: [bot/handlers/user/hw_solver.py#L61-L70](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py#L61-L70)
- **Async**: `No`
- **Return Type**: `tuple[str | None, str | None, str | None, str | None, int]`

#### Purpose & Architectural Intent
Извлекает идентификаторы и метаданные медиафайла (фото или документа).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `msg` | `Message` | Input parameter |
| `target` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `m = msg if (msg.photo or msg.document) else target`
2. `if m.photo:`
3. `if m.document:`
4. `return None, None, None, None, 0`

---

### `compute_content_hash`
- **Signature**: `def compute_content_hash(text: str | None, unique_id: str | None) -> str`
- **Source Reference**: [bot/handlers/user/hw_solver.py#L73-L80](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py#L73-L80)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Вычисляет SHA256 хэш промпта и уникального ID файла для защиты от дубликатов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str | None` | Input parameter |
| `unique_id` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `hasher = hashlib.sha256()`
2. `if text:`
3. `if unique_id:`
4. `return hasher.hexdigest()`

---

### `is_hw_allowed`
- **Signature**: `async def is_hw_allowed(msg: Message, target: Message, user_id: int) -> bool`
- **Source Reference**: [bot/handlers/user/hw_solver.py#L83-L96](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py#L83-L96)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет лимиты пользователя, статус обработки и наличие учебного содержимого.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `msg` | `Message` | Input parameter |
| `target` | `Message` | Input parameter |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if user_id != config.ALLOWED_USER_ID and not await check_user_rate_limit(user_id):`
2. `if await is_message_processed(msg.message_id):`
3. `has_media = bool(msg.photo or msg.document or target.photo or target.document)`
4. `prompt = combine_prompt_and_instructions(msg, target)`
5. `if not is_valid_homework_prompt(prompt, has_media):`
6. `return True`

---

### `acknowledge_hw_task`
- **Signature**: `async def acknowledge_hw_task(bot: Bot, msg: Message) -> None`
- **Source Reference**: [bot/handlers/user/hw_solver.py#L99-L108](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py#L99-L108)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Ставит реакцию-подтверждение о принятии задачи в очередь нейросети.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `bot` | `Bot` | Input parameter |
| `msg` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `dispatch_hw_task`
- **Signature**: `async def dispatch_hw_task( bot: Bot, msg: Message, user_id: int, prompt: str, meta: tuple[str | None, str | None, str | None, int] ) -> None`
- **Source Reference**: [bot/handlers/user/hw_solver.py#L111-L132](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py#L111-L132)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Формирует payload и отправляет задачу в очередь воркера para-solver.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `bot` | `Bot` | Input parameter |
| `msg` | `Message` | Input parameter |
| `user_id` | `int` | Input parameter |
| `prompt` | `str` | Input parameter |
| `meta` | `tuple[str | None, str | None, str | None, int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `f_id, f_name, mime, f_size = meta`
2. `task = {`
3. `await push_hw_task(task)`
4. `await acknowledge_hw_task(bot, msg)`

---

### `validate_hw_file_size`
- **Signature**: `async def validate_hw_file_size(bot: Bot, msg: Message, f_size: int, f_name: str | None) -> bool`
- **Source Reference**: [bot/handlers/user/hw_solver.py#L135-L148](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py#L135-L148)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет размер медиафайла (не более 20 МБ) для предотвращения OOM.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `bot` | `Bot` | Input parameter |
| `msg` | `Message` | Input parameter |
| `f_size` | `int` | Input parameter |
| `f_name` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if f_size > MAX_HW_FILE_SIZE:`
2. `return True`

---

### `handle_new_homework`
- **Signature**: `async def handle_new_homework(msg: Message, bot: Bot) -> None`
- **Source Reference**: [bot/handlers/user/hw_solver.py#L155-L175](file:///home/u/Рабочий стол/para/bot/handlers/user/hw_solver.py#L155-L175)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Перехватывает сообщение с ДЗ и отправляет в очередь воркера solver.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `msg` | `Message` | Input parameter |
| `bot` | `Bot` | Input parameter |

#### Step-by-Step Logic Execution
1. `user_id = msg.from_user.id if msg.from_user else 0`
2. `target = msg.reply_to_message if msg.reply_to_message else msg`
3. `if not await is_hw_allowed(msg, target, user_id):`
4. `prompt = combine_prompt_and_instructions(msg, target)`
5. `f_id, u_id, f_name, mime, f_size = extract_media_meta(msg, target)`
6. `if not await validate_hw_file_size(bot, msg, f_size, f_name):`

---
