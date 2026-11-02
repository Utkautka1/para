# Component Reference: `utils/doc_generator.py`
> **File Path**: [`utils/doc_generator.py`](../../utils/doc_generator.py)
> **Subsystem**: `GOST Document Generator`

## 1. Purpose
Модуль генерации отчетов в формате DOCX по точному образцу файла ГОСТ 7.32-2017.


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |
| [`setup_gost_margins`](#setup_gost_margins) | Function | L31–L44 | `None` | Настраивает размеры полей документа по государственному... |
| [`setup_page_numbering`](#setup_page_numbering) | Function | L47–L62 | `None` | Настраивает нумерацию страниц по центру нижнего колонти... |
| [`setup_gost_styles`](#setup_gost_styles) | Function | L65–L78 | `None` | Устанавливает типографику по умолчанию для базового сти... |
| [`format_table_row_cells`](#format_table_row_cells) | Function | L81–L96 | `None` | Заполняет и стилизует ячейки в строке таблицы подписей ... |
| [`add_title_signature_table`](#add_title_signature_table) | Function | L99–L126 | `None` | Добавляет аккуратную таблицу подписей 'Выполнил/Провери... |
| [`add_title_header`](#add_title_header) | Function | L129–L144 | `None` | Добавляет официальную шапку Министерства и Университета... |
| [`create_title_page`](#create_title_page) | Function | L147–L172 | `None` | Создает официальный титульный лист по образцу ГОСТ с по... |
| [`clean_math_text`](#clean_math_text) | Function | L175–L188 | `str` | Очищает LaTeX конструкции и спецсимволы формул для текс... |
| [`format_gost_paragraph`](#format_gost_paragraph) | Function | L191–L204 | `None` | Применяет форматирование основного текста по ГОСТ к абз... |
| [`add_bookmark_to_paragraph`](#add_bookmark_to_paragraph) | Function | L207–L219 | `None` | Внедряет внутреннюю XML-закладку Word (bookmark) в указ... |
| [`to_xml_text`](#to_xml_text) | Function | L226–L235 | `str` | Готовит произвольную строку к вставке в текстовый узел ... |
| [`add_toc_hyperlink`](#add_toc_hyperlink) | Function | L238–L259 | `None` | Добавляет строку в раздел СОДЕРЖАНИЕ с активной кликабе... |
| [`extract_headings_from_text`](#extract_headings_from_text) | Function | L262–L282 | `list[tuple[str, str, int, int]]` | Извлекает заголовки уровней H1 (#) и H2 (##) из Markdow... |
| [`build_table_of_contents`](#build_table_of_contents) | Function | L285–L299 | `None` | Формирует отдельную страницу СОДЕРЖАНИЕ со списком разд... |
| [`_apply_heading_formatting`](#_apply_heading_formatting) | Function | L302–L321 | `None` | Применяет визуальный стиль ГОСТ к параграфу заголовка. |
| [`add_gost_heading`](#add_gost_heading) | Function | L324–L336 | `None` | Добавляет структурный заголовок раздела в документ Word... |
| [`add_gost_heading_with_bookmark`](#add_gost_heading_with_bookmark) | Function | L339–L352 | `None` | Добавляет заголовок главы с привязкой внутренней заклад... |
| [`parse_markdown_table_rows`](#parse_markdown_table_rows) | Function | L355–L371 | `list[list[str]]` | Парсит текстовые строки Markdown-таблицы в двумерный ма... |
| [`_append_cell_run`](#_append_cell_run) | Function | L374–L387 | `None` | Добавляет фрагмент текста в параграф ячейки таблицы с н... |
| [`fill_table_cell`](#fill_table_cell) | Function | L390–L408 | `None` | Заполняет ячейку таблицы Word с поддержкой Markdown-раз... |
| [`add_docx_table_from_markdown`](#add_docx_table_from_markdown) | Function | L411–L429 | `None` | Создает аккуратную таблицу Word стиля 'Table Grid' из M... |
| [`_consume_markdown_table`](#_consume_markdown_table) | Function | L432–L446 | `tuple[list[str], int]` | Выделяет непрерывную группу строк Markdown-таблицы из о... |
| [`process_document_content_lines`](#process_document_content_lines) | Function | L449–L470 | `None` | Последовательно обрабатывает текстовые строки решения з... |
| [`add_formatted_paragraph`](#add_formatted_paragraph) | Function | L473–L491 | `None` | Добавляет форматированный текстовый абзац по стандарту ... |
| [`init_gost_document`](#init_gost_document) | Function | L494–L507 | `Document` | Создает и настраивает новый объект Word-документа по ГО... |
| [`create_solution_docx`](#create_solution_docx) | Function | L510–L536 | `str` | Генерирует академический DOCX-отчет по образцу ГОСТ 7.3... |

---

## 3. Comprehensive Function Specifications

### `setup_gost_margins`
```python
def setup_gost_margins(doc: Document) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L31-L44`](../../utils/doc_generator.py#L31-L44)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Настраивает размеры полей документа по государственному стандарту ГОСТ 7.32-2017.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import setup_gost_margins

# Execute call
result = setup_gost_margins(doc=...)
```

---

### `setup_page_numbering`
```python
def setup_page_numbering(doc: Document) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L47-L62`](../../utils/doc_generator.py#L47-L62)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Настраивает нумерацию страниц по центру нижнего колонтитула.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import setup_page_numbering

# Execute call
result = setup_page_numbering(doc=...)
```

---

### `setup_gost_styles`
```python
def setup_gost_styles(doc: Document) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L65-L78`](../../utils/doc_generator.py#L65-L78)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Устанавливает типографику по умолчанию для базового стиля 'Normal'.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import setup_gost_styles

# Execute call
result = setup_gost_styles(doc=...)
```

---

### `format_table_row_cells`
```python
def format_table_row_cells(row, left_txt: str, right_txt: str) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L81-L96`](../../utils/doc_generator.py#L81-L96)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Заполняет и стилизует ячейки в строке таблицы подписей исполнителей.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `row` | `Any` | Yes | Parameter `row` of type `Any`. |
| `left_txt` | `str` | Yes | Parameter `left_txt` of type `str`. |
| `right_txt` | `str` | Yes | Parameter `right_txt` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import format_table_row_cells

# Execute call
result = format_table_row_cells(row=..., left_txt=..., right_txt=...)
```

---

### `add_title_signature_table`
```python
def add_title_signature_table( doc: Document, student_name: str = "Student", teacher_name: str = "Instructor", year: int | None = None, group_name: str | None = None, ) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L99-L126`](../../utils/doc_generator.py#L99-L126)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет аккуратную таблицу подписей 'Выполнил/Проверил' по образцу ГОСТ.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |
| `student_name` | `str` | Yes | Full name of the student recorded in the academic roster. |
| `teacher_name` | `str` | Yes | Parameter `teacher_name` of type `str`. |
| `year` | `int | None` | Yes | Parameter `year` of type `int | None`. |
| `group_name` | `str | None` | Yes | Academic group identifier (e.g., '1-KPD-3'). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import add_title_signature_table

# Execute call
result = add_title_signature_table(doc=..., student_name=..., teacher_name=...)
```

---

### `add_title_header`
```python
def add_title_header(doc: Document) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L129-L144`](../../utils/doc_generator.py#L129-L144)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет официальную шапку Министерства и Университета на титульный лист.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import add_title_header

# Execute call
result = add_title_header(doc=...)
```

---

### `create_title_page`
```python
def create_title_page( doc: Document, student_name: str = "Student", teacher_name: str = "Instructor", year: int | None = None, group_name: str | None = None, ) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L147-L172`](../../utils/doc_generator.py#L147-L172)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Создает официальный титульный лист по образцу ГОСТ с последующим разрывом страницы.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |
| `student_name` | `str` | Yes | Full name of the student recorded in the academic roster. |
| `teacher_name` | `str` | Yes | Parameter `teacher_name` of type `str`. |
| `year` | `int | None` | Yes | Parameter `year` of type `int | None`. |
| `group_name` | `str | None` | Yes | Academic group identifier (e.g., '1-KPD-3'). |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import create_title_page

# Execute call
result = create_title_page(doc=..., student_name=..., teacher_name=...)
```

---

### `clean_math_text`
```python
def clean_math_text(text: str) -> str
```

- **Source Reference**: [`utils/doc_generator.py#L175-L188`](../../utils/doc_generator.py#L175-L188)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Очищает LaTeX конструкции и спецсимволы формул для текстового вывода.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import clean_math_text

# Execute call
result = clean_math_text(text=...)
```

---

### `format_gost_paragraph`
```python
def format_gost_paragraph(p) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L191-L204`](../../utils/doc_generator.py#L191-L204)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Применяет форматирование основного текста по ГОСТ к абзацу Word.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `p` | `Any` | Yes | Parameter `p` of type `Any`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import format_gost_paragraph

# Execute call
result = format_gost_paragraph(p=...)
```

---

### `add_bookmark_to_paragraph`
```python
def add_bookmark_to_paragraph(p, bookmark_name: str, bookmark_id: int) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L207-L219`](../../utils/doc_generator.py#L207-L219)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Внедряет внутреннюю XML-закладку Word (bookmark) в указанный параграф.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `p` | `Any` | Yes | Parameter `p` of type `Any`. |
| `bookmark_name` | `str` | Yes | Parameter `bookmark_name` of type `str`. |
| `bookmark_id` | `int` | Yes | Parameter `bookmark_id` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import add_bookmark_to_paragraph

# Execute call
result = add_bookmark_to_paragraph(p=..., bookmark_name=..., bookmark_id=...)
```

---

### `to_xml_text`
```python
def to_xml_text(text: str) -> str
```

- **Source Reference**: [`utils/doc_generator.py#L226-L235`](../../utils/doc_generator.py#L226-L235)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Готовит произвольную строку к вставке в текстовый узел WordprocessingML.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Yes | Parameter `text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import to_xml_text

# Execute call
result = to_xml_text(text=...)
```

---

### `add_toc_hyperlink`
```python
def add_toc_hyperlink(doc: Document, text: str, bookmark_name: str) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L238-L259`](../../utils/doc_generator.py#L238-L259)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет строку в раздел СОДЕРЖАНИЕ с активной кликабельной гиперссылкой.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |
| `text` | `str` | Yes | Parameter `text` of type `str`. |
| `bookmark_name` | `str` | Yes | Parameter `bookmark_name` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import add_toc_hyperlink

# Execute call
result = add_toc_hyperlink(doc=..., text=..., bookmark_name=...)
```

---

### `extract_headings_from_text`
```python
def extract_headings_from_text(solution_text: str) -> list[tuple[str, str, int, int]]
```

- **Source Reference**: [`utils/doc_generator.py#L262-L282`](../../utils/doc_generator.py#L262-L282)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[tuple[str, str, int, int]]`

#### Overview & Architectural Purpose
Извлекает заголовки уровней H1 (#) и H2 (##) из Markdown-текста решения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `solution_text` | `str` | Yes | Parameter `solution_text` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import extract_headings_from_text

# Execute call
result = extract_headings_from_text(solution_text=...)
```

---

### `build_table_of_contents`
```python
def build_table_of_contents(doc: Document, headings: list[tuple[str, str, int, int]]) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L285-L299`](../../utils/doc_generator.py#L285-L299)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Формирует отдельную страницу СОДЕРЖАНИЕ со списком разделов и гиперссылками.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |
| `headings` | `list[tuple[str, str, int, int]]` | Yes | Parameter `headings` of type `list[tuple[str, str, int, int]]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import build_table_of_contents

# Execute call
result = build_table_of_contents(doc=..., headings=...)
```

---

### `_apply_heading_formatting`
```python
def _apply_heading_formatting(p, title: str, level: int) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L302-L321`](../../utils/doc_generator.py#L302-L321)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Применяет визуальный стиль ГОСТ к параграфу заголовка.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `p` | `Any` | Yes | Parameter `p` of type `Any`. |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `level` | `int` | Yes | Progressive student academic gamification tier level. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import _apply_heading_formatting

# Execute call
result = _apply_heading_formatting(p=..., title=..., level=...)
```

---

### `add_gost_heading`
```python
def add_gost_heading(doc: Document, title: str, level: int, page_break: bool = False) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L324-L336`](../../utils/doc_generator.py#L324-L336)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет структурный заголовок раздела в документ Word.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `level` | `int` | Yes | Progressive student academic gamification tier level. |
| `page_break` | `bool` | Yes | Parameter `page_break` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import add_gost_heading

# Execute call
result = add_gost_heading(doc=..., title=..., level=...)
```

---

### `add_gost_heading_with_bookmark`
```python
def add_gost_heading_with_bookmark(doc: Document, title: str, level: int, bm_id: int) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L339-L352`](../../utils/doc_generator.py#L339-L352)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет заголовок главы с привязкой внутренней закладки Word.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |
| `title` | `str` | Yes | Parameter `title` of type `str`. |
| `level` | `int` | Yes | Progressive student academic gamification tier level. |
| `bm_id` | `int` | Yes | Parameter `bm_id` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import add_gost_heading_with_bookmark

# Execute call
result = add_gost_heading_with_bookmark(doc=..., title=..., level=...)
```

---

### `parse_markdown_table_rows`
```python
def parse_markdown_table_rows(table_lines: list[str]) -> list[list[str]]
```

- **Source Reference**: [`utils/doc_generator.py#L355-L371`](../../utils/doc_generator.py#L355-L371)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `list[list[str]]`

#### Overview & Architectural Purpose
Парсит текстовые строки Markdown-таблицы в двумерный массив ячеек.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `table_lines` | `list[str]` | Yes | Parameter `table_lines` of type `list[str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import parse_markdown_table_rows

# Execute call
result = parse_markdown_table_rows(table_lines=...)
```

---

### `_append_cell_run`
```python
def _append_cell_run(p, text_part: str, is_header: bool, is_bold: bool) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L374-L387`](../../utils/doc_generator.py#L374-L387)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет фрагмент текста в параграф ячейки таблицы с нужным начертанием.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `p` | `Any` | Yes | Parameter `p` of type `Any`. |
| `text_part` | `str` | Yes | Parameter `text_part` of type `str`. |
| `is_header` | `bool` | Yes | Parameter `is_header` of type `bool`. |
| `is_bold` | `bool` | Yes | Parameter `is_bold` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import _append_cell_run

# Execute call
result = _append_cell_run(p=..., text_part=..., is_header=...)
```

---

### `fill_table_cell`
```python
def fill_table_cell(cell, cell_text: str, is_header: bool) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L390-L408`](../../utils/doc_generator.py#L390-L408)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Заполняет ячейку таблицы Word с поддержкой Markdown-разметки жирного шрифта.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cell` | `Any` | Yes | Parameter `cell` of type `Any`. |
| `cell_text` | `str` | Yes | Parameter `cell_text` of type `str`. |
| `is_header` | `bool` | Yes | Parameter `is_header` of type `bool`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import fill_table_cell

# Execute call
result = fill_table_cell(cell=..., cell_text=..., is_header=...)
```

---

### `add_docx_table_from_markdown`
```python
def add_docx_table_from_markdown(doc: Document, table_lines: list[str]) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L411-L429`](../../utils/doc_generator.py#L411-L429)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Создает аккуратную таблицу Word стиля 'Table Grid' из Markdown-блока.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |
| `table_lines` | `list[str]` | Yes | Parameter `table_lines` of type `list[str]`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import add_docx_table_from_markdown

# Execute call
result = add_docx_table_from_markdown(doc=..., table_lines=...)
```

---

### `_consume_markdown_table`
```python
def _consume_markdown_table(lines: list[str], start_idx: int) -> tuple[list[str], int]
```

- **Source Reference**: [`utils/doc_generator.py#L432-L446`](../../utils/doc_generator.py#L432-L446)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `tuple[list[str], int]`

#### Overview & Architectural Purpose
Выделяет непрерывную группу строк Markdown-таблицы из общего списка строк.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `lines` | `list[str]` | Yes | Parameter `lines` of type `list[str]`. |
| `start_idx` | `int` | Yes | Parameter `start_idx` of type `int`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import _consume_markdown_table

# Execute call
result = _consume_markdown_table(lines=..., start_idx=...)
```

---

### `process_document_content_lines`
```python
def process_document_content_lines(doc: Document, lines: list[str], heading_map: dict) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L449-L470`](../../utils/doc_generator.py#L449-L470)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Последовательно обрабатывает текстовые строки решения задачи.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |
| `lines` | `list[str]` | Yes | Parameter `lines` of type `list[str]`. |
| `heading_map` | `dict` | Yes | Parameter `heading_map` of type `dict`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import process_document_content_lines

# Execute call
result = process_document_content_lines(doc=..., lines=..., heading_map=...)
```

---

### `add_formatted_paragraph`
```python
def add_formatted_paragraph(doc: Document, line: str) -> None
```

- **Source Reference**: [`utils/doc_generator.py#L473-L491`](../../utils/doc_generator.py#L473-L491)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `None`

#### Overview & Architectural Purpose
Добавляет форматированный текстовый абзац по стандарту ГОСТ.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `doc` | `Document` | Yes | Parameter `doc` of type `Document`. |
| `line` | `str` | Yes | Parameter `line` of type `str`. |

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import add_formatted_paragraph

# Execute call
result = add_formatted_paragraph(doc=..., line=...)
```

---

### `init_gost_document`
```python
def init_gost_document() -> Document
```

- **Source Reference**: [`utils/doc_generator.py#L494-L507`](../../utils/doc_generator.py#L494-L507)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `Document`

#### Overview & Architectural Purpose
Создает и настраивает новый объект Word-документа по ГОСТ.

#### Parameters Contract
*This method takes no input parameters.*

#### Concurrency & Side Effects
- Stateless pure functional computation without external mutations.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import init_gost_document

# Execute call
result = init_gost_document()
```

---

### `create_solution_docx`
```python
def create_solution_docx( solution_text: str, output_path: str | None = None, student_name: str = "Student", teacher_name: str = "Instructor", year: int | None = None, group_name: str | None = None, ) -> str
```

- **Source Reference**: [`utils/doc_generator.py#L510-L536`](../../utils/doc_generator.py#L510-L536)
- **Execution Mode**: `Synchronous`
- **Return Contract**: `str`

#### Overview & Architectural Purpose
Генерирует академический DOCX-отчет по образцу ГОСТ 7.32-2017 из текста решения.

#### Parameters Contract
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `solution_text` | `str` | Yes | Parameter `solution_text` of type `str`. |
| `output_path` | `str | None` | Yes | Parameter `output_path` of type `str | None`. |
| `student_name` | `str` | Yes | Full name of the student recorded in the academic roster. |
| `teacher_name` | `str` | Yes | Parameter `teacher_name` of type `str`. |
| `year` | `int | None` | Yes | Parameter `year` of type `int | None`. |
| `group_name` | `str | None` | Yes | Academic group identifier (e.g., '1-KPD-3'). |

#### Concurrency & Side Effects
- Emits structured telemetry events to system logging subsystem.

#### Fault Tolerance & Error Modes
Propagates unexpected runtime errors up the call stack to global exception handlers.

#### Production Usage Example
```python
from utils.doc_generator import create_solution_docx

# Execute call
result = create_solution_docx(solution_text=..., output_path=..., student_name=...)
```

---
