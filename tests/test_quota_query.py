"""Test quota query directly."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("Testing quota query...")
print(f"Database: {DATABASE_URL.split('@')[1].split('/')[1].split('?')[0] if '@' in DATABASE_URL else 'unknown'}")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

try:
    with engine.connect() as conn:
        # Test 1: Check if tables exist
        print("\n1. Checking if tables exist...")
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('tenant_quotas', 'tenant_quota_usage')
        """))
        tables = [row[0] for row in result]
        print(f"   Found tables: {tables}")
        
        # Test 2: Query tenant_quotas
        print("\n2. Querying tenant_quotas...")
        result = conn.execute(text("SELECT * FROM tenant_quotas LIMIT 1"))
        row = result.fetchone()
        if row:
            print(f"   ✓ Found quota record: tenant_id={row[1]}")
        else:
            print("   ✗ No quota records found")
        
        # Test 3: Query tenant_quota_usage with parameters
        print("\n3. Testing quota usage query...")
        tenant_id = 'badcd123-6cc6-4011-b01b-d33d1153f10d'
        period_type = 'daily'
        period_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = conn.execute(
            text("""
                SELECT query_count, document_count, storage_bytes, 
                       active_db_connections, concurrent_queries, api_calls_count
                FROM tenant_quota_usage
                WHERE tenant_id = :tenant_id 
                AND period_type = :period_type 
                AND period_start = :period_start
            """),
            {"tenant_id": tenant_id, "period_type": period_type, "period_start": period_start}
        )
        row = result.fetchone()
        
        if row:
            print(f"   ✓ Found usage record: {row}")
        else:
            print(f"   ℹ No usage record found (this is normal for new tenants)")
            print(f"     tenant_id: {tenant_id}")
            print(f"     period_type: {period_type}")
            print(f"     period_start: {period_start}")
        
        # Test 4: Check all tenants
        print("\n4. Checking all tenants...")
        result = conn.execute(text("SELECT id, name FROM tenants LIMIT 5"))
        tenants = result.fetchall()
        print(f"   Found {len(tenants)} tenants:")
        for tenant in tenants:
            print(f"     - {tenant[0]}: {tenant[1]}")
        
        print("\n✓ All queries executed successfully!")
        print("\nThe tables exist and queries work. The issue might be:")
        print("  1. Server needs a restart to pick up new tables")
        print("  2. Connection pool needs to be refreshed")
        print("  3. SQLAlchemy metadata needs to be updated")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()