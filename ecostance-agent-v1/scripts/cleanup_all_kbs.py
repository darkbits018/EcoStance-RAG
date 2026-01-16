#!/usr/bin/env python3
"""
Cleanup script to remove all knowledge bases when switching embedding models
This removes:
1. All Qdrant collections
2. All database records
3. Local configuration files
"""

import sys
import os
sys.path.insert(0, '.')

from qdrant_client import QdrantClient
from quickship_agent.config import QDRANT_URL, QDRANT_API_KEY, DATABASE_URL
import json
import psycopg2
from urllib.parse import urlparse

def cleanup_qdrant_collections():
    """Remove all collections from Qdrant"""
    print("🧹 Cleaning up Qdrant collections...")
    
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Get all collections
        collections = client.get_collections()
        
        if not collections.collections:
            print("   No collections found in Qdrant")
            return
        
        for collection in collections.collections:
            collection_name = collection.name
            print(f"   Deleting collection: {collection_name}")
            client.delete_collection(collection_name)
        
        print(f"✅ Deleted {len(collections.collections)} collections from Qdrant")
        
    except Exception as e:
        print(f"❌ Error cleaning up Qdrant: {e}")

def cleanup_database():
    """Remove all knowledge base records from database"""
    print("🧹 Cleaning up database records...")
    
    try:
        # Parse database URL
        parsed = urlparse(DATABASE_URL)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Count existing records
        cursor.execute("SELECT COUNT(*) FROM tenant_knowledge_bases")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("   No knowledge base records found in database")
        else:
            # Delete all records
            cursor.execute("DELETE FROM tenant_knowledge_bases")
            conn.commit()
            print(f"✅ Deleted {count} knowledge base records from database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error cleaning up database: {e}")

def cleanup_local_config():
    """Clean up local configuration files"""
    print("🧹 Cleaning up local configuration...")
    
    try:
        # Clean kbs.json
        kbs_file = "data/config/kbs.json"
        if os.path.exists(kbs_file):
            with open(kbs_file, 'w') as f:
                json.dump([], f, indent=2)
            print("✅ Cleaned up kbs.json")
        
        # Clean any other config files if they exist
        config_files = [
            "data/config/collections.json",
            "data/config/embeddings.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'w') as f:
                    json.dump({}, f, indent=2)
                print(f"✅ Cleaned up {config_file}")
        
    except Exception as e:
        print(f"❌ Error cleaning up local config: {e}")

def main():
    print("🚀 Starting complete knowledge base cleanup...")
    print("   This will remove ALL knowledge bases and collections")
    print("   Reason: Switching from 384-dim to 1024-dim embeddings (BGE-M3)")
    print()
    
    # Cleanup in order
    cleanup_qdrant_collections()
    cleanup_database()
    cleanup_local_config()
    
    print()
    print("✅ Complete cleanup finished!")
    print("🔄 You can now create new knowledge bases with BGE-M3 embeddings")

if __name__ == "__main__":
    main()