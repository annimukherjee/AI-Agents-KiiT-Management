from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import imaplib
import email
import re
import sqlite3
import os
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Create FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

# Configure Google Generative AI client
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Database setup - create table if it doesn't exist
def setup_database():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        rollnum TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
setup_database()

def fetch_bonafide_emails(username, password):
    imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
    imap_server.login(username, password)
    imap_server.select("inbox")

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

def extract_plain_text_from_email(msg):
    text_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    text_content = part.get_payload(decode=True).decode(errors="ignore")
                except Exception:
                    pass
                break
    else:
        text_content = msg.get_payload(decode=True).decode(errors="ignore")
    return text_content

def extract_student_info_from_text(email_text):
    prompt = (
        "Extract and format exactly like this - Name: <student name>, Roll Number: <roll number>. "
        "Extract from this email:\n\n"
        f"{email_text}"
    )
    response = model.generate_content(prompt)
    result = response.text
    return result

def parse_extraction_result(result_text):
    name_match = re.search(r"Name:\s*([^,]+)", result_text)
    roll_match = re.search(r"Roll Number:\s*([A-Za-z0-9]+)", result_text)

    name = name_match.group(1).strip() if name_match else None
    rollnum = roll_match.group(1).strip() if roll_match else None

    if rollnum:
        rollnum = re.sub(r'[.,]$', '', rollnum)

    return name, rollnum

def check_student_in_db(rollnum):
    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM students WHERE rollnum=?", (rollnum,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.Error:
        # Return None if any database error occurs
        return None

class VerificationResponse(BaseModel):
    message: str

@app.get("/verify-bonafide")
async def verify_bonafide():
    try:
        username = os.environ.get("EMAIL")
        password = os.environ.get("EMAIL_PASSWORD")

        if not username or not password:
            return {"message": "Email credentials not configured"}

        # Fetch emails
        emails = fetch_bonafide_emails(username, password)
        if not emails:
            return {"message": "No bonafide emails found"}

        # Process the most recent email
        msg = emails[0]
        email_text = extract_plain_text_from_email(msg)

        # Extract student info
        extraction_result = extract_student_info_from_text(email_text)
        name, rollnum = parse_extraction_result(extraction_result)

        if not name or not rollnum:
            return {"message": "Could not extract student information"}

        # Verify with database - if db doesn't exist yet, we'll return the extracted info anyway
        verified_name = check_student_in_db(rollnum)
        if verified_name:
            return {"message": f"Verification: Student '{verified_name}' found in the database."}
        else:
            # For testing, insert the extracted data into the database
            try:
                conn = sqlite3.connect('students.db')
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO students (rollnum, name) VALUES (?, ?)",
                               (rollnum, name))
                conn.commit()
                conn.close()
                return {"message": f"Student not in database. Extracted Name: {name}, Roll Number: {rollnum}"}
            except sqlite3.Error:
                return {"message": f"Database error. Extracted Name: {name}, Roll Number: {rollnum}"}

    except Exception as e:
        return {"message": f"Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)