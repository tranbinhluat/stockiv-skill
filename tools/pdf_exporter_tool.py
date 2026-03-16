import os
import re
import base64
import mimetypes
import markdown
from weasyprint import HTML, CSS
from crewai.tools import tool


def _embed_images_in_html(html_text: str) -> str:
    """Replace local file <img src="/path/to/img.png"> with base64 data URIs."""

    def _replace_src(match):
        prefix = match.group(1)
        img_path = match.group(2)
        suffix = match.group(3)
        if os.path.exists(img_path):
            mime_type = mimetypes.guess_type(img_path)[0] or "image/png"
            with open(img_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            return f"{prefix}data:{mime_type};base64,{img_data}{suffix}"
        return match.group(0)

    # Match <img ... src="/absolute/path/to/image.ext" ...>
    return re.sub(
        r'(<img[^>]*\ssrc=["\'])(/[^"\']+\.(?:png|jpg|jpeg|gif|svg|webp))(["\'])',
        _replace_src,
        html_text,
    )


@tool("markdown_to_pdf")
def markdown_to_pdf(
    markdown_content: str,
    output_file_path: str,
    financial_summary_path: str = "",
) -> str:
    """
    Converts markdown content string into a beautifully formatted PDF file.
    Optionally appends a financial summary as an A3 landscape appendix.

    Args:
        markdown_content (str): The markdown text to convert.
        output_file_path (str): The absolute path where the PDF should be saved.
        financial_summary_path (str): Optional path to a financial summary .md file
            to append as a landscape appendix section.

    Returns:
        str: A success message with the file path if successful, or an error message.
    """
    try:
        # Sanitize: strip invalid UTF-8 bytes that LLMs occasionally emit
        if isinstance(markdown_content, bytes):
            markdown_content = markdown_content.decode("utf-8", errors="replace")
        else:
            markdown_content = markdown_content.encode(
                "utf-8", errors="replace"
            ).decode("utf-8")

        # Normalize: LLMs often pass literal 'None' string instead of empty
        if financial_summary_path and financial_summary_path.strip().lower() in (
            "none",
            "null",
            "",
        ):
            financial_summary_path = ""

        # If financial_summary_path provided, read and append as appendix
        appendix_html = ""
        if financial_summary_path and os.path.exists(financial_summary_path):
            with open(financial_summary_path, "r", encoding="utf-8") as f:
                financial_md = f.read()

            # Add clickable link in main report body
            markdown_content += (
                "\n\n---\n\n📊 **[Xem Dữ liệu Tài chính chi tiết →](#appendix)**\n"
            )

            # Convert financial markdown to HTML separately for appendix styling
            financial_html = markdown.markdown(
                financial_md, extensions=["tables", "fenced_code"]
            )
            appendix_html = (
                '<section class="appendix">'
                '<a id="appendix"></a>'
                "<h1>Phụ lục: Dữ liệu Tài chính</h1>"
                f"{financial_html}"
                "</section>"
            )

        # Convert main markdown to HTML
        html_text = markdown.markdown(
            markdown_content, extensions=["tables", "fenced_code", "nl2br"]
        )

        # Embed local images as base64 data URIs (after HTML conversion)
        html_text = _embed_images_in_html(html_text)

        # CSS: A4 portrait for main, A3 landscape for appendix
        css = CSS(
            string="""
            @page {
                size: A4;
                margin: 2cm;
            }
            @page appendix {
                size: A3 landscape;
                margin: 1.5cm;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                font-size: 11pt;
            }
            h1 { font-size: 18pt; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }
            h2 { font-size: 15pt; }
            h3 { font-size: 13pt; }
            p { margin-bottom: 1em; }
            ul, ol { margin-bottom: 1em; padding-left: 2em; }
            li { margin-bottom: 0.5em; }
            img {
                display: block;
                max-width: 60%;
                height: auto;
                margin: 1em auto;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
            }
            h1, h2, h3 { color: #1a365d; margin-top: 1.5em; margin-bottom: 0.5em; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 1em;
                margin-bottom: 1em;
                font-size: 10pt;
            }
            th, td {
                border: 1px solid #cbd5e0;
                padding: 8px 12px;
                text-align: left;
            }
            th { background-color: #f7fafc; font-weight: bold; }
            .appendix {
                page: appendix;
                page-break-before: always;
                font-size: 9pt;
            }
            .appendix h1 {
                font-size: 16pt;
                color: #1a365d;
                border-bottom: 2px solid #2b6cb0;
            }
            .appendix table {
                font-size: 8pt;
            }
            .appendix th, .appendix td {
                padding: 4px 8px;
            }
        """
        )

        # Full HTML wrapper
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Report</title>
        </head>
        <body>
            {html_text}
            {appendix_html}
        </body>
        </html>
        """

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)

        HTML(string=full_html).write_pdf(output_file_path, stylesheets=[css])
        return f"Successfully generated PDF at {output_file_path}"
    except Exception as e:
        return f"Error generating PDF: {str(e)}"
