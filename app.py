from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import markdown
import os
from datetime import datetime
import tempfile
from weasyprint import HTML
from latex2pdf import save_latex_as_pdf
from io import BytesIO

app = Flask(__name__)

# Create a directory for storing PDFs if it doesn't exist
UPLOAD_FOLDER = 'generated_pdfs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure Gemini API
genai.configure(api_key='AIzaSyBFFMPRr2y3woemAzEvmTPLWEaHgPaNoD0')
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data['prompt']
        format_type = data['format']
        tone = data.get('tone', 'neutral')
        pages = data.get('pages', '')
        grade = data.get('grade', '')
        words = data.get('words', '')

        # Format-specific instructions
        format_instructions = {
            'markdown': 'Use standard Markdown syntax with headers, lists, and emphasis where appropriate.',
            'latex': 'Use proper LaTeX syntax including document class and necessary packages.'
        }

        # Construct the enhanced prompt
        enhanced_prompt = f"""
        Generate content in {format_type} format with the following specifications:
        Topic: {prompt}
        Tone: {tone}
        {f'Target Pages: {pages}' if pages else ''}
        {f'Grade Level: {grade}' if grade else ''}
        {f'Target Word Count: {words}' if words else ''}
        
        Format Instructions: {format_instructions.get(format_type, '')}
        """

        # Generate content using Gemini
        response = model.generate_content(enhanced_prompt)
        generated_content = response.text

        return jsonify({
            'content': generated_content,
            'format': format_type,
            'success': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    try:
        data = request.json
        content = data.get('content')
        format_type = data.get('format', 'markdown')

        if not content:
            raise ValueError("No content provided")

        # Create a unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"document_{timestamp}"
        
        # Convert to PDF based on format
        if format_type == "markdown":
            # Convert markdown to HTML
            html_content = markdown.markdown(content)
            # Create a basic HTML document with some styling
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ 
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 2cm;
                        max-width: 21cm;
                    }}
                    h1, h2, h3 {{ color: #333; }}
                    pre {{ background: #f5f5f5; padding: 1em; border-radius: 4px; }}
                </style>
            </head>
            <body>{html_content}</body>
            </html>
            """
            # Convert HTML to PDF
            pdf_path = os.path.join(UPLOAD_FOLDER, f"{filename}.pdf")
            HTML(string=full_html).write_pdf(pdf_path)
        elif format_type == "latex":
            # Use save_latex_as_pdf function
            if " '''latex " in content:
                print(True)
            pdf_path = save_latex_as_pdf(content, output_dir=UPLOAD_FOLDER, output_filename=filename)
            if not pdf_path:
                raise ValueError("Failed to generate PDF from LaTeX")
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        # Send the file back to the client
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"{filename}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
