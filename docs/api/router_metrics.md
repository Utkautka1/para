# Component Reference: `api/router/metrics.py`
> **File Path**: [`api/router/metrics.py`](../../api/router/metrics.py)
> **Subsystem**: `Prometheus Metrics API`

## 1. Purpose
Роутер телеметрии Prometheus — GET /metrics.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_prometheus_metrics`](#get_prometheus_metrics) | Function | L18–L28 | `Response` | Экспортирует системные метрики в формате текстового про... |

---

## 3. Comprehensive Function Specifications

### `get_prometheus_metrics`
```python
async def get_prometheus_metrics() -> Response
```

- **Source Reference**: [`api/router/metrics.py#L18-L28`](../../api/router/metrics.py#L18-L28)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `Response`

#### Overview & Architectural Purpose
Экспортирует системные метрики в формате текстового протокола Prometheus.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.metrics import get_prometheus_metrics

# Execute call
result = await get_prometheus_metrics()
```

---
