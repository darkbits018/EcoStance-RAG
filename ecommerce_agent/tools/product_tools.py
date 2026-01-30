import requests
import json
from langchain_core.tools import tool
from ..config import ECOMMERCE_API_URL

@tool
def find_products(search: str = None, category_slug: str = None):
    """
    Search for products by name or filter by category.
    Useful when a user asks for 'sony headphones', 'gaming laptop', etc.
    Returns: A list of product dictionaries.
    """
    params = {}
    if search:
        params['search'] = search
    if category_slug:
        params['category'] = category_slug
    
    try:
        response = requests.get(f"{ECOMMERCE_API_URL}/products", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error connecting to store API: {str(e)}"

@tool
def get_all_categories():
    """
    Returns a list of all available product categories.
    Useful when a user asks 'what do you sell?' or 'show me categories'.
    """
    try:
        response = requests.get(f"{ECOMMERCE_API_URL}/categories")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error fetching categories: {str(e)}"

@tool
def get_my_orders(user_id: str):
    """
    Get orders for the specific user_id.
    Useful when a user asks 'where is my order' or 'order history'.
    """
    if not user_id:
        return {"error": "User ID is required to fetch orders"}
        
    try:
        response = requests.get(f"{ECOMMERCE_API_URL}/orders", params={"user_id": user_id})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error fetching orders: {str(e)}"
