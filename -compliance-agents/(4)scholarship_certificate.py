import imaplib
import email
import re
import sqlite3
import os
import time
import logging
import shutil
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
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib import colors

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='ai_scholarship_generator.log')
logger = logging.getLogger()

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Create certificates directory if it doesn't exist
CERTIFICATES_DIR = "scholarship_certificates"
if not os.path.exists(CERTIFICATES_DIR):
    os.makedirs(CERTIFICATES_DIR)
    logger.info(f"Created certificates directory: {CERTIFICATES_DIR}")

def check_dependencies():
    """Check if all required packages are installed and install if missing"""
    try:
        import schedule
    except ImportError:
        logger.info("Schedule package not found. Attempting to install...")
        try:
            import subprocess
            subprocess.check_call(["pip", "install", "schedule"])
            logger.info("Schedule package installed successfully.")
        except Exception as e:
            logger.error(f"Failed to install schedule package: {str(e)}")
            logger.error("Please install manually with: pip install schedule")
            exit(1)

def check_and_process_emails():
    """Main function to check emails and process scholarship certificate requests using AI"""
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
        
        # Search for ALL emails with [SCHOLARSHIP] in the subject (both read and unread)
        status, messages = imap_server.search(None, 'SUBJECT "[SCHOLARSHIP]"')
        email_ids = messages[0].split()
        
        if not email_ids:
            logger.info("No scholarship certificate requests found")
            imap_server.logout()
            return
        
        logger.info(f"Found {len(email_ids)} scholarship certificate requests")
        
        # Update scholarship eligibility before processing any emails
        update_scholarship_eligibility()
        
        for email_id in email_ids:
            try:
                process_single_email(imap_server, email_id, username, password)
            except Exception as e:
                logger.error(f"Error processing email {email_id}: {str(e)}")
        
        imap_server.logout()
        
    except Exception as e:
        logger.error(f"Error connecting to email server: {str(e)}")

def update_scholarship_eligibility():
    """Update scholarship eligibility for all students"""
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        # Check if the scholarship_eligible column exists
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Add the scholarship_eligible column if it doesn't exist
        if 'scholarship_eligible' not in column_names:
            logger.info("Adding scholarship_eligible column to students table")
            cursor.execute("ALTER TABLE students ADD COLUMN scholarship_eligible INTEGER DEFAULT 0")
        
        # Check if scholarship_criteria table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scholarship_criteria'")
        table_exists = cursor.fetchone()
        
        # Create scholarship_criteria table if it doesn't exist
        if not table_exists:
            logger.info("Creating scholarship_criteria table")
            cursor.execute('''
            CREATE TABLE scholarship_criteria (
                id INTEGER PRIMARY KEY,
                min_cgpa REAL NOT NULL,
                min_attendance REAL NOT NULL,
                last_updated TEXT
            )
            ''')
            cursor.execute('''
            INSERT INTO scholarship_criteria (id, min_cgpa, min_attendance, last_updated)
            VALUES (1, 8.5, 75.0, datetime('now'))
            ''')
            conn.commit()
        
        # Get current criteria
        cursor.execute("SELECT min_cgpa, min_attendance FROM scholarship_criteria WHERE id = 1")
        criteria = cursor.fetchone()
        if not criteria:
            logger.error("Scholarship criteria not found")
            conn.close()
            return
        
        min_cgpa, min_attendance = criteria
        
        # Update eligibility flags
        cursor.execute('''
        UPDATE students
        SET scholarship_eligible = CASE
            WHEN cgpa >= ? AND attendance >= ? THEN 1
            ELSE 0
        END
        ''', (min_cgpa, min_attendance))
        
        conn.commit()
        rows_updated = cursor.rowcount
        logger.info(f"Updated scholarship eligibility for {rows_updated} students")
        
        conn.close()
    except Exception as e:
        logger.error(f"Error updating scholarship eligibility: {str(e)}")

