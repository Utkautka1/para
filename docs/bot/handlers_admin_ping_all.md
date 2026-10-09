# Module Specification: `bot/handlers/admin/ping_all.py`
> **Path**: [`bot/handlers/admin/ping_all.py`](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py)  
> **Subsystem**: `Supergroup Alert Dispatch`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль хэндлера общего пинга одногруппников (/all). Позволяет администратору (ALLOWED_USER_ID) пинговать всех одногруппников в любом топике группы от лица бота. Список одногруппников подтягивается из единого источника birthdays.json. Особенности реализации: 1. Теги упоминаний прикрепляются открытым текстом внизу сообщения без спойлеров для мгновенной видимости и отправки push-уведомлений. 2. Для пользователей с username используется @username, без username — кликабельная ссылка <a href="tg://user?id=...">Имя</a>. 3. Отправитель команды автоматически исключается из пинга. 4. Исходное сообщение команды удаляется, пост отправляется от лица бота. 5. Полностью сохраняется исходное HTML-форматирование автора (жирный, курсив, ссылки). 6. Поддерживается ответ на сообщение (reply) и медиафайлы с подписью.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`load_classmates_list`](#load_classmates_list) | Function | L39–L46 | `list[dict[str, Any]]` | Загружает актуальный список одногруппников из JSON-файла. |
| [`resolve_person_tg_id`](#resolve_person_tg_id) | Function | L49–L56 | `int | None` | Извлекает tg_id из записи или постоянного кэша пользователей |
| [`format_mention_tag`](#format_mention_tag) | Function | L59–L74 | `str | None` | Формирует кликабельный тег упоминания. |
| [`is_sender`](#is_sender) | Function | L77–L85 | `bool` | Проверяет, является ли запись в реестре отправителем команды |
| [`build_mentions_block`](#build_mentions_block) | Function | L88–L100 | `str` | Формирует список тегов упоминаний участников чата без автора |
| [`extract_broadcast_text`](#extract_broadcast_text) | Function | L103–L116 | `str` | Извлекает пользовательский HTML-текст после команды /all или |
| [`build_broadcast_message`](#build_broadcast_message) | Function | L119–L127 | `str` | Собирает итоговый HTML: текст автора сверху, блок пингов в с |
| [`safe_delete_command_message`](#safe_delete_command_message) | Function | L130–L144 | `None` | Безопасно удаляет триггер-сообщение автора команды. |
| [`send_broadcast_payload`](#send_broadcast_payload) | Function | L147–L168 | `Message` | Отправляет пост от лица бота в целевой чат и топик (текст ил |
| [`validate_group_chat`](#validate_group_chat) | Function | L171–L180 | `bool` | Проверяет, что команда вызвана в группе или супергруппе, а н |
| [`compose_broadcast_content`](#compose_broadcast_content) | Function | L183–L195 | `tuple[str, int | None]` | Формирует итоговый HTML рассылки и определяет ID реплая. |
| [`dispatch_broadcast`](#dispatch_broadcast) | Function | L198–L210 | `None` | Выполняет отправку поста и удаление исходной команды с логир |
| [`cmd_ping_all`](#cmd_ping_all) | Function | L214–L224 | `None` | Координирует валидацию, компоновку и отправку общего пинга г |

---

## 3. Exhaustive Function Specifications

### `load_classmates_list`
- **Signature**: `async def load_classmates_list() -> list[dict[str, Any]]`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L39-L46](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L39-L46)
- **Async**: `Yes`
- **Return Type**: `list[dict[str, Any]]`

#### Purpose & Architectural Intent
Загружает актуальный список одногруппников из JSON-файла. Используем data/birthdays.json как единый источник правды, чтобы не дублировать данные студентов в разных файлах.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `return await load_json(BIRTHDAYS_FILE_PATH, default=[])`

---

### `resolve_person_tg_id`
- **Signature**: `def resolve_person_tg_id(person: dict[str, Any]) -> int | None`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L49-L56](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L49-L56)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Извлекает tg_id из записи или постоянного кэша пользователей.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `person` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `if person.get("tg_id"):`
2. `username = person.get("username")`
3. `return get_cached_user_id(username) if username else None`

---

### `format_mention_tag`
- **Signature**: `def format_mention_tag(person: dict[str, Any]) -> str | None`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L59-L74](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L59-L74)
- **Async**: `No`
- **Return Type**: `str | None`

#### Purpose & Architectural Intent
Формирует кликабельный тег упоминания. Приоритет отдается tg_id: Telegram шлет пуш-уведомление ТОЛЬКО для ссылок tg://user?id= (text_mention), а обычный @username ботом игнорирует.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `person` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `tg_id = resolve_person_tg_id(person)`
2. `username = person.get("username")`
3. `name = html.escape(person.get("full_name", ""))`
4. `if tg_id:`
5. `if username:`
6. `return None`

---

### `is_sender`
- **Signature**: `def is_sender(person: dict[str, Any], sender_id: int | None, sender_username: str | None) -> bool`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L77-L85](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L77-L85)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, является ли запись в реестре отправителем команды. Сверяет как по числовому Telegram ID, так и по регистронезависимому юзернейму.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `person` | `dict[str, Any]` | Input parameter |
| `sender_id` | `int | None` | Input parameter |
| `sender_username` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if sender_id and person.get("tg_id") == sender_id:`
2. `return bool(sender_username and person.get("username") and person["username"].lower()`

---

### `build_mentions_block`
- **Signature**: `def build_mentions_block(classmates: list[dict[str, Any]], sender: User | None) -> str`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L88-L100](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L88-L100)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует список тегов упоминаний участников чата без автора команды.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `classmates` | `list[dict[str, Any]]` | Input parameter |
| `sender` | `User | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `sender_id = sender.id if sender else None`
2. `sender_user = sender.username if sender else None`
3. `tags = [`
4. `valid_tags = [t for t in tags if t]`
5. `return " ".join(valid_tags)`

---

### `extract_broadcast_text`
- **Signature**: `def extract_broadcast_text(html_text: str) -> str`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L103-L116](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L103-L116)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Извлекает пользовательский HTML-текст после команды /all или .all. Отрезает саму команду с префиксом (/ или .) и упоминанием бота, сохраняя все дочерние теги разметки (жирный, курсив, ссылки, моноширинный).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `html_text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `return re.sub(`

---

### `build_broadcast_message`
- **Signature**: `def build_broadcast_message(user_html: str, mentions: str, has_reply: bool = False) -> str`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L119-L127](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L119-L127)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Собирает итоговый HTML: текст автора сверху, блок пингов в самом низу.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_html` | `str` | Input parameter |
| `mentions` | `str` | Input parameter |
| `has_reply` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if user_html:`
2. `if has_reply:`
3. `return f"📢 <b>Общий сбор группы!</b>\n\n{mentions}"`

---

### `safe_delete_command_message`
- **Signature**: `async def safe_delete_command_message(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L130-L144](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L130-L144)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Безопасно удаляет триггер-сообщение автора команды. Игнорирует ошибки, если сообщение уже удалено пользователем или таймером.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `send_broadcast_payload`
- **Signature**: `async def send_broadcast_payload(message: Message, final_html: str, reply_to_id: int | None) -> Message`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L147-L168](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L147-L168)
- **Async**: `Yes`
- **Return Type**: `Message`

#### Purpose & Architectural Intent
Отправляет пост от лица бота в целевой чат и топик (текст или медиа). При наличии фото/видео/документа копирует его с новым описанием.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `final_html` | `str` | Input parameter |
| `reply_to_id` | `int | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `thread_id = message.message_thread_id`
2. `if message.photo or message.video or message.document or message.animation:`
3. `return await message.bot.send_message(`

---

### `validate_group_chat`
- **Signature**: `async def validate_group_chat(message: Message) -> bool`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L171-L180](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L171-L180)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет, что команда вызвана в группе или супергруппе, а не в ЛС. При вызове в приватном диалоге выводит предупреждение и возвращает False.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if message.chat.type == "private":`
2. `return True`

---

### `compose_broadcast_content`
- **Signature**: `def compose_broadcast_content( classmates: list[dict[str, Any]], message: Message ) -> tuple[str, int | None]`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L183-L195](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L183-L195)
- **Async**: `No`
- **Return Type**: `tuple[str, int | None]`

#### Purpose & Architectural Intent
Формирует итоговый HTML рассылки и определяет ID реплая. Размещает текст автора вверху, а пинги одногруппников — внизу сообщения.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `classmates` | `list[dict[str, Any]]` | Input parameter |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `mentions = build_mentions_block(classmates, message.from_user)`
2. `user_html = extract_broadcast_text(message.html_text or "")`
3. `reply_id = message.reply_to_message.message_id if message.reply_to_message else None`
4. `final_text = build_broadcast_message(user_html, mentions, has_reply=bool(reply_id))`
5. `return final_text, reply_id`

---

### `dispatch_broadcast`
- **Signature**: `async def dispatch_broadcast(message: Message, final_text: str, reply_id: int | None) -> None`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L198-L210](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L198-L210)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Выполняет отправку поста и удаление исходной команды с логированием. Перехватывает ошибки доставки, информируя инициатора команды при сбое.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `final_text` | `str` | Input parameter |
| `reply_id` | `int | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `cmd_ping_all`
- **Signature**: `async def cmd_ping_all(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/ping_all.py#L214-L224](file:///home/u/Рабочий стол/para/bot/handlers/admin/ping_all.py#L214-L224)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Координирует валидацию, компоновку и отправку общего пинга группы. Выступает чистым оркестратором без смешения бизнес-логики.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not await validate_group_chat(message):`
2. `classmates = await load_classmates_list()`
3. `final_text, reply_id = compose_broadcast_content(classmates, message)`
4. `await dispatch_broadcast(message, final_text, reply_id)`

---
