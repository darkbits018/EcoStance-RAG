import logging
import httpx
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class CustomCRMFetchService:
    """
    Service to fetch emails from the Custom CRM API.
    """
    def __init__(self, base_url: str = "http://localhost:8001/api/v1"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)

    def fetch_emails(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch all available emails from the CRM by paginating through the API.
        
        Args:
            limit: Number of items per page.
            
        Returns:
            List of email dictionaries as returned by the CRM.
        """
        all_emails = []
        page = 1
        
        try:
            while True:
                logger.info(f"Fetching Custom CRM emails page {page}...")
                response = self.client.get(f"/emails/", params={"page": page, "limit": limit})
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch emails from Custom CRM: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                if not data:
                    break
                
                all_emails.extend(data)
                
                # If we got fewer than the limit, we've reached the end
                if len(data) < limit:
                    break
                
                page += 1
                
            return all_emails
            
        except Exception as e:
            logger.error(f"Error fetching from Custom CRM: {e}")
            raise e
        finally:
            self.client.close()

    def get_email_details(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch full details for a single email if needed (e.g. if list view is truncated).
        """
        try:
            response = self.client.get(f"/emails/{email_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error fetching email details for {email_id}: {e}")
            return None
