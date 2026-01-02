#!/usr/bin/env python3
"""
Generate a JWT token for testing API endpoints.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.auth.jwt_handler import create_access_token

def generate_token():
    """Generate a JWT token for the admin user."""
    
    # User data from the database query
    user_data = {
        "user_id": "aaee40bd-d5fe-4610-ba15-12dc8144b499",
        "tenant_id": "49747231-7c5a-4aa8-90b4-ff34fa7dd7b9",
        "email": "admin@example.com",
        "role": "tenant_admin"
    }
    
    # Create token with 1 hour expiry
    token = create_access_token(
        data=user_data,
        expires_delta=timedelta(hours=1)
    )
    
    print("Generated JWT Token:")
    print("=" * 50)
    print(token)
    print("\n" + "=" * 50)
    print("Use this token in Authorization header as:")
    print(f"Authorization: Bearer {token}")
    print("\nOr test with curl:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/tenant/permissions/my-permissions')
    
    return token

if __name__ == "__main__":
    generate_token()