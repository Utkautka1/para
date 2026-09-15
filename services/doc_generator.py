"""
Модуль генерации аккуратных документов DOCX с красивым форматированием математики и матриц.
"""

import re
from docx import Document
from docx.shared import Pt, RGBColor
from core.logger import get_logger

log = get_logger("doc_generator")


def clean_math_text(text: str) -> str:
    """
    Очищает LaTeX конструкции, превращая их в стандартный читаемый математический текст.

    :param text: Исходная строка с LaTeX
    :return: Читаемая строка
    """
    t = text.replace("$$", "").replace("$", "")
    t = t.replace("\\cdot", "·").replace("\\Delta", "Δ")
    t = t.replace("\\begin{vmatrix}", "| ").replace("\\end{vmatrix}", " |")
    t = re.sub(r'\\([a-zA-Z]+)', r'\1', t)
    return t.strip()


def add_formatted_paragraph(doc: Document, line: str) -> None:
    """
    Добавляет форматированный параграф в DOCX документ.

    :param doc: Объект документа Word
    :param line: Текстовая строка
    """
    cleaned = clean_math_text(line)
    if not cleaned:
        return
    
    p = doc.add_paragraph()
    if line.startswith("**") and line.endswith("**"):
        run = p.add_run(cleaned.replace("**", ""))
        run.bold = True
    else:
        p.add_run(cleaned)


def create_solution_docx(solution_text: str, output_path: str = "/tmp/solution.docx") -> str:
    """
    Генерирует аккуратный Word DOCX документ с решением задания.

    :param solution_text: Текст решения от DeepSeek
    :param output_path: Путь для сохранения файла
    :return: Путь к созданному файлу
    """
    log.debug(f"Создание DOCX документа решения: {output_path}")
    doc = Document()
    doc.add_heading("Готовое решение домашнего задания", level=1)
    
    for line in solution_text.split("\n"):
        if line.startswith("# "):
            doc.add_heading(clean_math_text(line.replace("# ", "")), level=2)
        elif line.startswith("## "):
            doc.add_heading(clean_math_text(line.replace("## ", "")), level=3)
        elif line.startswith("### "):
            doc.add_heading(clean_math_text(line.replace("### ", "")), level=4)
        else:
            add_formatted_paragraph(doc, line)

    doc.save(output_path)
    log.info(f"DOCX файл с решением успешно создан: {output_path}")
    return output_path
