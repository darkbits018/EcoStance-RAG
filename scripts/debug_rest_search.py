
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

collection_name = "tenant_a5ff464b-b13d-45fd-a418-def60ba7d503_test2"
url = f"{QDRANT_URL}/collections/{collection_name}/points/scroll"

headers = {
    "api-key": QDRANT_API_KEY,
    "Content-Type": "application/json"
}

print(f"Running text search on {url}...")

payload = {
    "limit": 100,
    "with_payload": True,
    "with_vector": False,
    "filter": {
        "should": [
            {
                "key": "text",
                "match": {"text": "General Policy"}
            },
            {
                "key": "text",
                "match": {"text": "hygiene"}
            }
        ]
    }
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"Found matches: {len(data['result']['points'])}")
        
        for point in data['result']['points']:
            print(f"\nID: {point['id']}")
            text = point['payload'].get('text', '')
            print(f"Source: {point['payload'].get('source', 'unknown')}")
            print(f"Preview: {text[:200]}...")
            
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Request failed: {e}")
