import logging
import os
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from ..config import (
    GOOGLE_API_KEY,
    GROQ_API_KEY,
    LLM_PROVIDER,
    QDRANT_URL,
    QDRANT_API_KEY,
    EMBEDDING_MODEL_NAME,
    AGENT_MODEL
)
from app.services.qdrant_service import get_qdrant_client
from app.services.embedding_service import load_embedding_model

logger = logging.getLogger(__name__)


def get_llm():
    """Initializes and returns the LLM based on provider configuration."""
    if LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
             raise ValueError("GROQ_API_KEY must be set for groq provider.")
        return ChatGroq(
            model_name=AGENT_MODEL,
            groq_api_key=GROQ_API_KEY,
            temperature=0.1
        )
    else:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY must be set for gemini provider.")
        return ChatGoogleGenerativeAI(
            model=AGENT_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.1
        )


def get_vector_store(collection_name: str):
    """Initializes and returns a Qdrant vector store using singleton client and model."""
    # Use singleton embedding model via LangChain wrapper
    base_model = load_embedding_model()
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        client=base_model
    )
    
    # Use singleton Qdrant client
    client = get_qdrant_client()
    
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
        content_payload_key="text",
    )


def format_docs(docs: list[Document]) -> str:
    """Formats a list of Documents into a single string."""
    if not docs:
        return "No relevant documents found."
    return "\n\n".join(doc.page_content for doc in docs)


def create_rag_chain(vector_store: QdrantVectorStore):
    """Creates a stateful RAG chain with conversation memory using LCEL."""
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    llm = get_llm()

    # Stateful Answering Prompt
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant. Use the following context to answer the user's question. If you don't know the answer based on the context, say you don't know."),
            ("human", """Context from documents:
{context}

Question: {question}

Answer:"""),
        ]
    )

    # Define the stateful RAG chain
    rag_chain = (
        RunnablePassthrough.assign(
            context=lambda x: format_docs(retriever.invoke(x["question"]))
        )
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain


def execute_query(collection_name: str, query: str, chat_history: list = None) -> str:
    """
    Executes a query against the stateful RAG chain.
    """
    try:
        if chat_history is None:
            chat_history = []
        
        vector_store = get_vector_store(collection_name)
        rag_chain = create_rag_chain(vector_store)
        
        # Log the retrieval count for debugging
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        retrieved_docs = retriever.invoke(query)
        logger.info(f"Retrieved {len(retrieved_docs)} chunks from {collection_name}")

        # Invoke the rag_chain
        answer = rag_chain.invoke({
            "question": query,
            "chat_history": chat_history
        })
        
        return answer
    except Exception as e:
        logger.error(f"Error in RAG execute_query: {e}", exc_info=True)
        return f"I encountered an error while searching the knowledge base: {str(e)}"
