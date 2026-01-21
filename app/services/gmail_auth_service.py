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
from app.models.tenant_user import TenantUser

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

    def get_authorization_url(self, tenant_id: str, user_id: Optional[str] = None) -> str:
        """
        Generate the Google OAuth authorization URL.
        State parameter includes tenant_id and user_id to identify return.
        """
        flow = Flow.from_client_config(
            self._get_client_config(),
            scopes=SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        
        # State can be a JSON or delimited string
        state_str = f"{tenant_id}:{user_id}" if user_id else tenant_id
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state_str,
            prompt='consent' # Force consent to ensure refresh token is returned
        )
        return authorization_url

    def exchange_code_for_token(self, code: str, tenant_id: str, user_id: Optional[str] = None) -> Dict:
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
            
            # Save credentials
            self._save_credentials(tenant_id, credentials, user_id)
            
            return {
                "message": "Successfully connected Gmail",
                "email": self._get_user_email(credentials)
            }
        except Exception as e:
            logger.error(f"Failed to exchange token: {str(e)}")
            raise

    def get_credentials(self, tenant_id: str, user_id: Optional[str] = None) -> Optional[Credentials]:
        """
        Retrieve and refresh credentials for a tenant or specific user.
        """
        if user_id:
            user = self.db.query(TenantUser).filter(
                TenantUser.tenant_id == tenant_id,
                TenantUser.user_id == user_id
            ).first()
            if not user or not user.gmail_config or 'oauth' not in user.gmail_config:
                return None
            creds_data = user.gmail_config['oauth']
        else:
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant or not tenant.gmail_config or 'oauth' not in tenant.gmail_config:
                return None
            creds_data = tenant.gmail_config['oauth']
            
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save updated tokens
            self._save_credentials(tenant_id, creds, user_id)
            
        return creds

    def _save_credentials(self, tenant_id: str, credentials: Credentials, user_id: Optional[str] = None):
        """
        Persist credentials to Database (should be encrypted in production).
        """
        creds_json = json.loads(credentials.to_json())
        
        if user_id:
            user = self.db.query(TenantUser).filter(
                TenantUser.tenant_id == tenant_id,
                TenantUser.user_id == user_id
            ).first()
            if not user:
                raise ValueError("User not found")
            
            config = dict(user.gmail_config) if user.gmail_config else {}
            config['oauth'] = creds_json
            config['enabled'] = True
            user.gmail_config = config
        else:
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                raise ValueError("Tenant not found")
                
            config = dict(tenant.gmail_config) if tenant.gmail_config else {}
            config['oauth'] = creds_json
            config['enabled'] = True
            tenant.gmail_config = config
            
        self.db.commit()

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
