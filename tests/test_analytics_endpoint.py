"""
Comprehensive test for the Analytics endpoint
Tests the /api/v1/usage/summary endpoint with proper authentication
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def login_super_admin(email: str, password: str):
    """Login and get JWT token"""
    login_url = f"{BASE_URL}/api/v1/auth/login"
    
    payload = {
        "email": email,
        "password": password
    }
    
    print(f"Logging in as: {email}")
    response = requests.post(login_url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def test_usage_summary(token: str, start_date: str, end_date: str):
    """Test the usage summary endpoint"""
    endpoint = f"{BASE_URL}/api/v1/usage/summary"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    print(f"\nTesting: GET {endpoint}")
    print(f"Date range: {start_date} to {end_date}")
    print("-" * 70)
    
    response = requests.get(endpoint, headers=headers, params=params)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!\n")
        print("Response Data:")
        print(json.dumps(data, indent=2))
        
        # Validate response structure
        expected_fields = {
            "total_queries": int,
            "total_documents": int,
            "total_storage_gb": (int, float),
            "active_tenants": int,
            "avg_queries_per_tenant": int,
            "avg_response_time_ms": int
        }
        
        print("\n" + "-" * 70)
        print("Field Validation:")
        all_valid = True
        for field, expected_type in expected_fields.items():
            if field in data:
                value = data[field]
                if isinstance(value, expected_type):
                    print(f"  ✅ {field}: {value} ({type(value).__name__})")
                else:
                    print(f"  ⚠️  {field}: {value} (expected {expected_type}, got {type(value).__name__})")
            else:
                print(f"  ❌ {field}: MISSING")
                all_valid = False
        
        print("-" * 70)
        if all_valid:
            print("✅ All fields present and valid!")
        else:
            print("⚠️  Some fields are missing or invalid")
            
        return True
        
    elif response.status_code == 401:
        print("❌ UNAUTHORIZED")
        print("Token may be invalid or expired")
        print(f"Response: {response.text}")
        return False
        
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def main():
    print("=" * 70)
    print("ANALYTICS ENDPOINT TEST")
    print("=" * 70)
    print()
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=2)
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️  Server responded but health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server")
        print(f"Make sure the server is running on {BASE_URL}")
        print("Run: python run_app.py")
        return
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return
    
    print()
    print("-" * 70)
    print("STEP 1: Login")
    print("-" * 70)
    
    # Get credentials
    print("\nEnter super admin credentials:")
    email = input("Email (or press Enter for default 'admin@platform.com'): ").strip()
    if not email:
        email = "admin@platform.com"
    
    password = input("Password (or press Enter for default 'admin123'): ").strip()
    if not password:
        password = "admin123"
    
    # Login
    token = login_super_admin(email, password)
    
    if not token:
        print("\n❌ Cannot proceed without valid token")
        print("\nTo create a super admin:")
        print("  python create_super_admin.py")
        return
    
    print()
    print("-" * 70)
    print("STEP 2: Test Usage Summary Endpoint")
    print("-" * 70)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Test endpoint
    success = test_usage_summary(token, start_date_str, end_date_str)
    
    print()
    print("=" * 70)
    if success:
        print("✅ TEST PASSED!")
        print("The Analytics endpoint is working correctly!")
    else:
        print("❌ TEST FAILED")
        print("Check the error messages above")
    print("=" * 70)


if __name__ == "__main__":
    main()