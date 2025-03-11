from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import imaplib
import email
import re
import sqlite3
import uvicorn
import os
from email.header import decode_header
from dotenv import load_dotenv
import google.generativeai as genai
import smtplib
from email.message import EmailMessage
import mimetypes
from email.utils import parseaddr
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from noc_frontend import router as noc_router


load_dotenv()

app = FastAPI()

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the Google Generative AI client
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Data models for the API
class StudentInfo(BaseModel):
    name: str
    rollnum: str
    email: str
    email_text: str
    verified: bool

class BonafideRequest(BaseModel):
    students: List[StudentInfo]

# Step 1: Connect to Gmail and fetch emails with "[BONAFIDE]" in the subject
def fetch_bonafide_emails(username, password):
    imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
    imap_server.login(username, password)
    imap_server.select("inbox")

    # Search for emails with "[BONAFIDE]" in the subject
    status, messages = imap_server.search(None, '(SUBJECT "[BONAFIDE]")')
    email_ids = messages[0].split()
    emails = []

    for email_id in email_ids:
        res, msg_data = imap_server.fetch(email_id, "(RFC822)")
        if res != "OK":
            continue
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        emails.append(msg)

    imap_server.logout()
    return emails

# Step 2: Extract plain text content from the email
def extract_plain_text_from_email(msg):
    text_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    text_content = part.get_payload(decode=True).decode(errors="ignore")
                except Exception as e:
                    print("Error decoding text:", e)
                break
    else:
        text_content = msg.get_payload(decode=True).decode(errors="ignore")
    return text_content

# Step 3: Use Google's Generative AI LLM to extract Name and Roll Number from the email text
def extract_student_info_from_text(email_text):
    prompt = (
        "Extract and format exactly like this - Name: <student name>, Roll Number: <roll number>. "
        "Extract from this email:\n\n"
        f"{email_text}"
    )
    response = model.generate_content(prompt)
    result = response.text
    # print(f"Raw LLM output: {result}")  # Debug print
    return result

def parse_extraction_result(result_text):
    # First try the formatted pattern
    name_match = re.search(r"Name:\s*([^,]+)", result_text)
    roll_match = re.search(r"Roll Number:\s*([A-Za-z0-9]+)", result_text)

    if not name_match or not roll_match:
        # Fallback pattern: look for roll number pattern in original text
        roll_pattern = r"roll(?:\s+(?:no|number|#))?\.*\s*:?\s*([A-Za-z0-9]+)"
        roll_match = re.search(roll_pattern, result_text, re.IGNORECASE)

        # For name, take any text before "roll" if we didn't find it in the formatted way
        if not name_match:
            name_pattern = r"(?:I am|This is)?\s*([A-Za-z\s]+?)(?:\s*,|\s+roll)"
            name_match = re.search(name_pattern, result_text, re.IGNORECASE)

    name = name_match.group(1).strip() if name_match else None
    rollnum = roll_match.group(1).strip() if roll_match else None

    # Clean up the roll number (remove any trailing periods or commas)
    if rollnum:
        rollnum = re.sub(r'[.,]$', '', rollnum)

    return name, rollnum

# Step 5: Verify the student information against the database
def check_student_in_db(rollnum):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE rollnum=?", (rollnum,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Generate a PDF Bonafide Certificate
def generate_pdf(name, rollnum, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setTitle("BONAFIDE CERT")
    # Prepare the certificate content
    text = f"{name} with {rollnum} is a Bonafide student of KIIT University"
    c.drawString(100, 750, text)
    c.save()
    print(f"PDF generated at: {output_path}")

# Send an email with the PDF attached
def send_email_with_attachment(sender, recipient, subject, body, attachment_path):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body)

    # Read and attach the PDF file
    with open(attachment_path, "rb") as f:
        file_data = f.read()
    mime_type, _ = mimetypes.guess_type(attachment_path)
    if mime_type is None:
        mime_type = "application/octet-stream"
    maintype, subtype = mime_type.split("/", 1)

    msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=os.path.basename(attachment_path))

    # Connect to the SMTP server (here using Gmail's SMTP server with SSL)
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(sender, os.environ.get("EMAIL_PASSWORD"))
        smtp.send_message(msg)
    print(f"Email sent with attachment {attachment_path} to {recipient}.")

# New endpoint to fetch bonafide requests from emails
@app.get("/fetch-bonafide-requests", response_model=List[StudentInfo])
async def fetch_bonafide_requests():
    username = os.environ.get("EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")
    emails = fetch_bonafide_emails(username, password)

    if not emails:
        return []

    students = []
    for msg in emails:
        email_text = extract_plain_text_from_email(msg)
        extraction_result = extract_student_info_from_text(email_text)
        name, rollnum = parse_extraction_result(extraction_result)

        # Check if the student exists in the database
        verified_name = check_student_in_db(rollnum)

        students.append(
            StudentInfo(
                name=name or "Unknown",
                rollnum=rollnum or "Unknown",
                email=parseaddr(msg.get("From"))[1],
                email_text=email_text[:200] + "..." if len(email_text) > 200 else email_text,
                verified=verified_name is not None
            )
        )

    return students

# New endpoint to process and send certificates
@app.post("/send-certificates")
async def send_certificates(request: BonafideRequest):
    username = os.environ.get("EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")

    processed_count = 0

    for student in request.students:
        if not student.verified:
            continue  # Skip unverified students

        # Get the verified name from the database (more accurate than email extraction)
        verified_name = check_student_in_db(student.rollnum)
        if not verified_name:
            continue

        # Generate certificate
        pdf_filename = f"{student.rollnum}_bonafide.pdf"
        generate_pdf(verified_name, student.rollnum, pdf_filename)

        # Send email with the certificate
        send_email_with_attachment(
            username,
            student.email,
            "Bonafide Certificate",
            "Please find attached your Bonafide Certificate.",
            pdf_filename
        )

        processed_count += 1

    return JSONResponse(
        status_code=200,
        content={"message": f"Processed and sent {processed_count} certificates", "count": processed_count}
    )
app.include_router(noc_router)

if __name__ == "__main__":
    # Run the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)