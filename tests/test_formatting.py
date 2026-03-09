from tools.report_finder_tools import download_and_convert_pdf
import os


def main():
    print("Testing formatting of PMT 2025 download...")
    url = "https://static2.vietstock.vn/data/HNX/2025/BCTN/VN/PMT_Baocaothuongnien_2025.pdf"

    # Clean previous tests
    for file in os.listdir("data/processed/annual_reports"):
        if "PMT" in file:
            os.remove(os.path.join("data/processed/annual_reports", file))

    res = download_and_convert_pdf.func(
        url,
        "PMT",
        "data/processed/annual_reports/PMT_annual_report_2025.md",
        "data/raw/annual_reports",
    )
    print(res)

    print("\nChecking generated files:")
    for file in os.listdir("data/processed/annual_reports"):
        if "PMT" in file:
            print(f"- {file}")


if __name__ == "__main__":
    main()
