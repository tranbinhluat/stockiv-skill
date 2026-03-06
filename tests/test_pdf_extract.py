import fitz  # PyMuPDF
import sys

pdf_path = "data/raw/annual_reports/FPT_annual_report.pdf"
try:
    doc = fitz.open(pdf_path)
    print(f"PDF opened successfully. Number of pages: {len(doc)}")
    
    # Try to extract text from first page
    if len(doc) > 0:
        page = doc[0]
        text = page.get_text()
        print(f"Page 1 Text Length: {len(text)}")
        print(f"Page 1 Snippet: {text[:200]}")
except Exception as e:
    print(f"Failed to open PDF with fitz: {e}")
