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
    Save LaTeX code as a PDF.
    
    Args:
        latex_code (str): The LaTeX code to compile.
        output_dir (str): Directory where the PDF will be saved.
        output_filename (str): The name of the output PDF file (without extension).
        
    Returns:
        str: Path to the generated PDF file.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Write LaTeX code to a temporary .tex file
    tex_file_path = os.path.join(output_dir, f"{output_filename}.tex")
    with open(tex_file_path, "w") as tex_file:
        tex_file.write(latex_code)
    
    # Compile the .tex file into a PDF using pdflatex
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", output_dir, tex_file_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print(f"Error compiling LaTeX: {e.stderr.decode('utf-8')}")
        return None
    
    # Return the path to the generated PDF
    return os.path.join(output_dir, f"{output_filename}.pdf")

# Main script
if __name__ == "__main__":
    # Ensure pdflatex is installed
    ensure_pdflatex_installed()
    
    # Example LaTeX code
    latex_code = r"""
    \documentclass{article}
    \usepackage[utf8]{inputenc}
    \title{Sample Document}
    \author{John Doe}
    \date{\today}
    \begin{document}
    \maketitle
    Hello, World! This is a sample LaTeX document compiled to PDF.
    \end{document}
    """
    
    # Save as PDF
    output_pdf = save_latex_as_pdf(latex_code, output_dir="output", output_filename="sample")
    if output_pdf:
        print(f"PDF generated: {output_pdf}")

