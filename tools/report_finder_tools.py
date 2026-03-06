import os
import json
import requests
import pymupdf4llm
from crewai.tools import tool

@tool("Search Annual Report PDF")
def search_annual_report_pdf(ticker: str, year: str) -> str:
    """
    Searches the web for the Annual Report (Báo cáo thường niên) PDF of a specific stock ticker and year.

    Args:
        ticker: The stock symbol (e.g., 'FPT')
        year: The year of the annual report (e.g., '2023')

    Returns:
        A JSON string containing the top URL results. You should look for URLs ending in .pdf.
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return "Error: BRAVE_API_KEY environment variable is not set."

    query = f"{ticker} báo cáo thường niên {year} filetype:pdf"
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"Accept": "application/json", "X-Subscription-Token": api_key}

    params = {
        "q": query,
        "count": 5,
        "search_lang": "vi",
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        if "web" in data and "results" in data["web"]:
            for item in data["web"]["results"]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", "")
                })

        return json.dumps(results, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"Error executing Brave Search for Annual Report: {str(e)}"

@tool("Download and Convert PDF to Markdown")
def download_and_convert_pdf(url: str, ticker: str) -> str:
    """
    Downloads a PDF file from a given URL and converts it to Markdown using pymupdf4llm.
    Saves the output to data/processed/annual_reports/{ticker}_annual_report.md.

    Args:
        url: The direct URL to the PDF file.
        ticker: The stock symbol (e.g., 'FPT')

    Returns:
        A success message with the path to the saved markdown file, or an error message.
    """
    output_md_dir = "data/processed/annual_reports"
    output_pdf_dir = "data/raw/annual_reports"
    os.makedirs(output_md_dir, exist_ok=True)
    os.makedirs(output_pdf_dir, exist_ok=True)
    
    pdf_path = f"{output_pdf_dir}/{ticker}_annual_report.pdf"
    md_path = f"{output_md_dir}/{ticker}_annual_report.md"

    try:
        # Download the PDF
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Try to convert to Markdown
        md_text = pymupdf4llm.to_markdown(pdf_path)

        # Some Vietnamese PDFs are entirely scanned images (0 extracted text).
        # We perform a quick heuristic check to see if we need OCR.
        if len(md_text.strip()) < 500:
             # Fallback: force basic OCR extraction (requires Tesseract to be installed, 
             # but PyMuPDF has basic image-to-text hooks if configured).
             # A safer fallback for an AI pipeline without heavy OCR deps is to notify the agent.
             return f"Error: PDF downloaded successfully, but the file appears to be a scanned image with no readable text. Cannot extract Markdown. Path: {pdf_path}"

        # Save Markdown
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)

        return f"Successfully downloaded PDF to {pdf_path} and converted. Markdown saved to {md_path}."

    except Exception as e:
        return f"Error downloading or converting PDF from {url}: {str(e)}"
