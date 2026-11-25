"""Export the saved notebook, including code and outputs, to an editable Word report.

Install export dependencies: python -m pip install -r requirements-report.txt
Run from any folder: python scripts/export_report.py
This exports saved outputs; it does not rerun model inference.
"""

from pathlib import Path

import nbformat
from bs4 import BeautifulSoup, NavigableString, Tag
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from nbconvert.filters import markdown2html


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "Lab4_Machine_Translation.ipynb"
REPORT = ROOT / "Lab4_Machine_Translation_Report.docx"


def set_font(style, name, size):
    style.font.name = name
    style.font.size = Pt(size)


def shade(element, fill):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    element.append(shading)


def field(paragraph, instruction):
    element = OxmlElement("w:fldSimple")
    element.set(qn("w:instr"), instruction)
    paragraph._p.append(element)


def make_document():
    document = Document()
    properties = document.core_properties
    properties.title = "Lab 4: Foreign Language to English Translation"
    properties.author = "Albert Kabore"
    properties.subject = (
        "English-to-Romanian machine translation; PhD Student in Artificial "
        "Intelligence, University of the Cumberlands"
    )
    properties.keywords = "machine translation, T5, WMT16, BLEU"
    properties.comments = "Exported from the notebook's saved content and outputs."

    section = document.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.top_margin = section.bottom_margin = Inches(0.6)
    section.left_margin = section.right_margin = Inches(0.65)
    section.header_distance = section.footer_distance = Inches(0.25)

    normal = document.styles["Normal"]
    set_font(normal, "Arial", 10.5)
    normal.paragraph_format.line_spacing = 1.1
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.widow_control = True
    for name, size in [("Title", 22), ("Heading 1", 16), ("Heading 2", 12)]:
        style = document.styles[name]
        set_font(style, "Arial", size)
        style.font.color.rgb = RGBColor.from_string("18212B")
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(14 if name != "Title" else 0)
        style.paragraph_format.space_after = Pt(9)

    for name, size in [("Lab Code", 8), ("Lab Output", 7.8)]:
        style = document.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = normal
        set_font(style, "Consolas", size)
        style.paragraph_format.line_spacing = 1
        style.paragraph_format.space_before = Pt(5)
        style.paragraph_format.space_after = Pt(7)
        style.paragraph_format.left_indent = Inches(0.08)
        style.paragraph_format.right_indent = Inches(0.08)
        style.paragraph_format.keep_together = False
        style.paragraph_format.widow_control = False

    if "Hyperlink" not in document.styles:
        document.styles.add_style("Hyperlink", WD_STYLE_TYPE.CHARACTER)
    link_style = document.styles["Hyperlink"]
    link_style.font.color.rgb = RGBColor.from_string("174F7C")
    link_style.font.underline = True

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(document.styles["Footer"], "Arial", 8)
    footer.add_run("Albert Kabore · Lab 4 · ")
    field(footer, "PAGE")
    footer.add_run(" / ")
    field(footer, "NUMPAGES")
    update_fields = OxmlElement("w:updateFields")
    update_fields.set(qn("w:val"), "true")
    document.settings.element.append(update_fields)
    return document


