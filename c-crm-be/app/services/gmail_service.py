from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from app.models.connection import GmailConnection
from app.models.email import Email
from datetime import datetime
import json
from bs4 import BeautifulSoup

class GmailService:
    def __init__(self, connection: GmailConnection):
        # Re-inject client config if needed for refresh
        from app.core.config import settings
        
        self.creds = Credentials(
            token=connection.access_token,
            refresh_token=connection.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )
        
        self.service = build('gmail', 'v1', credentials=self.creds)

    def list_messages(self, query: str):
        """Yields message objects (id, threadId) matching query."""
        next_page_token = None
        while True:
            results = self.service.users().messages().list(
                userId='me', q=query, pageToken=next_page_token
            ).execute()
            messages = results.get('messages', [])
            for msg in messages:
                yield msg
            
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

    def get_message_detail(self, message_id: str, dump_task_id=None) -> Email:
        """Fetches and parses a single message."""
        msg = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])
        
        # Extract headers
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        to = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
        date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        
        # Parse Date (Basic attempt, might need dateutil for robustness)
        received_at = datetime.utcnow()
        try:
            # Example: "Tue, 15 Nov 1994 12:45:26 +0000"
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            # Make timezone unaware for sqlite simplicity or keep aware? 
            # SQLModel/Pydantic likes naive usually or standard ISO. 
            # Let's convert to UTC naive for simplicity
            received_at = dt.replace(tzinfo=None) # Simple strip
        except:
            pass

        # Extract Body
        body_text = ""
        body_html = ""
        
        def parse_parts(parts):
            text = ""
            html = ""
            for part in parts:
                mime_type = part.get('mimeType')
                data = part.get('body', {}).get('data', '')
                if data:
                     decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                     if mime_type == 'text/plain':
                         text += decoded
                     elif mime_type == 'text/html':
                         html += decoded
                
                if part.get('parts'):
                    t, h = parse_parts(part.get('parts'))
                    text += t
                    html += h
            return text, html

        if 'parts' in payload:
            body_text, body_html = parse_parts(payload['parts'])
        else:
            # Single part
            data = payload.get('body', {}).get('data', '')
            if data:
                decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                if payload.get('mimeType') == 'text/html':
                    body_html = decoded
                else:
                    body_text = decoded

        # Create snippet from body if msg snippet empty
        snippet = msg.get('snippet', body_text[:200])

        return Email(
            id=msg['id'],
            thread_id=msg['threadId'],
            dump_task_id=dump_task_id,
            sender=sender,
            recipients=to,
            subject=subject,
            snippet=snippet,
            body_text=body_text,
            body_html=body_html,
            received_at=received_at,
            labels=json.dumps(msg.get('labelIds', []))
        )
