"""
Dynamics 365 Fetch Service.
Handles fetching Email activities from Dataverse/Dynamics CRM.
"""
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DynamicsFetchService:
    def __init__(self, resource_url: str, access_token: str):
        self.base_url = resource_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Prefer': 'odata.include-annotations="*"'
        }

    def fetch_recent_emails(self, lookback_minutes: int = 60) -> List[Dict]:
        """
        Fetch emails created/modified in the last N minutes.
        Only fetches 'Inbound' emails (directioncode=1) to avoid bot loops.
        """
        since = (datetime.utcnow() - timedelta(minutes=lookback_minutes)).isoformat() + 'Z'
        
        # Select fields: subject, body, sender, createdon
        # Filter: createdon > since AND directioncode eq true (Incoming)
        # Note: directioncode: True=Incoming, False=Outgoing
        
        query = (
            f"/api/data/v9.2/emails?"
            f"$select=activityid,subject,description,sender,to,createdon,directioncode&"
            f"$filter=createdon gt {since} and directioncode eq true&"
            f"$orderby=createdon desc"
        )
        
        return self._execute_query(query)

    def fetch_tracked_emails(self) -> List[Dict]:
        """
        Fetch emails that were explicitly 'tracked' recently.
        This often relies on the 'regardingobjectid' being set or specific categories.
        For now, returns all incoming emails as a baseline.
        """
        # Placeholder for specific 'Flagged' logic if using a custom field.
        return self.fetch_recent_emails(lookback_minutes=60)

    def _execute_query(self, query_path: str) -> List[Dict]:
        url = f"{self.base_url}{query_path}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            emails = []
            for item in data.get('value', []):
                emails.append(self._parse_email(item))
                
            return emails
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch emails from Dynamics: {e}")
            raise

    def _parse_email(self, item: Dict) -> Dict:
        """Parse Dataverse JSON into a standard dict."""
        body_html = item.get('description', '')
        text_content = self._clean_html(body_html) if body_html else ""
        
        return {
            "id": item.get('activityid'),
            "subject": item.get('subject', 'No Subject'),
            "sender": item.get('sender', 'Unknown'), # This is often a complex object in Dataverse
            "created_at": item.get('createdon'),
            "body": text_content,
            "raw_body": body_html,
            "source": "dynamics"
        }

    def _clean_html(self, html_content: str) -> str:
        """Remove HTML tags."""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator='\n').strip()
