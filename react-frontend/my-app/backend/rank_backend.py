import imaplib
import email
import re
import sqlite3
import os
import time
import logging
import shutil
import sys
from email.header import decode_header
from dotenv import load_dotenv
import google.generativeai as genai
import smtplib
from email.message import EmailMessage
import mimetypes
from email.utils import parseaddr
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate
from fastapi import APIRouter

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ai_certificate_generator.log'
)
logger = logging.getLogger()

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Create certificates directory if it doesn't exist
CERTIFICATES_DIR = "certificates"
if not os.path.exists(CERTIFICATES_DIR):
    os.makedirs(CERTIFICATES_DIR)
    logger.info(f"Created certificates directory: {CERTIFICATES_DIR}")

# Set up the FastAPI router
router = APIRouter(
    prefix="/ranking",  # Adds this prefix to all routes
    tags=["ranking"],   # For API documentation grouping
)

def check_and_process_emails():
    """Main function to check emails and process rank certificate requests using AI."""
    username = os.environ.get("EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")
    
    if not username or not password:
        logger.error("Email credentials not found in environment variables")
        return
    
    try:
        # Connect to the IMAP server
        imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
        imap_server.login(username, password)
        imap_server.select("inbox")
        
        # Search for emails with subject containing "[RANK]"
        status, messages = imap_server.search(None, '(SUBJECT "[RANK]")')
        email_ids = messages[0].split()
        
        if not email_ids:
            logger.info("No rank certificate requests found")
            imap_server.logout()
            return
        
        logger.info(f"Found {len(email_ids)} rank certificate requests")
        
        # Update database ranks before processing any emails
        update_student_ranks()
        
        for email_id in email_ids:
            try:
                process_single_email(imap_server, email_id, username, password)
            except Exception as e:
                logger.error(f"Error processing email {email_id}: {str(e)}")
        
        imap_server.logout()
        
    except Exception as e:
        logger.error(f"Error connecting to email server: {str(e)}")

def update_student_ranks():
    """Update all student ranks in the database based on sorted CGPA."""
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        # Get all students sorted by CGPA in descending order
        # Updated query to use roll_no instead of an id column.
        cursor.execute("SELECT roll_no, cgpa FROM students ORDER BY cgpa DESC, name ASC")
        student_rows = cursor.fetchall()
        
        # Update ranks based on sorted order
        for rank, (roll_no, _) in enumerate(student_rows, 1):
            cursor.execute("UPDATE students SET college_rank = ? WHERE roll_no = ?", (rank, roll_no))
        
        # Set rank_generation to 1 to indicate ranks have been generated
        cursor.execute("UPDATE students SET rank_generation = 1")
        
        conn.commit()
        conn.close()
        logger.info(f"Updated ranks for {len(student_rows)} students")
    except Exception as e:
        logger.error(f"Error updating student ranks: {str(e)}")

