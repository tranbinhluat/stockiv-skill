import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.report_finder_tools import _ocr_pdf_to_markdown

pdf_path = "data/raw/annual_reports/FPT_annual_report.pdf"

print("Starting OCR extraction test on the first 2 pages of the PDF...")
# We'll just test the OCR function
text = _ocr_pdf_to_markdown(pdf_path)
print(f"Extracted length: {len(text)}")
print(f"Snippet: {text[:500]}")
