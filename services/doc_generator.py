"""
Модуль генерации отчетов в формате DOCX по ГОСТ 7.32-2017 с интерактивным Содержанием.

Создает кликабельное Содержание (гиперссылки на разделы) по стандарту ГОСТ:
- Поля: левое 30 мм, правое 15 мм, верхнее и нижнее 20 мм.
- Шрифт: Times New Roman 14 pt, полуторный интервал, красная строка 1.25 см.
- Раздел "СОДЕРЖАНИЕ" с внутренними гиперссылками на соответствующие заглавные разделы.
- Соблюдение персональных метаданных авторов (1-КПД-3, Иван Иванов).
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
    Настраивает размеры полей документа по стандарту ГОСТ 7.32-2017.
    """
    for section in doc.sections:
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(1.5)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)


def setup_page_numbering(doc: Document) -> None:
    """
    Настраивает параметры нижнего колонтитула по ГОСТ.
    """
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)


def setup_gost_styles(doc: Document) -> None:
    """
    Настраивает параметры основного стиля (Times New Roman, 14pt, черный цвет).
    """
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(14)
    font.color.rgb = RGBColor(0, 0, 0)


def add_title_block(doc: Document) -> None:
    """
    Добавляет блок авторства по ГОСТ для группы 1-КПД-3.
    """
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.line_spacing = 1.15
    run1 = p.add_run("Выполнил: студент гр. 1-КПД-3\nИван Иванов\n\n")
    run1.bold = True
    run2 = p.add_run("Проверил: преподаватель\nИван Иванов\n")
    run2.bold = True
    p.paragraph_format.space_after = Pt(12)


def clean_math_text(text: str) -> str:
    """
    Очищает LaTeX конструкции и точки в конце заголовков по ГОСТ.
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
    Добавляет внутреннюю закладку Word к параграфу заголовка для гиперссылок.
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
    Создает интерактивный блок СОДЕРЖАНИЕ с гиперссылками на все разделы.
    """
    if not headings:
        return
    add_gost_heading(doc, "СОДЕРЖАНИЕ", level=1)
    for _, title, _, idx in headings:
        bm_name = f"sec_bm_{idx}"
        add_toc_hyperlink(doc, title, bm_name)
    doc.add_page_break()


def add_gost_heading(doc: Document, title: str, level: int) -> None:
    """
    Добавляет базовый заголовок раздела по ГОСТ.
    """
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    clean_t = clean_math_text(title)
    run = p.add_run(clean_t.upper() if level == 1 else clean_t)
    run.bold = True
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0, 0, 0)


def add_gost_heading_with_bookmark(doc: Document, title: str, level: int, bm_id: int) -> None:
    """
    Добавляет заголовок с привязаной закладкой для гиперссылок из Содержания.
    """
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    clean_t = clean_math_text(title)
    run = p.add_run(clean_t.upper() if level == 1 else clean_t)
    run.bold = True
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0, 0, 0)
    add_bookmark_to_paragraph(p, f"sec_bm_{bm_id}", bm_id)


def add_formatted_paragraph(doc: Document, line: str) -> None:
    """
    Добавляет форматированный абзац по ГОСТ с поддержкой **жирного** текста.
    """
    cleaned = clean_math_text(line)
    if not cleaned:
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
    Генерирует аккуратный Word DOCX документ с интерактивным Содержанием по ГОСТ.
    """
    log.debug(f"Создание DOCX документа решения с гиперссылками в Содержании: {output_path}")
    doc = Document()
    setup_gost_margins(doc)
    setup_gost_styles(doc)
    setup_page_numbering(doc)

    headings = extract_headings_from_text(solution_text)
    add_gost_heading(doc, "ОТЧЕТ ПО ВЫПОЛНЕНИЮ ЗАДАНИЯ", level=1)
    add_title_block(doc)
    build_table_of_contents(doc, headings)

    heading_map = {h[0]: (h[1], h[2], h[3]) for h in headings}
    for line in solution_text.split("\n"):
        if line in heading_map:
            title, level, bm_id = heading_map[line]
            add_gost_heading_with_bookmark(doc, title, level, bm_id)
        else:
            add_formatted_paragraph(doc, line)

    doc.save(output_path)
    log.info(f"DOCX файл с кликабельным Содержанием успешно создан: {output_path}")
    return output_path
