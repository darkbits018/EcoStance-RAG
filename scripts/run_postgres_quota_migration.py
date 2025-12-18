"""Run quota tables migration on PostgreSQL."""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

def run_migration():
    """Create quota tables in PostgreSQL."""
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL not found in .env file")
        return False
    
    print(f"Connecting to PostgreSQL...")
    print(f"Database: {database_url.split('@')[1].split('/')[1].split('?')[0] if '@' in database_url else 'unknown'}")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✓ Connected to PostgreSQL")
        
        # Check if tables already exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('tenant_quotas', 'tenant_quota_usage')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if len(existing_tables) == 2:
            print("✓ Quota tables already exist")
            print("  - tenant_quotas")
            print("  - tenant_quota_usage")
        else:
            print(f"\nCreating quota tables...")
            
            # Read and execute migration
            with open('migrations/005_create_quota_tables_postgres.sql', 'r') as f:
                sql_script = f.read()
            
            cursor.execute(sql_script)
            conn.commit()
            
            print("✓ Quota tables created successfully")
            print("  - tenant_quotas")
            print("  - tenant_quota_usage")
        
        # Verify and show table info
        print("\n" + "="*60)
        print("QUOTA TABLES STATUS:")
        print("="*60)
        
        for table in ['tenant_quotas', 'tenant_quota_usage']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✓ {table}: {count} rows")
        
        # Show all tables in database
        print("\n" + "="*60)
        print("ALL TABLES IN DATABASE:")
        print("="*60)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} rows")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Migration completed successfully!")
        print("\nNext step: Restart your FastAPI server")
        return True
        
    except Exception as e:
        print(f"\n✗ Error running migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)