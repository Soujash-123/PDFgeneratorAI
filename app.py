from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import markdown
import os
from datetime import datetime
import tempfile
from md2pdf import markdown_to_pdf
from io import BytesIO

app = Flask(__name__)

# Create a directory for storing PDFs if it doesn't exist
UPLOAD_FOLDER = 'generated_pdfs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure Gemini API
genai.configure(api_key='GEMINI_API_KEY')
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data['prompt']
    format_type = data['format']
    tone = data.get('tone', 'neutral')
    pages = data.get('pages', '')
    grade = data.get('grade', '')
    words = data.get('words', '')

    # Construct the enhanced prompt
    enhanced_prompt = f"""
    Generate content in {format_type} format with the following specifications:
    Topic: {prompt}
    Tone: {tone}
    {'Pages: ' + pages if pages else ''}
    {'Grade Level: ' + grade if grade else ''}
    {'Word Count: ' + words if words else ''}
    """

    # Generate content using Gemini
    response = model.generate_content(enhanced_prompt)
    generated_content = response.text

    return jsonify({
        'content': generated_content,
        'format': format_type
    })

@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    try:
        data = request.json
        content = data['content']
        
        # Create a unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"document_{timestamp}.pdf"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Convert markdown to PDF
        markdown_to_pdf(content, filepath)

        # Send the file back to the client
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
