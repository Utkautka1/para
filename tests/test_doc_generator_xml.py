"""
Unit-тесты защиты сборки docx от XML-инъекций (utils/doc_generator.py).

Проверяет:
  1. Экранирование '&', '<', '>' в тексте заголовков из ответа LLM (to_xml_text)
  2. Удаление управляющих символов, запрещённых в XML 1.0
  3. Что заголовок с разметкой попадает в оглавление как текст, а не как XML-узлы
"""

from docx import Document

from utils.doc_generator import add_toc_hyperlink, to_xml_text


def test_to_xml_text_escapes_markup_and_strips_control_chars() -> None:
    assert to_xml_text("x < 3 & y > 1\x00\x0b") == "x &lt; 3 &amp; y &gt; 1"


def test_toc_hyperlink_keeps_injected_markup_as_text() -> None:
    doc = Document()
    payload = '</w:t><w:instrText>INCLUDEPICTURE "http://evil"</w:instrText><w:t>'
    add_toc_hyperlink(doc, payload, "sec_bm_1")

    paragraph = doc.paragraphs[-1]._p
    assert not paragraph.xpath(".//w:instrText")
    assert [t.text for t in paragraph.xpath(".//w:t")] == [payload]
