"""
Test script for the /api/v1/usage/summary endpoint
"""
import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/v1/usage/summary"

# Super admin token (you'll need to replace this with an actual token)
# For testing, you can get a token by logging in as the super admin
SUPER_ADMIN_TOKEN = "your-super-admin-token-here"

def test_usage_summary():
    """Test the usage summary endpoint"""
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Format dates as YYYY-MM-DD
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {SUPER_ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "start_date": start_date_str,
        "end_date": end_date_str
    }
    
    print(f"Testing endpoint: {ENDPOINT}")
    print(f"Date range: {start_date_str} to {end_date_str}")
    print("-" * 60)
    
    try:
        response = requests.get(ENDPOINT, headers=headers, params=params)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 60)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print("\nResponse Data:")
            print(json.dumps(data, indent=2))
            
            # Validate response structure
            expected_fields = [
                "total_queries",
                "total_documents", 
                "total_storage_gb",
                "active_tenants",
                "avg_queries_per_tenant",
                "avg_response_time_ms"
            ]
            
            print("\n" + "-" * 60)
            print("Field Validation:")
            for field in expected_fields:
                if field in data:
                    print(f"  ✅ {field}: {data[field]}")
                else:
                    print(f"  ❌ {field}: MISSING")
                    
        elif response.status_code == 401:
            print("❌ UNAUTHORIZED")
            print("Please update SUPER_ADMIN_TOKEN with a valid token")
            print(f"Response: {response.text}")
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Usage Summary Endpoint Test")
    print("=" * 60)
    print()
    
    # Check if token is set
    if SUPER_ADMIN_TOKEN == "your-super-admin-token-here":
        print("⚠️  WARNING: SUPER_ADMIN_TOKEN not set!")
        print()
        print("To get a token:")
        print("1. Start the server: python run_app.py")
        print("2. Login as super admin to get a JWT token")
        print("3. Update SUPER_ADMIN_TOKEN in this script")
        print()
        print("Proceeding with test anyway (will get 401)...")
        print()
    
    test_usage_summary()