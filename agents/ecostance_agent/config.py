"""
Configuration for EcoStance AI Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM Provider Configuration ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Agent Configuration ---
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash-lite")
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.2"))

# --- Integration URLs ---
# Mock or real URLs for certificates and products
CERTIFICATE_API_URL = os.getenv("CERTIFICATE_API_URL", "http://localhost:5000/api/certificates")
ECOMMERCE_API_URL = os.getenv("ECOMMERCE_API_URL", "http://localhost:5000/api")
