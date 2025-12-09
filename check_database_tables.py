"""Check database tables and their structure."""
import sqlite3

def check_database():
    """Display database structure and status."""
    try:
        conn = sqlite3.connect('tenant_system.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("=" * 60)
        print(f"DATABASE: tenant_system.db")
        print("=" * 60)
        print(f"\nTotal tables: {len(tables)}\n")
        
        for table in tables:
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            print(f"📊 {table}")
            print(f"   Rows: {count}")
            print(f"   Columns: {len(columns)}")
            
            if count > 0 and count <= 5:
                # Show sample data for small tables
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                if rows:
                    print(f"   Sample: {rows[0][:3] if len(rows[0]) > 3 else rows[0]}")
            print()
        
        # Check for quota tables specifically
        print("-" * 60)
        print("QUOTA SYSTEM STATUS:")
        print("-" * 60)
        
        quota_tables = ['tenant_quotas', 'tenant_quota_usage']
        for table in quota_tables:
            if table in tables:
                print(f"✓ {table} exists")
            else:
                print(f"✗ {table} MISSING - Run setup_quota_system.py")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
