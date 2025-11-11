import streamlit as st
import requests
import os
import time

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# --- Custom CSS for better chat UI ---
def inject_custom_css():
    st.markdown("""
    <style>
    /* Make chat input sticky */
    div[data-testid="stChatInput"] {
        position: -webkit-sticky; /* for Safari */
        position: sticky;
        bottom: 0;
        z-index: 100;
        background-color: #0e1117; /* Match streamlit dark theme */
    }

    /* Style chat input */
    .stChatInput > div {
        border-radius: 25px !important;
        border: 2px solid #4CAF50 !important;
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.2) !important;
    }
    
    .stChatInput input {
        font-size: 16px !important;
        padding: 12px 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions to Interact with Backend ---

def get_knowledge_bases():
    """Fetches the list of available knowledge bases from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/manage/knowledge-bases/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching knowledge bases: {e}")
        return []

def upload_file(uploaded_file):
    """Uploads a file to the backend and returns its path."""
    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    try:
        response = requests.post(f"{BACKEND_URL}/upload/", files=files)
        response.raise_for_status()
        return response.json().get("file_path")
    except requests.exceptions.RequestException as e:
        st.error(f"Error during file upload: {e}")
        return None

def process_file(file_path, collection_name):
    """Triggers the processing pipeline for an already uploaded file."""
    data = {'file_path': file_path, 'collection_name': collection_name}
    try:
        response = requests.post(f"{BACKEND_URL}/upload-to-qdrant/", data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error during file processing: {e}")
        return None

def query_rag_agent(collection_name, query):
    """Sends a query to the RAG agent and gets an answer."""
    data = {'collection_name': collection_name, 'query': query}
    try:
        response = requests.post(f"{BACKEND_URL}/query/", data=data)
        response.raise_for_status()
        return response.json().get("answer", "No answer found.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error querying the agent: {e}")
        return "Error: Could not get a response from the backend."

def delete_knowledge_base(collection_name):
    """Deletes a knowledge base."""
    try:
        response = requests.delete(f"{BACKEND_URL}/manage/knowledge-bases/{collection_name}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting knowledge base: {e}")
        return False

def get_knowledge_base_details(collection_name):
    """Gets detailed information about a knowledge base including files."""
    try:
        response = requests.get(f"{BACKEND_URL}/manage/knowledge-bases/{collection_name}/details")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching knowledge base details: {e}")
        return None

def delete_file_from_kb(collection_name, filename):
    """Deletes a specific file from a knowledge base."""
    try:
        response = requests.delete(f"{BACKEND_URL}/manage/knowledge-bases/{collection_name}/files/{filename}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting file: {e}")
        return False

def reindex_file_in_kb(collection_name, filename):
    """Reindexes a specific file in a knowledge base."""
    try:
        response = requests.post(f"{BACKEND_URL}/manage/knowledge-bases/{collection_name}/files/{filename}/reindex")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error reindexing file: {e}")
        return False

# --- Streamlit UI ---

st.set_page_config(page_title="EcoStance RAG Agent", layout="wide")

# Inject custom CSS for sticky chat input
inject_custom_css()

st.title("EcoStance RAG Agent 🤖")
st.write("Upload documents, manage your knowledge bases, and ask questions.")

# --- Sidebar for Management ---
with st.sidebar:
    st.header("Configuration")
    
    # Get the list of knowledge bases
    knowledge_bases = get_knowledge_bases()
    
    st.subheader("Select Knowledge Base")
    if 'selected_kb' not in st.session_state or st.session_state.selected_kb not in knowledge_bases:
        st.session_state.selected_kb = knowledge_bases[0] if knowledge_bases else None

    selected_kb = st.selectbox(
        "Choose a knowledge base to chat with:",
        options=knowledge_bases,
        key='selected_kb'
    )
    
    st.divider()

    st.subheader("Manage Knowledge Bases")
    if selected_kb and st.button(f"Delete '{selected_kb}'"):
        with st.spinner(f"Deleting {selected_kb}..."):
            if delete_knowledge_base(selected_kb):
                st.success(f"Knowledge base '{selected_kb}' deleted.")
                time.sleep(1) # Give a moment for the user to see the message
                st.rerun()
            else:
                st.error("Deletion failed.")

    st.divider()

    st.subheader("Add New Document")
    new_kb_name = st.text_input("Enter new knowledge base name (or select existing):", value=selected_kb or "")
    uploaded_file = st.file_uploader(
        "Upload a document", 
        type=['pdf', 'docx', 'txt', 'md', 'xlsx', 'xls', 'csv', 'html', 'htm', 'sql', 'jsonl'],
        help="Supported formats: PDF, Word, Text, Markdown, Excel, CSV, HTML, SQL, JSONL"
    )

    if st.button("Upload and Process"):
        if uploaded_file and new_kb_name:
            with st.spinner(f"Step 1/2: Uploading '{uploaded_file.name}'..."):
                file_path = upload_file(uploaded_file)
            
            if file_path:
                st.success(f"File uploaded successfully. Path: {file_path}")
                with st.spinner(f"Step 2/2: Processing file into '{new_kb_name}'..."):
                    result = process_file(file_path, new_kb_name)
                
                if result:
                    st.success("File processed and added to knowledge base successfully!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.warning("Please provide both a file and a knowledge base name.")


# --- Main Interface with Tabs ---
tab1, tab2 = st.tabs(["💬 Chat", "📁 Manage Files"])

with tab1:
    st.header(f"Chat with: {selected_kb}" if selected_kb else "Chat")

    if selected_kb:
        if "messages" not in st.session_state or st.session_state.get("current_kb") != selected_kb:
            st.session_state.messages = []
            st.session_state.current_kb = selected_kb

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about the documents..."):
            # Add user message to session state
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get assistant response
            with st.spinner("Thinking..."):
                response = query_rag_agent(selected_kb, prompt)
            
            # Add assistant message to session state
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to update the display
            st.rerun()
    else:
        st.info("Please create or select a knowledge base from the sidebar to begin.")

with tab2:
    st.header("📁 Knowledge Base File Management")
    
    if selected_kb:
        st.subheader(f"Files in '{selected_kb}'")
        
        # Get knowledge base details
        with st.spinner("Loading knowledge base details..."):
            kb_details = get_knowledge_base_details(selected_kb)
        
        if kb_details and not kb_details.get('error'):
            # Show knowledge base statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Points", kb_details.get('total_points', 0))
            with col2:
                st.metric("Files Count", kb_details.get('files_count', 0))
            with col3:
                st.metric("Vector Size", kb_details.get('vector_size', 0))
            with col4:
                total_chunks = sum(f.get('chunk_count', 0) for f in kb_details.get('files', []))
                st.metric("Total Chunks", total_chunks)
            
            st.divider()
            
            # Show files table
            files = kb_details.get('files', [])
            if files:
                st.subheader("📄 Indexed Files")
                
                for i, file_info in enumerate(files):
                    with st.expander(f"📄 {file_info.get('filename', 'Unknown')} ({file_info.get('chunk_count', 0)} chunks)"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**File Type:** {file_info.get('file_type', 'Unknown')}")
                            st.write(f"**Upload Date:** {file_info.get('upload_date', 'Unknown')}")
                            st.write(f"**File Size:** {file_info.get('file_size', 'Unknown')}")
                            st.write(f"**Total Characters:** {file_info.get('total_characters', 0):,}")
                            st.write(f"**Chunks:** {file_info.get('chunk_count', 0)}")
                        
                        with col2:
                            filename = file_info.get('filename')
                            
                            # Reindex button
                            if st.button(f"🔄 Reindex", key=f"reindex_{i}"):
                                with st.spinner(f"Reindexing {filename}..."):
                                    if reindex_file_in_kb(selected_kb, filename):
                                        st.success(f"Successfully reindexed {filename}")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Reindexing failed")
                            
                            # Delete button
                            if st.button(f"🗑️ Delete", key=f"delete_{i}", type="secondary"):
                                if st.session_state.get(f"confirm_delete_{i}"):
                                    with st.spinner(f"Deleting {filename}..."):
                                        if delete_file_from_kb(selected_kb, filename):
                                            st.success(f"Successfully deleted {filename}")
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error("Deletion failed")
                                else:
                                    st.session_state[f"confirm_delete_{i}"] = True
                                    st.warning("Click delete again to confirm")
                                    
            else:
                st.info("No files found in this knowledge base.")
        
        elif kb_details and kb_details.get('error'):
            st.error(f"Error loading knowledge base: {kb_details.get('error')}")
        else:
            st.error("Failed to load knowledge base details.")
    
    else:
        st.info("Please select a knowledge base from the sidebar to manage its files.")
