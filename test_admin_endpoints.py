"""
Test script to verify all Super Admin API endpoints are registered.
"""
from app.main import app
from fastapi.routing import APIRoute

def test_admin_endpoints():
    """Check that all required admin endpoints are registered."""
    
    required_endpoints = [
        # Dashboard
        ("GET", "/api/v1/admin/dashboard/summary"),
        
        # Tenant Management
        ("GET", "/api/v1/admin/tenants/search"),
        ("GET", "/api/v1/tenants"),
        ("GET", "/api/v1/tenants/{tenant_id}"),
        ("POST", "/api/v1/tenants/register"),
        ("PUT", "/api/v1/tenants/{tenant_id}"),
        ("DELETE", "/api/v1/admin/tenants/{tenant_id}"),
        ("POST", "/api/v1/admin/tenants/{tenant_id}/suspend"),
        ("POST", "/api/v1/admin/tenants/{tenant_id}/reactivate"),
        ("PATCH", "/api/v1/admin/tenants/{tenant_id}/tier"),
        ("GET", "/api/v1/admin/tenants/{tenant_id}/activity"),
        
        # System Health
        ("GET", "/api/v1/admin/health/system"),
        
        # Quota Management
        ("GET", "/api/v1/admin/quotas/templates"),
        ("PUT", "/api/v1/admin/quotas/templates/{tier}"),
        ("PUT", "/api/v1/admin/quotas/{tenant_id}"),
        
        # Audit Logs
        ("GET", "/api/v1/admin/audit-logs"),
        ("GET", "/api/v1/admin/audit-logs/{log_id}"),
        
        # Maintenance
        ("POST", "/api/v1/admin/cleanup/sessions"),
        ("POST", "/api/v1/admin/cleanup/temp-files"),
        ("POST", "/api/v1/admin/cleanup/audit-logs"),
        ("POST", "/api/v1/admin/cleanup/all"),
        
        # Settings
        ("GET", "/api/v1/admin/settings"),
        ("PUT", "/api/v1/admin/settings"),
    ]
    
    # Get all registered routes
    registered_routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            for method in route.methods:
                registered_routes.append((method, route.path))
    
    print("=" * 80)
    print("SUPER ADMIN API ENDPOINT VERIFICATION")
    print("=" * 80)
    print()
    
    missing = []
    found = []
    
    for method, path in required_endpoints:
        # Normalize path for comparison (handle path parameters and trailing slashes)
        normalized_path = path.replace("{tenant_id}", "{id}").replace("{log_id}", "{id}").replace("{tier}", "{id}")
        
        # Check if endpoint exists
        endpoint_found = False
        for reg_method, reg_path in registered_routes:
            reg_normalized = reg_path.replace("{tenant_id}", "{id}").replace("{log_id}", "{id}").replace("{tier}", "{id}")
            # Handle trailing slashes
            if method == reg_method and (
                path == reg_path or 
                normalized_path == reg_normalized or
                path.rstrip('/') == reg_path.rstrip('/') or
                normalized_path.rstrip('/') == reg_normalized.rstrip('/')
            ):
                endpoint_found = True
                break
        
        if endpoint_found:
            found.append((method, path))
            print(f"✅ {method:6} {path}")
        else:
            missing.append((method, path))
            print(f"❌ {method:6} {path}")
    
    print()
    print("=" * 80)
    print(f"SUMMARY: {len(found)}/{len(required_endpoints)} endpoints found")
    print("=" * 80)
    
    if missing:
        print()
        print("Missing endpoints:")
        for method, path in missing:
            print(f"  - {method} {path}")
        return False
    else:
        print()
        print("🎉 All required Super Admin API endpoints are registered!")
        return True


if __name__ == "__main__":
    success = test_admin_endpoints()
    exit(0 if success else 1)
