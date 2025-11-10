import streamlit as st
import requests
import os
import time

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

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

# --- Streamlit UI ---

st.set_page_config(page_title="EcoStance RAG Agent", layout="wide")

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
    uploaded_file = st.file_uploader("Upload a document", type=['pdf', 'docx', 'txt', 'md'])

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


# --- Main Chat Interface ---
st.header(f"Chat with: {selected_kb}" if selected_kb else "Chat")

if selected_kb:
    if "messages" not in st.session_state or st.session_state.get("current_kb") != selected_kb:
        st.session_state.messages = []
        st.session_state.current_kb = selected_kb

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about the documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = query_rag_agent(selected_kb, prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Please create or select a knowledge base from the sidebar to begin.")