class ReportWriter:
    def __init__(self, document):
        self.document = document

    def inline(self, node, paragraph, *, bold=False, italic=False, code=False, link=None):
        if isinstance(node, NavigableString):
            run = paragraph.add_run(str(node))
            run.bold, run.italic = bold, italic
            if code:
                run.font.name = "Consolas"
                run.font.size = Pt(9)
            if link is not None:
                run.style = "Hyperlink"
                link.append(run._r)
            return
        if not isinstance(node, Tag) or node.name in {"style", "script"}:
            return
        if "anchor-link" in node.get("class", []):
            return
        if node.name == "br":
            paragraph.add_run().add_break()
            return
        if node.name == "a" and node.get("href"):
            hyperlink = OxmlElement("w:hyperlink")
            relation = paragraph.part.relate_to(
                node["href"],
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                is_external=True,
            )
            hyperlink.set(qn("r:id"), relation)
            paragraph._p.append(hyperlink)
            link = hyperlink
        for child in node.children:
            self.inline(
                child, paragraph,
                bold=bold or node.name in {"strong", "b"},
                italic=italic or node.name in {"em", "i"},
                code=code or node.name == "code", link=link,
            )

    def numbered_list_id(self):
        """Create a native Word list that starts at one for each HTML ordered list."""
        numbering = self.document.part.numbering_part.element
        abstract_ids = [int(n.get(qn("w:abstractNumId"))) for n in numbering.findall(qn("w:abstractNum"))]
        abstract_id = max(abstract_ids, default=-1) + 1
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), str(abstract_id))
        level = OxmlElement("w:lvl")
        level.set(qn("w:ilvl"), "0")
        for name, value in [("start", "1"), ("numFmt", "decimal"), ("lvlText", "%1.")]:
            child = OxmlElement(f"w:{name}")
            child.set(qn("w:val"), value)
            level.append(child)
        properties = OxmlElement("w:pPr")
        indent = OxmlElement("w:ind")
        indent.set(qn("w:left"), "360")
        indent.set(qn("w:hanging"), "240")
        properties.append(indent)
        level.append(properties)
        abstract.append(level)
        numbering.insert_element_before(abstract, "w:num", "w:numIdMacAtCleanup")
        return numbering.add_num(abstract_id).numId

    def table(self, node):
        rows = node.find_all("tr")
        if not rows:
            return
        column_count = max(len(row.find_all(["th", "td"], recursive=False)) for row in rows)
        table = self.document.add_table(rows=0, cols=column_count)
        table.style = "Table Grid"
        table.autofit = False
        ratios = {
            3: [0.07, 0.465, 0.465],
            5: [0.28, 0.1, 0.38, 0.1, 0.14],
        }.get(column_count, [1 / column_count] * column_count)
        for column, ratio in zip(table.columns, ratios):
            column.width = Inches(7.2 * ratio)
        for index, source_row in enumerate(rows):
            row = table.add_row()
            cells = source_row.find_all(["th", "td"], recursive=False)
            for cell, source_cell, ratio in zip(row.cells, cells, ratios):
                cell.width = Inches(7.2 * ratio)
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
                paragraph = cell.paragraphs[0]
                paragraph.paragraph_format.space_after = Pt(3)
                paragraph.paragraph_format.space_before = Pt(3)
                paragraph.paragraph_format.line_spacing = 1.05
                for child in source_cell.children:
                    self.inline(child, paragraph, bold=source_cell.name == "th")
                for run in paragraph.runs:
                    run.font.size = Pt(8.5)
                if index == 0:
                    shade(cell._tc.get_or_add_tcPr(), "EDF1F5")
            if index == 0:
                repeat = OxmlElement("w:tblHeader")
                row._tr.get_or_add_trPr().append(repeat)
            no_split = OxmlElement("w:cantSplit")
            row._tr.get_or_add_trPr().append(no_split)
        self.document.add_paragraph().paragraph_format.space_after = Pt(2)

    def code(self, text, *, output=False):
        paragraph = self.document.add_paragraph(text, style="Lab Output" if output else "Lab Code")
        if not output:
            shade(paragraph._p.get_or_add_pPr(), "F3F5F7")

    def blocks(self, node):
        for child in node.children:
            if not isinstance(child, Tag) or child.name in {"style", "script"}:
                continue
            if child.name in {"h1", "h2", "h3"}:
                level = int(child.name[1]) - 1
                paragraph = self.document.add_heading(level=level)
                for inline in child.children:
                    self.inline(inline, paragraph, bold=True)
                text = paragraph.text
                if text.startswith(("Part A:", "Part B:")) or text in {"Final Insights", "References"}:
                    paragraph.paragraph_format.page_break_before = True
            elif child.name == "p":
                paragraph = self.document.add_paragraph()
                for inline in child.children:
                    self.inline(inline, paragraph)
            elif child.name in {"ul", "ol"}:
                number_id = self.numbered_list_id() if child.name == "ol" else None
                for item in child.find_all("li", recursive=False):
                    paragraph = self.document.add_paragraph(style="List Paragraph" if number_id else "List Bullet")
                    if number_id is not None:
                        numbering = paragraph._p.get_or_add_pPr().get_or_add_numPr()
                        numbering.get_or_add_ilvl().val = 0
                        numbering.get_or_add_numId().val = number_id
                    for inline in item.children:
                        self.inline(inline, paragraph)
            elif child.name == "pre":
                self.code(child.get_text().removesuffix("\n"))
            elif child.name == "table":
                self.table(child)
            else:
                self.blocks(child)

    def html(self, text):
        self.blocks(BeautifulSoup(text, "html.parser"))


def main():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(notebook)
    document = make_document()
    writer = ReportWriter(document)
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            writer.html(markdown2html(cell.source))
        elif cell.cell_type == "code":
            writer.code(cell.source)
            stream = ""
            for output in cell.get("outputs", []):
                if output.output_type == "stream":
                    stream += output.text
                    continue
                if stream:
                    writer.code(stream.removesuffix("\n"), output=True)
                    stream = ""
                if output.output_type == "error":
                    raise ValueError("Notebook contains an error output; resolve it before export.")
                data = output.get("data", {})
                if "text/html" in data:
                    writer.html(data["text/html"])
                elif "text/plain" in data:
                    writer.code(data["text/plain"], output=True)
            if stream:
                writer.code(stream.removesuffix("\n"), output=True)
    document.save(REPORT)
    print(f"Exported {REPORT.name} ({REPORT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
