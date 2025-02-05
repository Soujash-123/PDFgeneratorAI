from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import markdown
import os
import subprocess
import tempfile
from datetime import datetime
from weasyprint import HTML
from io import BytesIO

app = Flask(__name__)

# Create a directory for storing PDFs if it doesn't exist
UPLOAD_FOLDER = 'generated_pdfs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure Gemini API
genai.configure(api_key='AIzaSyBFFMPRr2y3woemAzEvmTPLWEaHgPaNoD0')
model = genai.GenerativeModel("gemini-1.5-flash")

def compile_latex(latex_content, output_path):
    """
    Compile LaTeX content to PDF using pdflatex.
    Returns tuple (success, error_message)
    """
    try:
        # Create a temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write LaTeX content to temporary file
            tex_path = os.path.join(temp_dir, 'document.tex')
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Run pdflatex twice to resolve references
            for _ in range(2):
                process = subprocess.Popen(
                    ['pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    return False, f"LaTeX compilation failed: {stdout.decode('utf-8')}"
            
            # Move the generated PDF to the desired location
            temp_pdf = os.path.join(temp_dir, 'document.pdf')
            if os.path.exists(temp_pdf):
                os.rename(temp_pdf, output_path)
                return True, ""
            else:
                return False, "PDF file was not generated"
                
    except Exception as e:
        return False, f"Error during LaTeX compilation: {str(e)}"

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
            'latex': '''Generate complete LaTeX document with proper structure including:
                     \\documentclass{article}
                     \\usepackage commands
                     \\begin{document}
                     content
                     \\end{document}'''
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
        
        # Clean up LaTeX content if needed
        if format_type == 'latex':
            generated_content = generated_content.replace('```latex', '').replace('```', '').strip()
            
            # Ensure proper LaTeX structure
            if not '\\documentclass' in generated_content:
                generated_content = f"""\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}
\\begin{{document}}
{generated_content}
\\end{{document}}"""

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
        pdf_path = os.path.join(UPLOAD_FOLDER, f"{filename}.pdf")
        
        if format_type == "markdown":
            # Convert Markdown to HTML and then to PDF
            html_content = markdown.markdown(content)
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
            HTML(string=full_html).write_pdf(pdf_path)
        
        elif format_type == "latex":
            # Compile LaTeX to PDF
            success, error_message = compile_latex(content, pdf_path)
            if not success:
                raise ValueError(f"LaTeX compilation failed: {error_message}")
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        # Verify PDF was created
        if not os.path.exists(pdf_path):
            raise ValueError("Failed to generate PDF file")

        # Send the file back to the client
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"{filename}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        error_message = str(e)
        print(f"Error in PDF conversion: {error_message}")
        return jsonify({
            'success': False,
            'error': error_message
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
