import imaplib
import email
import re
import sqlite3
import os
from email.header import decode_header
from dotenv import load_dotenv
import google.generativeai as genai  # Import the Google Generative AI client
import smtplib
from email.message import EmailMessage
import mimetypes
from email.utils import parseaddr

# For PDF generation using ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

load_dotenv()

# Configure the Google Generative AI client
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

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

# Step 3: Use Google's Generative AI LLM to extract Name and Roll Number from the email text.
def extract_student_info_from_text(email_text):
    prompt = (
        "Extract and format exactly like this - Name: <student name>, Roll Number: <roll number>. "
        "Extract from this email:\n\n"
        f"{email_text}"
    )
    response = model.generate_content(prompt)
    result = response.text
    print(f"Raw LLM output: {result}")  # Debug print
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

# New Function: Generate a PDF Bonafide Certificate
def generate_pdf(name, rollnum, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setTitle("BONAFIDE CERT")
    # Prepare the certificate content
    text = f"{name} with {rollnum} is a Bonafide student of KIIT University"
    c.drawString(100, 750, text)
    c.save()
    print(f"PDF generated at: {output_path}")

# New Function: Send an email with the PDF attached
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

# Main orchestration
def main():
    username = os.environ.get("EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")  # Consider using an app-specific password or OAuth2 for security
    emails = fetch_bonafide_emails(username, password)
    print(f"Fetched {len(emails)} bonafide emails.")
    
    for idx, msg in enumerate(emails):
        print(f"\nProcessing email {idx+1}...")
        email_text = extract_plain_text_from_email(msg)
        print("Email text (first 200 chars):")
        print(email_text[:200])
        
        # Extract student info using the Google Generative AI LLM
        extraction_result = extract_student_info_from_text(email_text)
        print("LLM Extraction Result:")
        print(extraction_result)
        
        # Parse the extraction result to get name and roll number
        name, rollnum = parse_extraction_result(extraction_result)
        if name and rollnum:
            print(f"Extracted Name: {name}, Roll Number: {rollnum}")
            
            # Verify with the student database
            verified_name = check_student_in_db(rollnum)
            if verified_name:
                print(f"Verification: Student '{verified_name}' found in the database.")
                
                # Generate the PDF Bonafide Certificate
                pdf_filename = f"{rollnum}_bonafide.pdf"
                generate_pdf(verified_name, rollnum, pdf_filename)
                
                # Extract the sender's email address from the original email
                sender_email = parseaddr(msg.get("From"))[1]
                
                # Prepare email details to send the certificate
                email_subject = "Bonafide Certificate"
                email_body = "Please find attached your Bonafide Certificate."
                send_email_with_attachment(username, sender_email, email_subject, email_body, pdf_filename)
            else:
                print("Verification: Student not found in the database.")
        else:
            print("Failed to extract student info.")
            
if __name__ == "__main__":
    main()