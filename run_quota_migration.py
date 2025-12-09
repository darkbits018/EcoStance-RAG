"""Run quota tables migration."""
import sqlite3

def run_migration():
    conn = sqlite3.connect('tenant_system.db')
    cursor = conn.cursor()
    
    with open('migrations/005_create_quota_tables.sql', 'r') as f:
        sql = f.read()
    
    cursor.executescript(sql)
    conn.commit()
    conn.close()
    
    print("✓ Quota tables created successfully")

if __name__ == "__main__":
    run_migration()
