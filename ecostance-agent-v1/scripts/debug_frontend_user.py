#!/usr/bin/env python3
"""
Debug script to check what user the frontend is actually using.
"""

import sys
import os
import requests

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://localhost:8000"

def debug_frontend_auth():
    """Debug what user the frontend is actually authenticated as."""
    print("Debugging Frontend Authentication")
    print("=" * 50)
    
    # Try to simulate what the frontend is doing
    # Based on the error, it seems like the frontend is sending some kind of auth
    
    # Test 1: No auth (should get 401)
    print("\n1. Testing with no authentication:")
    response = requests.get(f"{BASE_URL}/api/v1/tenant/debug/current-user")
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        try:
            error = response.json()
            print(f"   Error: {error.get('message', 'Unknown')}")
        except:
            print(f"   Raw: {response.text}")
    
    # Test 2: With X-Tenant-ID header (what frontend might be doing)
    print("\n2. Testing with X-Tenant-ID header:")
    headers = {"X-Tenant-ID": "49747231-7c5a-4aa8-90b4-ff34fa7dd7b9"}
    response = requests.get(f"{BASE_URL}/api/v1/tenant/debug/current-user", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   User ID: {data.get('current_user', {}).get('user_id', 'Unknown')}")
        print(f"   Tenant ID: {data.get('current_user', {}).get('tenant_id', 'Unknown')}")
        print(f"   Has TENANT_VIEW: {data.get('has_tenant_view', False)}")
        print(f"   Total permissions: {data.get('total_permissions', 0)}")
    else:
        try:
            error = response.json()
            print(f"   Error: {error.get('message', 'Unknown')}")
            print(f"   Detail: {error.get('detail', 'No detail')}")
        except:
            print(f"   Raw: {response.text}")
    
    # Test 3: Check if there are any cookies or session data
    print("\n3. Testing common session scenarios:")
    
    # Try different tenant IDs that might exist
    tenant_ids = [
        "49747231-7c5a-4aa8-90b4-ff34fa7dd7b9",  # Default Organization
        "platform-admin-tenant-id",              # Platform Admin (non-UUID)
        "da39648f-1bbe-402c-968d-6af62a65ec61",  # Test Company
    ]
    
    for tenant_id in tenant_ids:
        print(f"\n   Testing tenant: {tenant_id}")
        headers = {"X-Tenant-ID": tenant_id}
        response = requests.get(f"{BASE_URL}/api/v1/tenant/debug/current-user", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User found: {data.get('current_user', {}).get('user_id', 'Unknown')}")
            print(f"   ✅ Permissions: {data.get('total_permissions', 0)}")
            break
        elif response.status_code == 400:
            print(f"   ❌ Invalid tenant ID format")
        elif response.status_code == 401:
            print(f"   ❌ Not authenticated")
        else:
            try:
                error = response.json()
                print(f"   ❌ Error: {error.get('message', 'Unknown')}")
            except:
                print(f"   ❌ Status: {response.status_code}")

if __name__ == "__main__":
    debug_frontend_auth()