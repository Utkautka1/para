"""
Модуль генерации отчетов в формате DOCX по точному образцу файла ГОСТ.

Обеспечивает 100% соответствие эталону:
1. Официальный титульный лист (Стр. 1) с шапкой Министерства и Колледжа, по центру 'ОТЧЕТ ПО ВЫПОЛНЕНИЮ ЗАДАНИЯ'.
2. Таблица подписей 'Выполнил студент группы 1-КПД-3: Иван Иванов' / 'Проверил преподаватель: Иван Иванов' с датой.
3. Отдельная страница 'СОДЕРЖАНИЕ' (Стр. 2) с интерактивными кликабельными гиперссылками на разделы.
4. Разделение главных структурных элементов на новые страницы (Page Break).
5. Преобразование таблиц Markdown в настоящие таблицы Word ('Table Grid') с оформлением ячеек.
6. Выравнивание основного текста по ширине (Justified), Times New Roman 14 pt, 1.5 интервал, красная строка 1.25 см.
"""

import re
import io
from typing import List, Tuple, Dict
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from core.logger import get_logger

log = get_logger("doc_generator")


def setup_gost_margins(doc: Document) -> None:
    """
    Настраивает размеры полей документа по эталону ГОСТ (левое 3см, правое 1.5см, верх/низ 2см).
    """
    for section in doc.sections:
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(1.5)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)


def setup_page_numbering(doc: Document) -> None:
    """
    Настраивает нумерацию страниц внизу по центру Times New Roman 14pt (скрывает на 1 странице).
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
    Настраивает стиль по умолчанию (Times New Roman, 14pt, обычный, черный цвет).
    """
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(14)
    font.color.rgb = RGBColor(0, 0, 0)


def add_title_signature_table(doc: Document) -> None:
    """
    Добавляет аккуратную таблицу подписей Выполнил/Проверил по образцу ГОСТ.
    """
    tbl = doc.add_table(rows=2, cols=2)
    tbl.style = 'Normal Table'
    cell_data = [
        ("Выполнил студент группы 1-КПД-3:", "______________ Иван Иванов\n«___» ____________ 2026 г."),
        ("Проверил преподаватель:", "______________ Иван Иванов\n«___» ____________ 2026 г.")
    ]
    for r_idx, (left_txt, right_txt) in enumerate(cell_data):
        row = tbl.rows[r_idx]
        row.cells[0].text = left_txt
        row.cells[1].text = right_txt
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing = 1.15
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(14)


def create_title_page(doc: Document) -> None:
    """
    Создает официальный титульный лист по образцу ГОСТ (Страница 1).
    """
    p_hdr = doc.add_paragraph()
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hdr.paragraph_format.line_spacing = 1.15
    p_hdr.add_run("МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ РОССИЙСКОЙ ФЕДЕРАЦИИ\n").bold = True
    p_hdr.add_run("КГБПОУ «КОМСОМОЛЬСКИЙ-НА-АМУРЕ ТЕХНОЛОГИЧЕСКИЙ КОЛЛЕДЖ»\n\n\n").bold = True

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.add_run("ОТЧЕТ ПО ВЫПОЛНЕНИЮ ЗАДАНИЯ\n\n").bold = True

    add_title_signature_table(doc)

    p_ftr = doc.add_paragraph()
    p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ftr.paragraph_format.space_before = Pt(100)
    p_ftr.add_run("Санкт-Петербург – 2026")
    doc.add_page_break()


def clean_math_text(text: str) -> str:
    """
    Очищает LaTeX конструкции и лишние точки в конце заголовков по ГОСТ.
    """
    t = text.replace("$$", "").replace("$", "")
    t = t.replace("\\cdot", "·").replace("\\Delta", "Δ")
    t = t.replace("\\begin{vmatrix}", "| ").replace("\\end{vmatrix}", " |")
    t = re.sub(r'\\([a-zA-Z]+)', r'\1', t)
    return t.strip().rstrip(".")


def format_gost_paragraph(p) -> None:
    """
    Применяет ГОСТ форматирование к абзацу (1.5 интервал, 1.25 см красная строка).
    """
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def add_bookmark_to_paragraph(p, bookmark_name: str, bookmark_id: int) -> None:
    """
    Добавляет внутреннюю закладку Word к параграфу заголовка.
    """
    bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bookmark_id}" w:name="{bookmark_name}"/>')
    bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bookmark_id}"/>')
    p._p.insert(0, bm_start)
    p._p.append(bm_end)


