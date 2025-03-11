import os
import base64
import random
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from agno.agent import Agent
from agno.models.google import Gemini

SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.send']

os.environ["GOOGLE_API_KEY"] = ""
os.environ["AGNO_API_KEY"] = ""

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def get_email_body(payload):
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'body' in part:
                body = part['body'].get('data', '')
                break
    else:
        body = payload['body'].get('data', '')

    if body:
        return base64.urlsafe_b64decode(body).decode('utf-8')
    return "No body content found."


def extract_relevant_info(email_content):
    agent = Agent(model=Gemini(id="gemini-2.0-flash-thinking-exp-1219"))
    task = (
        f"Extract the following details from the email: Name, Roll Number, and Reset Information.\n\n"
        f"Email Content: {email_content}"
    )
    
    try:
        print("Running agent to extract info...")
        response = agent.run(task)
        if response is None:
            return "Error: Agent returned no response. Check your model or API key."
        if not isinstance(response, str):
            return "Error: Unexpected response format from agent."
        return response
    except Exception as e:
        return f"Error while extracting info: {str(e)}"


def generate_random_code():
    return str(random.randint(100000, 999999))


def send_acknowledgment(service, recipient):
    reset_code = generate_random_code()
    message_body = (
        f"From: me\n"
        f"To: {recipient}\n"
        f"Subject: Acknowledgment - WIFI RESET\n\n"
        f"Your email has been acknowledged!\n\n"
        f"Here is your reset code: {reset_code}\n\n"
        f"Best,\nSupport Team"
    )
    
    message = {
        'raw': base64.urlsafe_b64encode(message_body.encode("utf-8")).decode("utf-8")
    }
    service.users().messages().send(userId='me', body=message).execute()
    print(f"Acknowledgment sent to {recipient} with reset code {reset_code}")


def fetch_wifi_reset_emails(service):
    results = service.users().messages().list(userId='me', q='subject:"WIFI RESET" -in:sent').execute()
    messages = results.get('messages', [])

    if not messages:
        print("No WIFI RESET emails found.")
        return

    for msg in messages:
        msg_id = msg['id']
        message = service.users().messages().get(userId='me', id=msg_id).execute()

        payload = message['payload']
        headers = payload['headers']
        sender = None

        for header in headers:
            if header['name'] == 'Subject':
                print(f"Subject: {header['value']}")
            if header['name'] == 'From':
                sender = header['value']

        body = get_email_body(payload)
        print(f"Email content: {body}")

        if sender:
            print("Sending acknowledgment with reset code...")
            send_acknowledgment(service, sender)


if __name__ == "__main__":
    service = authenticate_gmail()
    fetch_wifi_reset_emails(service)
