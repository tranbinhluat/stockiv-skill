from tools.report_finder_tools import search_annual_report_pdf, download_and_convert_pdf
import json


def main():
    print("Testing Search for PMT 2025 (UPCOM/HNX)...")
    res1 = search_annual_report_pdf.func("PMT", "2025")
    print("Search Result PMT:", res1)

    print("\nTesting Search for FPT 2024 (HOSE)...")
    res2 = search_annual_report_pdf.func("FPT", "2024")
    print("Search Result FPT:", res2)

    try:
        urls = json.loads(res2)
        if urls and len(urls) > 0:
            direct_url = urls[0]["url"]
            print(
                f"\nTesting Download and Convert for FPT 2024 with URL {direct_url}..."
            )
            res_dl = download_and_convert_pdf.func(
                direct_url,
                "FPT_test",
                "data/processed/annual_reports/FPT_test_annual_report_2024.md",
                "data/raw/annual_reports",
            )
            print("Download Result:", res_dl)
    except Exception as e:
        print("Failed to parse search JSON:", e)


if __name__ == "__main__":
    main()
