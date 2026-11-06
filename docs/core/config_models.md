# Component Reference: `core/config_models.py`
> **File Path**: [`core/config_models.py`](../../core/config_models.py)
> **Subsystem**: `Domain Configuration Models`

## 1. Purpose
Доменные модели конфигурации распределенной системы Para.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`TelegramConfig.allowed_admin_user_ids`](#telegramconfigallowed_admin_user_ids) | Method | L38–L43 | `set[int]` | Все главные администраторы (включая указанных через зап... |
| [`TelegramConfig.allowed_attendance_user_ids`](#telegramconfigallowed_attendance_user_ids) | Method | L46–L48 | `set[int]` | Множество доверенных администраторов для фиксации посещ... |
| [`ScheduleConfig.timezone`](#scheduleconfigtimezone) | Method | L67–L69 | `ZoneInfo` | Объект таймзоны для синхронизации расписания занятий. |

---

## 3. Comprehensive Function Specifications

## Class Model: `TelegramConfig`

Конфигурация Telegram-бота, ролевого доступа и идентификаторов топиков форума.

### `TelegramConfig.allowed_admin_user_ids`
```python
def allowed_admin_user_ids(self) -> set[int]
```

- **Source Reference**: [`core/config_models.py#L38-L43`](../../core/config_models.py#L38-L43)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `set[int]`

#### Overview & Architectural Purpose
Все главные администраторы (включая указанных через запятую в ALLOWED_USER_ID).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.config_models import allowed_admin_user_ids

# Execute call
result = allowed_admin_user_ids()
```

---

### `TelegramConfig.allowed_attendance_user_ids`
```python
def allowed_attendance_user_ids(self) -> set[int]
```

- **Source Reference**: [`core/config_models.py#L46-L48`](../../core/config_models.py#L46-L48)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `set[int]`

#### Overview & Architectural Purpose
Множество доверенных администраторов для фиксации посещаемости.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.config_models import allowed_attendance_user_ids

# Execute call
result = allowed_attendance_user_ids()
```

---

## Class Model: `ScheduleConfig`

Конфигурация внешних эндпоинтов расписания КТМУ, таймзоны и параметров кэширования.

### `ScheduleConfig.timezone`
```python
def timezone(self) -> ZoneInfo
```

- **Source Reference**: [`core/config_models.py#L67-L69`](../../core/config_models.py#L67-L69)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `ZoneInfo`

#### Overview & Architectural Purpose
Объект таймзоны для синхронизации расписания занятий.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.config_models import timezone

# Execute call
result = timezone()
```

---

## Class Model: `CampusConfig`

Конфигурация физических корпусов и удаленных локаций колледжа.

## Class Model: `RedisConfig`

Конфигурация подключения к серверу Redis и глобального L2 кэширования.

## Class Model: `YandexConfig`

Конфигурация интеграции с Яндекс Документами и журналами посещаемости WOPI.

## Class Model: `ApiConfig`

Конфигурация двухпротокольного API-шлюза (HTTP/REST и gRPC HTTP/2).

## Class Model: `AiSolverConfig`

Конфигурация очередей и клиента модели DeepSeek для решения домашних заданий.

## Class Model: `WhisperConfig`

Конфигурация модели распознавания речи faster-whisper и лимитов аудио.

## Class Model: `NotificationConfig`

Конфигурация расписания уведомлений и параметров троттлинга инлайн-кнопок.

## Class Model: `DatabaseConfig`

Конфигурация реляционной базы данных SQLite и параметров резервного копирования.

## Class Model: `TracingConfig`

Конфигурация распределенного трейсинга OpenTelemetry и Jaeger OTLP.
