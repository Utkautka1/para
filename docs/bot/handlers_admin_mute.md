# Module Specification: `bot/handlers/admin/mute.py`
> **Path**: [`bot/handlers/admin/mute.py`](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py)  
> **Subsystem**: `Moderation Ban Engine`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Хэндлеры команд модерации и ограничения отправки сообщений (Мут в топиках).

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`cache_user_from_message`](#cache_user_from_message) | Function | L21–L32 | `None` | Сохраняет username и user_id участников в постоянный кэш. |
| [`_find_in_admins`](#_find_in_admins) | Function | L35–L47 | `tuple[int, str] | None` | Ищет пользователя среди администраторов чата. |
| [`_find_in_registry`](#_find_in_registry) | Function | L50–L60 | `tuple[int, str] | None` | Ищет пользователя в реестре студентов по username. |
| [`resolve_user_id_by_username`](#resolve_user_id_by_username) | Function | L63–L72 | `tuple[int, str] | None` | Находит ID пользователя по юзернейму через кэш, реестр или а |
| [`_resolve_from_entities`](#_resolve_from_entities) | Function | L76–L83 | `tuple[int, str] | None` | Извлекает ID пользователя из сущностей упоминания (text_ment |
| [`resolve_target_identity`](#resolve_target_identity) | Function | L86–L98 | `tuple[int | None, str]` | Определяет ID и отображаемое имя из аргументов или сущностей |
| [`_strip_mute_prefix`](#_strip_mute_prefix) | Function | L101–L107 | `str` | Удаляет префикс команды мута из текста. |
| [`parse_reply_mute_args`](#parse_reply_mute_args) | Function | L110–L119 | `tuple[str, str]` | Парсит длительность и причину при реплае. |
| [`parse_standalone_mute_args`](#parse_standalone_mute_args) | Function | L122–L136 | `tuple[int | None, str, str, str]` | Парсит аргументы при прямом указании ID/@username без реплая |
| [`extract_target_id_and_args`](#extract_target_id_and_args) | Function | L139–L145 | `tuple[int | None, str, str, str]` | Извлекает target_id, имя, время и причину из реплая или текс |
| [`apply_user_restriction`](#apply_user_restriction) | Function | L148–L156 | `None` | Применяет ограничение отправки сообщений для пользователя. |
| [`_apply_unmute_permissions`](#_apply_unmute_permissions) | Function | L159–L166 | `None` | Снимает ограничения на отправку всех типов сообщений. |
| [`send_mute_notification`](#send_mute_notification) | Function | L169–L175 | `None` | Отправляет отчет о муте/размуте в чат или топик. |
| [`_safe_delete_message`](#_safe_delete_message) | Function | L178–L189 | `None` | Удаляет сервисную команду в публичном чате без выброса исклю |
| [`_build_mute_report`](#_build_mute_report) | Function | L192–L199 | `str` | Формирует HTML-текст отчета о наложении мута. |
| [`is_mute_command`](#is_mute_command) | Function | L202–L207 | `bool` | Проверяет команду наложения мута. |
| [`is_unmute_command`](#is_unmute_command) | Function | L210–L215 | `bool` | Проверяет команду снятия мута. |
| [`cmd_mute_user`](#cmd_mute_user) | Function | L219–L236 | `None` | Ограничивает отправку сообщений пользователем в основном чат |
| [`cmd_unmute_user`](#cmd_unmute_user) | Function | L240–L256 | `None` | Снимает ограничение отправки сообщений с пользователя. |

---

## 3. Exhaustive Function Specifications

### `cache_user_from_message`
- **Signature**: `def cache_user_from_message(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/mute.py#L21-L32](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L21-L32)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Сохраняет username и user_id участников в постоянный кэш.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if message.from_user and message.from_user.username:`
2. `if message.reply_to_message and message.reply_to_message.from_user:`
3. `if message.entities:`

---

### `_find_in_admins`
- **Signature**: `async def _find_in_admins(bot, chat_id: int, clean: str) -> tuple[int, str] | None`
- **Source Reference**: [bot/handlers/admin/mute.py#L35-L47](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L35-L47)
- **Async**: `Yes`
- **Return Type**: `tuple[int, str] | None`

#### Purpose & Architectural Intent
Ищет пользователя среди администраторов чата.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `bot` | `Any` | Input parameter |
| `chat_id` | `int` | Input parameter |
| `clean` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`
2. `return None`

---

### `_find_in_registry`
- **Signature**: `def _find_in_registry(clean: str) -> tuple[int, str] | None`
- **Source Reference**: [bot/handlers/admin/mute.py#L50-L60](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L50-L60)
- **Async**: `No`
- **Return Type**: `tuple[int, str] | None`

#### Purpose & Architectural Intent
Ищет пользователя в реестре студентов по username.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `clean` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `from services.classmates_auth import load_classmates_registry`
2. `registry = load_classmates_registry()`
3. `for student in registry:`
4. `return None`

---

### `resolve_user_id_by_username`
- **Signature**: `async def resolve_user_id_by_username(bot, chat_id: int, username: str) -> tuple[int, str] | None`
- **Source Reference**: [bot/handlers/admin/mute.py#L63-L72](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L63-L72)
- **Async**: `Yes`
- **Return Type**: `tuple[int, str] | None`

#### Purpose & Architectural Intent
Находит ID пользователя по юзернейму через кэш, реестр или админов.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `bot` | `Any` | Input parameter |
| `chat_id` | `int` | Input parameter |
| `username` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `clean = username.lstrip("@").lower()`
2. `cached_id = get_cached_user_id(clean)`
3. `if cached_id:`
4. `reg_match = _find_in_registry(clean)`
5. `if reg_match:`
6. `return await _find_in_admins(bot, chat_id, clean)`

---

### `_resolve_from_entities`
- **Signature**: `def _resolve_from_entities(message: Message) -> tuple[int, str] | None`
- **Source Reference**: [bot/handlers/admin/mute.py#L76-L83](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L76-L83)
- **Async**: `No`
- **Return Type**: `tuple[int, str] | None`

#### Purpose & Architectural Intent
Извлекает ID пользователя из сущностей упоминания (text_mention).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not message.entities:`
2. `for e in message.entities:`
3. `return None`

---

### `resolve_target_identity`
- **Signature**: `async def resolve_target_identity(message: Message, target_raw: str) -> tuple[int | None, str]`
- **Source Reference**: [bot/handlers/admin/mute.py#L86-L98](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L86-L98)
- **Async**: `Yes`
- **Return Type**: `tuple[int | None, str]`

#### Purpose & Architectural Intent
Определяет ID и отображаемое имя из аргументов или сущностей сообщения.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `target_raw` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if target_raw.isdigit():`
2. `from_ent = _resolve_from_entities(message)`
3. `if from_ent:`
4. `if target_raw.startswith("@"):`
5. `return None, f"<b>{html.escape(target_raw)}</b>"`

---

### `_strip_mute_prefix`
- **Signature**: `def _strip_mute_prefix(text: str) -> str`
- **Source Reference**: [bot/handlers/admin/mute.py#L101-L107](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L101-L107)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Удаляет префикс команды мута из текста.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `clean_text = text.strip()`
2. `for prefix in [".закрыть рот", ".закрой рот"]:`
3. `return clean_text`

---

### `parse_reply_mute_args`
- **Signature**: `def parse_reply_mute_args(text: str) -> tuple[str, str]`
- **Source Reference**: [bot/handlers/admin/mute.py#L110-L119](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L110-L119)
- **Async**: `No`
- **Return Type**: `tuple[str, str]`

#### Purpose & Architectural Intent
Парсит длительность и причину при реплае.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `parts = _strip_mute_prefix(text).split(maxsplit=1)`
2. `if not parts or not parts[0]:`
3. `first, rest = parts[0], parts[1] if len(parts) > 1 else ""`
4. `if parse_duration_to_seconds(first) is not None:`
5. `reason = f"{first} {rest}".strip() if rest else first`
6. `return "10м", reason`

---

### `parse_standalone_mute_args`
- **Signature**: `async def parse_standalone_mute_args(message: Message) -> tuple[int | None, str, str, str]`
- **Source Reference**: [bot/handlers/admin/mute.py#L122-L136](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L122-L136)
- **Async**: `Yes`
- **Return Type**: `tuple[int | None, str, str, str]`

#### Purpose & Architectural Intent
Парсит аргументы при прямом указании ID/@username без реплая.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `parts = (message.text or "").strip().split(maxsplit=3)`
2. `if len(parts) < 2:`
3. `target_raw = parts[1]`
4. `second = parts[2] if len(parts) > 2 else "10м"`
5. `third = parts[3] if len(parts) > 3 else "без указания причины"`
6. `if parse_duration_to_seconds(second) is not None:`

---

### `extract_target_id_and_args`
- **Signature**: `async def extract_target_id_and_args(message: Message) -> tuple[int | None, str, str, str]`
- **Source Reference**: [bot/handlers/admin/mute.py#L139-L145](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L139-L145)
- **Async**: `Yes`
- **Return Type**: `tuple[int | None, str, str, str]`

#### Purpose & Architectural Intent
Извлекает target_id, имя, время и причину из реплая или текста.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if message.reply_to_message and message.reply_to_message.from_user:`
2. `return await parse_standalone_mute_args(message)`

---

### `apply_user_restriction`
- **Signature**: `async def apply_user_restriction(bot, chat_id: int, user_id: int, duration_sec: int) -> None`
- **Source Reference**: [bot/handlers/admin/mute.py#L148-L156](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L148-L156)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Применяет ограничение отправки сообщений для пользователя.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `bot` | `Any` | Input parameter |
| `chat_id` | `int` | Input parameter |
| `user_id` | `int` | Input parameter |
| `duration_sec` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `until_dt = datetime.now(TIMEZONE) + timedelta(seconds=duration_sec)`
2. `await bot.restrict_chat_member(`

---

### `_apply_unmute_permissions`
- **Signature**: `async def _apply_unmute_permissions(bot, chat_id: int, user_id: int) -> None`
- **Source Reference**: [bot/handlers/admin/mute.py#L159-L166](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L159-L166)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Снимает ограничения на отправку всех типов сообщений.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `bot` | `Any` | Input parameter |
| `chat_id` | `int` | Input parameter |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `full_perms = ChatPermissions(`
2. `await bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=full_per`

---

### `send_mute_notification`
- **Signature**: `async def send_mute_notification(message: Message, res_text: str) -> None`
- **Source Reference**: [bot/handlers/admin/mute.py#L169-L175](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L169-L175)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет отчет о муте/размуте в чат или топик.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |
| `res_text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if message.chat.type == "private":`

---

### `_safe_delete_message`
- **Signature**: `async def _safe_delete_message(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/mute.py#L178-L189](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L178-L189)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Удаляет сервисную команду в публичном чате без выброса исключений.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if message.chat.type != "private":`

---

### `_build_mute_report`
- **Signature**: `def _build_mute_report(target_name: str, time_raw: str, reason: str) -> str`
- **Source Reference**: [bot/handlers/admin/mute.py#L192-L199](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L192-L199)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует HTML-текст отчета о наложении мута.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `target_name` | `str` | Input parameter |
| `time_raw` | `str` | Input parameter |
| `reason` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `return (`

---

### `is_mute_command`
- **Signature**: `def is_mute_command(text: str | None) -> bool`
- **Source Reference**: [bot/handlers/admin/mute.py#L202-L207](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L202-L207)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет команду наложения мута.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not text:`
2. `t = text.lower().strip()`
3. `return t.startswith((".закрыть рот", ".закрой рот"))`

---

### `is_unmute_command`
- **Signature**: `def is_unmute_command(text: str | None) -> bool`
- **Source Reference**: [bot/handlers/admin/mute.py#L210-L215](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L210-L215)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет команду снятия мута.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not text:`
2. `t = text.lower().strip()`
3. `return t.startswith((".открыть рот", ".открой рот"))`

---

### `cmd_mute_user`
- **Signature**: `async def cmd_mute_user(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/mute.py#L219-L236](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L219-L236)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Ограничивает отправку сообщений пользователем в основном чате группы.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `cache_user_from_message(message)`
2. `if not message.from_user or message.from_user.id != ALLOWED_USER_ID:`
3. `target_id, target_name, time_raw, reason = await extract_target_id_and_args(message)`
4. `if not target_id:`
5. `duration_sec = parse_duration_to_seconds(time_raw) or 600`
6. `target_chat_id = message.chat.id if message.chat.type != "private" else TOPIC_CHAT_ID`

---

### `cmd_unmute_user`
- **Signature**: `async def cmd_unmute_user(message: Message) -> None`
- **Source Reference**: [bot/handlers/admin/mute.py#L240-L256](file:///home/u/Рабочий стол/para/bot/handlers/admin/mute.py#L240-L256)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Снимает ограничение отправки сообщений с пользователя.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `message` | `Message` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not message.from_user or message.from_user.id != ALLOWED_USER_ID:`
2. `target_id, target_name, _, _ = await extract_target_id_and_args(message)`
3. `if not target_id:`
4. `target_chat_id = message.chat.id if message.chat.type != "private" else TOPIC_CHAT_ID`
5. `try:`

---
