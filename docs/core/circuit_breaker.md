# Component Reference: `core/circuit_breaker.py`
> **File Path**: [`core/circuit_breaker.py`](../../core/circuit_breaker.py)
> **Subsystem**: `Resilience & Circuit Breaker`

## 1. Purpose
Модуль асинхронного Circuit Breaker и повторных попыток с экспоненциальным backoff.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`CircuitOpenError.__init__`](#circuitopenerror__init__) | Method | L34–L37 | `Any` | Executes core domain logic for `__init__`. |
| [`CircuitBreaker.__init__`](#circuitbreaker__init__) | Method | L43–L50 | `Any` | Executes core domain logic for `__init__`. |
| [`CircuitBreaker.state`](#circuitbreakerstate) | Method | L53–L59 | `CircuitState` | Возвращает актуальное состояние с учетом истечения reco... |
| [`CircuitBreaker.check_permission`](#circuitbreakercheck_permission) | Method | L61–L70 | `None` | Проверяет право на выполнение запроса или выбрасывает C... |
| [`CircuitBreaker.record_success`](#circuitbreakerrecord_success) | Method | L72–L79 | `None` | Сбрасывает счетчик ошибок при успешном завершении запро... |
| [`CircuitBreaker._dispatch_open_alert`](#circuitbreaker_dispatch_open_alert) | Method | L81–L95 | `None` | Асинхронно инициирует отправку алерта администратору пр... |
| [`CircuitBreaker.record_failure`](#circuitbreakerrecord_failure) | Method | L97–L106 | `None` | Фиксирует сбой и переводит в OPEN при превышении порога... |
| [`async_retry_with_backoff`](#async_retry_with_backoff) | Function | L109–L130 | `T` | Выполняет асинхронную операцию с экспоненциальным backo... |

---

## 3. Comprehensive Function Specifications

## Class Model: `CircuitState`

Состояния конечного автомата Circuit Breaker.

## Class Model: `CircuitOpenError`

Исключение, выбрасываемое при блокировке запроса открытым Circuit Breaker.

### `CircuitOpenError.__init__`
```python
def __init__(self, name: str, retry_after: float)
```

- **Source Reference**: [`core/circuit_breaker.py#L34-L37`](../../core/circuit_breaker.py#L34-L37)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Executes core domain logic for `__init__`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` | Yes | Parameter `name` of type `str`. |
| `retry_after` | `float` | Yes | Parameter `retry_after` of type `float`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.circuit_breaker import __init__

# Execute call
result = __init__(name=..., retry_after=...)
```

---

## Class Model: `CircuitBreaker`

Управляет защитой внешних вызовов от каскадных сбоев.

### `CircuitBreaker.__init__`
```python
def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout: float = 30.0)
```

- **Source Reference**: [`core/circuit_breaker.py#L43-L50`](../../core/circuit_breaker.py#L43-L50)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Any`

#### Overview & Architectural Purpose
Executes core domain logic for `__init__`.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` | Yes | Parameter `name` of type `str`. |
| `failure_threshold` | `int` | Yes | Parameter `failure_threshold` of type `int`. |
| `recovery_timeout` | `float` | Yes | Parameter `recovery_timeout` of type `float`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.circuit_breaker import __init__

# Execute call
result = __init__(name=..., failure_threshold=..., recovery_timeout=...)
```

---

### `CircuitBreaker.state`
```python
def state(self) -> CircuitState
```

- **Source Reference**: [`core/circuit_breaker.py#L53-L59`](../../core/circuit_breaker.py#L53-L59)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `CircuitState`

#### Overview & Architectural Purpose
Возвращает актуальное состояние с учетом истечения recovery timeout.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.circuit_breaker import state

# Execute call
result = state()
```

---

### `CircuitBreaker.check_permission`
```python
async def check_permission(self) -> None
```

- **Source Reference**: [`core/circuit_breaker.py#L61-L70`](../../core/circuit_breaker.py#L61-L70)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Проверяет право на выполнение запроса или выбрасывает CircuitOpenError.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from core.circuit_breaker import check_permission

# Execute call
result = await check_permission()
```

---

### `CircuitBreaker.record_success`
```python
async def record_success(self) -> None
```

- **Source Reference**: [`core/circuit_breaker.py#L72-L79`](../../core/circuit_breaker.py#L72-L79)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Сбрасывает счетчик ошибок при успешном завершении запроса.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.circuit_breaker import record_success

# Execute call
result = await record_success()
```

---

### `CircuitBreaker._dispatch_open_alert`
```python
def _dispatch_open_alert(self, error: Exception) -> None
```

- **Source Reference**: [`core/circuit_breaker.py#L81-L95`](../../core/circuit_breaker.py#L81-L95)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Асинхронно инициирует отправку алерта администратору при переходе в OPEN.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `error` | `Exception` | Yes | Parameter `error` of type `Exception`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Encapsulates faults within `try/except` blocks, logging errors and returning safe fallback defaults.

#### Production Usage Example
```python
from core.circuit_breaker import _dispatch_open_alert

# Execute call
result = _dispatch_open_alert(error=...)
```

---

### `CircuitBreaker.record_failure`
```python
async def record_failure(self, error: Exception) -> None
```

- **Source Reference**: [`core/circuit_breaker.py#L97-L106`](../../core/circuit_breaker.py#L97-L106)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Фиксирует сбой и переводит в OPEN при превышении порога.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `error` | `Exception` | Yes | Parameter `error` of type `Exception`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from core.circuit_breaker import record_failure

# Execute call
result = await record_failure(error=...)
```

---

### `async_retry_with_backoff`
```python
async def async_retry_with_backoff( coro_fn: Callable[[], Awaitable[T]], max_retries: int = 3, base_delay: float = 0.5, max_delay: float = 5.0, retryable_exceptions: tuple[type[Exception], ...] = (Exception,), ) -> T
```

- **Source Reference**: [`core/circuit_breaker.py#L109-L130`](../../core/circuit_breaker.py#L109-L130)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `T`

#### Overview & Architectural Purpose
Выполняет асинхронную операцию с экспоненциальным backoff и jitter.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `coro_fn` | `Callable[[], Awaitable[T]]` | Yes | Parameter `coro_fn` of type `Callable[[], Awaitable[T]]`. |
| `max_retries` | `int` | Yes | Parameter `max_retries` of type `int`. |
| `base_delay` | `float` | Yes | Parameter `base_delay` of type `float`. |
| `max_delay` | `float` | Yes | Parameter `max_delay` of type `float`. |
| `retryable_exceptions` | `tuple[type[Exception], ...]` | Yes | Parameter `retryable_exceptions` of type `tuple[type[Exception], ...]`. |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from core.circuit_breaker import async_retry_with_backoff

# Execute call
result = await async_retry_with_backoff(coro_fn=..., max_retries=..., base_delay=...)
```

---
