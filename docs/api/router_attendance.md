# Component Reference: `api/router/attendance.py`
> **File Path**: [`api/router/attendance.py`](../../api/router/attendance.py)
> **Subsystem**: `Attendance API`

## 1. Purpose
Роутер посещаемости — GET /attendance/stats, student, session, mark, commit.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`get_attendance_stats`](#get_attendance_stats) | Function | L39–L52 | `AttendanceStatsResponse` | Возвращает агрегированную годовую статистику посещаемос... |
| [`_calculate_attendance_rate`](#_calculate_attendance_rate) | Function | L55–L69 | `float` | Вычисляет процент посещаемости студента по сумме меток ... |
| [`get_student_attendance`](#get_student_attendance) | Function | L73–L96 | `StudentPersonalStatsResponse` | Возвращает детальную статистику посещаемости конкретног... |
| [`_build_session_response`](#_build_session_response) | Function | L99–L123 | `ActiveSessionResponse` | Преобразует состояние доменной сессии старосты в Pydant... |
| [`get_current_session`](#get_current_session) | Function | L127–L139 | `ActiveSessionResponse` | Возвращает текущее состояние интерактивной сессии отмет... |
| [`start_session`](#start_session) | Function | L143–L158 | `ActiveSessionResponse` | Инициализирует новую сессию опроса посещаемости пары ст... |
| [`mark_student`](#mark_student) | Function | L162–L176 | `ActiveSessionResponse` | Записывает статус посещаемости для текущего студента в ... |
| [`batch_present`](#batch_present) | Function | L182–L196 | `ActiveSessionResponse` | Массово проставляет статус 'П' (присутствует) всем оста... |
| [`commit_session`](#commit_session) | Function | L200–L219 | `CommitAttendanceResponse` | Фиксирует результаты сессии опроса в таблицу Яндекс Док... |
| [`cancel_session`](#cancel_session) | Function | L223–L235 | `CancelSessionResponse` | Сбрасывает и отменяет текущую незавершённую сессию стар... |

---

## 3. Comprehensive Function Specifications

### `get_attendance_stats`
```python
async def get_attendance_stats(force_refresh: bool = Query(default=False)) -> AttendanceStatsResponse
```

- **Source Reference**: [`api/router/attendance.py#L39-L52`](../../api/router/attendance.py#L39-L52)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `AttendanceStatsResponse`

#### Overview & Architectural Purpose
Возвращает агрегированную годовую статистику посещаемости всех студентов.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `force_refresh` | `bool` | Yes | Parameter `force_refresh` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.attendance import get_attendance_stats

# Execute call
result = await get_attendance_stats(force_refresh=...)
```

---

### `_calculate_attendance_rate`
```python
def _calculate_attendance_rate(total_marks: dict) -> float
```

- **Source Reference**: [`api/router/attendance.py#L55-L69`](../../api/router/attendance.py#L55-L69)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `float`

#### Overview & Architectural Purpose
Вычисляет процент посещаемости студента по сумме меток 'П' и 'О'.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `total_marks` | `dict` | Yes | Parameter `total_marks` of type `dict`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.attendance import _calculate_attendance_rate

# Execute call
result = _calculate_attendance_rate(total_marks=...)
```

---

### `get_student_attendance`
```python
async def get_student_attendance(fio: str) -> StudentPersonalStatsResponse
```

- **Source Reference**: [`api/router/attendance.py#L73-L96`](../../api/router/attendance.py#L73-L96)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `StudentPersonalStatsResponse`

#### Overview & Architectural Purpose
Возвращает детальную статистику посещаемости конкретного студента по ФИО.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fio` | `str` | Yes | Full canonical name of the student in Cyrillic nominative format. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.attendance import get_student_attendance

# Execute call
result = await get_student_attendance(fio=...)
```

---

### `_build_session_response`
```python
def _build_session_response(s) -> ActiveSessionResponse
```

- **Source Reference**: [`api/router/attendance.py#L99-L123`](../../api/router/attendance.py#L99-L123)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `ActiveSessionResponse`

#### Overview & Architectural Purpose
Преобразует состояние доменной сессии старосты в Pydantic DTO ответа.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `s` | `Any` | Yes | Parameter `s` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.attendance import _build_session_response

# Execute call
result = _build_session_response(s=...)
```

---

### `get_current_session`
```python
async def get_current_session() -> ActiveSessionResponse
```

- **Source Reference**: [`api/router/attendance.py#L127-L139`](../../api/router/attendance.py#L127-L139)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `ActiveSessionResponse`

#### Overview & Architectural Purpose
Возвращает текущее состояние интерактивной сессии отметки старосты.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.attendance import get_current_session

# Execute call
result = await get_current_session()
```

---

### `start_session`
```python
async def start_session(payload: StartSessionRequest) -> ActiveSessionResponse
```

- **Source Reference**: [`api/router/attendance.py#L143-L158`](../../api/router/attendance.py#L143-L158)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `ActiveSessionResponse`

#### Overview & Architectural Purpose
Инициализирует новую сессию опроса посещаемости пары старостой (Admin only).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `payload` | `StartSessionRequest` | Yes | Parameter `payload` of type `StartSessionRequest`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.attendance import start_session

# Execute call
result = await start_session(payload=...)
```

---

### `mark_student`
```python
async def mark_student(payload: MarkStudentRequest) -> ActiveSessionResponse
```

- **Source Reference**: [`api/router/attendance.py#L162-L176`](../../api/router/attendance.py#L162-L176)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `ActiveSessionResponse`

#### Overview & Architectural Purpose
Записывает статус посещаемости для текущего студента в очереди (Admin only).

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `payload` | `MarkStudentRequest` | Yes | Parameter `payload` of type `MarkStudentRequest`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.attendance import mark_student

# Execute call
result = await mark_student(payload=...)
```

---

### `batch_present`
```python
async def batch_present() -> ActiveSessionResponse
```

- **Source Reference**: [`api/router/attendance.py#L182-L196`](../../api/router/attendance.py#L182-L196)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `ActiveSessionResponse`

#### Overview & Architectural Purpose
Массово проставляет статус 'П' (присутствует) всем оставшимся студентам (Admin only).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.attendance import batch_present

# Execute call
result = await batch_present()
```

---

### `commit_session`
```python
async def commit_session() -> CommitAttendanceResponse
```

- **Source Reference**: [`api/router/attendance.py#L200-L219`](../../api/router/attendance.py#L200-L219)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `CommitAttendanceResponse`

#### Overview & Architectural Purpose
Фиксирует результаты сессии опроса в таблицу Яндекс Документов (Admin only).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Explicitly raises domain exceptions (e.g., `PermissionError`, `ValueError`) upon invariant violation.

#### Production Usage Example
```python
from api.router.attendance import commit_session

# Execute call
result = await commit_session()
```

---

### `cancel_session`
```python
async def cancel_session() -> CancelSessionResponse
```

- **Source Reference**: [`api/router/attendance.py#L223-L235`](../../api/router/attendance.py#L223-L235)
- **Execution Mode**: `Asynchronous (non-blocking)`
- **Return Contract**: `CancelSessionResponse`

#### Overview & Architectural Purpose
Сбрасывает и отменяет текущую незавершённую сессию старосты (Admin only).

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from api.router.attendance import cancel_session

# Execute call
result = await cancel_session()
```

---
