import requests
import json
from typing import List, Dict, Any

# You would configure this to point to your actual backend API URL
# For development/demo, we assume it runs on localhost:3000 or similar
BASE_URL = "http://localhost:3000/api"

def find_products(search: str = None, category_slug: str = None) -> List[Dict[str, Any]]:
    """
    Search for products by name or filter by category.
    Returns: List of product dictionaries.
    """
    params = {}
    if search:
        params['search'] = search
    if category_slug:
        params['category'] = category_slug
    
    try:
        # TIMEOUT added for safety
        response = requests.get(f"{BASE_URL}/products", params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Return empty list on error so the agent knows nothing was found
        # In a real app, you might want to log this error
        print(f"Error fetching products: {e}")
        return []

def get_all_categories() -> List[Dict[str, Any]]:
    """
    Returns a list of all available product categories.
    """
    try:
        response = requests.get(f"{BASE_URL}/categories", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

def get_my_orders(user_id: str) -> List[Dict[str, Any]]:
    """
    Get orders for the logged-in user.
    Args:
        user_id: The ID of the authenticated user.
    """
    if not user_id:
        return []
        
    try:
        # This assumes the backend accepts user_id as a query param
        # In production, this would likely be handled via the Auth header
        response = requests.get(f"{BASE_URL}/orders", params={"user_id": user_id}, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []
