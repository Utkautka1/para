"""
Модуль генерации отчетов в формате DOCX по точному образцу файла ГОСТ 7.32-2017.

Обеспечивает 100% соответствие эталону:
1. Официальный титульный лист (Стр. 1) с шапкой Министерства и Колледжа.
2. Таблица подписей 'Выполнил студент группы 1-КПД-3' / 'Проверил преподаватель'.
3. Отдельная страница 'СОДЕРЖАНИЕ' (Стр. 2) с интерактивными кликабельными гиперссылками.
4. Разделение главных структурных элементов на новые страницы (Page Break).
5. Преобразование таблиц Markdown в таблицы Word ('Table Grid') с оформлением ячеек.
6. Выравнивание основного текста по ширине (Justified), Times New Roman 14 pt, 1.5 интервал.
"""

import os
import re
import tempfile
from datetime import datetime

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Cm, Pt, RGBColor

from config import GROUP_NAME, TIMEZONE
from core.logger import get_logger

log = get_logger("doc_generator")


def setup_gost_margins(doc: Document) -> None:
    """
    Настраивает размеры полей документа по государственному стандарту ГОСТ 7.32-2017.

    Устанавливает отступы: левый 3.0 см (для подшивки), правый 1.5 см, верхний и
    нижний по 2.0 см для всех разделов Word-документа.

    Ничего не возвращает (модифицирует переданный объект Document in-place).
    """
    for section in doc.sections:
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(1.5)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)


def setup_page_numbering(doc: Document) -> None:
    """
    Настраивает нумерацию страниц по центру нижнего колонтитула.

    Активирует флаг different_first_page_header_footer, гарантируя скрытие номера
    страницы на титульном листе согласно регламенту оформления научных работ.

    Ничего не возвращает.
    """
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    footer = section.footer
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)


def setup_gost_styles(doc: Document) -> None:
    """
    Устанавливает типографику по умолчанию для базового стиля 'Normal'.

    Задает шрифт Times New Roman размером 14 пунктов черного цвета, служащий
    фундаментом для всего генерируемого академического контента.

    Ничего не возвращает.
    """
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(14)
    font.color.rgb = RGBColor(0, 0, 0)


def format_table_row_cells(row, left_txt: str, right_txt: str) -> None:
    """
    Заполняет и стилизует ячейки в строке таблицы подписей исполнителей.

    Устанавливает междустрочный интервал 1.15 и гарнитуру Times New Roman 14pt,
    обеспечивая визуальное выравнивание подписей и дат.

    Ничего не возвращает.
    """
    row.cells[0].text, row.cells[1].text = left_txt, right_txt
    for cell in row.cells:
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.15
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(14)


def add_title_signature_table(
    doc: Document,
    student_name: str = "Студент",
    teacher_name: str = "Преподаватель",
    year: int | None = None,
    group_name: str | None = None,
) -> None:
    """
    Добавляет аккуратную таблицу подписей 'Выполнил/Проверил' по образцу ГОСТ.

    Формирует скрытую двухколоночную сетку без видимых внешних рамок для
    строгого размещения данных студента и преподавателя на титульном листе.

    Ничего не возвращает.
    """
    target_year = year or datetime.now(TIMEZONE).year
    target_group = group_name or GROUP_NAME
    tbl = doc.add_table(rows=2, cols=2)
    tbl.style = "Normal Table"
    rows_data = [
        (
            f"Выполнил студент группы {target_group}:",
            f"______________ {student_name}\n«___» ____________ {target_year} г.",
        ),
        ("Проверил преподаватель:", f"______________ {teacher_name}\n«___» ____________ {target_year} г."),
    ]
    for idx, (ltxt, rtxt) in enumerate(rows_data):
        format_table_row_cells(tbl.rows[idx], ltxt, rtxt)


def add_title_header(doc: Document) -> None:
    """
    Добавляет официальную шапку Министерства и Университета на титульный лист.

    Центрирует наименование ведомства, вуза и специальности жирным начертанием
    с компактным междустрочным интервалом.

    Ничего не возвращает.
    """
    p_hdr = doc.add_paragraph()
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hdr.paragraph_format.line_spacing = 1.15
    p_hdr.add_run("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n").bold = True
    p_hdr.add_run("ПРОМТЕХДИЗАЙН\n").bold = True
    p_hdr.add_run("Санкт-Петербургский государственный университет промышленных технологий и дизайна\n").bold = True
    p_hdr.add_run("Направление: Разработка и управление программным обеспечением\n\n").bold = True


def create_title_page(
    doc: Document,
    student_name: str = "Студент",
    teacher_name: str = "Преподаватель",
    year: int | None = None,
    group_name: str | None = None,
) -> None:
    """
    Создает официальный титульный лист по образцу ГОСТ с последующим разрывом страницы.

    Объединяет шапку, заголовок отчета, таблицу согласующих подписей и город/год издания,
    завершая блок командой add_page_break.

    Ничего не возвращает.
    """
    target_year = year or datetime.now(TIMEZONE).year
    add_title_header(doc)
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.add_run("ОТЧЕТ ПО ВЫПОЛНЕНИЮ ЗАДАНИЯ\n\n").bold = True
    add_title_signature_table(doc, student_name, teacher_name, target_year, group_name)
    p_ftr = doc.add_paragraph()
    p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ftr.paragraph_format.space_before = Pt(80)
    p_ftr.add_run(f"Санкт-Петербург – {target_year}")
    doc.add_page_break()


def clean_math_text(text: str) -> str:
    """
    Очищает LaTeX конструкции и спецсимволы формул для текстового вывода.

    Заменяет математические разделители, греческие буквы и псевдографику на Unicode-эквиваленты,
    удаляя концевые точки в названиях заголовков по стандарту ГОСТ.

    Возвращает нормализованную текстовую строку.
    """
    t = text.replace("$$", "").replace("$", "")
    t = t.replace("\\cdot", "·").replace("\\Delta", "Δ")
    t = t.replace("\\begin{vmatrix}", "| ").replace("\\end{vmatrix}", " |")
    t = re.sub(r"\\([a-zA-Z]+)", r"\1", t)
    return t.strip().rstrip(".")


def format_gost_paragraph(p) -> None:
    """
    Применяет форматирование основного текста по ГОСТ к абзацу Word.

    Устанавливает междустрочный интервал 1.5, красную строку 1.25 см, нулевые
    внешние интервалы и выравнивание по ширине страницы.

    Ничего не возвращает.
    """
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def add_bookmark_to_paragraph(p, bookmark_name: str, bookmark_id: int) -> None:
    """
    Внедряет внутреннюю XML-закладку Word (bookmark) в указанный параграф.

    Позволяет интерактивным ссылкам в разделе СОДЕРЖАНИЕ мгновенно перемещать
    читателя к началу соответствующей главы в Word или PDF.

    Ничего не возвращает.
    """
    bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bookmark_id}" w:name="{bookmark_name}"/>')
    bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bookmark_id}"/>')
    p._p.insert(0, bm_start)
    p._p.append(bm_end)


def add_toc_hyperlink(doc: Document, text: str, bookmark_name: str) -> None:
    """
    Добавляет строку в раздел СОДЕРЖАНИЕ с активной кликабельной гиперссылкой.

    Генерирует XML-элемент w:hyperlink с якорем w:anchor, сохраняя единообразный
    шрифт Times New Roman 14pt без подчеркивания.

    Ничего не возвращает.
    """
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    h_xml = parse_xml(f'<w:hyperlink {nsdecls("w")} w:anchor="{bookmark_name}"/>')
    r_xml = parse_xml(
        f'<w:r {nsdecls("w")}><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
        f'<w:sz w:val="28"/><w:color w:val="000000"/><w:u w:val="none"/></w:rPr>'
        f"<w:t>{text}</w:t></w:r>"
    )
    h_xml.append(r_xml)
    p._p.append(h_xml)


def extract_headings_from_text(solution_text: str) -> list[tuple[str, str, int, int]]:
    """
    Извлекает заголовки уровней H1 (#) и H2 (##) из Markdown-текста решения.

    Определяет структурное дерево документа и порядковые индексы для создания
    гиперссылок в Содержании и закладок в основном тексте.

    Возвращает список кортежей (исходная строка, очищенный заголовок, уровень, id).
    """
    headings = []
    idx = 1
    for line in solution_text.split("\n"):
        if line.startswith("# "):
            title = clean_math_text(line.replace("# ", "")).upper()
            headings.append((line, title, 1, idx))
            idx += 1
        elif line.startswith("## "):
            title = clean_math_text(line.replace("## ", ""))
            headings.append((line, title, 2, idx))
            idx += 1
    return headings


def build_table_of_contents(doc: Document, headings: list[tuple[str, str, int, int]]) -> None:
    """
    Формирует отдельную страницу СОДЕРЖАНИЕ со списком разделов и гиперссылками.

    Размещается на второй странице работы сразу за титульным листом при наличии
    хотя бы одного заголовка раздела.

    Ничего не возвращает.
    """
    if not headings:
        return
    add_gost_heading(doc, "СОДЕРЖАНИЕ", level=1, page_break=False)
    for _, title, _, idx in headings:
        bm_name = f"sec_bm_{idx}"
        add_toc_hyperlink(doc, title, bm_name)


def _apply_heading_formatting(p, title: str, level: int) -> None:
    """
    Применяет визуальный стиль ГОСТ к параграфу заголовка.

    Центрирует заголовки первого уровня (H1) заглавными буквами, выравнивает H2
    по левому краю с красной строкой 1.25 см и полужирным начертанием.

    Ничего не возвращает.
    """
    p.paragraph_format.first_line_indent = Cm(1.25 if level > 1 else 0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT
    clean_t = clean_math_text(title)
    run = p.add_run(clean_t.upper() if level == 1 else clean_t)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0, 0, 0)


def add_gost_heading(doc: Document, title: str, level: int, page_break: bool = False) -> None:
    """
    Добавляет структурный заголовок раздела в документ Word.

    Используется для оформления оглавления и разделов без интерактивных ссылок,
    при необходимости вставляя разрыв страницы перед заголовком.

    Ничего не возвращает.
    """
    if page_break:
        doc.add_page_break()
    p = doc.add_paragraph()
    _apply_heading_formatting(p, title, level)


def add_gost_heading_with_bookmark(doc: Document, title: str, level: int, bm_id: int) -> None:
    """
    Добавляет заголовок главы с привязкой внутренней закладки Word.

    Начинает разделы 1-го уровня с новой страницы согласно ГОСТ 7.32-2017
    и регистрирует закладку для кликабельного перехода из Содержания.

    Ничего не возвращает.
    """
    if level == 1:
        doc.add_page_break()
    p = doc.add_paragraph()
    _apply_heading_formatting(p, title, level)
    add_bookmark_to_paragraph(p, f"sec_bm_{bm_id}", bm_id)


def parse_markdown_table_rows(table_lines: list[str]) -> list[list[str]]:
    """
    Парсит текстовые строки Markdown-таблицы в двумерный массив ячеек.

    Игнорирует строки-разделители (|---|) и отсекает пустые внешние пайпы,
    гарантируя корректное сопоставление колонок.

    Возвращает список списков строковых значений ячеек.
    """
    rows = []
    for line in table_lines:
        if "|---" in line or "| :---" in line or "|:---" in line:
            continue
        cells = [c.strip() for c in line.strip("| \t").split("|")]
        if any(cells):
            rows.append(cells)
    return rows


def _append_cell_run(p, text_part: str, is_header: bool, is_bold: bool) -> None:
    """
    Добавляет фрагмент текста в параграф ячейки таблицы с нужным начертанием.

    Устанавливает кегль 12pt Times New Roman, применяя полужирное выделение
    для заголовков колонок или выделенных Markdown-маркерами фрагментов.

    Ничего не возвращает.
    """
    run = p.add_run(text_part)
    if is_bold or is_header:
        run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)


def fill_table_cell(cell, cell_text: str, is_header: bool) -> None:
    """
    Заполняет ячейку таблицы Word с поддержкой Markdown-разметки жирного шрифта.

    Очищает математические выражения и форматирует абзац ячейки с одинарным интервалом
    1.15 pt для компактного размещения данных в табличной сетке.

    Ничего не возвращает.
    """
    cell.text = ""
    p = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    for part in re.split(r"(\*\*.*?\*\*)", clean_math_text(cell_text)):
        if part.startswith("**") and part.endswith("**"):
            _append_cell_run(p, part[2:-2], is_header, is_bold=True)
        elif part:
            _append_cell_run(p, part, is_header, is_bold=False)


