# Module Specification: `utils/doc_generator.py`
> **Path**: [`utils/doc_generator.py`](file:///home/u/Рабочий стол/para/utils/doc_generator.py)  
> **Subsystem**: `GOST Document Generator`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Модуль генерации отчетов в формате DOCX по точному образцу файла ГОСТ 7.32-2017. Обеспечивает 100% соответствие эталону: 1. Официальный титульный лист (Стр. 1) с шапкой Министерства и Колледжа. 2. Таблица подписей 'Выполнил студент группы 1-КПД-3' / 'Проверил преподаватель'. 3. Отдельная страница 'СОДЕРЖАНИЕ' (Стр. 2) с интерактивными кликабельными гиперссылками. 4. Разделение главных структурных элементов на новые страницы (Page Break). 5. Преобразование таблиц Markdown в таблицы Word ('Table Grid') с оформлением ячеек. 6. Выравнивание основного текста по ширине (Justified), Times New Roman 14 pt, 1.5 интервал.

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`setup_gost_margins`](#setup_gost_margins) | Function | L29–L35 | `None` | Настраивает размеры полей документа по эталону ГОСТ. |
| [`setup_page_numbering`](#setup_page_numbering) | Function | L38–L46 | `None` | Настраивает нумерацию страниц внизу по центру Times New Roma |
| [`setup_gost_styles`](#setup_gost_styles) | Function | L49–L55 | `None` | Настраивает стиль по умолчанию (Times New Roman, 14pt, обычн |
| [`format_table_row_cells`](#format_table_row_cells) | Function | L58–L66 | `None` | Заполняет и форматирует ячейки строки таблицы подписей. |
| [`add_title_signature_table`](#add_title_signature_table) | Function | L69–L86 | `None` | Добавляет аккуратную таблицу подписей Выполнил/Проверил по о |
| [`add_title_header`](#add_title_header) | Function | L89–L97 | `None` | Добавляет официальную шапку Министерства и Университета на т |
| [`create_title_page`](#create_title_page) | Function | L100–L118 | `None` | Создает официальный титульный лист по образцу ГОСТ (Страница |
| [`clean_math_text`](#clean_math_text) | Function | L121–L127 | `str` | Очищает LaTeX конструкции и лишние точки в конце заголовков  |
| [`format_gost_paragraph`](#format_gost_paragraph) | Function | L130–L136 | `None` | Применяет ГОСТ форматирование к абзацу (1.5 интервал, 1.25 с |
| [`add_bookmark_to_paragraph`](#add_bookmark_to_paragraph) | Function | L139–L144 | `None` | Добавляет внутреннюю закладку Word к параграфу заголовка. |
| [`add_toc_hyperlink`](#add_toc_hyperlink) | Function | L147–L161 | `None` | Добавляет пункт СОДЕРЖАНИЯ с кликабельной гиперссылкой по ГО |
| [`extract_headings_from_text`](#extract_headings_from_text) | Function | L164–L177 | `list[tuple[str, str, int, int]]` | Извлекает все заголовки из текста решения для построения Сод |
| [`build_table_of_contents`](#build_table_of_contents) | Function | L180–L187 | `None` | Создает отдельную страницу СОДЕРЖАНИЕ с гиперссылками по ГОС |
| [`add_gost_heading`](#add_gost_heading) | Function | L190–L205 | `None` | Добавляет заголовок раздела по ГОСТ. |
| [`add_gost_heading_with_bookmark`](#add_gost_heading_with_bookmark) | Function | L208–L224 | `None` | Добавляет заголовок с привязаной закладкой и разрывом страни |
| [`parse_markdown_table_rows`](#parse_markdown_table_rows) | Function | L227–L236 | `list[list[str]]` | Парсит строки маркдаун таблицы в двумерный массив ячеек. |
| [`fill_table_cell`](#fill_table_cell) | Function | L239–L256 | `None` | Заполняет ячейку таблицы Word с очисткой и поддержкой жирног |
| [`add_docx_table_from_markdown`](#add_docx_table_from_markdown) | Function | L259–L270 | `None` | Создает настоящую аккуратную таблицу Word по ГОСТ из Markdow |
| [`process_document_content_lines`](#process_document_content_lines) | Function | L273–L290 | `None` | Обрабатывает строки документа, распознавая таблицы, заголовк |
| [`add_formatted_paragraph`](#add_formatted_paragraph) | Function | L293–L305 | `None` | Добавляет форматированный параграф по ГОСТ. |
| [`init_gost_document`](#init_gost_document) | Function | L308–L314 | `Document` | Инициализирует документ Word с ГОСТ полями, стилями и нумера |
| [`create_solution_docx`](#create_solution_docx) | Function | L317–L336 | `str` | Генерирует 100% соответствующий ГОСТ 7.32-2017 Word DOCX док |

---

## 3. Exhaustive Function Specifications

### `setup_gost_margins`
- **Signature**: `def setup_gost_margins(doc: Document) -> None`
- **Source Reference**: [utils/doc_generator.py#L29-L35](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L29-L35)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Настраивает размеры полей документа по эталону ГОСТ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |

#### Step-by-Step Logic Execution
1. `for section in doc.sections:`

---

### `setup_page_numbering`
- **Signature**: `def setup_page_numbering(doc: Document) -> None`
- **Source Reference**: [utils/doc_generator.py#L38-L46](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L38-L46)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Настраивает нумерацию страниц внизу по центру Times New Roman 14pt.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |

#### Step-by-Step Logic Execution
1. `section = doc.sections[0]`
2. `section.different_first_page_header_footer = True`
3. `footer = section.footer`
4. `p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()`
5. `p.alignment = WD_ALIGN_PARAGRAPH.CENTER`
6. `p.paragraph_format.space_before = Pt(0)`

---

### `setup_gost_styles`
- **Signature**: `def setup_gost_styles(doc: Document) -> None`
- **Source Reference**: [utils/doc_generator.py#L49-L55](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L49-L55)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Настраивает стиль по умолчанию (Times New Roman, 14pt, обычный).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |

#### Step-by-Step Logic Execution
1. `style = doc.styles["Normal"]`
2. `font = style.font`
3. `font.name = "Times New Roman"`
4. `font.size = Pt(14)`
5. `font.color.rgb = RGBColor(0, 0, 0)`

---

### `format_table_row_cells`
- **Signature**: `def format_table_row_cells(row, left_txt: str, right_txt: str) -> None`
- **Source Reference**: [utils/doc_generator.py#L58-L66](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L58-L66)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Заполняет и форматирует ячейки строки таблицы подписей.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `row` | `Any` | Input parameter |
| `left_txt` | `str` | Input parameter |
| `right_txt` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `row.cells[0].text, row.cells[1].text = left_txt, right_txt`
2. `for cell in row.cells:`

---

### `add_title_signature_table`
- **Signature**: `def add_title_signature_table( doc: Document, student_name: str = "Студент", teacher_name: str = "Преподаватель", year: int | None = None, group_name: str | None = None, ) -> None`
- **Source Reference**: [utils/doc_generator.py#L69-L86](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L69-L86)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Добавляет аккуратную таблицу подписей Выполнил/Проверил по образцу ГОСТ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |
| `student_name` | `str` | Input parameter |
| `teacher_name` | `str` | Input parameter |
| `year` | `int | None` | Input parameter |
| `group_name` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `target_year = year or datetime.now(TIMEZONE).year`
2. `target_group = group_name or GROUP_NAME`
3. `tbl = doc.add_table(rows=2, cols=2)`
4. `tbl.style = "Normal Table"`
5. `rows_data = [`
6. `for idx, (ltxt, rtxt) in enumerate(rows_data):`

---

### `add_title_header`
- **Signature**: `def add_title_header(doc: Document) -> None`
- **Source Reference**: [utils/doc_generator.py#L89-L97](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L89-L97)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Добавляет официальную шапку Министерства и Университета на титульный лист.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |

#### Step-by-Step Logic Execution
1. `p_hdr = doc.add_paragraph()`
2. `p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER`
3. `p_hdr.paragraph_format.line_spacing = 1.15`
4. `p_hdr.add_run("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n").bold`
5. `p_hdr.add_run("ПРОМТЕХДИЗАЙН\n").bold = True`
6. `p_hdr.add_run("Санкт-Петербургский государственный университет промышленных технологи`

---

### `create_title_page`
- **Signature**: `def create_title_page( doc: Document, student_name: str = "Студент", teacher_name: str = "Преподаватель", year: int | None = None, group_name: str | None = None, ) -> None`
- **Source Reference**: [utils/doc_generator.py#L100-L118](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L100-L118)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Создает официальный титульный лист по образцу ГОСТ (Страница 1).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |
| `student_name` | `str` | Input parameter |
| `teacher_name` | `str` | Input parameter |
| `year` | `int | None` | Input parameter |
| `group_name` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `target_year = year or datetime.now(TIMEZONE).year`
2. `add_title_header(doc)`
3. `p_title = doc.add_paragraph()`
4. `p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER`
5. `p_title.add_run("ОТЧЕТ ПО ВЫПОЛНЕНИЮ ЗАДАНИЯ\n\n").bold = True`
6. `add_title_signature_table(doc, student_name, teacher_name, target_year, group_name)`

---

### `clean_math_text`
- **Signature**: `def clean_math_text(text: str) -> str`
- **Source Reference**: [utils/doc_generator.py#L121-L127](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L121-L127)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Очищает LaTeX конструкции и лишние точки в конце заголовков по ГОСТ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `t = text.replace("$$", "").replace("$", "")`
2. `t = t.replace("\\cdot", "·").replace("\\Delta", "Δ")`
3. `t = t.replace("\\begin{vmatrix}", "| ").replace("\\end{vmatrix}", " |")`
4. `t = re.sub(r"\\([a-zA-Z]+)", r"\1", t)`
5. `return t.strip().rstrip(".")`

---

### `format_gost_paragraph`
- **Signature**: `def format_gost_paragraph(p) -> None`
- **Source Reference**: [utils/doc_generator.py#L130-L136](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L130-L136)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Применяет ГОСТ форматирование к абзацу (1.5 интервал, 1.25 см красная строка).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `p` | `Any` | Input parameter |

#### Step-by-Step Logic Execution
1. `p.paragraph_format.line_spacing = 1.5`
2. `p.paragraph_format.first_line_indent = Cm(1.25)`
3. `p.paragraph_format.space_before = Pt(0)`
4. `p.paragraph_format.space_after = Pt(0)`
5. `p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY`

---

### `add_bookmark_to_paragraph`
- **Signature**: `def add_bookmark_to_paragraph(p, bookmark_name: str, bookmark_id: int) -> None`
- **Source Reference**: [utils/doc_generator.py#L139-L144](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L139-L144)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Добавляет внутреннюю закладку Word к параграфу заголовка.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `p` | `Any` | Input parameter |
| `bookmark_name` | `str` | Input parameter |
| `bookmark_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bookmark_id}" w:name="{`
2. `bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bookmark_id}"/>')`
3. `p._p.insert(0, bm_start)`
4. `p._p.append(bm_end)`

---

### `add_toc_hyperlink`
- **Signature**: `def add_toc_hyperlink(doc: Document, text: str, bookmark_name: str) -> None`
- **Source Reference**: [utils/doc_generator.py#L147-L161](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L147-L161)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Добавляет пункт СОДЕРЖАНИЯ с кликабельной гиперссылкой по ГОСТ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |
| `text` | `str` | Input parameter |
| `bookmark_name` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `p = doc.add_paragraph()`
2. `p.paragraph_format.line_spacing = 1.5`
3. `p.paragraph_format.first_line_indent = Cm(0)`
4. `p.paragraph_format.space_before = Pt(0)`
5. `p.paragraph_format.space_after = Pt(2)`
6. `h_xml = parse_xml(f'<w:hyperlink {nsdecls("w")} w:anchor="{bookmark_name}"/>')`

---

### `extract_headings_from_text`
- **Signature**: `def extract_headings_from_text(solution_text: str) -> list[tuple[str, str, int, int]]`
- **Source Reference**: [utils/doc_generator.py#L164-L177](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L164-L177)
- **Async**: `No`
- **Return Type**: `list[tuple[str, str, int, int]]`

#### Purpose & Architectural Intent
Извлекает все заголовки из текста решения для построения Содержания.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `solution_text` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `headings = []`
2. `idx = 1`
3. `for line in solution_text.split("\n"):`
4. `return headings`

---

### `build_table_of_contents`
- **Signature**: `def build_table_of_contents(doc: Document, headings: list[tuple[str, str, int, int]]) -> None`
- **Source Reference**: [utils/doc_generator.py#L180-L187](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L180-L187)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Создает отдельную страницу СОДЕРЖАНИЕ с гиперссылками по ГОСТ (Страница 2).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |
| `headings` | `list[tuple[str, str, int, int]]` | Input parameter |

#### Step-by-Step Logic Execution
1. `if not headings:`
2. `add_gost_heading(doc, "СОДЕРЖАНИЕ", level=1, page_break=False)`
3. `for _, title, _, idx in headings:`

---

### `add_gost_heading`
- **Signature**: `def add_gost_heading(doc: Document, title: str, level: int, page_break: bool = False) -> None`
- **Source Reference**: [utils/doc_generator.py#L190-L205](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L190-L205)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Добавляет заголовок раздела по ГОСТ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |
| `title` | `str` | Input parameter |
| `level` | `int` | Input parameter |
| `page_break` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `if page_break:`
2. `p = doc.add_paragraph()`
3. `p.paragraph_format.first_line_indent = Cm(1.25 if level > 1 else 0)`
4. `p.paragraph_format.space_before = Pt(12)`
5. `p.paragraph_format.space_after = Pt(12)`
6. `p.paragraph_format.line_spacing = 1.5`

---

### `add_gost_heading_with_bookmark`
- **Signature**: `def add_gost_heading_with_bookmark(doc: Document, title: str, level: int, bm_id: int) -> None`
- **Source Reference**: [utils/doc_generator.py#L208-L224](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L208-L224)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Добавляет заголовок с привязаной закладкой и разрывом страницы для 1 уровня.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |
| `title` | `str` | Input parameter |
| `level` | `int` | Input parameter |
| `bm_id` | `int` | Input parameter |

#### Step-by-Step Logic Execution
1. `if level == 1:`
2. `p = doc.add_paragraph()`
3. `p.paragraph_format.first_line_indent = Cm(1.25 if level > 1 else 0)`
4. `p.paragraph_format.space_before = Pt(12)`
5. `p.paragraph_format.space_after = Pt(12)`
6. `p.paragraph_format.line_spacing = 1.5`

---

### `parse_markdown_table_rows`
- **Signature**: `def parse_markdown_table_rows(table_lines: list[str]) -> list[list[str]]`
- **Source Reference**: [utils/doc_generator.py#L227-L236](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L227-L236)
- **Async**: `No`
- **Return Type**: `list[list[str]]`

#### Purpose & Architectural Intent
Парсит строки маркдаун таблицы в двумерный массив ячеек.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `table_lines` | `list[str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `rows = []`
2. `for line in table_lines:`
3. `return rows`

---

### `fill_table_cell`
- **Signature**: `def fill_table_cell(cell, cell_text: str, is_header: bool) -> None`
- **Source Reference**: [utils/doc_generator.py#L239-L256](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L239-L256)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Заполняет ячейку таблицы Word с очисткой и поддержкой жирного шрифта (**).

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `cell` | `Any` | Input parameter |
| `cell_text` | `str` | Input parameter |
| `is_header` | `bool` | Input parameter |

#### Step-by-Step Logic Execution
1. `cell.text = ""`
2. `p = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph()`
3. `p.paragraph_format.space_before = Pt(2)`
4. `p.paragraph_format.space_after = Pt(2)`
5. `p.paragraph_format.line_spacing = 1.15`
6. `cleaned = clean_math_text(cell_text)`

---

### `add_docx_table_from_markdown`
- **Signature**: `def add_docx_table_from_markdown(doc: Document, table_lines: list[str]) -> None`
- **Source Reference**: [utils/doc_generator.py#L259-L270](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L259-L270)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Создает настоящую аккуратную таблицу Word по ГОСТ из Markdown строк.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |
| `table_lines` | `list[str]` | Input parameter |

#### Step-by-Step Logic Execution
1. `rows_data = parse_markdown_table_rows(table_lines)`
2. `if not rows_data:`
3. `table = doc.add_table(rows=len(rows_data), cols=max(len(r) for r in rows_data))`
4. `table.style = "Table Grid"`
5. `for r_idx, row in enumerate(rows_data):`

---

### `process_document_content_lines`
- **Signature**: `def process_document_content_lines(doc: Document, lines: list[str], heading_map: dict) -> None`
- **Source Reference**: [utils/doc_generator.py#L273-L290](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L273-L290)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Обрабатывает строки документа, распознавая таблицы, заголовки и параграфы.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |
| `lines` | `list[str]` | Input parameter |
| `heading_map` | `dict` | Input parameter |

#### Step-by-Step Logic Execution
1. `i = 0`
2. `while i < len(lines):`

---

### `add_formatted_paragraph`
- **Signature**: `def add_formatted_paragraph(doc: Document, line: str) -> None`
- **Source Reference**: [utils/doc_generator.py#L293-L305](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L293-L305)
- **Async**: `No`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Добавляет форматированный параграф по ГОСТ.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `doc` | `Document` | Input parameter |
| `line` | `str` | Input parameter |

#### Step-by-Step Logic Execution
1. `cleaned = clean_math_text(line)`
2. `if not cleaned or cleaned.startswith("---"):`
3. `p = doc.add_paragraph()`
4. `format_gost_paragraph(p)`
5. `parts = re.split(r"(\*\*.*?\*\*)", cleaned)`
6. `for part in parts:`

---

### `init_gost_document`
- **Signature**: `def init_gost_document() -> Document`
- **Source Reference**: [utils/doc_generator.py#L308-L314](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L308-L314)
- **Async**: `No`
- **Return Type**: `Document`

#### Purpose & Architectural Intent
Инициализирует документ Word с ГОСТ полями, стилями и нумерацией.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `doc = Document()`
2. `setup_gost_margins(doc)`
3. `setup_gost_styles(doc)`
4. `setup_page_numbering(doc)`
5. `return doc`

---

### `create_solution_docx`
- **Signature**: `def create_solution_docx( solution_text: str, output_path: str | None = None, student_name: str = "Студент", teacher_name: str = "Преподаватель", year: int | None = None, group_name: str | None = None, ) -> str`
- **Source Reference**: [utils/doc_generator.py#L317-L336](file:///home/u/Рабочий стол/para/utils/doc_generator.py#L317-L336)
- **Async**: `No`
- **Return Type**: `str`

#### Purpose & Architectural Intent
Генерирует 100% соответствующий ГОСТ 7.32-2017 Word DOCX документ по образцу.

#### Parameters Contract
| Parameter | Type / Constraint | Description |
| :--- | :--- | :--- |
| `solution_text` | `str` | Input parameter |
| `output_path` | `str | None` | Input parameter |
| `student_name` | `str` | Input parameter |
| `teacher_name` | `str` | Input parameter |
| `year` | `int | None` | Input parameter |
| `group_name` | `str | None` | Input parameter |

#### Step-by-Step Logic Execution
1. `target_path = output_path or os.path.join(tempfile.gettempdir(), "solution.docx")`
2. `log.debug(f"Создание DOCX документа решения по ГОСТ: {target_path}")`
3. `doc = init_gost_document()`
4. `create_title_page(doc, student_name, teacher_name, year, group_name)`
5. `headings = extract_headings_from_text(solution_text)`
6. `build_table_of_contents(doc, headings)`

---