def process_single_email(imap_server, email_id, username, password):
    """Process a single email request using AI for information extraction."""
    # Fetch the email
    res, msg_data = imap_server.fetch(email_id, "(RFC822)")
    if res != "OK":
        logger.error(f"Failed to fetch email with ID {email_id}")
        return
    
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    # Extract sender information
    sender_email = parseaddr(msg["From"])[1]
    subject = msg["Subject"]
    logger.info(f"Processing request from {sender_email}, Subject: {subject}")
    
    # Extract email text content
    email_text = extract_plain_text_from_email(msg)
    
    # Use AI to extract student information
    extraction_result = extract_student_info_from_text(email_text)
    name, rollnum = parse_extraction_result(extraction_result)
    
    if not rollnum:
        logger.warning(f"Could not extract roll number from email from {sender_email}")
        send_error_email(
            username, password, sender_email, 
            "Student Information Not Found", 
            "We could not identify your roll number in your request. Please include your name and roll number clearly in your email."
        )
        # Mark as read
        imap_server.store(email_id, '+FLAGS', '\\Seen')
        return
    
    # Get student information from database
    student_info = get_student_info(rollnum)
    
    if not student_info:
        logger.warning(f"Student with roll number {rollnum} not found in database")
        send_error_email(
            username, password, sender_email, 
            "Student Not Found", 
            f"We could not find a student with roll number {rollnum} in our database."
        )
        # Mark as read
        imap_server.store(email_id, '+FLAGS', '\\Seen')
        return
    
    # Verify name if database has it
    db_name, cgpa, department, rank = student_info
    
    # If AI-extracted name doesn't match database name, use database name
    if name and db_name and not names_likely_match(name, db_name):
        logger.warning(f"Name mismatch: extracted '{name}', database has '{db_name}'")
        name = db_name  # Use database name for certificate
    
    # Generate certificate
    pdf_filename = os.path.join(CERTIFICATES_DIR, f"{rollnum}_rank_certificate.pdf")
    
    try:
        generate_rank_certificate(db_name, rollnum, cgpa, rank, department, pdf_filename)
        # Send certificate by email
        send_certificate_email(username, password, sender_email, db_name, pdf_filename)
        logger.info(f"Certificate sent to {sender_email} for student {rollnum}")
        
        # Update the database to mark rank certificate as generated
        update_rank_certificate_status(rollnum)
        logger.info(f"Certificate saved at: {pdf_filename}")
    except Exception as e:
        logger.error(f"Error generating or sending certificate: {str(e)}")
        send_error_email(
            username, password, sender_email, 
            "Certificate Generation Failed", 
            "We encountered an error while generating your certificate. Please contact the administrator."
        )
    finally:
        # Mark email as read
        imap_server.store(email_id, '+FLAGS', '\\Seen')

def update_rank_certificate_status(rollnum):
    """Update the database to mark rank certificate as generated."""
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET rank_generation = 1 WHERE roll_no = ?", (rollnum,))
        conn.commit()
        conn.close()
        logger.info(f"Updated rank_generation status for student {rollnum}")
    except Exception as e:
        logger.error(f"Error updating rank_generation status: {str(e)}")

def extract_plain_text_from_email(msg):
    """Extract plain text content from an email message."""
    text_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
                
            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    text_content = part.get_payload(decode=True).decode(charset)
                    break
                except Exception:
                    text_content = part.get_payload(decode=True).decode(errors="ignore")
                    break
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            text_content = msg.get_payload(decode=True).decode(charset)
        except Exception:
            text_content = msg.get_payload(decode=True).decode(errors="ignore")
    
    return text_content

def extract_student_info_from_text(email_text):
    """Use Gemini AI to extract student information from email text."""
    try:
        logger.info("Using AI to extract student information")
        prompt = (
            "Extract only the following information from this email:\n"
            "1. Student's full name\n"
            "2. Student's roll number or ID\n\n"
            "Format your response exactly like this with no other text:\n"
            "Name: <extracted student name>\n"
            "Roll Number: <extracted roll number>\n\n"
            "If you cannot find one of these pieces of information, use 'Unknown' for that field.\n\n"
            f"Email text:\n{email_text}"
        )
        
        response = model.generate_content(prompt)
        result = response.text
        logger.info(f"AI extraction result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in AI extraction: {str(e)}")
        return "Name: Unknown\nRoll Number: Unknown"

def parse_extraction_result(result_text):
    """Parse the AI extraction result to obtain name and roll number."""
    name_match = re.search(r"Name:\s*([^\n]+)", result_text)
    roll_match = re.search(r"Roll Number:\s*([A-Za-z0-9]+)", result_text)
    
    name = name_match.group(1).strip() if name_match else None
    rollnum = roll_match.group(1).strip() if roll_match else None
    
    # Clean up roll number (remove trailing punctuation)
    if rollnum:
        rollnum = re.sub(r'[.,]$', '', rollnum)
        if rollnum.lower() == "unknown":
            rollnum = None
    
    if name and name.lower() == "unknown":
        name = None
        
    logger.info(f"Parsed name: {name}, roll number: {rollnum}")
    return name, rollnum

def names_likely_match(name1, name2):
    """Check if two names likely refer to the same person."""
    n1 = ' '.join(name1.lower().split())
    n2 = ' '.join(name2.lower().split())
    
    if n1 == n2:
        return True
    if n1 in n2 or n2 in n1:
        return True
    
    words1 = set(n1.split())
    words2 = set(n2.split())
    common_words = words1.intersection(words2)
    
    if len(common_words) >= 2 or (len(common_words) == 1 and len(words1) == 1 and len(words2) == 1):
        return True
        
    return False

