"""
Gmail Fetch Service.
Handles fetching raw emails and parsing them.
"""
import base64
import logging
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

class GmailFetchService:
    def __init__(self, credentials):
        self.service = build('gmail', 'v1', credentials=credentials)

    def fetch_emails(self, query: str = None, max_results: int = 10) -> List[Dict]:
        """
        Fetch list of emails matching query.
        Query format: https://support.google.com/mail/answer/7190
        """
        try:
            logger.info(f"Fetching emails from Gmail with query: '{query}'")
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_data = []
            
            for msg in messages:
                full_msg = self.service.users().messages().get(
                    userId='me', 
                    id=msg['id'], 
                    format='full'
                ).execute()
                parsed = self._parse_email(full_msg)
                if parsed:
                    email_data.append(parsed)
                    
            return email_data
            
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            raise

    def _parse_email(self, message: Dict) -> Optional[Dict]:
        """Extract relevant fields from raw Gmail message."""
        try:
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Extract Body
            body = self._get_email_body(payload)
            
            # Clean HTML
            text_content = self._clean_html(body)
            
            return {
                "id": message['id'],
                "threadId": message['threadId'],
                "subject": subject,
                "sender": sender,
                "date": date_str,
                "snippet": message.get('snippet', ''),
                "body": text_content,
                "raw_body": body  # Keep raw if needed for advanced processing
            }
        except Exception as e:
            logger.warning(f"Failed to parse email {message.get('id')}: {e}")
            return None

    def _get_email_body(self, payload: Dict) -> str:
        """Recursively search for email body in payload parts."""
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8')
                elif part.get('mimeType') == 'text/html':
                    # Prefer HTML if available (will strip tags later) or keep looking
                    data = part['body'].get('data')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8')
                elif 'parts' in part:
                    body += self._get_email_body(part)
        else:
            # Single part email
            data = payload['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        return body

    def _clean_html(self, html_content: str) -> str:
        """Remove HTML tags and return clean text."""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator='\n').strip()
