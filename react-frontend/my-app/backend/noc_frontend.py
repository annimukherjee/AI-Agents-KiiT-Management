import imaplib
import email
import re
import sqlite3
import os
from email.header import decode_header
from dotenv import load_dotenv
from datetime import datetime
import io
from fastapi import APIRouter
import google.generativeai as genai  # Google Generative AI client
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


load_dotenv()

EMAIL_ACCOUNT    = os.environ.get("EMAIL")            # e.g., "your_email@gmail.com"
EMAIL_PASSWORD   = os.environ.get("EMAIL_PASSWORD")     # App Password or actual password
GOOGLE_API_KEY   = os.environ.get("GOOGLE_API_KEY")       # for Gemini
IMAP_SERVER      = "imap.gmail.com"
SMTP_SERVER      = "smtp.gmail.com"
SMTP_PORT        = 587

router = APIRouter(
    prefix="/noc",  # Optional: adds this prefix to all routes
    tags=["noc"],   # Optional: for API documentation grouping
)

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def fetch_noc_emails(username, password):
    imap_server = imaplib.IMAP4_SSL(IMAP_SERVER)
    imap_server.login(username, password)
    imap_server.select("inbox")

    status, messages = imap_server.search(None, '(SUBJECT "[NOC]")')
    if status != "OK":
        print("No emails found or error in search.")
        imap_server.logout()
        return []

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

def extract_student_info_with_llm(email_text):
    prompt = f"""
    You are given an email from a student requesting an NOC.
    Please extract the following fields exactly as separate lines in the format shown:
    Name: <NAME>
    Roll Number: <ROLL>
    From Date: <FROM_DATE>
    To Date: <TO_DATE>
    Pronoun: <PRONOUN>
    CGPA: <CGPA>
    ---
    Email:
    {email_text}
    """
    response = model.generate_content(prompt)
    result = response.text
    print(f"Raw LLM output:\n{result}\n")
    return result

def parse_extraction_result(result_text):
    name_match      = re.search(r"Name:\s*(.*)", result_text)
    roll_match      = re.search(r"Roll Number:\s*(.*)", result_text)
    from_date_match = re.search(r"From Date:\s*(.*)", result_text)
    to_date_match   = re.search(r"To Date:\s*(.*)", result_text)
    pronoun_match   = re.search(r"Pronoun:\s*(.*)", result_text)
    cgpa_match      = re.search(r"CGPA:\s*(.*)", result_text)

    name      = name_match.group(1).strip() if name_match else ""
    rollnum   = roll_match.group(1).strip() if roll_match else ""
    from_date = from_date_match.group(1).strip() if from_date_match else ""
    to_date   = to_date_match.group(1).strip() if to_date_match else ""
    pronoun   = pronoun_match.group(1).strip().lower() if pronoun_match else "his"
    cgpa      = cgpa_match.group(1).strip() if cgpa_match else "0"

    return name, rollnum, from_date, to_date, pronoun, cgpa


def check_student_in_db(rollnum):
    if not os.path.exists("students.db"):
        return None
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE rollnum=?", (rollnum,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def generate_noc_pdf_in_memory(name, rollnum, from_date, to_date, pronoun, cgpa):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    textobject = c.beginText()
    textobject.setTextOrigin(inch, height - inch)  # 1 inch margin
    textobject.setFont("Times-Roman", 12)

    # Determine title from pronoun: "Mr." for his, "Mrs." for her, default to "Mr."
    title = "Mr." if pronoun == "his" else "Mrs." if pronoun == "her" else "Mr."

    # Compute performance based on CGPA
    try:
        cgpa_val = float(cgpa)
    except:
        cgpa_val = 0.0
    if cgpa_val > 8.5:
        performance = "good"
    elif cgpa_val > 7.5:
        performance = "satisfactory"
    else:
        performance = "unsatisfactory"

    # Current date for the "Dated:" line
    current_date = datetime.now().strftime("%Y-%m-%d")

    lines = [
        "KALINGA INSTITUTE OF INDUSTRIAL TECHNOLOGY",
        "(To be given on Letter Head) To be signed by HOD/Principal",
        f"Dated: {current_date}",
        "",
        "Subject:- No Objection Certificate for Department of Justice Internship Programme.",
        "",
        f"It is certified that {title} {name} (Roll Number: {rollnum}) is a bonafide student.",
        f"The KIIT COLLEGE has no objection for doing the Internship Programme from {from_date} to {to_date}.",
        f"It is certified that {title} {name} is not registered for any course requiring attendance in the class during the said period.",
        "",
        f"The conduct of the student as reported by KIIT has been found {performance}.",
        "",
        "(KIIT , Bhubaneshwar)"
    ]

    for line in lines:
        textobject.textLine(line)
    c.drawText(textobject)
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

def send_noc_certificate(to_email, pdf_buffer, name):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ACCOUNT
    msg["To"] = to_email
    msg["Subject"] = "Your NOC Certificate"

    body = f"Dear {name},\n\nPlease find attached your NOC Certificate.\n\nRegards,\nYour Institution"
    msg.attach(MIMEText(body, "plain"))

    # Attach PDF from in-memory buffer
    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_buffer.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename="noc_certificate.pdf")
    msg.attach(part)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

@router.get("/generatenoc")
async def process_noc():
    emails = fetch_noc_emails(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    print(f"Fetched {len(emails)} emails with [NOC].")

    for idx, msg in enumerate(emails, start=1):
        print(f"\nProcessing email {idx}...")

        # Extract sender (student) email
        from_header = msg.get("From", "")
        match = re.search(r"<(.+?)>", from_header)
        student_email = match.group(1) if match else from_header

        email_text = extract_plain_text_from_email(msg)
        if not email_text.strip():
            print("No text content found in this email.")
            continue

        # Use Gemini LLM to parse student info (including CGPA)
        llm_output = extract_student_info_with_llm(email_text)
        name, rollnum, from_date, to_date, pronoun, cgpa = parse_extraction_result(llm_output)
        print(f"Extracted details => Name: {name}, Roll: {rollnum}, Period: {from_date} to {to_date}, Pronoun: {pronoun}, CGPA: {cgpa}")

        # (Optional) Verify with database
        verified_name = check_student_in_db(rollnum)
        if verified_name:
            print(f"DB Verification: Student '{verified_name}' found for roll '{rollnum}'.")
        else:
            print("No DB match found or DB not used. Proceeding without verification.")

        # Generate the NOC PDF into an in-memory buffer
        pdf_buffer = generate_noc_pdf_in_memory(name, rollnum, from_date, to_date, pronoun, cgpa)
        print("Generated in-memory PDF for NOC certificate.")

        # Send the PDF to the student's email
        send_noc_certificate(student_email, pdf_buffer, name)
        print(f"Sent NOC certificate to {student_email}")

    return {"message": "NOC emails processed and certificates sent."}

