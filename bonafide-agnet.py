import imaplib
import email
from email.header import decode_header
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def fetch_bonafide_emails(username, password):
    # Connect securely to Gmail's IMAP server
    imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
    imap_server.login(username, password)
    imap_server.select("inbox")  # You can change this to a specific folder if needed

    # Search for emails with "[BONAFIDE]" in the subject
    status, messages = imap_server.search(None, '(SUBJECT "[BONAFIDE]")')
    email_ids = messages[0].split()
    emails = []
    
    # Loop over each email ID and fetch its content
    for email_id in email_ids:
        res, msg_data = imap_server.fetch(email_id, "(RFC822)")
        if res != "OK":
            continue
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        emails.append(msg)
    
    imap_server.logout()
    return emails

def save_email_as_pdf(msg, output_path):
    # Extract plain text content from the email
    text_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    text_content = part.get_payload(decode=True).decode()
                except Exception as e:
                    print("Error decoding text:", e)
                break
    else:
        text_content = msg.get_payload(decode=True).decode()
    
    # Create a PDF using ReportLab
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    text_object = c.beginText(40, height - 40)
    text_object.setFont("Helvetica", 12)
    
    # Add the email text line by line
    for line in text_content.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)
    c.save()
    print(f"Saved email to {output_path}")

def main():
    # Email credentials
    username = "mukh.aniruddha@gmail.com"
    password = "**** **** **** ****"  # Consider using an app-specific password or OAuth2 for security
    
    # Fetch emails
    emails = fetch_bonafide_emails(username, password)
    for i in emails:
        print("----------------------------")
        print(i)
        print("----------------------------")
    print(f"Fetched {len(emails)} bonafide emails.")
    
    # Create PDFs
    os.makedirs("pdf_emails", exist_ok=True)
    pdf_paths = []
    for idx, msg in enumerate(emails):
        pdf_filename = os.path.join("pdf_emails", f"email_{idx}.pdf")
        save_email_as_pdf(msg, pdf_filename)
        pdf_paths.append(pdf_filename)

if __name__ == "__main__":
    main()