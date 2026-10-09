# Module Specification: `api/router/teachers.py`
> **Path**: [`api/router/teachers.py`](file:///home/u/Рабочий стол/para/api/router/teachers.py)  
> **Subsystem**: `Teachers API`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Роутер преподавателей — GET /teachers, search, custom, refresh. Предоставляет контакты и ссылки видеосвязи (Zoom, Яндекс Телемост) из официального документа Яндекс Диска и пользовательских настроек.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`list_teachers`](#list_teachers) | Function | L28–L32 | `TeachersResponse` | Полный реестр преподавателей (ФИО + ссылка на занятие). |
| [`search_teachers`](#search_teachers) | Function | L36–L45 | `TeacherSearchResponse` | Поиск преподавателей по фрагменту фамилии или имени. |
| [`get_teacher`](#get_teacher) | Function | L49–L56 | `TeacherSingleResponse` | Получение контакта конкретного преподавателя по фамилии. |
| [`add_custom_teacher`](#add_custom_teacher) | Function | L60–L65 | `TeacherSingleResponse` | Добавление или обновление персональной ссылки преподавателя  |
| [`remove_custom_teacher`](#remove_custom_teacher) | Function | L70–L73 | `dict[str, str]` | Удаление кастомного преподавателя (Admin only). |
| [`refresh_teachers`](#refresh_teachers) | Function | L77–L80 | `TeachersRefreshResponse` | Принудительная загрузка актуального .docx с Яндекс Диска (Ad |

---

## 3. Exhaustive Function Specifications

### `list_teachers`
- **Signature**: `async def list_teachers(force_refresh: bool = Query(default=False)) -> TeachersResponse`
- **Source Reference**: [api/router/teachers.py#L28-L32](file:///home/u/Рабочий стол/para/api/router/teachers.py#L28-L32)
- **Async**: `Yes`
- **Return Type**: `TeachersResponse`

#### Purpose & Architectural Intent
Полный реестр преподавателей (ФИО + ссылка на занятие).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `force_refresh` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `raw = await get_teacher_links(force_refresh=force_refresh)`
2. `teachers = {k: TeacherItem(**v) for k, v in raw.items()}`
3. `return TeachersResponse(count=len(teachers), teachers=teachers)`

---

### `search_teachers`
- **Signature**: `async def search_teachers(q: str = Query(..., min_length=2, description="Поисковый запрос (часть фамилии)")) -> TeacherSearchResponse`
- **Source Reference**: [api/router/teachers.py#L36-L45](file:///home/u/Рабочий стол/para/api/router/teachers.py#L36-L45)
- **Async**: `Yes`
- **Return Type**: `TeacherSearchResponse`

#### Purpose & Architectural Intent
Поиск преподавателей по фрагменту фамилии или имени.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `q` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `raw = await get_teacher_links(force_refresh=False)`
2. `query_lower = q.strip().lower()`
3. `matches = [`
4. `return TeacherSearchResponse(query=q, count=len(matches), results=matches)`

---

### `get_teacher`
- **Signature**: `async def get_teacher(last_name: str) -> TeacherSingleResponse`
- **Source Reference**: [api/router/teachers.py#L49-L56](file:///home/u/Рабочий стол/para/api/router/teachers.py#L49-L56)
- **Async**: `Yes`
- **Return Type**: `TeacherSingleResponse`

#### Purpose & Architectural Intent
Получение контакта конкретного преподавателя по фамилии.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `last_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `raw = await get_teacher_links(force_refresh=False)`
2. `key = last_name.strip().lower()`
3. `if key not in raw:`
4. `item = TeacherItem(**raw[key])`
5. `return TeacherSingleResponse(key=key, teacher=item)`

---

### `add_custom_teacher`
- **Signature**: `async def add_custom_teacher(payload: CustomTeacherCreateRequest) -> TeacherSingleResponse`
- **Source Reference**: [api/router/teachers.py#L60-L65](file:///home/u/Рабочий стол/para/api/router/teachers.py#L60-L65)
- **Async**: `Yes`
- **Return Type**: `TeacherSingleResponse`

#### Purpose & Architectural Intent
Добавление или обновление персональной ссылки преподавателя (Admin only).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `payload` | `CustomTeacherCreateRequest` | Input parameter |

#### Step-by-Step Logic Execution
1. `key = payload.last_name.strip().lower()`
2. `save_custom_teacher(key, payload.full_name, payload.link_info)`
3. `item = TeacherItem(full_name=payload.full_name, link_info=payload.link_info)`
4. `return TeacherSingleResponse(key=key, teacher=item)`

---

### `remove_custom_teacher`
- **Signature**: `async def remove_custom_teacher(last_name: str) -> dict[str, str]`
- **Source Reference**: [api/router/teachers.py#L70-L73](file:///home/u/Рабочий стол/para/api/router/teachers.py#L70-L73)
- **Async**: `Yes`
- **Return Type**: `dict[str, str]`

#### Purpose & Architectural Intent
Удаление кастомного преподавателя (Admin only).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `last_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `delete_custom_teacher(last_name.strip().lower())`
2. `return {"status": "ok", "deleted": last_name}`

---

### `refresh_teachers`
- **Signature**: `async def refresh_teachers() -> TeachersRefreshResponse`
- **Source Reference**: [api/router/teachers.py#L77-L80](file:///home/u/Рабочий стол/para/api/router/teachers.py#L77-L80)
- **Async**: `Yes`
- **Return Type**: `TeachersRefreshResponse`

#### Purpose & Architectural Intent
Принудительная загрузка актуального .docx с Яндекс Диска (Admin only).

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `raw = await get_teacher_links(force_refresh=True)`
2. `return TeachersRefreshResponse(status="ok", count=len(raw))`

---
