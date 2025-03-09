import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.send']


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


def send_acknowledgment(service, recipient):
    message = {
        'raw': base64.urlsafe_b64encode(
            f"From: me\nTo: {recipient}\nSubject: Acknowledgment - WIFI RESET\n\nYour email has been acknowledged! Here's a test reset code: 123456"
            .encode("utf-8")
        ).decode("utf-8")
    }
    service.users().messages().send(userId='me', body=message).execute()
    print(f"Acknowledgment sent to {recipient}")


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
            send_acknowledgment(service, sender)


if __name__ == "__main__":
    service = authenticate_gmail()
    fetch_wifi_reset_emails(service)