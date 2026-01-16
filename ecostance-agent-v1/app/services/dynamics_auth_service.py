"""
Dynamics 365 Authentication Service.
Handles obtaining OAuth tokens via Client Credentials flow.
"""
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)

class DynamicsAuthService:
    def __init__(self, db: Session):
        self.db = db

    def save_config(self, tenant_id: str, config: Dict):
        """Save Dynamics configuration to the tenant."""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")
        
        # In a real app, encrypt client_secret here!
        current_config = dict(tenant.dynamics_config) if tenant.dynamics_config else {}
        current_config.update(config)
        
        tenant.dynamics_config = current_config
        self.db.commit()
        self.db.refresh(tenant)

    def get_token(self, tenant_id: str) -> str:
        """Get a valid access token, refreshing if necessary."""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant or not tenant.dynamics_config:
            raise ValueError("Dynamics 365 not configured for this tenant")
        
        config = tenant.dynamics_config
        
        # Check if we have a valid cached token
        # (Simplified caching mechanism using the JSON config itself)
        if 'access_token' in config and 'expires_at' in config:
            expires_at = datetime.fromisoformat(config['expires_at'])
            if expires_at > datetime.utcnow() + timedelta(minutes=5):
                return config['access_token']
        
        # Request new token
        return self._fetch_new_token(tenant, config)

    def _fetch_new_token(self, tenant: Tenant, config: Dict) -> str:
        """Fetch a new token from Microsoft Identity Platform."""
        ms_tenant_id = config.get('tenant_id')
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        resource_url = config.get('resource_url')
        
        if not all([ms_tenant_id, client_id, client_secret, resource_url]):
            raise ValueError("Incomplete Dynamics configuration")
            
        token_url = f"https://login.microsoftonline.com/{ms_tenant_id}/oauth2/v2.0/token"
        
        payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': f"{resource_url}/.default"
        }
        
        try:
            response = requests.post(token_url, data=payload)
            response.raise_for_status()
            token_data = response.json()
            
            access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3599)
            
            # Save valid token back to DB to cache it
            expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
            
            # Update config securely
            new_config = dict(tenant.dynamics_config)
            new_config['access_token'] = access_token
            new_config['expires_at'] = expires_at.isoformat()
            
            tenant.dynamics_config = new_config
            self.db.commit()
            
            return access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate with Dynamics: {e}")
            if e.response:
                logger.error(f"Response: {e.response.text}")
            raise ValueError(f"Authentication failed: {str(e)}")
