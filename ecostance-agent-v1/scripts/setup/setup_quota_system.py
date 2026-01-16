"""Setup quota system - create tables and initialize data."""
import sqlite3
import sys

def check_table_exists(cursor, table_name):
    """Check if a table exists."""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None

def setup_quota_tables():
    """Create quota tables if they don't exist."""
    try:
        conn = sqlite3.connect('tenant_system.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        quota_table_exists = check_table_exists(cursor, 'tenant_quotas')
        usage_table_exists = check_table_exists(cursor, 'tenant_quota_usage')
        
        if quota_table_exists and usage_table_exists:
            print("✓ Quota tables already exist")
        else:
            print("Creating quota tables...")
            
            # Read and execute migration
            with open('migrations/005_create_quota_tables.sql', 'r') as f:
                sql = f.read()
            
            cursor.executescript(sql)
            conn.commit()
            
            print("✓ Quota tables created successfully")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\nDatabase tables ({len(tables)}):")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} rows")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error setting up quota tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_quota_tables()
    sys.exit(0 if success else 1)