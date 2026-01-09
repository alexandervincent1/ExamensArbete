import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
base_dir = os.path.dirname(__file__)
BASE_PATH = os.path.join(base_dir, 'gmail_config') + os.sep
creds_path = os.path.join(BASE_PATH, 'credentials.json')

_creds = None


def _extract_body_from_payload(payload):
    """Hämta text från Gmail payload (text/plain eller text/html)."""
    if not payload:
        return ''
    body = payload.get('body', {}).get('data')
    if body:
        try:
            padded = body + '=' * (-len(body) % 4)
            decoded = base64.urlsafe_b64decode(padded)
            return decoded.decode('utf-8', errors='replace')
        except Exception:
            return ''
    parts = payload.get('parts') or []
    for part in parts:
        txt = _extract_body_from_payload(part)
        if txt:
            return txt
    return ''


def login():
    global _creds
    creds = None  
    token_path = os.path.join(BASE_PATH, 'token.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and getattr(creds, 'refresh_token', None):
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(BASE_PATH, exist_ok=True)
        with open(token_path, 'w', encoding='utf-8') as token_file:
            token_file.write(creds.to_json())
    
    _creds = creds
    return creds
    

def logout():
    os.remove("/Users/master/Desktop/ExamensArbete/src/backend/gmail_config/token.json")

    
def my_emails(antal):
    """Hämta ett visst antal mail från Gmail."""
    global _creds
    
    messages_out = []
    try:
        service = build('gmail', 'v1', credentials=_creds)
        page_token = None

        while True:
            result = service.users().messages().list(userId='me', pageToken=page_token).execute()
            messages = result.get('messages', []) or []

            for msg in messages:
                if len(messages_out) >= antal:
                    return messages_out

                msg_id = msg.get('id')
                txt = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                payload = txt.get('payload', {}) or {}
                headers = payload.get('headers', []) or []

                subject, sender = None, None
                for h in headers:
                    if h.get('name') == 'Subject':
                        subject = h.get('value')
                    elif h.get('name') == 'From':
                        sender = h.get('value')

                body_text = _extract_body_from_payload(payload)
                messages_out.append({
                    'id': msg_id,
                    'sender': sender,
                    'subject': subject,
                    'body': body_text 
                })

            page_token = result.get('nextPageToken')
            if not page_token:
                break

    except HttpError as error:
        print("Error:", error)

    return messages_out



if __name__ == "__main__":
    my_emails()
    _extract_body_from_payload()