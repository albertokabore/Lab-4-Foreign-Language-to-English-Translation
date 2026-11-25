"""Export the saved notebook, including code and outputs, to a printable PDF.

Optional export dependencies: python -m pip install nbconvert playwright
Browser setup, if needed: python -m playwright install chromium
Run from any folder: python scripts/export_report.py
This exports saved outputs; it does not rerun model inference.
"""

from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "Lab4_Machine_Translation.ipynb"
REPORT = ROOT / "Lab4_Machine_Translation_Report.pdf"

CSS = """
@page { size: Letter; }
* { box-sizing: border-box; }
body { margin: 0; font: 10pt/1.45 Arial, sans-serif; color: #18212b; }
h1 { font-size: 23pt; line-height: 1.2; margin: 0 0 16pt; }
h2 { font-size: 17pt; margin: 18pt 0 10pt; }
h3 { font-size: 12pt; margin: 15pt 0 8pt; }
h1, h2, h3 { break-after: avoid; }
p { margin: 7pt 0; orphans: 3; widows: 3; }
ul, ol { padding-left: 19pt; }
li { margin: 5pt 0; }
a { color: #174f7c; text-decoration: none; overflow-wrap: anywhere; }
a.anchor-link { display: none; }
code { font: 8.5pt Consolas, monospace; overflow-wrap: anywhere; }
pre { font: 7.6pt/1.35 Consolas, monospace; white-space: pre-wrap;
      overflow-wrap: anywhere; word-break: normal; margin: 0; }
.input_area { background: #f3f5f7; border: 1px solid #dbe0e5;
              padding: 9pt; margin: 10pt 0 5pt; }
.output_area { padding: 5pt 7pt; margin-bottom: 8pt; }
.prompt { display: none; }
.cell, .input, .output, .output_wrapper, .output_area { height: auto;
          max-height: none; overflow: visible; }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt;
        margin: 10pt 0; table-layout: fixed; }
th, td { padding: 5pt; border: 1px solid #d7dce1; text-align: left;
         vertical-align: top; overflow-wrap: anywhere; }
th { background: #edf1f5; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
.section-start { break-before: page; }
"""


def main():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(notebook)
    exporter = HTMLExporter(
        template_name="basic", exclude_input_prompt=True, exclude_output_prompt=True
    )
    body, _ = exporter.from_notebook_node(notebook)
    document = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<title>Lab 4: English to Romanian Translation | Albert Kabore</title>'
        f"<style>{CSS}</style></head><body>{body}</body></html>"
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content(document, wait_until="load")
            page.evaluate("""() => {
                document.querySelectorAll('h2').forEach(heading => {
                    if (/^Part [AB]:/.test(heading.textContent)
                        || heading.id === 'Final-Insights' || heading.id === 'References') {
                        heading.closest('.cell').classList.add('section-start');
                    }
                });
            }""")
            page.pdf(
                path=str(REPORT),
                format="Letter",
                print_background=True,
                display_header_footer=True,
                header_template="<span></span>",
                footer_template=(
                    '<div style="font-size:8px;color:#65717d;width:100%;'
                    'text-align:center;font-family:Arial">'
                    'Albert Kabore · Lab 4 · <span class="pageNumber"></span> / '
                    '<span class="totalPages"></span></div>'
                ),
                margin={"top": "0.55in", "bottom": "0.55in", "left": "0.55in", "right": "0.55in"},
            )
        finally:
            browser.close()
    print(f"Exported {REPORT.name} ({REPORT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
