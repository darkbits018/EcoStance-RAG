"""Check PostgreSQL tables and schemas."""
import os
from dotenv import load_dotenv
import psycopg2

def check_tables():
    """Check what tables exist in PostgreSQL."""
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL not found")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("="*60)
        print("CHECKING POSTGRESQL DATABASE")
        print("="*60)
        
        # Check current schema
        cursor.execute("SELECT current_schema()")
        current_schema = cursor.fetchone()[0]
        print(f"\nCurrent schema: {current_schema}")
        
        # Check search path
        cursor.execute("SHOW search_path")
        search_path = cursor.fetchone()[0]
        print(f"Search path: {search_path}")
        
        # List all schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            ORDER BY schema_name
        """)
        schemas = [row[0] for row in cursor.fetchall()]
        print(f"\nAvailable schemas: {', '.join(schemas)}")
        
        # Check for quota tables in all schemas
        print("\n" + "="*60)
        print("SEARCHING FOR QUOTA TABLES IN ALL SCHEMAS")
        print("="*60)
        
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('tenant_quotas', 'tenant_quota_usage')
            ORDER BY table_schema, table_name
        """)
        quota_tables = cursor.fetchall()
        
        if quota_tables:
            print("\nFound quota tables:")
            for schema, table in quota_tables:
                cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
                count = cursor.fetchone()[0]
                print(f"  ✓ {schema}.{table}: {count} rows")
        else:
            print("\n✗ No quota tables found in any schema!")
        
        # List all tables in public schema
        print("\n" + "="*60)
        print("ALL TABLES IN PUBLIC SCHEMA")
        print("="*60)
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\nTotal tables: {len(tables)}\n")
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM public."{table[0]}"')
            count = cursor.fetchone()[0]
            marker = "✓" if table[0] in ['tenant_quotas', 'tenant_quota_usage'] else " "
            print(f"{marker} {table[0]}: {count} rows")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_tables()