def get_student_info(rollnum):
    """Retrieve student information from the database."""
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        # Adjust the query as per your database schema using roll_no
        cursor.execute("SELECT name, cgpa, 'Computer Science' as department, college_rank FROM students WHERE roll_no = ?", (rollnum,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Database error when retrieving student info: {str(e)}")
        return None

def generate_rank_certificate(name, rollnum, cgpa, rank, department, output_path):
    """Generate a professional-looking rank certificate PDF."""
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Certificate title
        title_style = styles["Title"]
        title = Paragraph("<b>RANK CERTIFICATE</b>", title_style)
        story.append(title)
        story.append(Paragraph("<br/><br/>", styles["Normal"]))
        
        # Current date
        current_date = time.strftime("%B %d, %Y")
        story.append(Paragraph(f"Date: {current_date}", styles["Normal"]))
        story.append(Paragraph("<br/><br/>", styles["Normal"]))
        
        # Certificate content
        certificate_text = f"""
        <para spaceBefore="10">
        This is to certify that <b>{name}</b> with Roll Number <b>{rollnum}</b> 
        from the <b>{department}</b> department has achieved <b>Rank {rank}</b> 
        with a CGPA of <b>{cgpa}</b> in the academic performance ranking.
        </para>
        """
        story.append(Paragraph(certificate_text, styles["Normal"]))
        story.append(Paragraph("<br/><br/><br/>", styles["Normal"]))
        
        # Authority signature
        signature_text = """
        <para>
        <b>Academic Office</b><br/>
        University Administration
        </para>
        """
        story.append(Paragraph(signature_text, styles["Normal"]))
        
        # Build PDF
        doc.build(story)
        logger.info(f"Certificate generated successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise

def send_certificate_email(username, password, recipient_email, student_name, pdf_path):
    """Send an email with the rank certificate attached."""
    try:
        msg = EmailMessage()
        msg['Subject'] = f'Your Rank Certificate - {student_name}'
        msg['From'] = username
        msg['To'] = recipient_email
        
        msg.set_content(f"""
        Dear {student_name},
        
        Please find attached your rank certificate as requested.
        
        If you have any questions, please contact the academic office.
        
        Regards,
        Academic Administration
        """)
        
        with open(pdf_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(pdf_path)
        
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(username, password)
            smtp.send_message(msg)
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise

def send_error_email(username, password, recipient_email, subject, message):
    """Send an error notification email."""
    try:
        msg = EmailMessage()
        msg['Subject'] = f'[RANK] {subject}'
        msg['From'] = username
        msg['To'] = recipient_email
        
        msg.set_content(f"""
        Dear Student,
        
        {message}
        
        Please submit a new request with the correct information.
        
        Regards,
        Academic Administration
        """)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(username, password)
            smtp.send_message(msg)
        
        return True

    except Exception as e:
        logger.error(f"Error sending error email: {str(e)}")
        return False

def schedule_periodic_check():
    """Run the email check periodically."""
    import schedule
    import time
    
    # Schedule to run every 15 minutes
    schedule.every(15).minutes.do(check_and_process_emails)
    
    logger.info("Starting scheduled email checking service")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def reset_database_ranks():
    """Reset all ranks in database based on CGPA sorting."""
    try:
        update_student_ranks()
        print("Database ranks have been reset according to CGPA")
    except Exception as e:
        print(f"Error resetting ranks: {e}")

@router.get("/rankchecker")
async def rankcheck():
    """
    API endpoint to process rank certificate requests.
    
    - If a '--reset-ranks' flag is passed via command line, the database ranks are reset.
    - If RUN_AS_SERVICE is true, the email-check service runs periodically.
    - Otherwise, it updates ranks and processes the emails once.
    """
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--reset-ranks":
            reset_database_ranks()
        elif os.environ.get("RUN_AS_SERVICE", "false").lower() == "true":
            schedule_periodic_check()
        else:
            update_student_ranks()
            logger.info("Starting AI-powered rank certificate generator")
            check_and_process_emails()
            logger.info("Processing complete")
        return {"status": "Processing complete"}
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return {"error": str(e)}
