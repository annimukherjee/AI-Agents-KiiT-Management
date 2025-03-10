import easyocr
import numpy as np
from pdf2image import convert_from_path

# Load OCR model
reader = easyocr.Reader(['en'])

# Convert PDF pages to images
pdf_path = r"C:\Users\AmanDeep\OneDrive\Desktop\AI-Agents-KiiT-Management\-academic-activities\midsems.pdf"   # Change this to your actual PDF path
images = convert_from_path(pdf_path, dpi=300)

extracted_text = ""

for img in images:
    img_np = np.array(img)  # Convert PIL image to NumPy array
    result = reader.readtext(img_np, detail=0)  # Extract text
    extracted_text += "\n".join(result) + "\n\n"

# Save extracted text to a file (optional)
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(extracted_text)

print("✅ Extracted Text:\n", extracted_text)
