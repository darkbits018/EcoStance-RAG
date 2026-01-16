#!/usr/bin/env python3
"""
Fix chat configuration to remove deleted KBs and use correct KB name.
"""
import sys
import os
sys.path.insert(0, '.')

from app.db.database import SessionLocal
from app.models.public_chat import PublicChatConfig
import json

def fix_chat_config():
    """Fix the chat configuration."""
    db = SessionLocal()
    
    try:
        # Get CertifyDigital tenant config
        tenant_id = "badcd123-6cc6-4011-b01b-d33d1153f10d"
        config = db.query(PublicChatConfig).filter(
            PublicChatConfig.tenant_id == tenant_id
        ).first()
        
        if config:
            print(f"Current allowed_kbs: {config.allowed_kbs}")
            
            # Update to only include the existing KB with correct name
            config.allowed_kbs = json.dumps(["multilanguage-test"])
            
            db.commit()
            print(f"✅ Updated chat config for CertifyDigital")
            print(f"New allowed_kbs: {config.allowed_kbs}")
        else:
            print("❌ No chat config found for CertifyDigital tenant")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_chat_config()