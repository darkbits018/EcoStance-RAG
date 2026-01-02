#!/usr/bin/env python3
"""
Test script to verify API endpoints with proper authentication headers.
"""

import sys
import os
import requests
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://localhost:8000"

def test_with_jwt_token():
    """Test API endpoints using JWT token (proper authentication)."""
    print("Testing API endpoints with JWT token")
    print("=" * 50)
    
    # Use the JWT token for the admin user
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWFlZTQwYmQtZDVmZS00NjEwLWJhMTUtMTJkYzgxNDRiNDk5IiwidGVuYW50X2lkIjoiNDk3NDcyMzEtN2M1YS00YWE4LTkwYjQtZmYzNGZhN2RkN2I5IiwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJ0ZW5hbnRfYWRtaW4iLCJleHAiOjE3NjcxNzEzNDYsImlhdCI6MTc2NzE2Nzc0NiwidHlwZSI6ImFjY2VzcyJ9.juM9HObEiPBSplSupL-OI_4DQQV5cxc-B4EJxFdpYy4"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "/api/v1/tenant/debug/current-user",
        "/api/v1/tenant/permissions/my-permissions",
        "/api/v1/tenant/permissions/categories", 
        "/api/v1/tenant/roles",
        "/api/v1/tenant/users"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting: GET {endpoint}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                if isinstance(data, dict):
                    if 'debug' in data and data['debug']:
                        print(f"   Debug info:")
                        print(f"   - User ID: {data.get('current_user', {}).get('user_id', 'Unknown')}")
                        print(f"   - Tenant ID: {data.get('current_user', {}).get('tenant_id', 'Unknown')}")
                        print(f"   - TenantUser found: {data.get('tenant_user_found', False)}")
                        print(f"   - Total permissions: {data.get('total_permissions', 0)}")
                        print(f"   - Has TENANT_VIEW: {data.get('has_tenant_view', False)}")
                        print(f"   - Has TENANT_MANAGE_USERS: {data.get('has_tenant_manage_users', False)}")
                        if data.get('role_info'):
                            role = data['role_info']
                            print(f"   - Role: {role.get('role_name', 'Unknown')} ({role.get('type', 'Unknown')})")
                        if data.get('error'):
                            print(f"   - Error: {data['error']}")
                    elif 'total' in data:
                        print(f"   Total items: {data['total']}")
                    elif 'permissions' in data:
                        print(f"   Permissions: {len(data['permissions'])}")
                    elif 'roles' in data:
                        print(f"   Roles: {len(data['roles'])}")
                    elif 'users' in data:
                        print(f"   Users: {len(data['users'])}")
            else:
                print(f"❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Message: {error_data.get('message', 'Unknown error')}")
                    if 'detail' in error_data:
                        print(f"   Detail: {error_data['detail']}")
                except:
                    print(f"   Raw response: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is the server running?")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_jwt_token()