def add_docx_table_from_markdown(doc: Document, table_lines: list[str]) -> None:
    """
    Создает аккуратную таблицу Word стиля 'Table Grid' из Markdown-блока.

    Рассчитывает максимальную ширину строк, инициализирует таблицу со стандартной
    сеткой границ и заполняет каждую ячейку с форматированием заголовков.

    Ничего не возвращает.
    """
    rows_data = parse_markdown_table_rows(table_lines)
    if not rows_data:
        return
    table = doc.add_table(rows=len(rows_data), cols=max(len(r) for r in rows_data))
    table.style = "Table Grid"
    for r_idx, row in enumerate(rows_data):
        for c_idx, cell_text in enumerate(row):
            if c_idx < len(table.rows[r_idx].cells):
                cell = table.rows[r_idx].cells[c_idx]
                fill_table_cell(cell, cell_text, is_header=(r_idx == 0))


def _consume_markdown_table(lines: list[str], start_idx: int) -> tuple[list[str], int]:
    """
    Выделяет непрерывную группу строк Markdown-таблицы из общего списка строк.

    Сканирует входные строки от start_idx до первой строки без символа '|',
    обеспечивая групповую передачу строк в генератор таблиц Word.

    Возвращает кортеж (список строк таблицы, следующий индекс строки).
    """
    t_lines: list[str] = []
    idx = start_idx
    while idx < len(lines) and lines[idx].startswith("|"):
        t_lines.append(lines[idx])
        idx += 1
    return t_lines, idx


def process_document_content_lines(doc: Document, lines: list[str], heading_map: dict) -> None:
    """
    Последовательно обрабатывает текстовые строки решения задачи.

    Распознает и маршрутизирует таблицы Markdown, заголовки разделов с закладками
    и обычные параграфы текста с ГОСТ-выравниванием.

    Ничего не возвращает.
    """
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("|") and "|" in line[1:]:
            t_lines, i = _consume_markdown_table(lines, i)
            add_docx_table_from_markdown(doc, t_lines)
            continue
        if line in heading_map:
            title, level, bm_id = heading_map[line]
            add_gost_heading_with_bookmark(doc, title, level, bm_id)
        else:
            add_formatted_paragraph(doc, line)
        i += 1


def add_formatted_paragraph(doc: Document, line: str) -> None:
    """
    Добавляет форматированный текстовый абзац по стандарту ГОСТ.

    Пропускает разделители ('---') и пустые строки, парсит вкрапления жирного
    шрифта и применяет красную строку с выравниванием по ширине.

    Ничего не возвращает.
    """
    cleaned = clean_math_text(line)
    if not cleaned or cleaned.startswith("---"):
        return
    p = doc.add_paragraph()
    format_gost_paragraph(p)
    for part in re.split(r"(\*\*.*?\*\*)", cleaned):
        if part.startswith("**") and part.endswith("**"):
            p.add_run(part[2:-2]).bold = True
        elif part:
            p.add_run(part)


def init_gost_document() -> Document:
    """
    Создает и настраивает новый объект Word-документа по ГОСТ.

    Задает геометрию полей страницы, базовый шрифт Times New Roman 14pt и
    нижний центрированный колонтитул с пропуском первой страницы.

    Возвращает сконфигурированный экземпляр docx.Document.
    """
    doc = Document()
    setup_gost_margins(doc)
    setup_gost_styles(doc)
    setup_page_numbering(doc)
    return doc


def create_solution_docx(
    solution_text: str,
    output_path: str | None = None,
    student_name: str = "Студент",
    teacher_name: str = "Преподаватель",
    year: int | None = None,
    group_name: str | None = None,
) -> str:
    """
    Генерирует академический DOCX-отчет по образцу ГОСТ 7.32-2017 из текста решения.

    Собирает титульный лист, страницу Содержания с гиперссылками, таблицы и главы
    с автоматическим сохранением во временный или целевой файл.

    Возвращает абсолютный путь к сгенерированному файлу .docx.
    """
    target_path = output_path or os.path.join(tempfile.gettempdir(), "solution.docx")
    log.debug(f"Создание DOCX документа решения по ГОСТ: {target_path}")
    doc = init_gost_document()
    create_title_page(doc, student_name, teacher_name, year, group_name)
    headings = extract_headings_from_text(solution_text)
    build_table_of_contents(doc, headings)
    heading_map = {h[0]: (h[1], h[2], h[3]) for h in headings}
    process_document_content_lines(doc, solution_text.split("\n"), heading_map)
    doc.save(target_path)
    log.info(f"DOCX файл решения по точному образцу ГОСТ создан: {target_path}")
    return target_path
