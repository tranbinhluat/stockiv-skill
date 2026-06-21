import os
import json
import requests
import pymupdf4llm
from dotenv import load_dotenv


load_dotenv()


def search_annual_report_pdf(ticker: str, year: str) -> str:
    """
    Searches the web for the Annual Report (Báo cáo thường niên) PDF of a specific stock ticker and year.

    Args:
        ticker: The stock symbol (e.g., 'FPT')
        year: The year of the annual report (e.g., '2023')

    Returns:
        A JSON string containing the top URL results. You should look for URLs ending in .pdf.
    """
    import requests

    # 1. Try Vietstock direct URLs first to bypass search limits
    exchanges = ["HOSE", "HNX", "UPCOM"]
    extensions = ["pdf", "zip"]

    try:
        base_year = int(year)
    except ValueError:
        import datetime

        base_year = datetime.datetime.now().year

    years_to_check = [str(base_year - 1), str(base_year - 2)]

    print(
        f"Checking direct Vietstock URLs for {ticker} Annual Report (trying {years_to_check})..."
    )
    for target_year in years_to_check:
        for exchange in exchanges:
            for ext in extensions:
                url = f"https://static2.vietstock.vn/data/{exchange}/{target_year}/BCTN/VN/{ticker}_Baocaothuongnien_{target_year}.{ext}"
                try:
                    # Use HEAD request for speed
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ Found Vietstock direct URL: {url}")
                        return json.dumps(
                            [
                                {
                                    "title": f"Báo cáo thường niên {ticker} năm {target_year}",
                                    "url": url,
                                    "snippet": f"Direct Vietstock download URL for {target_year}",
                                }
                            ],
                            ensure_ascii=False,
                            indent=2,
                        )
                except Exception:
                    pass

    print(
        f"❌ Vietstock direct URL not found for {ticker} (tried {years_to_check}). Falling back to Brave Search..."
    )

    # 2. Fallback to Brave Search
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return "Error: BRAVE_API_KEY environment variable is not set."

    # Optimize Brave Search: ask specifically for the previous years
    query = f"{ticker} báo cáo thường niên ({years_to_check[0]} OR {years_to_check[1]}) filetype:pdf"
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
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("description", ""),
                    }
                )

        return json.dumps(results, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"Error executing Brave Search for Annual Report: {str(e)}"


def download_and_convert_pdf(url: str, ticker: str, md_path: str, pdf_dir: str) -> str:
    """
    Downloads a PDF file from a given URL and converts it to Markdown using pymupdf4llm.

    Args:
        url: The direct URL to the PDF file.
        ticker: The stock symbol (e.g., 'FPT')
        md_path: The exact path where the markdown output should be saved.
        pdf_dir: The directory where the raw downloaded PDF should be temporarily saved.

    Returns:
        A success message with the path to the saved markdown file, or an error message.
    """
    import zipfile
    import re
    import os

    output_md_dir = os.path.dirname(md_path)
    if output_md_dir:
        os.makedirs(output_md_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)

    # Determine extension from URL
    ext = url.split(".")[-1].lower()
    if ext not in ["pdf", "zip"]:
        ext = "pdf"

    # Attempt to extract year from URL
    year = "unknown"
    year_match = re.search(r"(20\d{2})", url)
    if year_match:
        year = year_match.group(1)

    download_path = f"{pdf_dir}/{ticker}_annual_report_{year}.{ext}"

    # CACHE CHECK: If the Markdown already exists, just return it
    if os.path.exists(md_path):
        return f"Cache hit: Annual report for {ticker} ({year}) already downloaded and converted at {md_path}."

    try:
        # Download the file if we don't already have it
        if not os.path.exists(download_path):
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            with open(download_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        target_pdf_path = download_path

        # If it's a zip file, extract and find the PDF
        if ext == "zip":
            found_pdf = False
            with zipfile.ZipFile(download_path, "r") as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.lower().endswith(".pdf"):
                        print(f"Extracting PDF {file_info.filename} from ZIP...")
                        target_pdf_path = (
                            f"{pdf_dir}/{ticker}_extracted_annual_report.pdf"
                        )
                        with open(target_pdf_path, "wb") as f_out:
                            f_out.write(zip_ref.read(file_info.filename))
                        found_pdf = True
                        break
            if not found_pdf:
                return f"Error: Downloaded ZIP file from {url} but could not find any PDF inside."

        # Try to convert to Markdown
        print(f"Converting {target_pdf_path} to Markdown...")
        md_text = pymupdf4llm.to_markdown(target_pdf_path)

        # Some Vietnamese PDFs are entirely scanned images (0 extracted text).
        if len(md_text.strip()) < 500:
            return f"Notice: We cannot convert PDF to markdown (image-based). Note it down: We don't have a readable annual report for {ticker} ({year})."

        # Save Markdown
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)

        return f"Successfully downloaded PDF to {target_pdf_path} and converted. Markdown saved to {md_path}."

    except Exception as e:
        return f"Error downloading or converting PDF from {url}: {str(e)}"
