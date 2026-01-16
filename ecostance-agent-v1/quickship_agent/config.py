"""
Configuration for QuickShip AI Agent
Load settings from environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- LLM Provider Configuration ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

# --- Google Gemini API Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Groq API Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Qdrant Configuration (for knowledge base features) ---
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# --- Embedding Model Configuration ---
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDING_VECTOR_SIZE = int(os.getenv("EMBEDDING_VECTOR_SIZE", "384"))
DISTANCE_METRIC = os.getenv("DISTANCE_METRIC", "Cosine")

# --- Database Configuration ---
QUICKSHIP_DB_PATH = os.getenv("QUICKSHIP_DB_PATH", "QuickShip.db")

# --- Agent Configuration ---
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash-lite")
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.3"))

# --- LLM Provider Model Mappings ---
GEMINI_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.0-pro"
]

GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",  # Deprecated - kept for reference
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "llama3-70b-8192",
    "llama3-8b-8192"
]
