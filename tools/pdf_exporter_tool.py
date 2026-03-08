import os
import markdown
from weasyprint import HTML, CSS
from crewai.tools import tool


@tool("markdown_to_pdf")
def markdown_to_pdf(markdown_content: str, output_file_path: str) -> str:
    """
    Converts markdown content string into a beautifully formatted PDF file.

    Args:
        markdown_content (str): The markdown text to convert.
        output_file_path (str): The absolute path where the PDF should be saved.

    Returns:
        str: A success message with the file path if successful, or an error message.
    """
    try:
        # Convert markdown to HTML (enable tables, fenced code, etc.)
        html_text = markdown.markdown(
            markdown_content, extensions=["tables", "fenced_code", "nl2br"]
        )

        # Simple clean CSS tailored for financial reports
        css = CSS(
            string="""
            @page { size: A4; margin: 2cm; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                font-size: 11pt;
            }
            h1, h2, h3 { color: #1a365d; margin-top: 1.5em; margin-bottom: 0.5em; }
            h1 { font-size: 18pt; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }
            h2 { font-size: 15pt; }
            h3 { font-size: 13pt; }
            p { margin-bottom: 1em; }
            ul, ol { margin-bottom: 1em; padding-left: 2em; }
            li { margin-bottom: 0.5em; }
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
        </body>
        </html>
        """

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)

        HTML(string=full_html).write_pdf(output_file_path, stylesheets=[css])
        return f"Successfully generated PDF at {output_file_path}"
    except Exception as e:
        return f"Error generating PDF: {str(e)}"
