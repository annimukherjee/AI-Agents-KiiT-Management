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
    prefix="/noc",  # Routes under /noc
    tags=["noc"],
)

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def fetch_noc_emails(username, password):
    imap_server = imaplib.IMAP4_SSL(IMAP_SERVER)
    imap_server.login(username, password)
    imap_server.select("inbox")

    # Updated search criteria:
    # 1. Subject has [NOC]
    # 2. NOT FROM the current email account (to exclude sent/replied emails)
    # 3. Only get UNSEEN (unread) emails to avoid processing previously handled requests
    search_criteria = f'(SUBJECT "[NOC]" NOT FROM "{username}" UNSEEN)'
    status, messages = imap_server.search(None, search_criteria)
    
    if status != "OK":
        print("No unread NOC emails found or error in search.")
        imap_server.logout()
        return []

    email_ids = messages[0].split()
    emails = []
    seen_message_ids = set()

    for email_id in email_ids:
        res, msg_data = imap_server.fetch(email_id, "(RFC822)")
        if res != "OK":
            continue
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        msg_id = msg.get("Message-ID")
        
        # Skip duplicates
        if msg_id in seen_message_ids:
            continue
        seen_message_ids.add(msg_id)
        
        # Store the email_id with the message for later reference
        msg.email_id = email_id
        emails.append(msg)

    imap_server.logout()
    return emails

def extract_plain_text_from_email(msg):
    text_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
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
    # Use the correct column name 'roll_no'
    cursor.execute("SELECT name FROM students WHERE roll_no=?", (rollnum,))
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

    # Determine title based on pronoun
    title = "Mr." if pronoun == "his" else "Mrs." if pronoun == "her" else "Mr."

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

def mark_emails_as_processed(emails):
    """Mark processed emails as read in the inbox"""
    imap_server = imaplib.IMAP4_SSL(IMAP_SERVER)
    imap_server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    imap_server.select("inbox")
    
    for msg in emails:
        if hasattr(msg, 'email_id'):
            # Mark the email as read
            imap_server.store(msg.email_id, '+FLAGS', '\\Seen')
    
    imap_server.logout()

# GET endpoint to fetch NOC requests from emails
@router.get("/fetch-noc-requests")
async def fetch_noc_requests():
    emails = fetch_noc_emails(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    print(f"Fetched {len(emails)} unread emails with [NOC].")
    student_requests = []
    processed_emails = []

    for msg in emails:
        # Extract sender email
        from_header = msg.get("From", "")
        match = re.search(r"<(.+?)>", from_header)
        student_email = match.group(1) if match else from_header

        email_text = extract_plain_text_from_email(msg)
        if not email_text.strip():
            continue

        # Extract student info using LLM
        llm_output = extract_student_info_with_llm(email_text)
        name, rollnum, from_date, to_date, pronoun, cgpa = parse_extraction_result(llm_output)
        print(f"Extracted details => Name: {name}, Roll: {rollnum}, Period: {from_date} to {to_date}, Pronoun: {pronoun}, CGPA: {cgpa}")

        verified_name = check_student_in_db(rollnum)
        verified = True if verified_name else False
        if verified_name:
            name = verified_name

        student_obj = {
            "name": name if name else "Unknown",
            "roll_no": rollnum if rollnum else "Unknown",
            "email": student_email,
            "email_text": email_text[:200] + "..." if len(email_text) > 200 else email_text,
            "verified": verified,
            "from_date": from_date,
            "to_date": to_date,
            "pronoun": pronoun,
            "cgpa": cgpa
        }
        student_requests.append(student_obj)
        processed_emails.append(msg)

    return student_requests

# POST endpoint to send NOC certificates for verified students
@router.post("/send-noc-certificates")
async def send_noc_certificates(request: list):
    processed_count = 0
    for student in request:
        if not student.get("verified", False):
            continue
        name = student.get("name")
        roll_no = student.get("roll_no")
        from_date = student.get("from_date")
        to_date = student.get("to_date")
        pronoun = student.get("pronoun")
        cgpa = student.get("cgpa")
        email_addr = student.get("email")
        pdf_buffer = generate_noc_pdf_in_memory(name, roll_no, from_date, to_date, pronoun, cgpa)
        send_noc_certificate(email_addr, pdf_buffer, name)
        processed_count += 1
    return {"message": f"Processed and sent {processed_count} certificates", "count": processed_count}