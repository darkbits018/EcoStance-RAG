import requests
from langchain_core.tools import tool
from ..config import ECOMMERCE_API_URL

@tool
def search_eco_products(search: str = None, category: str = None):
    """
    Search for eco-friendly products or filter by category.
    Returns: A list of products with sustainability ratings if available.
    """
    params = {}
    if search:
        params['search'] = search
    if category:
        params['category'] = category
    
from typing import Optional, Union

@tool
def search_eco_products(search: str = None, category: str = None, price_max: Optional[Union[str, float, int]] = None, item_type: str = "product"):
    """
    Search for eco-friendly items.
    - search: Keyword to search for (e.g., "wind", "Brazil").
    - category: Filter by category (e.g., "Carbon Offsets").
    - price_max: Max price filter. Can be a number or null.
    - item_type: "product" (default) or "project" to search the projects API.
    """
    # Clean up price_max which comes as string "" sometimes
    try:
        if price_max == "" or price_max is None:
            price_max = None
        else:
            price_max = float(price_max)
    except:
        price_max = None

    params = {}
    if price_max and price_max > 0:
        params['maxPrice'] = price_max
    
    # If explicit sort or implied "lowest price" (price_max=0 often means "cheapest" to LLMs)
    if price_max == 0:
        params['sortBy'] = 'price-asc'

    if category:
        params['category'] = category

    try:
        results = []
        
        # 1. Search PROJECTS if explicitly requested or logic suggests
        if item_type == "project" or (search and "project" in search.lower()):
            project_url = f"{ECOMMERCE_API_URL}/projects"
            project_params = {}
            if price_max: project_params['maxCost'] = price_max
            # Note: The project API doesn't list a 'q' search param, so we might need client-side filtering 
            # or relying on specific filters like 'type' if extracted.
            # However, for now, we'll fetch all and fuzzy match if search is present, or just list them.
            
            res = requests.get(project_url, params=project_params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data.get('success'):
                    projects = data.get('data', [])
                    
                    # Smart filtering: Only apply text search if it's NOT just a generic price query
                    # because "low cost" won't match "Amazon" but price_max filter handles it.
                    price_keywords = ["cost", "price", "cheap", "affordable", "budget", "expensive"]
                    is_generic_price_search = search and any(k in search.lower() for k in price_keywords)
                    
                    if search and not is_generic_price_search:
                        projects = [p for p in projects if search.lower() in p.get('title', '').lower() or search.lower() in p.get('description', '').lower()]
                    
                    # Mark as project type for the agent
                    for p in projects: p['item_type'] = 'project'
                    results.extend(projects)

            # Fallback Logic: If specific price filtered search returned 0 results, 
            # try again WITHOUT price limit so we don't return empty handed.
            if not results and (price_max or category):
               # Retry Projects without strict filters
               if item_type == "project" or (search and "project" in search.lower()):
                   res_retry = requests.get(project_url, params={}, timeout=5)
                   if res_retry.status_code == 200:
                       data_retry = res_retry.json()
                       if data_retry.get('success'):
                           # Return top 3 cheapest if we had a price filter originally
                           all_projects = data_retry.get('data', [])
                           # Sort by offsetCost if available
                           if price_max:
                               all_projects.sort(key=lambda x: x.get('offsetCost', 9999))
                           
                           # Mark type
                           for p in all_projects: p['item_type'] = 'project'
                           results.extend(all_projects)

               # Retry Products without strict filters
               if (item_type == "product" and not results) or item_type == "product":
                   url_retry = f"{ECOMMERCE_API_URL}/products"
                   res_retry = requests.get(url_retry, params={}, timeout=5)
                   if res_retry.status_code == 200:
                       data_retry = res_retry.json()
                       if data_retry.get('success'):
                           all_products = data_retry.get('data', [])
                           if price_max:
                               all_products.sort(key=lambda x: x.get('price', 9999))
                           
                           for p in all_products: p['item_type'] = 'product'
                           results.extend(all_products)
            if search:
                # Use the dedicated search endpoint
                url = f"{ECOMMERCE_API_URL}/products/search/query"
                params['q'] = search
            else:
                # Use listing endpoint with filters
                url = f"{ECOMMERCE_API_URL}/products"
            
            res = requests.get(url, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data.get('success'):
                    products = data.get('data', [])
                    
                    # If search endpoint returned nothing, try fuzzy client-side search on ALL products
                    if not products and search:
                         url_all = f"{ECOMMERCE_API_URL}/products"
                         res_all = requests.get(url_all, timeout=5)
                         if res_all.status_code == 200:
                             data_all = res_all.json()
                             if data_all.get('success'):
                                 all_items = data_all.get('data', [])
                                 # Fuzzy match
                                 products = [
                                     p for p in all_items 
                                     if search.lower() in p.get('name', '').lower() 
                                     or search.lower() in str(p.get('tags', [])).lower()
                                     or search.lower() in p.get('category', '').lower()
                                 ]

                    # Mark as product type
                    for p in products: p['item_type'] = 'product'
                    results.extend(products)

        return results

    except Exception as e:
        return f"Error connecting to store API: {str(e)}"

@tool
def get_eco_impact_summary(user_id: str):
    """
    Get a summary of a user's total carbon offset impact based on their orders.
    Useful for 'What is my total impact?' or 'Show my eco summary'.
    """
    if not user_id:
        return {"error": "User ID is required to calculate impact."}
        
    try:
        # Mock calculation based on simulated order history
        return {
            "user_id": user_id,
            "total_co2_offset": "45.8 tons",
            "trees_planted_equivalent": 183,
            "ranking": "Top 5% Eco-Warrior",
            "next_milestone": "50 tons (Silver Badge)"
        }
    except Exception as e:
        return f"Error calculating impact: {str(e)}"
