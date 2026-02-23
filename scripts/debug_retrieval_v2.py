
import asyncio
import os
import sys
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore

# Add project root to path
sys.path.append(os.getcwd())
load_dotenv()

from app.services.qdrant_service import get_qdrant_client
from app.services.embedding_service import get_langchain_embeddings
from app.services.reranker_service import get_reranker_service

async def debug_retrieval():
    tenant_id = "a5ff464b-b13d-45fd-a418-def60ba7d503"
    kb_name = "test2"
    
    # Try the known collection name
    collection_name = f"tenant_{tenant_id}_{kb_name}"
    
    query = "explain general policy"
    
    print(f"--- Debugging Retrieval for '{query}' in '{collection_name}' ---")
    
    # 1. Setup Retrieval
    try:
        client = get_qdrant_client()
        embeddings = get_langchain_embeddings()
        
        # Check point count
        count = client.count(collection_name).count
        print(f"Total vectors in collection: {count}")
        
        qdrant_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
            content_payload_key="text",
        )
        
        # 2. Vector Search (Top 20 to cast a wide net)
        print("\n[1] Performing Vector Search (Top 20)...")
        # Ensure we use search_kwargs correctly
        retriever = qdrant_store.as_retriever(search_kwargs={"k": 20})
        docs = retriever.invoke(query)
        
        if not docs:
            print("No documents found via vector search!")
            return

        doc_texts = []
        print(f"Found {len(docs)} candidates.")
        
        for i, doc in enumerate(docs[:5]): # Show first 5 raw vector matches
            print(f"\nVector Rank {i+1}:")
            print(f"Source: {doc.metadata.get('source', 'unknown')}")
            # print(f"Content Preview: {doc.page_content[:200]}...")
            
        doc_texts = [d.page_content for d in docs]

        # 3. Rerank
        print("\n[2] Reranking Top 20 Candidates...")
        reranker = get_reranker_service()
        ranked = reranker.rerank(query, doc_texts, top_k=5)
        
        print("\n--- Final Top 5 Reranked Results ---")
        for text, score in ranked:
            print(f"\nRerank Score: {score:.4f}")
            # Find metadata for this text
            original_doc = next((d for d in docs if d.page_content == text), None)
            source = original_doc.metadata.get('source', 'unknown') if original_doc else "unknown"
            print(f"Source: {source}")
            print(f"Content: {text}...") 
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_retrieval())
