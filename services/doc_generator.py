"""
Модуль генерации аккуратных документов (PDF / DOCX) с решениями ДЗ.

Форматирует текстовое решение задачи в стиле Senior-документа.
"""

import os
from docx import Document
from core.logger import get_logger

log = get_logger("doc_generator")


def create_solution_docx(solution_text: str, output_path: str = "/tmp/solution.docx") -> str:
    """
    Генерирует аккуратный DOCX документ с решением задания.

    :param solution_text: Текст решения от DeepSeek
    :param output_path: Путь для сохранения файла
    :return: Путь к созданному файлу
    """
    log.debug(f"Создание DOCX документа решения: {output_path}")
    doc = Document()
    doc.add_heading("Готовое решение домашнего задания", level=1)
    
    for line in solution_text.split("\n"):
        if line.startswith("# "):
            doc.add_heading(line.replace("# ", ""), level=2)
        elif line.startswith("## "):
            doc.add_heading(line.replace("## ", ""), level=3)
        elif line.strip():
            doc.add_paragraph(line)

    doc.save(output_path)
    log.info(f"DOCX файл с решением создан: {output_path}")
    return output_path
