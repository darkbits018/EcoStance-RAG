"""
Apply LLM Usage Tracking Migration
Run this script to create the llm_usage table
"""
import sqlite3
import psycopg2
import os
from pathlib import Path

def apply_sqlite_migration(db_path: str):
    """Apply migration to SQLite database"""
    print(f"Applying migration to SQLite database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. Skipping.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute migration
    migration_file = Path(__file__).parent / "010_create_llm_usage_table.sql"
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    try:
        cursor.executescript(migration_sql)
        conn.commit()
        print(f"✓ Migration applied successfully to {db_path}")
    except Exception as e:
        print(f"✗ Error applying migration to {db_path}: {e}")
        conn.rollback()
    finally:
        conn.close()

def apply_postgres_migration(connection_string: str):
    """Apply migration to PostgreSQL database"""
    print(f"Applying migration to PostgreSQL database")
    
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Read and execute migration
        migration_file = Path(__file__).parent / "010_create_llm_usage_table_postgres.sql"
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        cursor.execute(migration_sql)
        conn.commit()
        print("✓ Migration applied successfully to PostgreSQL")
    except Exception as e:
        print(f"✗ Error applying migration to PostgreSQL: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("LLM Usage Tracking Migration")
    print("=" * 60)
    
    # Apply to SQLite databases
    sqlite_databases = [
        "tenant_system.db",
        "QuickShip.db",
    ]
    
    for db in sqlite_databases:
        apply_sqlite_migration(db)
    
    # Apply to PostgreSQL if configured
    postgres_url = os.getenv("DATABASE_URL")
    if postgres_url:
        print("\nPostgreSQL connection found in environment")
        apply_postgres = input("Apply migration to PostgreSQL? (y/n): ")
        if apply_postgres.lower() == 'y':
            apply_postgres_migration(postgres_url)
    else:
        print("\nNo PostgreSQL connection found (DATABASE_URL not set)")
    
    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)
