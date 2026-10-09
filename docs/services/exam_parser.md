# Module Specification: `services/exam_parser.py`
> **Path**: [`services/exam_parser.py`](file:///home/u/Рабочий стол/para/services/exam_parser.py)  
> **Subsystem**: `Examination Parser`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Сервис парсинга и взаимодействия с экзаменами и аттестациями КТМУ. Извлекает полную нагрузку (loads), аттестации (Зачёты, Зачёты с оценкой, Контрольные работы) с точной привязкой к неделям семестра.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`is_assessment_type`](#is_assessment_type) | Function | L36–L44 | `tuple[bool, str]` | Проверяет, относится ли пара к видам аттестаций/экзаменов. |
| [`resolve_teacher_name`](#resolve_teacher_name) | Function | L47–L53 | `str` | Определяет полное имя преподавателя с учетом ссылок. |
| [`extract_load_weeks`](#extract_load_weeks) | Function | L56–L62 | `list[int]` | Извлекает и сортирует номера учебных недель из нагрузки. |
| [`parse_exam_from_load`](#parse_exam_from_load) | Function | L65–L88 | `tuple[str, ExamItem] | None` | Создает элемент ExamItem из нагрузки (loads) учебного плана. |
| [`enrich_exam_from_instance`](#enrich_exam_from_instance) | Function | L91–L112 | `None` | Уточняет аудиторию и недели из запланированного экземпляра в |
| [`get_group_exams`](#get_group_exams) | Function | L115–L139 | `list[ExamItem]` | Извлекает аттестации как из расписания (instances), так и из |

---

## 3. Exhaustive Function Specifications

### `is_assessment_type`
- **Signature**: `def is_assessment_type(type_id: str, l_types: dict[str, str]) -> tuple[bool, str]`
- **Source Reference**: [services/exam_parser.py#L36-L44](file:///home/u/Рабочий стол/para/services/exam_parser.py#L36-L44)
- **Async**: `No`
- **Return Type**: `tuple[bool, str]`

#### Purpose & Architectural Intent
Проверяет, относится ли пара к видам аттестаций/экзаменов. :return: Кортеж (флаг_успеха, название_типа)

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `type_id` | `str` | Input parameter |
| `l_types` | `dict[str, str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `t_name = EXAM_TYPE_MAPPING.get(type_id) or l_types.get(type_id, "")`
2. `is_valid = t_name in ("Контрольная работа", "Зачёт", "Диф. зачёт", "Курсовая работа")`
3. `return is_valid, t_name`

---

### `resolve_teacher_name`
- **Signature**: `def resolve_teacher_name(raw_teacher: str, teacher_links: dict[str, Any]) -> str`
- **Source Reference**: [services/exam_parser.py#L47-L53](file:///home/u/Рабочий стол/para/services/exam_parser.py#L47-L53)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Определяет полное имя преподавателя с учетом ссылок.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `raw_teacher` | `str` | Input parameter |
| `teacher_links` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `last_name = raw_teacher.split()[0].lower() if raw_teacher else ""`
2. `t_info = teacher_links.get(last_name)`
3. `return t_info.get("full_name") if t_info else raw_teacher`

---

### `extract_load_weeks`
- **Signature**: `def extract_load_weeks(load: dict[str, Any]) -> list[int]`
- **Source Reference**: [services/exam_parser.py#L56-L62](file:///home/u/Рабочий стол/para/services/exam_parser.py#L56-L62)
- **Async**: `No`
- **Return Type**: `list[int]`

#### Purpose & Architectural Intent
Извлекает и сортирует номера учебных недель из нагрузки.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `load` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `weeks_keys = list(load.get("weeklyPairs", {}).keys())`
2. `weeks = [int(w) for w in weeks_keys if w.isdigit()] if weeks_keys else load.get("cust`
3. `return sorted(weeks)`

---

### `parse_exam_from_load`
- **Signature**: `def parse_exam_from_load( load: dict[str, Any], entity_maps: tuple[dict, dict, dict, dict, dict], teacher_links: dict[str, Any] ) -> tuple[str, ExamItem] | None`
- **Source Reference**: [services/exam_parser.py#L65-L88](file:///home/u/Рабочий стол/para/services/exam_parser.py#L65-L88)
- **Async**: `No`
- **Return Type**: `tuple[str, ExamItem] | None`

#### Purpose & Architectural Intent
Создает элемент ExamItem из нагрузки (loads) учебного плана.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `load` | `dict[str, Any]` | Input parameter |
| `entity_maps` | `tuple[dict, dict, dict, dict, dict]` | Input parameter |
| `teacher_links` | `dict[str, Any]` | Input parameter |

#### Step-by-Step Logic Execution
1. `subjs, teachs, _, _, l_types = entity_maps`
2. `valid, type_name = is_assessment_type(load.get("typeId", ""), l_types)`
3. `if not valid or not is_item_for_group(load, GROUP_ID):`
4. `subj_name = clean_subject_title(subjs.get(load.get("subjectId"), "Аттестация"))`
5. `teacher_name = resolve_teacher_name(teachs.get(load.get("teacherId"), "Преподаватель"`
6. `is_remote = load.get("format") == "remote"`

---

### `enrich_exam_from_instance`
- **Signature**: `def enrich_exam_from_instance( inst: dict[str, Any], entity_maps: tuple[dict, dict, dict, dict, dict], exams_dict: dict[str, ExamItem] ) -> None`
- **Source Reference**: [services/exam_parser.py#L91-L112](file:///home/u/Рабочий стол/para/services/exam_parser.py#L91-L112)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Уточняет аудиторию и недели из запланированного экземпляра в сетке.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `inst` | `dict[str, Any]` | Input parameter |
| `entity_maps` | `tuple[dict, dict, dict, dict, dict]` | Input parameter |
| `exams_dict` | `dict[str, ExamItem]` | Input parameter |

#### Step-by-Step Logic Execution
1. `subjs, _, rms, _, l_types = entity_maps`
2. `valid, type_name = is_assessment_type(inst.get("typeId", ""), l_types)`
3. `if not valid or not is_item_for_group(inst, GROUP_ID):`
4. `subj_name = clean_subject_title(subjs.get(inst.get("subjectId"), "Аттестация"))`
5. `subgroup = inst.get("subgroup", 0)`
6. `key = f"{subj_name}_{type_name}_{subgroup}"`

---

### `get_group_exams`
- **Signature**: `async def get_group_exams() -> list[ExamItem]`
- **Source Reference**: [services/exam_parser.py#L115-L139](file:///home/u/Рабочий стол/para/services/exam_parser.py#L115-L139)
- **Async**: `Yes`
- **Return Type**: `list[ExamItem]`

#### Purpose & Architectural Intent
Извлекает аттестации как из расписания (instances), так и из нагрузки (loads). :return: Список объектов ExamItem

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `data = await fetch_schedule_data(force_refresh=False)`
2. `if not data:`
3. `entity_maps = extract_entity_maps(data)`
4. `teacher_links = await get_teacher_links(force_refresh=False)`
5. `exams_dict: dict[str, ExamItem] = {}`
6. `for load in data.get("loads", []):`

---
