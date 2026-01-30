"""
Generic Agent Service
A simplified agent that only uses RAG and basic DB tools.
"""
import logging
import json
import re
from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from .config import AGENT_MODEL, GOOGLE_API_KEY, AGENT_TEMPERATURE
from .tools.kb_tools import create_search_knowledge_base_tool, create_list_knowledge_bases_tool
from .tools.db_tools import create_db_query_tool

logger = logging.getLogger(__name__)

GENERIC_SYSTEM_PROMPT = """
You are a helpful AI Assistant.
Your goal is to answer questions using the available knowledge base and database.

GUIDELINES:
1. Use `search_knowledge_base` to find info in documents (FAQs, policies, etc.)
2. Use `query_database` for structured data if you know the schema.
3. Be concise and professional.
4. If you don't know the answer, say so.
"""

class GenericAgentService:
    def __init__(self, tenant_id: str = None, **kwargs):
        self.llm = ChatGoogleGenerativeAI(
            model=AGENT_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=AGENT_TEMPERATURE
        )
        self.tenant_id = tenant_id
        
        # Build tools
        self.tools = [
            create_search_knowledge_base_tool(tenant_id),
            create_list_knowledge_bases_tool(tenant_id)
        ]
        
        # Check for DB path in kwargs or environment
        db_path = kwargs.get('database_connection')
        if db_path:
             self.tools.append(create_db_query_tool(db_path))
             
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.conversations: Dict[str, List[Dict]] = {}

    def chat(self, session_id: str, message: str, **kwargs) -> Dict:
        try:
            if session_id not in self.conversations:
                self.conversations[session_id] = []
            
            self.conversations[session_id].append({"role": "user", "content": message})
            
            tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
            
            full_prompt = f"""{GENERIC_SYSTEM_PROMPT}

Tools:
{tool_descriptions}

Query: "{message}"

Respond with ONLY the JSON selection:
{{
    "tool": "tool_name",
    "args": {{...}},
    "reasoning": "..."
}}
OR:
{{
    "tool": "none",
    "response": "..."
}}
"""
            result = self.llm.invoke([HumanMessage(content=full_prompt)])
            text = result.content
            
            # Parsing logic
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                decision = json.loads(match.group(0))
                tool_name = decision.get('tool')
                
                if tool_name == 'none':
                    res_text = decision.get('response', "Hello! How can I help?")
                    return {"response": res_text, "session_id": session_id, "success": True}
                
                if tool_name in self.tool_map:
                    args = decision.get('args', {})
                    tool_result = self.tool_map[tool_name].invoke(args)
                    return {"response": str(tool_result), "session_id": session_id, "success": True, "tool_used": tool_name}
            
            return {"response": text, "session_id": session_id, "success": True}
            
        except Exception as e:
            logger.error(f"Generic Agent Error: {e}")
            return {"response": "Sorry, an error occurred.", "session_id": session_id, "success": False, "error": str(e)}

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        return self.conversations.get(session_id, [])

    def reset_conversation(self, session_id: str) -> bool:
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False
