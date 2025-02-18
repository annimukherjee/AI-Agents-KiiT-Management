
import os
import sys
from PyPDF2 import PdfReader

def pdf_to_markdown(pdf_path, md_path):
    """
    Extracts text from a PDF file and writes it into a Markdown file.
    Each page is separated by a header for clarity.
    """
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return

    with open(md_path, 'w', encoding='utf-8') as md_file:
        # Use the PDF file name as the top-level Markdown header
        md_file.write(f'# {os.path.basename(pdf_path)}\n\n')
        
        # Iterate over each page in the PDF
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            md_file.write(f'## Page {page_num + 1}\n\n')
            md_file.write(text + "\n\n")

def convert_directory(pdf_directory):
    """
    Iterates through the specified directory, converting every PDF to Markdown.
    The output Markdown files will be saved in the same directory with a .md extension.
    """
    if not os.path.isdir(pdf_directory):
        print(f"The path {pdf_directory} is not a valid directory.")
        return

    # Process every file ending with '.pdf'
    for filename in os.listdir(pdf_directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_directory, filename)
            md_filename = os.path.splitext(filename)[0] + '.md'
            md_path = os.path.join(pdf_directory, md_filename)
            print(f"Converting '{pdf_path}' to '{md_path}'...")
            pdf_to_markdown(pdf_path, md_path)

    print("Conversion complete!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_pdf_to_md.py <directory_with_pdfs>")
        sys.exit(1)

    pdf_directory = sys.argv[1]
    convert_directory(pdf_directory)