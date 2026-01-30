"""Check database tables and their structure for local SQLite."""
import sqlite3

def check_database():
    """Display database structure and status."""
    try:
        conn = sqlite3.connect('QuickShip.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("=" * 60)
        print(f"DATABASE: QuickShip.db (Testing)")
        print("=" * 60)
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"📊 {table}: {count} rows")
        
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database()