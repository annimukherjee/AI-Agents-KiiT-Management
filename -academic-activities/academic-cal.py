import os
import fitz  # PyMuPDF for PDF text extraction
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load Gemini API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY is missing from .env file!")

print("✅ API Key Loaded Successfully!")

# Configure Gemini API
genai.configure(api_key=api_key)

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

    model = genai.GenerativeModel("gemini-1.5-flash")

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

# File path for the academic calendar PDF (Update as per your system)
academic_calendar_pdf_path = r"C:\Users\AmanDeep\OneDrive\Desktop\AI-Agents-KiiT-Management\-academic-activities\calender.pdf"

# Extract text from the academic calendar
calendar_text = extract_text_from_pdf(academic_calendar_pdf_path)

# Format the academic calendar using Gemini
formatted_calendar = format_calendar_with_gemini(calendar_text)

# Print Final Structured Output
print("\n📅 **Formatted Academic Calendar** 📅\n")
print(formatted_calendar)
