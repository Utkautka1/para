# Component Reference: `core/metrics.py`
> **File Path**: [`core/metrics.py`](../../core/metrics.py)
> **Subsystem**: `Prometheus Metrics Engine`

## 1. Purpose
Единый реестр метрик Prometheus для сервисов платформы para.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`normalize_http_method`](#normalize_http_method) | Function | L44–L51 | `str` | Сводит HTTP-метод к ограниченному набору значений лейбл... |
| [`record_http_request`](#record_http_request) | Function | L54–L63 | `None` | Фиксирует завершенный HTTP-запрос в счетчиках и гистогр... |
| [`record_ai_inference`](#record_ai_inference) | Function | L66–L74 | `None` | Регистрирует длительность инференса нейросетевой модели... |
| [`set_redis_queue_length`](#set_redis_queue_length) | Function | L77–L85 | `None` | Обновляет текущий размер очереди в Redis для мониторинг... |
| [`generate_metrics_payload`](#generate_metrics_payload) | Function | L88–L96 | `tuple[bytes, str]` | Экспортирует все накопленные метрики в стандартном текс... |

---

## 3. Comprehensive Function Specifications

### `normalize_http_method`
```python
def normalize_http_method(method: str) -> str
```

- **Source Reference**: [`core/metrics.py#L44-L51`](../../core/metrics.py#L44-L51)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Сводит HTTP-метод к ограниченному набору значений лейбла.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `method` | `str` | Yes | Parameter `method` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.metrics import normalize_http_method

# Execute call
result = normalize_http_method(method=...)
```

---

### `record_http_request`
```python
def record_http_request(method: str, endpoint: str, status: int, duration: float) -> None
```

- **Source Reference**: [`core/metrics.py#L54-L63`](../../core/metrics.py#L54-L63)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Фиксирует завершенный HTTP-запрос в счетчиках и гистограмме Prometheus.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `method` | `str` | Yes | Parameter `method` of type `str`. |
| `endpoint` | `str` | Yes | Parameter `endpoint` of type `str`. |
| `status` | `int` | Yes | Attendance status code ('Present', 'Late', 'Excused', 'Absent'). |
| `duration` | `float` | Yes | Audio duration in seconds. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.metrics import record_http_request

# Execute call
result = record_http_request(method=..., endpoint=..., status=...)
```

---

### `record_ai_inference`
```python
def record_ai_inference(subsystem: str, model: str, duration: float) -> None
```

- **Source Reference**: [`core/metrics.py#L66-L74`](../../core/metrics.py#L66-L74)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Регистрирует длительность инференса нейросетевой модели.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `subsystem` | `str` | Yes | Parameter `subsystem` of type `str`. |
| `model` | `str` | Yes | Parameter `model` of type `str`. |
| `duration` | `float` | Yes | Audio duration in seconds. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.metrics import record_ai_inference

# Execute call
result = record_ai_inference(subsystem=..., model=..., duration=...)
```

---

### `set_redis_queue_length`
```python
def set_redis_queue_length(queue_name: str, length: int) -> None
```

- **Source Reference**: [`core/metrics.py#L77-L85`](../../core/metrics.py#L77-L85)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Обновляет текущий размер очереди в Redis для мониторинга лага обработки.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `queue_name` | `str` | Yes | Parameter `queue_name` of type `str`. |
| `length` | `int` | Yes | Parameter `length` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.metrics import set_redis_queue_length

# Execute call
result = set_redis_queue_length(queue_name=..., length=...)
```

---

### `generate_metrics_payload`
```python
def generate_metrics_payload() -> tuple[bytes, str]
```

- **Source Reference**: [`core/metrics.py#L88-L96`](../../core/metrics.py#L88-L96)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[bytes, str]`

#### Overview & Architectural Purpose
Экспортирует все накопленные метрики в стандартном текстовом формате Prometheus.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.metrics import generate_metrics_payload

# Execute call
result = generate_metrics_payload()
```

---