def process_single_email(imap_server, email_id, username, password):
    """Process a single email request using AI for information extraction"""
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
    logger.info(f"Processing scholarship request from {sender_email}, Subject: {subject}")
    
    # Extract email text content
    email_text = extract_plain_text_from_email(msg)
    
    # Use AI to extract student information
    extraction_result = extract_student_info_from_text(email_text)
    name, roll_no = parse_extraction_result(extraction_result)
    
    if not roll_no:
        logger.warning(f"Could not extract roll number from email from {sender_email}")
        send_error_email(username, password, sender_email, 
                         "Student Information Not Found", 
                         "We could not identify your roll number in your request. Please include your name and roll number clearly in your email.")
        return
    
    # Get student information from database
    student_info = get_student_info(roll_no)
    
    if not student_info:
        logger.warning(f"Student with roll number {roll_no} not found in database")
        send_error_email(username, password, sender_email, 
                        "Student Not Found", 
                        f"We could not find a student with roll number {roll_no} in our database.")
        return
    
    # Verify name if database has it
    db_name, cgpa, attendance, department, rank, is_eligible = student_info
    
    # If AI-extracted name doesn't match database name, use database name
    if name and db_name and not names_likely_match(name, db_name):
        logger.warning(f"Name mismatch: extracted '{name}', database has '{db_name}'")
        name = db_name  # Use database name for certificate
    
    # Check if student is eligible for scholarship
    if not is_eligible:
        logger.info(f"Student {roll_no} is not eligible for scholarship (CGPA: {cgpa}, Attendance: {attendance})")
        send_ineligibility_email(username, password, sender_email, db_name, cgpa, attendance)
        return
    
    # Generate certificate
    pdf_filename = os.path.join(CERTIFICATES_DIR, f"{roll_no}_scholarship_certificate.pdf")
    
    try:
        generate_scholarship_certificate(db_name, roll_no, cgpa, attendance, rank, department, pdf_filename)
        # Send certificate by email
        send_certificate_email(username, password, sender_email, db_name, pdf_filename)
        logger.info(f"Scholarship certificate sent to {sender_email} for student {roll_no}")
        
        # We keep the PDF in the certificates directory
        logger.info(f"Certificate saved at: {pdf_filename}")
        
        # Update the database to record that a certificate was issued
        update_certificate_status(roll_no)
        
    except Exception as e:
        logger.error(f"Error generating or sending certificate: {str(e)}")
        send_error_email(username, password, sender_email, 
                        "Certificate Generation Failed", 
                        "We encountered an error while generating your scholarship certificate. Please contact the administrator.")

def update_certificate_status(roll_no):
    """Update the database to record that a certificate was issued"""
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        # Update the scholarship_certificate field to 1 (indicating a certificate was issued)
        cursor.execute("UPDATE students SET scholarship_certificate = 1 WHERE roll_no = ?", (roll_no,))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated certificate status for student {roll_no}")
    except Exception as e:
        logger.error(f"Error updating certificate status: {str(e)}")

def extract_plain_text_from_email(msg):
    """Extract plain text content from email message"""
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
    """Use Gemini AI to extract student information from email text"""
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
    """Parse the AI extraction result to get name and roll number"""
    name_match = re.search(r"Name:\s*([^\n]+)", result_text)
    roll_match = re.search(r"Roll Number:\s*([A-Za-z0-9]+)", result_text)
    
    name = name_match.group(1).strip() if name_match else None
    roll_no = roll_match.group(1).strip() if roll_match else None
    
    # Clean up roll number (remove trailing punctuation)
    if roll_no:
        roll_no = re.sub(r'[.,]$', '', roll_no)
        # Check if the text "Unknown" is in the roll number
        if roll_no.lower() == "unknown":
            roll_no = None
    
    # Check if the text "Unknown" is in the name
    if name and name.lower() == "unknown":
        name = None
        
    logger.info(f"Parsed name: {name}, roll number: {roll_no}")
    return name, roll_no

def names_likely_match(name1, name2):
    """Check if two names are likely to refer to the same person"""
    # Convert to lowercase and remove extra spaces
    n1 = ' '.join(name1.lower().split())
    n2 = ' '.join(name2.lower().split())
    
    # If exact match
    if n1 == n2:
        return True
    
    # If one name is contained in the other
    if n1 in n2 or n2 in n1:
        return True
    
    # Compare individual words (to handle name order differences)
    words1 = set(n1.split())
    words2 = set(n2.split())
    common_words = words1.intersection(words2)
    
    # If they share significant common words
    if len(common_words) >= 2 or (len(common_words) == 1 and len(words1) == 1 and len(words2) == 1):
        return True
        
    return False

