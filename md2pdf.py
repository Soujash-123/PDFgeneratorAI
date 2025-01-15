import markdown
from weasyprint import HTML
import tempfile
import os

def markdown_to_pdf(markdown_text, output_pdf_path, css_style=None):
    """
    Convert Markdown text to PDF
    
    Args:
        markdown_text (str): Input markdown text
        output_pdf_path (str): Path where the PDF will be saved
        css_style (str, optional): Custom CSS styling for the PDF
    """
    # Default CSS style if none provided
    if css_style is None:
        css_style = """
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 40px;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #333;
                margin-top: 20px;
            }
            code {
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: monospace;
            }
            pre {
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            blockquote {
                border-left: 4px solid #ccc;
                margin: 0;
                padding-left: 16px;
                color: #666;
            }
            a {
                color: #0366d6;
                text-decoration: none;
            }
            img {
                max-width: 100%;
                height: auto;
            }
        """

    # Convert Markdown to HTML
    html = markdown.markdown(
        markdown_text,
        extensions=[
            'extra',           # Tables, footnotes, attr_list, etc.
            'codehilite',      # Syntax highlighting
            'fenced_code',     # Fenced code blocks
            'tables',          # Tables
            'toc',            # Table of contents
            'nl2br'           # New lines to breaks
        ]
    )

    # Create complete HTML document with CSS
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <style>
                {css_style}
            </style>
        </head>
        <body>
            {html}
        </body>
    </html>
    """

    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
        f.write(html_content.encode('utf-8'))
        temp_html_path = f.name

    try:
        # Convert HTML to PDF
        HTML(filename=temp_html_path).write_pdf(output_pdf_path)
    finally:
        # Clean up temporary file
        os.unlink(temp_html_path)

# Example usage
if __name__ == "__main__":
    # Example markdown text
    markdown_text = """
    # Sample Markdown Document
    
    This is a **bold** text and this is *italic* text.
    
    ## Code Example
    ```python
    def hello_world():
        print("Hello, World!")
    ```
    
    ### List Example
    - Item 1
    - Item 2
    - Item 3
    
    > This is a blockquote
    """
    
    # Convert to PDF
    markdown_to_pdf(markdown_text, 'output.pdf')
