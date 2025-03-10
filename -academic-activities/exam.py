import easyocr
import numpy as np
import google.generativeai as genai
from pdf2image import convert_from_path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load Gemini API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY is missing from .env file!")

print("✅ API Key Loaded Successfully!")

# Configure Gemini API
genai.configure(api_key=api_key)

# Load OCR model
reader = easyocr.Reader(['en'])

# Convert PDF pages to images
pdf_path = r"C:\Users\AmanDeep\OneDrive\Desktop\AI-Agents-KiiT-Management\-academic-activities\midsems.pdf"
images = convert_from_path(pdf_path, dpi=300)

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

    model = genai.GenerativeModel("gemini-1.5-flash")

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