def get_student_info(roll_no):
    """Get student information from the database"""
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        # Check column names in the students table
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Determine which column name to use for roll number
        roll_field = "roll_no" if "roll_no" in column_names else "rollnum"
        
        # Check if department field exists
        dept_field = "department" if "department" in column_names else "'Engineering' as department"
        
        # Check if rank field exists
        rank_field = "college_rank" if "college_rank" in column_names else "rank"
        
        # Check if scholarship_eligible field exists
        eligible_field = "scholarship_eligible" if "scholarship_eligible" in column_names else "1 as scholarship_eligible"
        
        # Build query based on available columns
        query = f"""
        SELECT name, cgpa, attendance, {dept_field}, {rank_field}, {eligible_field}
        FROM students WHERE {roll_field} = ?
        """
        
        cursor.execute(query, (roll_no,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Database error when retrieving student info: {str(e)}")
        return None

def get_scholarship_criteria():
    """Get current scholarship criteria from database"""
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        # Check if scholarship_criteria table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scholarship_criteria'")
        table_exists = cursor.fetchone()
        
        # Create and populate with default values if it doesn't exist
        if not table_exists:
            cursor.execute('''
            CREATE TABLE scholarship_criteria (
                id INTEGER PRIMARY KEY,
                min_cgpa REAL NOT NULL,
                min_attendance REAL NOT NULL,
                last_updated TEXT
            )
            ''')
            cursor.execute('''
            INSERT INTO scholarship_criteria (id, min_cgpa, min_attendance, last_updated)
            VALUES (1, 8.5, 75.0, datetime('now'))
            ''')
            conn.commit()
            
            result = (8.5, 75.0)
        else:
            cursor.execute("SELECT min_cgpa, min_attendance FROM scholarship_criteria WHERE id = 1")
            result = cursor.fetchone()
            if not result:
                # Insert default values if no row exists
                cursor.execute('''
                INSERT INTO scholarship_criteria (id, min_cgpa, min_attendance, last_updated)
                VALUES (1, 8.5, 75.0, datetime('now'))
                ''')
                conn.commit()
                result = (8.5, 75.0)
        
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error retrieving scholarship criteria: {str(e)}")
        return (8.5, 75.0)  # Default values if error

def generate_scholarship_certificate(name, roll_no, cgpa, attendance, rank, department, output_path):
    """Generate a professional-looking scholarship certificate PDF"""
    try:
        # Get criteria
        min_cgpa, min_attendance = get_scholarship_criteria()
        
        # Create a PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add certificate title
        title_style = styles["Title"]
        title = Paragraph("<b>SCHOLARSHIP ELIGIBILITY CERTIFICATE</b>", title_style)
        story.append(title)
        
        # Add some space
        story.append(Spacer(1, 20))
        
        # Current date
        current_date = time.strftime("%B %d, %Y")
        date_paragraph = Paragraph(f"Date: {current_date}", styles["Normal"])
        story.append(date_paragraph)
        
        # Add some space
        story.append(Spacer(1, 20))
        
        # Certificate text - using separate paragraphs instead of HTML-like para tags
        normal_style = styles["Normal"]
        
        certificate_text1 = f"""This is to certify that <b>{name}</b> with Roll Number <b>{roll_no}</b> 
from the <b>{department}</b> department has achieved <b>Rank {rank}</b> 
with a CGPA of <b>{cgpa}</b> and attendance of <b>{attendance}%</b>."""

        certificate_text2 = f"""Based on the minimum eligibility criteria of <b>CGPA {min_cgpa}</b> and 
<b>Attendance {min_attendance}%</b>, the student is <b>ELIGIBLE</b> for 
the academic scholarship for the current term."""

        # Add paragraphs separately
        story.append(Paragraph(certificate_text1, normal_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(certificate_text2, normal_style))
        
        # Add some space
        story.append(Spacer(1, 40))
        
        # Authority signature
        signature_text = """<b>Scholarship Office</b><br/>
University Administration"""
        story.append(Paragraph(signature_text, styles["Normal"]))
        
        # Build the PDF
        doc.build(story)
        logger.info(f"Scholarship certificate generated successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise

def send_certificate_email(username, password, recipient_email, student_name, pdf_path):
    """Send an email with the scholarship certificate attached"""
    try:
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = f'Your Scholarship Eligibility Certificate - {student_name}'
        msg['From'] = username
        msg['To'] = recipient_email
        
        # Email body
        msg.set_content(f"""
        Dear {student_name},
        
        Congratulations! We are pleased to inform you that you are eligible for the academic scholarship.
        
        Please find attached your scholarship eligibility certificate as requested.
        
        To complete the scholarship process, please visit the scholarship office with this certificate
        and your ID card within the next 30 days.
        
        If you have any questions, please contact the scholarship office.
        
        Regards,
        Scholarship Administration
        """)
        
        # Attach the PDF
        with open(pdf_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(pdf_path)
        
        msg.add_attachment(file_data, 
                          maintype='application', 
                          subtype='pdf', 
                          filename=file_name)
        
        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(username, password)
            smtp.send_message(msg)
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise

def send_ineligibility_email(username, password, recipient_email, student_name, cgpa, attendance):
    """Send an email informing the student they are not eligible for the scholarship"""
    try:
        # Get current criteria
        min_cgpa, min_attendance = get_scholarship_criteria()
        
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = f'Scholarship Eligibility Status - {student_name}'
        msg['From'] = username
        msg['To'] = recipient_email
        
        # Determine which criteria were not met
        cgpa_met = cgpa >= min_cgpa
        attendance_met = attendance >= min_attendance
        
        # Email body
        msg.set_content(f"""
        Dear {student_name},
        
        Thank you for your scholarship application. After reviewing your academic record, we regret to inform you that you are currently not eligible for the scholarship.
        
        Your current academic status:
        - CGPA: {cgpa} (Minimum required: {min_cgpa}) - {"Met" if cgpa_met else "Not met"}
        - Attendance: {attendance}% (Minimum required: {min_attendance}%) - {"Met" if attendance_met else "Not met"}
        
        You may apply again in the next semester if your academic performance meets the eligibility criteria.
        
        If you have any questions or believe there is an error in our records, please contact the scholarship office.
        
        Regards,
        Scholarship Administration
        """)
        
        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(username, password)
            smtp.send_message(msg)
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending ineligibility email: {str(e)}")
        return False

def send_error_email(username, password, recipient_email, subject, message):
    """Send an error notification email"""
    try:
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = f'[SCHOLARSHIP] {subject}'
        msg['From'] = username
        msg['To'] = recipient_email
        
        # Email body
        msg.set_content(f"""
        Dear Student,
        
        {message}
        
        Please submit a new request with the correct information.
        
        Regards,
        Scholarship Administration
        """)
        
        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(username, password)
            smtp.send_message(msg)
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending error email: {str(e)}")
        return False

def schedule_periodic_check():
    """Run the email check periodically"""
    import schedule
    import time
    
    # Schedule to run every 15 minutes
    schedule.every(15).minutes.do(check_and_process_emails)
    
    logger.info("Starting scheduled email checking service")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Sleep for 1 minute between checks

def update_criteria(new_min_cgpa=None, new_min_attendance=None):
    """Update scholarship criteria in the database"""
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        # Check if scholarship_criteria table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scholarship_criteria'")
        table_exists = cursor.fetchone()
        
        # Create the table if it doesn't exist
        if not table_exists:
            cursor.execute('''
            CREATE TABLE scholarship_criteria (
                id INTEGER PRIMARY KEY,
                min_cgpa REAL NOT NULL,
                min_attendance REAL NOT NULL,
                last_updated TEXT
            )
            ''')
            cursor.execute('''
            INSERT INTO scholarship_criteria (id, min_cgpa, min_attendance, last_updated)
            VALUES (1, 8.5, 75.0, datetime('now'))
            ''')
            conn.commit()
            
            current_cgpa, current_attendance = 8.5, 75.0
        else:
            # Get current criteria
            cursor.execute("SELECT min_cgpa, min_attendance FROM scholarship_criteria WHERE id = 1")
            current = cursor.fetchone()
            
            if not current:
                # Insert default values if no row exists
                cursor.execute('''
                INSERT INTO scholarship_criteria (id, min_cgpa, min_attendance, last_updated)
                VALUES (1, 8.5, 75.0, datetime('now'))
                ''')
                conn.commit()
                current_cgpa, current_attendance = 8.5, 75.0
            else:
                current_cgpa, current_attendance = current
        
        # Use new values if provided, otherwise keep current values
        min_cgpa = new_min_cgpa if new_min_cgpa is not None else current_cgpa
        min_attendance = new_min_attendance if new_min_attendance is not None else current_attendance
        
        # Update criteria
        cursor.execute('''
        UPDATE scholarship_criteria 
        SET min_cgpa = ?, min_attendance = ?, last_updated = datetime('now')
        WHERE id = 1
        ''', (min_cgpa, min_attendance))
        
        conn.commit()
        conn.close()
        
        print(f"Scholarship criteria updated: CGPA >= {min_cgpa}, Attendance >= {min_attendance}%")
        return True
        
    except Exception as e:
        logger.error(f"Error updating scholarship criteria: {str(e)}")
        return False

def update_student_ranks():
    """Update student ranks within departments based on CGPA"""
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        # Check column names in the students table
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Check if department field exists
        has_department = "department" in column_names
        
        # Determine which column to use for rank
        rank_field = "college_rank" if "college_rank" in column_names else "rank"
        
        if has_department:
            # Get all departments
            cursor.execute("SELECT DISTINCT department FROM students")
            departments = cursor.fetchall()
            
            for dept in departments:
                department = dept[0]
                # Get all students in this department sorted by CGPA in descending order
                cursor.execute(f"""
                    SELECT id, cgpa FROM students 
                    WHERE department = ? 
                    ORDER BY cgpa DESC, name ASC
                """, (department,))
                student_rows = cursor.fetchall()
                
                # Update ranks based on sorted order within department
                for rank, (student_id, _) in enumerate(student_rows, 1):
                    cursor.execute(f"UPDATE students SET {rank_field} = ? WHERE id = ?", (rank, student_id))
        else:
            # If no department field, rank all students together
            cursor.execute("""
                SELECT id, cgpa FROM students 
                ORDER BY cgpa DESC, name ASC
            """)
            student_rows = cursor.fetchall()
            
            # Update ranks based on sorted order
            for rank, (student_id, _) in enumerate(student_rows, 1):
                cursor.execute(f"UPDATE students SET {rank_field} = ? WHERE id = ?", (rank, student_id))
        
        conn.commit()
        conn.close()
        logger.info("Updated ranks for students")
        return True
    except Exception as e:
        logger.error(f"Error updating student ranks: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    # Check dependencies first
    check_dependencies()
    
    parser = argparse.ArgumentParser(description='AI-powered Scholarship Certificate Generator')
    parser.add_argument('--service', action='store_true', help='Run as a scheduled service')
    parser.add_argument('--update-criteria', action='store_true', help='Update scholarship criteria')
    parser.add_argument('--min-cgpa', type=float, help='New minimum CGPA for scholarship eligibility')
    parser.add_argument('--min-attendance', type=float, help='New minimum attendance percentage for scholarship eligibility')
    parser.add_argument('--update-ranks', action='store_true', help='Update student ranks within departments')
    parser.add_argument('--process-once', action='store_true', help='Process emails once and exit')
    
    args = parser.parse_args()
    
    try:
        if args.update_ranks:
            update_student_ranks()
            
        if args.update_criteria:
            if update_criteria(args.min_cgpa, args.min_attendance):
                update_scholarship_eligibility()
        elif args.service or os.environ.get("RUN_AS_SERVICE", "false").lower() == "true":
            schedule_periodic_check()
        elif args.process_once:
            # Run once
            logger.info("Processing scholarship emails once")
            check_and_process_emails()
            logger.info("Processing complete")
        else:
            # Default behavior - run once
            logger.info("Starting AI-powered scholarship certificate generator")
            check_and_process_emails()
            logger.info("Processing complete")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")