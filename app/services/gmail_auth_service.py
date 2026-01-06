"""
Gmail Authentication Service.
Handles OAuth flow, token management, and credential storage.
"""
import os
import json
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from app.models.tenant import Tenant
# Assuming VaultService exists or we use direct storage for now
# from app.services.vault_service import VaultService 

logger = logging.getLogger(__name__)

# Scopes required for Gmail access
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

class GmailAuthService:
    def __init__(self, db: Session):
        self.db = db
        # Load client secrets from env or file
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5173/gmail/callback")
        
        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not configured.")

    def get_authorization_url(self, tenant_id: str) -> str:
        """
        Generate the Google OAuth authorization URL.
        State parameter includes tenant_id to identify return.
        """
        flow = Flow.from_client_config(
            self._get_client_config(),
            scopes=SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=tenant_id,
            prompt='consent' # Force consent to ensure refresh token is returned
        )
        return authorization_url

    def exchange_code_for_token(self, code: str, tenant_id: str) -> Dict:
        """
        Exchange authorization code for credentials and save them.
        """
        try:
            flow = Flow.from_client_config(
                self._get_client_config(),
                scopes=SCOPES
            )
            flow.redirect_uri = self.redirect_uri
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            # Save credentials to tenant
            self._save_credentials(tenant_id, credentials)
            
            return {
                "message": "Successfully connected Gmail",
                "email": self._get_user_email(credentials)
            }
        except Exception as e:
            logger.error(f"Failed to exchange token: {str(e)}")
            raise

    def get_credentials(self, tenant_id: str) -> Optional[Credentials]:
        """
        Retrieve and refresh credentials for a tenant.
        """
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant or not tenant.gmail_config or 'oauth' not in tenant.gmail_config:
            return None
            
        creds_data = tenant.gmail_config['oauth']
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save updated tokens
            self._save_credentials(tenant_id, creds)
            
        return creds

    def _save_credentials(self, tenant_id: str, credentials: Credentials):
        """
        Persist credentials to Database (should be encrypted in production).
        """
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")
            
        creds_json = json.loads(credentials.to_json())
        
        # Update gmail_config
        config = dict(tenant.gmail_config) if tenant.gmail_config else {}
        config['oauth'] = creds_json
        config['enabled'] = True
        
        tenant.gmail_config = config
        self.db.commit()
        self.db.refresh(tenant)

    def _get_client_config(self) -> Dict:
        """Construct client config for Flow."""
        return {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
    
    def _get_user_email(self, credentials) -> str:
        """Fetch user email for confirmation."""
        from googleapiclient.discovery import build
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info.get('email')
