"""
Configuration for Security Analyst AI Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM Provider Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

# --- Agent Configuration ---
AGENT_MODEL = os.getenv("AGENT_MODEL", "llama-3.3-70b-versatile")
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.2"))

# --- SIEM API Configuration ---
# The SIEM application might be running on a different port or host
SIEM_API_URL = os.getenv("SIEM_API_URL", "https://siem.securitycentric.net/api/v1")
SIEM_USERNAME = os.getenv("SIEM_USERNAME", "ai_security_analyst")
SIEM_PASSWORD = os.getenv("SIEM_PASSWORD", "ChooseAStrongPassword123!")

# --- Knowledge Base & DB Configuration ---
# Uses the main application's DATABASE_URL for asset lookups
DATABASE_URL = os.getenv("DATABASE_URL")
