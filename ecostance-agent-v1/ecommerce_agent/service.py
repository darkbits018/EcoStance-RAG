"""
E-Commerce Agent Service
Handles the specific logic for the E-Commerce Bot.
"""
import logging
import json
import re
from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from .config import AGENT_MODEL, GOOGLE_API_KEY, AGENT_TEMPERATURE
from .tools.product_tools import find_products, get_all_categories, get_my_orders

logger = logging.getLogger(__name__)

ECOMMERCE_SYSTEM_PROMPT = """
You are the E-Commerce Shopping Assistant.
Your goal is to help customers find products and check their orders.

### RESPONSE FORMAT RULES
1. **Normal Chat**: If you are just talking, greeting, or explaining, answer normally.
   - Example: "Hi there! I can help you find electronics."

2. **Data Found**: If you use a tool (like `find_products`) and get results, you MUST return a JSON object strictly following this format:
   ```json
   {
     "type": "product_list",
     "message": "Brief text introduction here",
     "data": { "items": [ ...raw tool results... ] }
   }
   ```

3. **Links/Actions**: If the user needs to specific page (like login), return:
   ```json
   {
     "type": "url_action",
     "message": "Please log in first",
     "data": { "url": "/login", "button_text": "Log In" }
   }
   ```

### AVAILABLE TOOLS:
1. `find_products(search, category_slug)`: Returns list of products.
2. `get_all_categories()`: Returns list of categories.
3. `get_my_orders(user_id)`: Returns order history.

### BEHAVIOR:
- Do NOT list products in the `message` text field.
- Do NOT describe the price or details in text if you are returning the JSON card. Let the UI handle it.
- Keep the `message` short.
- User Context: You have access to the user's ID. If they want to track an order but no user_id is provided, ask them to log in.
"""

# Strict whitelist of allowed tools for E-Commerce agent
SAFE_TOOL_WHITELIST = {"product_search", "categories", "orders"}

class EcommerceAgentService:
    def __init__(self, tenant_id: str = None, allowed_tools: List[str] = None, **kwargs):
        self.llm = ChatGoogleGenerativeAI(
            model=AGENT_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=AGENT_TEMPERATURE
        )
        self.tenant_id = tenant_id
        
        # Validate allowed tools
        requested_tools = allowed_tools if allowed_tools is not None else ["product_search", "categories", "orders"]
        self.allowed_tools = [t for t in requested_tools if t in SAFE_TOOL_WHITELIST]
        
        if not self.allowed_tools:
            logger.warning(f"No safe tools found for Ecommerce agent in: {requested_tools}. Using all safe tools.")
            self.allowed_tools = list(SAFE_TOOL_WHITELIST)

        # Map tools to internal objects with safety check
        self.tools = []
        if "product_search" in self.allowed_tools:
            self.tools.append(find_products)
        if "categories" in self.allowed_tools:
            self.tools.append(get_all_categories)
        if "orders" in self.allowed_tools:
            self.tools.append(get_my_orders)
            
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # In-memory conversation storage
        self.conversations: Dict[str, List[Dict]] = {}
        
    def _is_out_of_scope(self, message: str) -> bool:
        """Simple keyword check for clearly out-of-scope queries."""
        # Add e-commerce specific exclusions if needed
        return False

    def chat(self, session_id: str, message: str, user_id: str = None) -> Dict:
        """
        Process a chat message.
        Args:
            session_id: Unique session ID
            message: User input
            user_id: ID of the logged-in user (optional)
        """
        try:
            # Init history
            if session_id not in self.conversations:
                self.conversations[session_id] = []
                
            # Add user message
            self.conversations[session_id].append({"role": "user", "content": message})
            
            # Construct Prompt
            tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
            context_info = f"\nUser ID: {user_id if user_id else 'Not Logged In'}"
            
            full_prompt = f"""{ECOMMERCE_SYSTEM_PROMPT}

Tools Available:
{tool_descriptions}

Context:
{context_info}

Current Query: "{message}"

Respond with ONLY the JSON object for tool selection:
{{
    "tool": "tool_name",
    "args": {{...}},
    "reasoning": "..."
}}
OR if no tool is needed:
{{
    "tool": "none",
    "response": {{
        "type": "text",
        "message": "...",
        "data": null
    }}
}}
"""
            # Ask LLM to Decide
            result = self.llm.invoke([HumanMessage(content=full_prompt)])
            decision_text = result.content
            
            # Clean up cleanup code blocks
            match = re.search(r'```json\s*(\{.*?\})\s*```', decision_text, re.DOTALL)
            if match:
                decision_text = match.group(1)
            else:
                match = re.search(r'\{.*\}', decision_text, re.DOTALL)
                if match:
                    decision_text = match.group(0)

            decision = json.loads(decision_text)
            
            # Execute logic
            final_response = {}
            
            if decision['tool'] == 'none':
                final_response = decision['response']
            else:
                tool_name = decision['tool']
                if tool_name in self.tool_map:
                    # Inject user_id if needed
                    tool_args = decision.get('args', {})
                    if tool_name == 'get_my_orders' and user_id:
                         tool_args['user_id'] = user_id
                         
                    # Run Tool
                    tool_result = self.tool_map[tool_name].invoke(tool_args)
                    
                    # If tool returns data, format as per protocol
                    # (Note: In a real system the LLM would formatter this, but we force it here for reliability)
                    if isinstance(tool_result, (list, dict)):
                        # It's data
                        final_response = {
                            "type": "product_list" if tool_name == "find_products" else "data_view", # Simplify for now
                            "message": f"Here is what I found for you.",
                            "data": tool_result
                        }
                        if tool_name == "find_products":
                             final_response["data"] = {"items": tool_result} # match carousel spec
                    else:
                        # Error or string
                        final_response = {
                            "type": "text",
                            "message": str(tool_result),
                            "data": None
                        }
                else:
                    final_response = {
                        "type": "text",
                        "message": "Sorry, I tried to use a tool I don't have.",
                        "data": None
                    }

            # Save assistant response
            self.conversations[session_id].append({"role": "assistant", "content": json.dumps(final_response)})
            
            return {
                "response": final_response, # This is the JSON object the frontend expects
                "session_id": session_id,
                "success": True
            }

        except Exception as e:
            logger.error(f"Ecommerce Agent Error: {e}", exc_info=True)
            return {
                "response": {"type": "text", "message": "An error occurred.", "data": None},
                "session_id": session_id,
                "success": False,
                "error": str(e)
            }
