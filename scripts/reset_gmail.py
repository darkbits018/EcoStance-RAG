from app.db.database import SessionLocal, engine
from sqlalchemy import text
from app.services.qdrant_service import get_qdrant_client

def reset_gmail_integration():
    db = SessionLocal()
    qdrant = get_qdrant_client()
    
    print("WARNING: This will wipe all Gmail history and vectors.")
    
    # 1. Clear SQL Tables
    try:
        print("Cleaning SQL: gmail_messages...")
        db.execute(text("DELETE FROM gmail_messages"))
        
        print("Cleaning SQL: gmail_execution_logs...")
        db.execute(text("DELETE FROM gmail_execution_logs"))
        
        print("Cleaning SQL: tenant_knowledge_bases (Gmail only)...")
        # Find collections to delete first
        result = db.execute(text("SELECT collection_name FROM tenant_knowledge_bases WHERE collection_name LIKE '%gmail%'"))
        collections = [row[0] for row in result]
        
        db.execute(text("DELETE FROM tenant_knowledge_bases WHERE collection_name LIKE '%gmail%'"))
        db.commit()
        print("SQL Cleanup Complete.")
    except Exception as e:
        print(f"SQL Error: {e}")
        db.rollback()
        
    # 2. Delete Qdrant Collections
    for col_name in collections:
        print(f"Deleting Qdrant Collection: {col_name}")
        try:
            qdrant.delete_collection(col_name)
            print("Deleted.")
        except Exception as e:
            print(f"Qdrant Error (might not exist): {e}")

    print("--- RESET COMPLETE ---")
    print("You can now run 'Sync Now' to start fresh.")

if __name__ == "__main__":
    reset_gmail_integration()
