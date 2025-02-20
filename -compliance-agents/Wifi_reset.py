import os
import imaplib
import email
import pickle
import re
import base64
from email.header import decode_header
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from agno.agent import Agent
from agno.models.google import Gemini

# Load environment variables
load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]
CLIENT_SECRET_FILE = "client_secret_433401284352-evlh7ld266o648beaude1h9bumnajatq.apps.googleusercontent.com.json"

# Initialize Gemini AI Model
gemini_model = Gemini(id="gemini-2.0-flash-thinking-exp-1219")
agent = Agent(model=gemini_model, markdown=True)

def get_gmail_credentials():
    """Authenticate the user via OAuth and return valid credentials."""
    creds = None

    # Load previously saved credentials
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds

def get_authenticated_email(creds):
    """Retrieve the authenticated email securely."""
    if creds.id_token and "email" in creds.id_token:
        return creds.id_token["email"]

    try:
        service = build("oauth2", "v2", credentials=creds)
        user_info = service.userinfo().get().execute()
        return user_info.get("email")
    except Exception as e:
        print(f"Error fetching user email: {e}")
        return None

def generate_oauth2_string(username, access_token):
    """Generate OAuth2 authentication string for IMAP login."""
    auth_string = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode()).decode()

def fetch_wifi_reset_emails():
    """Fetch emails with the subject 'WIFI RESET' using OAuth authentication."""
    creds = get_gmail_credentials()
    
    # Get authenticated user's email
    email_address = get_authenticated_email(creds)
    if not email_address:
        print("Error: Could not retrieve the authenticated email.")
        return []

    try:
        imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
        oauth2_string = generate_oauth2_string(email_address, creds.token)
        imap_server.authenticate("XOAUTH2", lambda x: oauth2_string)
        imap_server.select("inbox")

        status, messages = imap_server.search(None, 'ALL')
        if status != "OK":
            print("No matching emails found.")
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

    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

def main():
    """Main function to authenticate, fetch, and summarize WiFi reset emails."""
    emails = fetch_wifi_reset_emails()
    if not emails:
        print("No WiFi reset emails found.")
        return

    print(f"Found {len(emails)} emails with 'WIFI RESET'.")
    for idx, msg in enumerate(emails):
        subject = decode_header(msg["Subject"])[0][0]
        print(f"\n📩 **Email Subject:** {subject}")

if __name__ == "__main__":
    main()
