import pymupdf4llm
import os


def main():
    pdf_path = "data/raw/annual_reports/FPT_Baocaothuongnien_2024.pdf"

    if not os.path.exists(pdf_path):
        print(f"❌ Error: Cannot find PDF at {pdf_path}")
        return

    print(f"Parsing {pdf_path} using our current pymupdf4llm.to_markdown() process...")

    try:
        md_text = pymupdf4llm.to_markdown(pdf_path)
        char_count = len(md_text.strip())
        print(f"\n✅ Extraction complete. Total characters: {char_count}")

        preview_path = "tests/FPT_Baocaothuongnien_2024_preview.md"
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(md_text)

        print(f"Saved full output to {preview_path}")

        print("\n" + "=" * 50)
        print("PREVIEW (First 1000 characters):")
        print("=" * 50)
        print(md_text[:1000])
        print("=" * 50)

    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")


if __name__ == "__main__":
    main()
