import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
BASE_PATH = os.path.join(os.path.dirname(__file__), 'gmail_config') + os.sep
creds = None


def _extract_body(payload):
    if not payload:
        return ''
    data = payload.get('body', {}).get('data')
    if data:
        return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
    for part in payload.get('parts', []):
        text = _extract_body(part)
        if text:
            return text
    return ''


def login():
    global creds
    token_path = BASE_PATH + 'token.json'
    creds = None
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(BASE_PATH + 'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
    return creds


def logout():
    token_path = BASE_PATH + 'token.json'
    if os.path.exists(token_path):
        os.remove(token_path)


def my_emails(antal):
    global creds
    service = build('gmail', 'v1', credentials=creds)
    result = service.users().messages().list(userId='me', maxResults=antal).execute()
    messages = []
    
    for msg in result.get('messages', []):
        data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = {h['name']: h['value'] for h in data.get('payload', {}).get('headers', [])}
        messages.append({
            'id': msg['id'],
            'sender': headers.get('From'),
            'subject': headers.get('Subject'),
            'body': _extract_body(data.get('payload', {}))
        })
    
    return messages

def get_latest_message_id_from_gmail():
    global creds
    service = build('gmail','v1', credentials=creds)
    result = service.users().messages().list(userId='me',maxResults=1).execute()
    messages = result.get('messages',[])
    if not messages:
        return None
    return messages[0]['id']