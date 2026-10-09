# Module Specification: `services/birthday_manager.py`
> **Path**: [`services/birthday_manager.py`](file:///home/u/Рабочий стол/para/services/birthday_manager.py)  
> **Subsystem**: `Student Lifecycle`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Менеджер дней рождения группы 1-КПД-3. Отвечает за: 1. Синхронизацию закрепленного реестра дней рождения в топике 6269. 2. Ежедневный пересчет дней до праздника и исполняющегося возраста. 3. Отправку персональных поздравлений в топик «Важное» (ID: 2).

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`calculate_days_and_age`](#calculate_days_and_age) | Function | L41–L60 | `dict[str, Any]` | Вычисляет оставшиеся дни до дня рождения и возраст именинник |
| [`format_person_tag`](#format_person_tag) | Function | L71–L82 | `str` | Формирует кликабельное имя человека (через username или tg:/ |
| [`format_days_left_badge`](#format_days_left_badge) | Function | L85–L101 | `str` | Формирует человекочитаемый бейдж оставшихся дней. |
| [`format_today_block`](#format_today_block) | Function | L104–L115 | `list[str]` | Формирует праздничный блок для именинников сегодняшнего дня. |
| [`format_age_badge`](#format_age_badge) | Function | L118–L130 | `str` | Формирует строку возраста с правильным склонением (лет/год/г |
| [`format_upcoming_block`](#format_upcoming_block) | Function | L133–L152 | `list[str]` | Формирует блок ближайших именинников в цитате. |
| [`season_sort_key`](#season_sort_key) | Function | L155–L159 | `int` | Вычисляет индекс сортировки даты внутри сезона. |
| [`format_season_block`](#format_season_block) | Function | L162–L178 | `list[str]` | Форматирует список именинников для одного сезона с указанием |
| [`format_birthday_registry_text`](#format_birthday_registry_text) | Function | L181–L197 | `str` | Формирует двухуровневый реестр дней рождения с сезонами и бл |
| [`pick_unique_wish`](#pick_unique_wish) | Function | L200–L214 | `str` | Выбирает случайное неповторяющееся поздравление для участник |
| [`get_person_mention`](#get_person_mention) | Function | L217–L227 | `str` | Формирует кликабельное упоминание для персонального поздравл |
| [`format_starosta_block`](#format_starosta_block) | Function | L230–L237 | `str` | Формирует блок слова старосты, если он задан. |
| [`format_congrats_message`](#format_congrats_message) | Function | L240–L257 | `str` | Формирует праздничное персональное поздравление от группы и  |
| [`_send_congrats_telegram`](#_send_congrats_telegram) | Function | L260–L272 | `None` | Отправляет поздравление в Telegram и фиксирует статус. |
| [`send_congrats_for_item`](#send_congrats_for_item) | Function | L275–L287 | `None` | Отправляет персональное поздравление в топик 'Важное' (ID: 2 |
| [`is_morning_congrats_time`](#is_morning_congrats_time) | Function | L290–L292 | `bool` | Проверяет наступление утреннего времени поздравлений (07:00  |
| [`check_and_send_birthday_congratulations`](#check_and_send_birthday_congratulations) | Function | L295–L304 | `None` | Проверяет сегодняшних именинников и отправляет поздравления  |
| [`_edit_existing_birthday_message`](#_edit_existing_birthday_message) | Function | L307–L317 | `bool` | Пытается отредактировать существующее сообщение реестра ДР. |
| [`_create_new_birthday_message`](#_create_new_birthday_message) | Function | L320–L335 | `bool` | Создает новое сообщение реестра ДР и закрепляет его без звук |
| [`update_birthday_pinned_message`](#update_birthday_pinned_message) | Function | L338–L344 | `bool` | Обновляет существующее или создает новое закрепленное сообще |
| [`sync_birthdays_topic`](#sync_birthdays_topic) | Function | L347–L359 | `bool` | Основной цикл синхронизации реестра ДР и проверки поздравлен |
| [`birthday_sync_loop`](#birthday_sync_loop) | Function | L362–L371 | `None` | Фоновый цикл проверки дней рождения (каждые 30 минут). |

---

## 3. Exhaustive Function Specifications

### `calculate_days_and_age`
- **Signature**: `def calculate_days_and_age(item: dict[str, Any], today: date) -> dict[str, Any]`
- **Source Reference**: [services/birthday_manager.py#L41-L60](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L41-L60)
- **Async**: `No`
- **Return Type**: `dict[str, Any]`

#### Purpose & Architectural Intent
Вычисляет оставшиеся дни до дня рождения и возраст именинника.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Input parameter |
| `today` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `b_day, b_month, b_year = item["day"], item["month"], item["year"]`
2. `try:`
3. `if bday_this_year < today:`
4. `return {**item, "days_until": days, "turning_age": age, "is_today": is_today}`

---

### `format_person_tag`
- **Signature**: `def format_person_tag(item: dict[str, Any]) -> str`
- **Source Reference**: [services/birthday_manager.py#L71-L82](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L71-L82)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует кликабельное имя человека (через username или tg://user?id).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `name = item["full_name"]`
2. `username = item.get("username")`
3. `tg_id = item.get("tg_id")`
4. `if username:`
5. `if tg_id:`
6. `return name`

---

### `format_days_left_badge`
- **Signature**: `def format_days_left_badge(days: int) -> str`
- **Source Reference**: [services/birthday_manager.py#L85-L101](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L85-L101)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует человекочитаемый бейдж оставшихся дней.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `days` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if days == 0:`
2. `if days == 1:`
3. `last_two = days % 100`
4. `last_one = days % 10`
5. `if 11 <= last_two <= 14:`
6. `if last_one == 1:`

---

### `format_today_block`
- **Signature**: `def format_today_block(today_items: list[dict[str, Any]]) -> list[str]`
- **Source Reference**: [services/birthday_manager.py#L104-L115](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L104-L115)
- **Async**: `No`
- **Return Type**: `list[str]`

#### Purpose & Architectural Intent
Формирует праздничный блок для именинников сегодняшнего дня.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `today_items` | `list[dict[str, Any]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not today_items:`
2. `lines = ["🎉 <b>СЕГОДНЯ ДЕНЬ РОЖДЕНИЯ!</b>", "<blockquote>"]`
3. `for i in today_items:`
4. `lines.append("</blockquote>\n")`
5. `return lines`

---

### `format_age_badge`
- **Signature**: `def format_age_badge(age: int) -> str`
- **Source Reference**: [services/birthday_manager.py#L118-L130](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L118-L130)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует строку возраста с правильным склонением (лет/год/года).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `age` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `last_two = age % 100`
2. `last_one = age % 10`
3. `if 11 <= last_two <= 14:`
4. `if last_one == 1:`
5. `if 2 <= last_one <= 4:`
6. `return f"{age} лет"`

---

### `format_upcoming_block`
- **Signature**: `def format_upcoming_block(items: list[dict[str, Any]]) -> list[str]`
- **Source Reference**: [services/birthday_manager.py#L133-L152](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L133-L152)
- **Async**: `No`
- **Return Type**: `list[str]`

#### Purpose & Architectural Intent
Формирует блок ближайших именинников в цитате.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `items` | `list[dict[str, Any]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `upcoming = [i for i in items if not i.get("is_today")]`
2. `near = [i for i in upcoming if i["days_until"] <= 45]`
3. `if len(near) < 3:`
4. `if not near:`
5. `lines = ["<blockquote>⏳ <b>БЛИЖАЙШИЕ ПРАЗДНИКИ:</b>"]`
6. `for i in near:`

---

### `season_sort_key`
- **Signature**: `def season_sort_key(item: dict[str, Any], months: list[int]) -> int`
- **Source Reference**: [services/birthday_manager.py#L155-L159](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L155-L159)
- **Async**: `No`
- **Return Type**: `int`

#### Purpose & Architectural Intent
Вычисляет индекс сортировки даты внутри сезона.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Input parameter |
| `months` | `list[int]` | Input parameter |

#### Step-by-Step Logic Execution
1. `return months.index(item["month"]) * 100 + item["day"]`

---

### `format_season_block`
- **Signature**: `def format_season_block(title: str, months: list[int], all_items: list[dict[str, Any]]) -> list[str]`
- **Source Reference**: [services/birthday_manager.py#L162-L178](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L162-L178)
- **Async**: `No`
- **Return Type**: `list[str]`

#### Purpose & Architectural Intent
Форматирует список именинников для одного сезона с указанием возраста.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `title` | `str` | Input parameter |
| `months` | `list[int]` | Input parameter |
| `all_items` | `list[dict[str, Any]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `s_items = [i for i in all_items if i["month"] in months]`
2. `s_items.sort(key=lambda x: season_sort_key(x, months))`
3. `if not s_items:`
4. `lines = [f"<b>{title}</b>"]`
5. `for i in s_items:`
6. `lines.append("")`

---

### `format_birthday_registry_text`
- **Signature**: `def format_birthday_registry_text(items: list[dict[str, Any]]) -> str`
- **Source Reference**: [services/birthday_manager.py#L181-L197](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L181-L197)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует двухуровневый реестр дней рождения с сезонами и ближайшими.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `items` | `list[dict[str, Any]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `lines = [`
2. `lines.extend(format_today_block([i for i in items if i.get("is_today")]))`
3. `lines.extend(format_upcoming_block(items))`
4. `for title, months in SEASONS_INFO:`
5. `lines.append("────────────────────────────")`
6. `lines.append("<i>🔄 Бот ежедневно обновляет реестр и поздравляет в 07:00</i>")`

---

### `pick_unique_wish`
- **Signature**: `def pick_unique_wish(person_key: str, wishes: list[str], history_file: str = HISTORY_FILE) -> str`
- **Source Reference**: [services/birthday_manager.py#L200-L214](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L200-L214)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Выбирает случайное неповторяющееся поздравление для участника.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `person_key` | `str` | Input parameter |
| `wishes` | `list[str]` | Input parameter |
| `history_file` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not wishes:`
2. `history: dict[str, list[int]] = load_json_file(history_file, {})`
3. `used_indices = set(history.get(person_key, []))`
4. `available = [idx for idx in range(len(wishes)) if idx not in used_indices]`
5. `if not available:`
6. `choice_idx = random.choice(available)  # nosec B311`

---

### `get_person_mention`
- **Signature**: `def get_person_mention(item: dict[str, Any]) -> str`
- **Source Reference**: [services/birthday_manager.py#L217-L227](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L217-L227)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует кликабельное упоминание для персонального поздравления.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `username = item.get("username")`
2. `tg_id = item.get("tg_id")`
3. `if username:`
4. `if tg_id:`
5. `return item["full_name"]`

---

### `format_starosta_block`
- **Signature**: `def format_starosta_block(starosta_text: str | None) -> str`
- **Source Reference**: [services/birthday_manager.py#L230-L237](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L230-L237)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует блок слова старосты, если он задан.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `starosta_text` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not starosta_text:`
2. `return (`

---

### `format_congrats_message`
- **Signature**: `def format_congrats_message( item: dict[str, Any], wish_text: str, starosta_text: str | None = None ) -> str`
- **Source Reference**: [services/birthday_manager.py#L240-L257](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L240-L257)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует праздничное персональное поздравление от группы и старосты.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Input parameter |
| `wish_text` | `str` | Input parameter |
| `starosta_text` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `mention = get_person_mention(item)`
2. `name = item["full_name"]`
3. `age = item.get("turning_age", 18)`
4. `is_starosta = name == "Стрыгин Дмитрий"`
5. `s_block = format_starosta_block(None if is_starosta else starosta_text)`
6. `mid = f"{s_block}\n\n" if s_block else ""`

---

### `_send_congrats_telegram`
- **Signature**: `async def _send_congrats_telegram( text: str, person_key: str, key: str, state: dict[str, bool] ) -> None`
- **Source Reference**: [services/birthday_manager.py#L260-L272](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L260-L272)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет поздравление в Telegram и фиксирует статус.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |
| `person_key` | `str` | Input parameter |
| `key` | `str` | Input parameter |
| `state` | `dict[str, bool]` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `send_congrats_for_item`
- **Signature**: `async def send_congrats_for_item(item: dict[str, Any], today_str: str) -> None`
- **Source Reference**: [services/birthday_manager.py#L275-L287](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L275-L287)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Отправляет персональное поздравление в топик 'Важное' (ID: 2).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `item` | `dict[str, Any]` | Input parameter |
| `today_str` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `congrats_state: dict[str, bool] = load_json_file(CONGRATS_STATE_FILE, {})`
2. `person_key = item["full_name"]`
3. `congrats_key = f"{today_str}_{person_key}"`
4. `if congrats_state.get(congrats_key):`
5. `wishes = load_json_file(WISHES_FILE, [])`
6. `s_wishes = load_json_file(STAROSTA_WISHES_FILE, [])`

---

### `is_morning_congrats_time`
- **Signature**: `def is_morning_congrats_time(now_dt: datetime) -> bool`
- **Source Reference**: [services/birthday_manager.py#L290-L292](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L290-L292)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет наступление утреннего времени поздравлений (07:00 МСК).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `now_dt` | `datetime` | Input parameter |

#### Step-by-Step Logic Execution
1. `return now_dt.hour >= 7`

---

### `check_and_send_birthday_congratulations`
- **Signature**: `async def check_and_send_birthday_congratulations(items: list[dict[str, Any]], today: date) -> None`
- **Source Reference**: [services/birthday_manager.py#L295-L304](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L295-L304)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Проверяет сегодняшних именинников и отправляет поздравления строго с 07:00.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `items` | `list[dict[str, Any]]` | Input parameter |
| `today` | `date` | Input parameter |

#### Step-by-Step Logic Execution
1. `now_dt = datetime.now(TIMEZONE)`
2. `if not is_morning_congrats_time(now_dt):`
3. `today_str = today.isoformat()`
4. `for item in items:`

---

### `_edit_existing_birthday_message`
- **Signature**: `async def _edit_existing_birthday_message(msg_id: int, text: str) -> bool`
- **Source Reference**: [services/birthday_manager.py#L307-L317](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L307-L317)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Пытается отредактировать существующее сообщение реестра ДР.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `msg_id` | `int` | Input parameter |
| `text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `_create_new_birthday_message`
- **Signature**: `async def _create_new_birthday_message(text: str) -> bool`
- **Source Reference**: [services/birthday_manager.py#L320-L335](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L320-L335)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Создает новое сообщение реестра ДР и закрепляет его без звука.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `update_birthday_pinned_message`
- **Signature**: `async def update_birthday_pinned_message(text: str) -> bool`
- **Source Reference**: [services/birthday_manager.py#L338-L344](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L338-L344)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Обновляет существующее или создает новое закрепленное сообщение реестра ДР.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `state = load_json_file(STATE_FILE, {})`
2. `main_msg_id = state.get("main_msg_id")`
3. `if main_msg_id and await _edit_existing_birthday_message(main_msg_id, text):`
4. `return await _create_new_birthday_message(text)`

---

### `sync_birthdays_topic`
- **Signature**: `async def sync_birthdays_topic() -> bool`
- **Source Reference**: [services/birthday_manager.py#L347-L359](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L347-L359)
- **Async**: `Yes`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Основной цикл синхронизации реестра ДР и проверки поздравлений.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `now_dt = datetime.now(TIMEZONE)`
2. `today = now_dt.date()`
3. `raw_birthdays: list[dict[str, Any]] = load_json_file(BIRTHDAYS_FILE, [])`
4. `if not raw_birthdays:`
5. `processed = [calculate_days_and_age(i, today) for i in raw_birthdays]`
6. `processed.sort(key=lambda x: x["days_until"])`

---

### `birthday_sync_loop`
- **Signature**: `async def birthday_sync_loop() -> None`
- **Source Reference**: [services/birthday_manager.py#L362-L371](file:///home/u/Рабочий стол/para/services/birthday_manager.py#L362-L371)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Фоновый цикл проверки дней рождения (каждые 30 минут).

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `log.info("Запущен фоновый сервис дней рождения КТМУ")`
2. `await asyncio.sleep(5)`
3. `while True:`

---
