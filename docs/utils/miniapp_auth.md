# Module Specification: `utils/miniapp_auth.py`
> **Path**: [`utils/miniapp_auth.py`](file:///home/u/Рабочий стол/para/utils/miniapp_auth.py)  
> **Subsystem**: `HMAC-SHA256 Auth`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль криптографической аутентификации Telegram Mini App и сессий тестеров. Реализует официальный алгоритм валидации Telegram.WebApp.initData через HMAC-SHA256, проверку срока действия auth_date для защиты от replay-атак и генерацию подписанных сессионных токенов для безопасного тестирования API через Swagger UI.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`_build_data_check_string`](#_build_data_check_string) | Function | L23–L28 | `str` | Формирует каноническую строку для проверки подписи initData. |
| [`_compute_init_data_hash`](#_compute_init_data_hash) | Function | L31–L34 | `str` | Вычисляет HMAC-SHA256 хеш данных initData с секретом бота. |
| [`_is_auth_date_valid`](#_is_auth_date_valid) | Function | L37–L44 | `bool` | Проверяет актуальность auth_date для защиты от replay-атак. |
| [`validate_telegram_init_data`](#validate_telegram_init_data) | Function | L47–L69 | `dict[str, Any] | None` | Валидирует строку initData от Telegram WebApp. |
| [`generate_tester_session`](#generate_tester_session) | Function | L72–L77 | `str` | Генерирует криптографически подписанный сессионный токен для |
| [`verify_tester_session`](#verify_tester_session) | Function | L80–L99 | `int | None` | Проверяет валидность сессионного токена тестера. |

---

## 3. Exhaustive Function Specifications

### `_build_data_check_string`
- **Signature**: `def _build_data_check_string(parsed_data: dict[str, str]) -> str`
- **Source Reference**: [utils/miniapp_auth.py#L23-L28](file:///home/u/Рабочий стол/para/utils/miniapp_auth.py#L23-L28)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Формирует каноническую строку для проверки подписи initData.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `parsed_data` | `dict[str, str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `sorted_items = sorted(`
2. `return "\n".join(f"{k}={v}" for k, v in sorted_items)`

---

### `_compute_init_data_hash`
- **Signature**: `def _compute_init_data_hash(data_check_str: str) -> str`
- **Source Reference**: [utils/miniapp_auth.py#L31-L34](file:///home/u/Рабочий стол/para/utils/miniapp_auth.py#L31-L34)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Вычисляет HMAC-SHA256 хеш данных initData с секретом бота.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `data_check_str` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()`
2. `return hmac.new(secret_key, data_check_str.encode(), hashlib.sha256).hexdigest()`

---

### `_is_auth_date_valid`
- **Signature**: `def _is_auth_date_valid(auth_date_str: str, max_age: int = SESSION_MAX_AGE_SECONDS) -> bool`
- **Source Reference**: [utils/miniapp_auth.py#L37-L44](file:///home/u/Рабочий стол/para/utils/miniapp_auth.py#L37-L44)
- **Async**: `No`
- **Return Type**: `bool`

#### Purpose & Architectural Intent
Проверяет актуальность auth_date для защиты от replay-атак.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `auth_date_str` | `str` | Input parameter |
| `max_age` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `try:`

---

### `validate_telegram_init_data`
- **Signature**: `def validate_telegram_init_data(init_data: str) -> dict[str, Any] | None`
- **Source Reference**: [utils/miniapp_auth.py#L47-L69](file:///home/u/Рабочий стол/para/utils/miniapp_auth.py#L47-L69)
- **Async**: `No`
- **Return Type**: `dict[str, Any] | None`

#### Purpose & Architectural Intent
Валидирует строку initData от Telegram WebApp. Проверяет HMAC-подпись хеша и время генерации данных. Возвращает словарь с данными пользователя или None при ошибке.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `init_data` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not init_data:`
2. `parsed = dict(parse_qsl(init_data, keep_blank_values=True))`
3. `received_hash = parsed.get("hash")`
4. `if not received_hash or not _is_auth_date_valid(parsed.get("auth_date", "")):`
5. `data_check_str = _build_data_check_string(parsed)`
6. `expected_hash = _compute_init_data_hash(data_check_str)`

---

### `generate_tester_session`
- **Signature**: `def generate_tester_session(user_id: int) -> str`
- **Source Reference**: [utils/miniapp_auth.py#L72-L77](file:///home/u/Рабочий стол/para/utils/miniapp_auth.py#L72-L77)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Генерирует криптографически подписанный сессионный токен для тестера.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `user_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `ts = int(datetime.now(UTC).timestamp())`
2. `payload = f"{user_id}:{ts}"`
3. `signature = hmac.new(API_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdi`
4. `return f"{payload}:{signature}"`

---

### `verify_tester_session`
- **Signature**: `def verify_tester_session(token: str, max_age: int = SESSION_MAX_AGE_SECONDS) -> int | None`
- **Source Reference**: [utils/miniapp_auth.py#L80-L99](file:///home/u/Рабочий стол/para/utils/miniapp_auth.py#L80-L99)
- **Async**: `No`
- **Return Type**: `int | None`

#### Purpose & Architectural Intent
Проверяет валидность сессионного токена тестера. Сверяет цифровую подпись токена и срок жизни сессии. Возвращает Telegram user_id тестера или None при невалидности.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `token` | `str` | Input parameter |
| `max_age` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not token or token.count(":") != 2:`
2. `raw_uid, raw_ts, signature = token.split(":")`
3. `payload = f"{raw_uid}:{raw_ts}"`
4. `expected_sig = hmac.new(API_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).he`
5. `if not hmac.compare_digest(signature, expected_sig):`
6. `if not _is_auth_date_valid(raw_ts, max_age=max_age):`

---
