import os
import sys
from pathlib import Path
import fitz  # PyMuPDF for PDF text extraction
import google.generativeai as genai
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

# Function to extract text from the academic calendar PDF
def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            extracted_text += page.get_text("text") + "\n"

    if not extracted_text.strip():
        print(f"⚠ Warning: No text found in {pdf_path}. It may be an image-based PDF.")

    return extracted_text.strip()

# Function to format extracted text using Gemini AI
def format_calendar_with_gemini(extracted_text):
    if not extracted_text:
        return "⚠ No valid extracted text available from the academic calendar."

    model = genai.GenerativeModel(AI_MODELS["gemini"])

    prompt = f""" 
    You are an expert in structuring academic data. Given the extracted text from a university academic calendar, your task is to:
    
    1. **Neatly format the calendar** for readability.
    2. **Organize the dates and events** clearly.
    3. Use **tables, bullet points, and bold formatting** where necessary.
    4. Ensure the output is professional and structured.
    5. Remove 'vice-chancellor' & 'Registrar words'
    6.Ensure just the Academic Calendar is extracted (Activity and dates)

    Extracted Text: 
    {extracted_text}
    """

    response = model.generate_content(prompt)
    return response.text if response else "⚠ Error: No response from Gemini AI."

# File path for the academic calendar PDF
academic_calendar_pdf_path = FILE_PATHS["academic_calendar"]

# Check if PDF file exists
if not academic_calendar_pdf_path.exists():
    raise FileNotFoundError(
        f"❌ Academic calendar PDF not found at: {academic_calendar_pdf_path}\n"
        f"Please ensure the file exists at the correct location."
    )

# Extract text from the academic calendar
calendar_text = extract_text_from_pdf(str(academic_calendar_pdf_path))

# Format the academic calendar using Gemini
formatted_calendar = format_calendar_with_gemini(calendar_text)

# Print Final Structured Output
print("\n📅 **Formatted Academic Calendar** 📅\n")
print(formatted_calendar)
