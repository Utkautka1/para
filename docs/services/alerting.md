# Component Reference: `services/alerting.py`
> **File Path**: [`services/alerting.py`](../../services/alerting.py)
> **Subsystem**: `Incident Alerting`

## 1. Purpose
Сервис мониторинга инцидентов и доставки критических алертов администратору.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`_check_redis_throttle`](#_check_redis_throttle) | Function | L51–L64 | `bool \| None` | Проверяет и выставляет распределенный ключ кулдауна в R... |
| [`_should_throttle_alert`](#_should_throttle_alert) | Function | L67–L77 | `bool` | Проверяет необходимость локального троттлинга уведомлен... |
| [`_is_alert_throttled`](#_is_alert_throttled) | Function | L80–L85 | `bool` | Координирует распределенный (Redis) и локальный (память... |
| [`_format_alert_text`](#_format_alert_text) | Function | L88–L100 | `str` | Форматирует HTML-текст алерта для Telegram. |
| [`_resolve_alert_destination`](#_resolve_alert_destination) | Function | L103–L111 | `tuple[int, int \| None]` | Определяет целевой chat_id и message_thread_id по уровн... |
| [`_record_incident_safe`](#_record_incident_safe) | Function | L114–L131 | `None` | Безопасно сохраняет событие инцидента в базу данных SQL... |
| [`_deliver_alert_message`](#_deliver_alert_message) | Function | L134–L155 | `bool` | Форматирует и отправляет сообщение алерта в Telegram. |
| [`send_admin_alert`](#send_admin_alert) | Function | L158–L172 | `bool` | Записывает инцидент в SQLite и отправляет Telegram-алер... |

---

## 3. Comprehensive Function Specifications

## Class Model: `IncidentType`

Типы системных инцидентов и сетевых отказов.

### `_check_redis_throttle`
```python
async def _check_redis_throttle(incident_type: str, cooldown_seconds: float) -> bool | None
```

- **Source Reference**: [`services/alerting.py#L51-L64`](../../services/alerting.py#L51-L64)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool | None`

#### Overview & Architectural Purpose
Проверяет и выставляет распределенный ключ кулдауна в Redis.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `incident_type` | `str` | Yes | Parameter `incident_type` of type `str`. |
| `cooldown_seconds` | `float` | Yes | Parameter `cooldown_seconds` of type `float`. |

#### Concurrency & Side Effects
- Mutates or reads Redis L2 key space via asynchronous connection pool.
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.alerting import _check_redis_throttle

# Execute call
result = await _check_redis_throttle(incident_type=..., cooldown_seconds=...)
```

---

### `_should_throttle_alert`
```python
def _should_throttle_alert(incident_type: str, cooldown_seconds: float = 300.0) -> bool
```

- **Source Reference**: [`services/alerting.py#L67-L77`](../../services/alerting.py#L67-L77)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Проверяет необходимость локального троттлинга уведомления в памяти процесса.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `incident_type` | `str` | Yes | Parameter `incident_type` of type `str`. |
| `cooldown_seconds` | `float` | Yes | Parameter `cooldown_seconds` of type `float`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.alerting import _should_throttle_alert

# Execute call
result = _should_throttle_alert(incident_type=..., cooldown_seconds=...)
```

---

### `_is_alert_throttled`
```python
async def _is_alert_throttled(incident_type: str, cooldown_seconds: float) -> bool
```

- **Source Reference**: [`services/alerting.py#L80-L85`](../../services/alerting.py#L80-L85)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Координирует распределенный (Redis) и локальный (память) троттлинг алертов.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `incident_type` | `str` | Yes | Parameter `incident_type` of type `str`. |
| `cooldown_seconds` | `float` | Yes | Parameter `cooldown_seconds` of type `float`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.alerting import _is_alert_throttled

# Execute call
result = await _is_alert_throttled(incident_type=..., cooldown_seconds=...)
```

---

### `_format_alert_text`
```python
def _format_alert_text( incident_type: str, severity: str, title: str, description: str, trace_id: str | None = None ) -> str
```

- **Source Reference**: [`services/alerting.py#L88-L100`](../../services/alerting.py#L88-L100)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Форматирует HTML-текст алерта для Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `incident_type` | `str` | Yes | Parameter `incident_type` of type `str`. |
| `severity` | `str` | Yes | Parameter `severity` of type `str`. |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `description` | `str` | Yes | Parameter `description` of type `str`. |
| `trace_id` | `str | None` | Yes | Parameter `trace_id` of type `str | None`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.alerting import _format_alert_text

# Execute call
result = _format_alert_text(incident_type=..., severity=..., title=...)
```

---

### `_resolve_alert_destination`
```python
def _resolve_alert_destination(severity: str) -> tuple[int, int | None]
```

- **Source Reference**: [`services/alerting.py#L103-L111`](../../services/alerting.py#L103-L111)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[int, int | None]`

#### Overview & Architectural Purpose
Определяет целевой chat_id и message_thread_id по уровню серьезности алерта.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `severity` | `str` | Yes | Parameter `severity` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.alerting import _resolve_alert_destination

# Execute call
result = _resolve_alert_destination(severity=...)
```

---

### `_record_incident_safe`
```python
async def _record_incident_safe( incident_type: str, severity: str, title: str, description: str, trace_id: str | None, ) -> None
```

- **Source Reference**: [`services/alerting.py#L114-L131`](../../services/alerting.py#L114-L131)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Безопасно сохраняет событие инцидента в базу данных SQLite.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `incident_type` | `str` | Yes | Parameter `incident_type` of type `str`. |
| `severity` | `str` | Yes | Parameter `severity` of type `str`. |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `description` | `str` | Yes | Parameter `description` of type `str`. |
| `trace_id` | `str | None` | Yes | Parameter `trace_id` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.alerting import _record_incident_safe

# Execute call
result = await _record_incident_safe(incident_type=..., severity=..., title=...)
```

---

### `_deliver_alert_message`
```python
async def _deliver_alert_message( incident_type: str, severity: str, title: str, description: str, trace_id: str | None, ) -> bool
```

- **Source Reference**: [`services/alerting.py#L134-L155`](../../services/alerting.py#L134-L155)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Форматирует и отправляет сообщение алерта в Telegram.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `incident_type` | `str` | Yes | Parameter `incident_type` of type `str`. |
| `severity` | `str` | Yes | Parameter `severity` of type `str`. |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `description` | `str` | Yes | Parameter `description` of type `str`. |
| `trace_id` | `str | None` | Yes | Parameter `trace_id` of type `str | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from services.alerting import _deliver_alert_message

# Execute call
result = await _deliver_alert_message(incident_type=..., severity=..., title=...)
```

---

### `send_admin_alert`
```python
async def send_admin_alert( incident_type: str, title: str, description: str, severity: str = IncidentSeverity.WARNING, trace_id: str | None = None, cooldown_seconds: float | None = None, ) -> bool
```

- **Source Reference**: [`services/alerting.py#L158-L172`](../../services/alerting.py#L158-L172)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `bool`

#### Overview & Architectural Purpose
Записывает инцидент в SQLite и отправляет Telegram-алерт администратору.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `incident_type` | `str` | Yes | Parameter `incident_type` of type `str`. |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `description` | `str` | Yes | Parameter `description` of type `str`. |
| `severity` | `str` | Yes | Parameter `severity` of type `str`. |
| `trace_id` | `str | None` | Yes | Parameter `trace_id` of type `str | None`. |
| `cooldown_seconds` | `float | None` | Yes | Parameter `cooldown_seconds` of type `float | None`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from services.alerting import send_admin_alert

# Execute call
result = await send_admin_alert(incident_type=..., title=..., description=...)
```

---
