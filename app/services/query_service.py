from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_qdrant import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document # Import Document for type hinting if needed
import logging

from app.config import GOOGLE_API_KEY, QDRANT_URL, QDRANT_API_KEY, EMBEDDING_MODEL_NAME

# Configure logging for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # Ensure basic config is set if not already

# --- Service Initialization ---

def get_llm():
    """Initializes and returns the Gemini LLM."""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY must be set in environment variables.")
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=GOOGLE_API_KEY)

def get_retriever(collection_name: str):
    """Initializes and returns a Qdrant retriever for a specific collection."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    qdrant_store = Qdrant.from_existing_collection(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=collection_name,
        embedding=embeddings,
        content_payload_key="text",
    )
    return qdrant_store.as_retriever(search_kwargs={"k": 3})

def format_docs(docs: list[Document]) -> str:
    """Formats a list of Documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

def create_rag_chain(collection_name: str):
    """Creates a stateless RAG chain using LCEL."""
    retriever = get_retriever(collection_name)
    llm = get_llm()

    # Answering Prompt - Using human message instead of system for better Gemini compatibility
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", """You are an expert assistant. Answer the following question based EXCLUSIVELY on the provided context below.

IMPORTANT RULES:
- If the context contains the answer, provide it directly and concisely
- If the context does not contain the answer, respond with "I don't know"
- DO NOT use any external knowledge or training data
- DO NOT make up information
- ONLY use information from the context provided

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""),
        ]
    )

    # Define the retrieval function
    def retrieve_and_format(inputs):
        question = inputs["question"]
        docs = retriever.invoke(question)
        formatted_context = format_docs(docs)
        logger.info(f"Context being passed to LLM: {formatted_context}")
        return formatted_context

    # Define the stateless RAG chain
    rag_chain = (
        RunnablePassthrough.assign(context=RunnableLambda(retrieve_and_format))
        | RunnableLambda(lambda x: logger.info(f"Final inputs to prompt: {x}") or x)
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def execute_query(collection_name: str, query: str) -> str:
    """
    Executes a query against the stateless RAG chain.
    """
    rag_chain = create_rag_chain(collection_name)
    
    # The chain is invoked with the 'question' key
    # To log context, we need to modify the chain to return it explicitly
    # For now, we'll run the retriever separately to log context.
    
    retriever = get_retriever(collection_name)
    retrieved_docs = retriever.invoke(query)
    formatted_context = format_docs(retrieved_docs)
    logger.info(f"Retrieved Context: {formatted_context}")

    # Invoke the rag_chain with the query
    answer = rag_chain.invoke({"question": query})
    
    return answer