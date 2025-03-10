import fitz  # PyMuPDF
import easyocr
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize EasyOCR Reader
reader = easyocr.Reader(["en"])  # Add other languages if needed

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            
            # If no text, use EasyOCR
            if not text:
                print(f"Page {page_num}: Using EasyOCR for text extraction...")
                pix = page.get_pixmap()
                img = fitz.Pixmap(pix, 0)  # Convert to grayscale
                text = "\n".join(reader.readtext(img.tobytes(), detail=0))
            
            extracted_text += f"\n--- Page {page_num} ---\n{text}"

    if not extracted_text.strip():
        print(f"⚠ Warning: No text found in {pdf_path}.")
    else:
        print("✅ Extracted text successfully!\n")

    return extracted_text.strip()

# Function to process text using Groq API
def process_with_groq(text):
    print("🤖 Sending text to Groq for processing...")

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an AI assistant that extracts structured holiday lists."},
            {"role": "user", "content": f"Extract and format a structured holiday list from the following and PRESENT IN A TABULAR FORMAT WHICH IS MUST:\n\n{text}"}
        ],
        "temperature": 0.5,
        "max_tokens": 1024
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "⚠ Error: No response from Groq.")
    else:
        return f"⚠ API Error: {response.status_code} - {response.text}"

# PDF File Path
holiday_pdf_path = r"C:\Users\AmanDeep\OneDrive\Desktop\AI-Agents-KiiT-Management\-academic-activities\holiday.pdf"

# Extract text
holiday_text = extract_text_from_pdf(holiday_pdf_path)

# Process with Groq if text was extracted
if holiday_text:
    print("✅ Proceeding with AI formatting...")
    ai_response = process_with_groq(holiday_text)
    
    print("\n🎉 **Formatted Holiday List** 🎉\n")
    print(ai_response)
else:
    print("⚠ No valid text extracted! Cannot proceed with AI processing.")
