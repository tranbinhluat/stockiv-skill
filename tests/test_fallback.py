from tools.report_finder_tools import search_annual_report_pdf


def main():
    print("Testing Search for PMT 2026 - Should fallback to 2025...")
    res1 = search_annual_report_pdf.func("PMT", "2026")
    print("Search Result PMT:", res1)


if __name__ == "__main__":
    main()