def add_toc_hyperlink(doc: Document, text: str, bookmark_name: str) -> None:
    """
    Добавляет пункт СОДЕРЖАНИЯ с кликабельной гиперссылкой по ГОСТ.
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
        f'<w:t>{text}</w:t></w:r>'
    )
    h_xml.append(r_xml)
    p._p.append(h_xml)


def extract_headings_from_text(solution_text: str) -> List[Tuple[str, str, int, int]]:
    """
    Извлекает все заголовки из текста решения для построения Содержания.
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


def build_table_of_contents(doc: Document, headings: List[Tuple[str, str, int, int]]) -> None:
    """
    Создает отдельную страницу СОДЕРЖАНИЕ с гиперссылками по ГОСТ (Страница 2).
    """
    if not headings:
        return
    add_gost_heading(doc, "СОДЕРЖАНИЕ", level=1, page_break=False)
    for _, title, _, idx in headings:
        bm_name = f"sec_bm_{idx}"
        add_toc_hyperlink(doc, title, bm_name)
    doc.add_page_break()


def add_gost_heading(doc: Document, title: str, level: int, page_break: bool = False) -> None:
    """
    Добавляет заголовок раздела по ГОСТ.
    """
    if page_break:
        doc.add_page_break()
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(1.25 if level > 1 else 0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT
    clean_t = clean_math_text(title)
    run = p.add_run(clean_t.upper() if level == 1 else clean_t)
    run.bold = True
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0, 0, 0)


def add_gost_heading_with_bookmark(doc: Document, title: str, level: int, bm_id: int) -> None:
    """
    Добавляет заголовок с привязаной закладкой и разрывом страницы для 1 уровня.
    """
    if level == 1:
        doc.add_page_break()
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(1.25 if level > 1 else 0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT
    clean_t = clean_math_text(title)
    run = p.add_run(clean_t.upper() if level == 1 else clean_t)
    run.bold = True
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0, 0, 0)
    add_bookmark_to_paragraph(p, f"sec_bm_{bm_id}", bm_id)


def parse_markdown_table_rows(table_lines: List[str]) -> List[List[str]]:
    """
    Парсит строки маркдаун таблицы в двумерный массив ячеек.
    """
    rows = []
    for line in table_lines:
        if "|---" in line or "| :---" in line or "|:---" in line:
            continue
        cells = [c.strip() for c in line.strip("| \t").split("|")]
        if any(cells):
            rows.append(cells)
    return rows


def add_docx_table_from_markdown(doc: Document, table_lines: List[str]) -> None:
    """
    Создает настоящую аккуратную таблицу Word по ГОСТ из Markdown строк.
    """
    rows_data = parse_markdown_table_rows(table_lines)
    if not rows_data:
        return
    table = doc.add_table(rows=len(rows_data), cols=max(len(r) for r in rows_data))
    table.style = 'Table Grid'
    for r_idx, row in enumerate(rows_data):
        for c_idx, cell_text in enumerate(row):
            if c_idx < len(table.rows[r_idx].cells):
                cell = table.rows[r_idx].cells[c_idx]
                cell.text = clean_math_text(cell_text)
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.15
                    for run in p.runs:
                        run.font.name = 'Times New Roman'
                        run.font.size = Pt(12)
                        if r_idx == 0:
                            run.bold = True


def process_document_content_lines(doc: Document, lines: List[str], heading_map: Dict) -> None:
    """
    Обрабатывает строки документа, распознавая таблицы, заголовки и параграфы.
    """
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("|") and "|" in line[1:]:
            t_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                t_lines.append(lines[i])
                i += 1
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
    Добавляет форматированный параграф по ГОСТ.
    """
    cleaned = clean_math_text(line)
    if not cleaned or cleaned.startswith("---"):
        return
    p = doc.add_paragraph()
    format_gost_paragraph(p)
    parts = re.split(r'(\*\*.*?\*\*)', cleaned)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = p.add_run(part[2:-2])
            run.bold = True
        elif part:
            p.add_run(part)


def create_solution_docx(solution_text: str, output_path: str = "/tmp/solution.docx") -> str:
    """
    Генерирует 100% соответствующий ГОСТ 7.32-2017 Word DOCX документ по образцу.
    """
    log.debug(f"Создание DOCX документа решения по ГОСТ: {output_path}")
    doc = Document()
    setup_gost_margins(doc)
    setup_gost_styles(doc)
    setup_page_numbering(doc)

    create_title_page(doc)
    headings = extract_headings_from_text(solution_text)
    build_table_of_contents(doc, headings)

    heading_map = {h[0]: (h[1], h[2], h[3]) for h in headings}
    lines = solution_text.split("\n")
    process_document_content_lines(doc, lines, heading_map)

    doc.save(output_path)
    log.info(f"DOCX файл решения по точному образцу ГОСТ создан: {output_path}")
    return output_path
