# University Schedule Extractor

This submodule extracts and formats university schedules from PDFs, including **Holiday Calendar**, **Exam Schedule**, and **Academic Calendar**. It processes both text-based and image-based PDFs using OCR and structures the output into tables with Google Gemini 1.5 Flash.

## Key Features
- **PDF to Text Extraction:** Extracts text from text-based PDFs using PyMuPDF.
- **OCR for Image PDFs:** Processes scanned PDFs with EasyOCR.
- **AI Formatting:** Leverages Google Gemini 1.5 Flash and groq to structure extracted data.
- **Automated Table Creation:** Outputs holidays, exams, and academic schedules in clear, tabular format.

## Installation
1. Install required dependencies:
​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​
pip install google-generativeai pymupdf python-dotenv pdf2image easyocr numpy Pillow
​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​
extras can be installed using : pip install -r requirements.txt

## Usage
- Provide paths to the target PDFs.
- Run the respective scripts:
- `holiday_calendar.py` for holidays.
- `exam_schedule.py` for exam schedules.
- `academic_calendar.py` for academic calendars.
- The output will be formatted and structured for easy reading.

## Expected Output
- **Holidays Table:** Date, holiday name, day.
- **Exam Schedule:** Date, time, course name, course code, exam type.
- **Academic Calendar:** Semester-wise key dates and events.

---
*This is a submodule of a larger project. Refer to the main repository for additional context.*
​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​
