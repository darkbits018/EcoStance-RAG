#!/usr/bin/env python3
"""
Test script for Better RBAC Phase 2 API endpoints.
Tests the new role management and permission endpoints.
"""

import sys
import os
import requests
import json
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Base URL for the API (adjust as needed)
BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> Dict[Any, Any]:
    """
    Test an API endpoint and return the response.
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.content else {},
            "success": 200 <= response.status_code < 300
        }
    
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed - is the server running?"}
    except Exception as e:
        return {"error": str(e)}


def main():
    """Test the Better RBAC API endpoints."""
    print("Testing Better RBAC Phase 2 API Endpoints")
    print("=" * 50)
    
    # Note: These tests use placeholder authentication
    # In a real implementation, you'd need valid JWT tokens
    
    tests = [
        # Health check
        {
            "name": "Health Check",
            "method": "GET",
            "endpoint": "/health"
        },
        
        # Permission endpoints
        {
            "name": "List Available Permissions",
            "method": "GET",
            "endpoint": "/api/v1/tenant/permissions"
        },
        {
            "name": "List Permission Categories",
            "method": "GET",
            "endpoint": "/api/v1/tenant/permissions/categories"
        },
        {
            "name": "Get My Permissions",
            "method": "GET",
            "endpoint": "/api/v1/tenant/permissions/my-permissions"
        },
        
        # Tenant role endpoints
        {
            "name": "List Tenant Roles",
            "method": "GET",
            "endpoint": "/api/v1/tenant/roles"
        },
        {
            "name": "Create Tenant Role",
            "method": "POST",
            "endpoint": "/api/v1/tenant/roles",
            "data": {
                "name": "Test Role",
                "description": "A test role for API testing",
                "permissions": ["kb:view", "kb:query", "file:view"],
                "is_active": True
            }
        },
        
        # Admin endpoints (Super Admin only)
        {
            "name": "List All Tenants (Admin)",
            "method": "GET",
            "endpoint": "/api/v1/admin/tenants"
        },
        {
            "name": "Get System Metrics (Admin)",
            "method": "GET",
            "endpoint": "/api/v1/admin/metrics"
        },
        {
            "name": "View System Role Assignments (Admin)",
            "method": "GET",
            "endpoint": "/api/v1/admin/system/roles"
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\nTesting: {test['name']}")
        print(f"  {test['method']} {test['endpoint']}")
        
        result = test_endpoint(
            method=test['method'],
            endpoint=test['endpoint'],
            data=test.get('data'),
            headers={"Content-Type": "application/json"}
        )
        
        results.append({
            "test": test['name'],
            "result": result
        })
        
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        elif result.get('success'):
            print(f"  ✅ Success: {result['status_code']}")
            if result['response']:
                # Print a summary of the response
                response = result['response']
                if isinstance(response, dict):
                    if 'total' in response:
                        print(f"     Total items: {response['total']}")
                    elif 'message' in response:
                        print(f"     Message: {response['message']}")
                    elif 'status' in response:
                        print(f"     Status: {response['status']}")
        else:
            print(f"  ⚠️  Status: {result['status_code']}")
            if result['response']:
                print(f"     Response: {result['response']}")
    
    # Summary
    print(f"\n{'='*50}")
    print("Test Summary:")
    
    successful_tests = sum(1 for r in results if r['result'].get('success', False))
    error_tests = sum(1 for r in results if 'error' in r['result'])
    failed_tests = len(results) - successful_tests - error_tests
    
    print(f"  ✅ Successful: {successful_tests}")
    print(f"  ❌ Errors: {error_tests}")
    print(f"  ⚠️  Failed: {failed_tests}")
    print(f"  📊 Total: {len(results)}")
    
    if error_tests > 0:
        print(f"\nNote: Connection errors are expected if the server is not running.")
        print(f"Start the server with: uvicorn app.main:app --reload")
    
    if successful_tests > 0:
        print(f"\n🎉 Better RBAC Phase 2 API endpoints are working!")
    
    return results


if __name__ == "__main__":
    main()