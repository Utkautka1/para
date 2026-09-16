"""
Модуль генерации отчетов в формате DOCX по ГОСТ 7.32-2017.

Соблюдает государственные стандарты колледжа по оформлению учебных работ:
- Поля: левое 30 мм (3.0 см), правое 15 мм (1.5 см), верхнее и нижнее 20 мм (2.0 см).
- Шрифт: Times New Roman, обычный, цвет черный, размер 14 pt.
- Выравнивание основного текста по ширине (Justified).
- Межстрочный интервал: полуторный (1.5).
- Красная строка (абзацный отступ): 1.25 см для всех параграфов и заголовков.
- Заголовки без точек в конце, с полужирным выделением и пустой строкой после.
- Нижний колонтитул с центрированным шрифтом Times New Roman 14 pt.
- Шапка выполения: Иван Иванов, Группа 1-КПД-3, преподаватель Иван Иванов.
"""

import re
import io
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
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


def add_gost_heading(doc: Document, title: str, level: int) -> None:
    """
    Добавляет заголовок раздела с красной строкой 1.25 см по ГОСТ 7.32-2017.
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


def create_solution_docx(solution_text: str, output_path: str = "/tmp/solution.docx") -> str:
    """
    Генерирует аккуратный Word DOCX документ по стандартам ГОСТ 7.32-2017.
    """
    log.debug(f"Создание DOCX документа решения по ГОСТ: {output_path}")
    doc = Document()
    setup_gost_margins(doc)
    setup_gost_styles(doc)
    setup_page_numbering(doc)

    add_gost_heading(doc, "ОТЧЕТ ПО ВЫПОЛНЕНИЮ ЗАДАНИЯ", level=1)
    add_title_block(doc)

    for line in solution_text.split("\n"):
        if line.startswith("# "):
            add_gost_heading(doc, line.replace("# ", ""), level=1)
        elif line.startswith("## "):
            add_gost_heading(doc, line.replace("## ", ""), level=2)
        elif line.startswith("### "):
            add_gost_heading(doc, line.replace("### ", ""), level=3)
        else:
            add_formatted_paragraph(doc, line)

    doc.save(output_path)
    log.info(f"DOCX файл с решением по ГОСТ создан: {output_path}")
    return output_path
