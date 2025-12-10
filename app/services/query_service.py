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
    """
    Initializes and returns the Gemini LLM with optimized settings.
    
    Temperature is set low (0.3) for more consistent, factual responses
    while still allowing some flexibility in phrasing.
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY must be set in environment variables.")
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,  # Slightly higher for more natural responses
        max_output_tokens=1024  # Ensure complete answers
    )

def get_retriever(collection_name: str, top_k: int = 5):
    """
    Initializes and returns a Qdrant retriever for a specific collection.
    
    Args:
        collection_name: Name of the Qdrant collection
        top_k: Number of chunks to retrieve (default: 5, increased for better coverage)
    
    Returns:
        Qdrant retriever instance
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    qdrant_store = Qdrant.from_existing_collection(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=collection_name,
        embedding=embeddings,
        content_payload_key="text",
    )
    # Retrieve more chunks for better context coverage
    # Higher k = more context but slower, lower k = faster but might miss info
    return qdrant_store.as_retriever(search_kwargs={"k": top_k})

def format_docs(docs: list[Document]) -> str:
    """Formats a list of Documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

def create_rag_chain(collection_name: str):
    """Creates a stateful RAG chain with conversation memory using LCEL."""
    retriever = get_retriever(collection_name)
    llm = get_llm()

    # Improved Answering Prompt - reduces "I don't know" responses
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are an expert assistant helping users find information from a knowledge base. Your goal is to provide helpful, accurate answers based on the provided context.

RESPONSE GUIDELINES:

1. PRIMARY GOAL: Answer the question using information from the context
   - Extract and synthesize relevant information
   - Connect related pieces of information logically
   - Provide complete, helpful answers

2. WHEN INFORMATION IS PARTIAL:
   - Answer what you CAN from the context
   - Be specific about what information is available
   - Example: "Based on the context, I can tell you that [answer]. However, I don't have information about [missing part]."

3. WHEN INFORMATION IS MISSING:
   - Only say "I don't have information" if the context is completely unrelated
   - Try to provide related information that might be helpful
   - Suggest what the user might want to ask instead

4. ANSWER QUALITY:
   - Be conversational and natural
   - Provide context and explanations
   - Use examples from the context when helpful
   - Structure longer answers with bullet points or paragraphs

5. ACCURACY:
   - Base answers on the context provided
   - Don't invent information not in the context
   - If making logical connections, make them clear
   - Cite specific details from the context

Remember: Your job is to be HELPFUL while staying ACCURATE. Provide the best answer possible with the information available."""),
            ("human", """Context from knowledge base:
{context}

User question: {question}

Provide a helpful, accurate answer based on the context above:"""),
        ]
    )

    # Define the retrieval function
    def retrieve_and_format(inputs):
        question = inputs["question"]
        docs = retriever.invoke(question)
        formatted_context = format_docs(docs)
        logger.info(f"Context being passed to LLM: {formatted_context}")
        return formatted_context
    
    # Define the chat history formatting function
    def format_chat_history(inputs):
        chat_history = inputs.get("chat_history", [])
        if not chat_history:
            return "No previous conversation."
        
        formatted_history = []
        for i, message in enumerate(chat_history):
            if i % 2 == 0:
                formatted_history.append(f"Human: {message.content}")
            else:
                formatted_history.append(f"Assistant: {message.content}")
        
        return "\n".join(formatted_history)

    # Define the stateful RAG chain
    rag_chain = (
        RunnablePassthrough.assign(
            context=RunnableLambda(retrieve_and_format),
            chat_history=RunnableLambda(format_chat_history)
        )
        | RunnableLambda(lambda x: logger.info(f"Final inputs to prompt: question={x.get('question')}, has_history={bool(x.get('chat_history'))}") or x)
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def execute_query(collection_name: str, query: str, chat_history: list = None, tenant_id: str = None) -> str:
    """
    Executes a query against the stateful RAG chain with conversation history.
    
    Args:
        collection_name: Qdrant collection name
        query: User query
        chat_history: Previous conversation messages
        tenant_id: Tenant identifier for filtering (optional, for future use)
    """
    if chat_history is None:
        chat_history = []
    
    rag_chain = create_rag_chain(collection_name)
    
    # Log the retrieval for debugging
    retriever = get_retriever(collection_name)
    retrieved_docs = retriever.invoke(query)
    formatted_context = format_docs(retrieved_docs)
    logger.info(f"Retrieved Context for tenant {tenant_id}: {formatted_context}")

    # Invoke the rag_chain with the query and chat history
    answer = rag_chain.invoke({
        "question": query,
        "chat_history": chat_history
    })
    
    return answer