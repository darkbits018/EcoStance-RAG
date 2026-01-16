import qdrant_client
from qdrant_client import QdrantClient
import sys

print(f"Python Version: {sys.version}")
# print(f"Qdrant Client Version: {qdrant_client.__version__}")

try:
    client = QdrantClient('localhost')
    print(f"Has 'search' method? {hasattr(client, 'search')}")
    print(f"Has 'query_points' method? {hasattr(client, 'query_points')}")
except Exception as e:
    print(f"Error init client: {e}")

try:
    import langchain_qdrant
    print(f"Langchain Qdrant Version: {langchain_qdrant.__version__}")
except ImportError:
    print("langchain_qdrant not installed")

try:
    import langchain_community.vectorstores.qdrant
    print("langchain_community.vectorstores.qdrant available")
except ImportError:
    print("langchain_community not available")
    