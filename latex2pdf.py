import os
import subprocess

def ensure_pdflatex_installed():
    """
    Ensure that pdflatex is installed on the system. If not, attempt to install it.
    """
    try:
        # Check if pdflatex is available
        subprocess.run(["pdflatex", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("pdflatex is already installed.")
    except FileNotFoundError:
        print("pdflatex is not installed. Attempting to install...")
        try:
            # Attempt to install pdflatex (Linux example: for Debian-based systems)
            subprocess.run(
                ["sudo", "apt-get", "update"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "texlive-latex-base"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print("pdflatex installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install pdflatex: {e.stderr.decode('utf-8')}")
            raise RuntimeError("pdflatex installation failed. Please install it manually.")

def save_latex_as_pdf(latex_code, output_dir, output_filename):
    """
    Save LaTeX code as a PDF with improved error handling.
    
    Args:
        latex_code (str): The LaTeX code to compile.
        output_dir (str): Directory where the PDF will be saved.
        output_filename (str): The name of the output PDF file (without extension).
        
    Returns:
        str: Path to the generated PDF file.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    tex_file_path = os.path.join(output_dir, f"{output_filename}.tex")
    with open(tex_file_path, "w", encoding="utf-8") as tex_file:
        tex_file.write(latex_code)
    
    original_dir = os.getcwd()
    os.chdir(output_dir)
    
    try:
        for _ in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", output_filename],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check for common LaTeX errors in the output
            if "! LaTeX Error:" in result.stdout or "! Emergency stop." in result.stdout:
                error_lines = [line for line in result.stdout.split('\n') if '! ' in line]
                raise subprocess.CalledProcessError(
                    1, 
                    "pdflatex", 
                    output=result.stdout.encode(), 
                    stderr=f"LaTeX compilation error: {'; '.join(error_lines)}".encode()
                )
        
        pdf_path = os.path.join(output_dir, f"{output_filename}.pdf")
        
        # Verify PDF was created
        if not os.path.exists(pdf_path):
            raise FileNotFoundError("PDF file was not created despite successful compilation")
            
        os.chdir(original_dir)
        return pdf_path
        
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
        print(f"LaTeX compilation error: {error_message}")
        os.chdir(original_dir)
        raise ValueError(f"LaTeX compilation failed: {error_message}")
        
    except Exception as e:
        print(f"Unexpected error in LaTeX compilation: {str(e)}")
        os.chdir(original_dir)
def docstring_to_string(docstring):
    # Strip the triple quotes and normalize whitespace
    return " ".join(docstring.strip().splitlines())
    

# Main script
if __name__ == "__main__":
    # Ensure pdflatex is installed
    ensure_pdflatex_installed()
    
    # Example LaTeX code in single line format
    latex_code = " ".join(r"""\documentclass{article} \usepackage{amsmath} \usepackage{amsfonts} \usepackage{amssymb} \title{An Analysis of abcd} \author{Your Name} \date{\today} \begin{document} \maketitle \begin{abstract} This paper provides a professional analysis of the topic abcd. Further details regarding the specific aspects of abcd to be analyzed will be provided within the body of the paper. The analysis will employ rigorous methodology and strive for clarity and precision in its presentation. \end{abstract} \section{Introduction} The term abcd can be interpreted in various contexts. This paper aims to explore the mathematical properties of abcd. \section{Methodology} We will analyze abcd using statistical methods and mathematical proofs. \section{Results} Our analysis shows that abcd exhibits interesting properties. \section{Discussion} The implications of our findings suggest that abcd has significant applications. \section{Conclusion} We have demonstrated the key properties of abcd and their implications. \end{document}""".strip().splitlines())
    output_pdf = save_latex_as_pdf(latex_code, output_dir="output", output_filename="sample")
    if output_pdf:
        print(f"PDF generated successfully: {output_pdf}")
    else:
        print("Failed to generate PDF")

