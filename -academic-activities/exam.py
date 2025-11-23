import easyocr
import numpy as np
import sys
from pathlib import Path
import google.generativeai as genai
from pdf2image import convert_from_path
from dotenv import load_dotenv

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import API_KEYS, AI_MODELS, FILE_PATHS

# Load environment variables
load_dotenv()

# Configure Gemini API
if not API_KEYS["google"]:
    raise ValueError("❌ GOOGLE_API_KEY is missing from .env file!")

print("✅ API Key Loaded Successfully!")
genai.configure(api_key=API_KEYS["google"])

# Load OCR model
reader = easyocr.Reader(['en'])

# File path for the exam schedule PDF
pdf_path = FILE_PATHS["exam_schedule"]

# Check if PDF file exists
if not pdf_path.exists():
    raise FileNotFoundError(
        f"❌ Exam schedule PDF not found at: {pdf_path}\n"
        f"Please ensure the file exists at the correct location."
    )

# Convert PDF pages to images
images = convert_from_path(str(pdf_path), dpi=300)

extracted_text = ""

for img in images:
    img_np = np.array(img)  # Convert PIL image to NumPy array
    result = reader.readtext(img_np, detail=0)  # Extract text
    extracted_text += "\n".join(result) + "\n\n"

# Save extracted text to a file (optional)
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(extracted_text)

print("✅ Extracted Text Saved.")

# 🔹 Function to format extracted text using Gemini AI
def format_exam_schedule_with_gemini(extracted_text):
    if not extracted_text.strip():
        return "⚠ No valid extracted text available from the academic calendar."

    model = genai.GenerativeModel(AI_MODELS["gemini"])

    prompt = f"""
You are an expert in structuring academic exam schedules. Given the extracted text from a university exam schedule, your task is to:

1. **Extract and organize the exam details into a clear table**.
2. **Remove any duplicate subjects or repeated information**.
3. **Ensure proper alignment of the table** with these columns:
   - **Date**
   - **Time** (if available)
   - **Course Name**
   - **Course Code**
   - **Exam Type** (Regular/Backlog)
4. **Ignore irrelevant text** such as administrative notes, venue details, or announcements.
5. **Ensure the table is structured correctly and formatted clearly** for easy readability.

### Extracted Text:
{extracted_text}

Now, generate a well-formatted table with this information.
"""
    response = model.generate_content(prompt)
    return response.text if response else "⚠ Error: No response from Gemini AI."

# 🔹 Generate formatted output
formatted_schedule = format_exam_schedule_with_gemini(extracted_text)

# 🔹 Save formatted output to a file (optional)
with open("formatted_exam_schedule.txt", "w", encoding="utf-8") as f:
    f.write(formatted_schedule)

# 🔹 Print formatted output (Fix Unicode Issues)
print("\n📅 **Formatted Exam Schedule** 📅\n".encode("utf-8", "ignore").decode())  
print(formatted_schedule.encode("utf-8", "ignore").decode())
