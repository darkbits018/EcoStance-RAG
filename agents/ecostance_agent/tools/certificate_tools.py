from langchain_core.tools import tool
import requests
import logging
from ..config import CERTIFICATE_API_URL

logger = logging.getLogger(__name__)

@tool
def get_certificate_details(identifier: str, type: str = "id"):
    """
    Get detailed information about a carbon offset certificate.
    - identifier: The ID, certificate number, or serial number.
    - type: The type of identifier provided ('id', 'number', or 'serial'). Default is 'id'.
    """
    if not identifier:
        return "Error: Identification value is required."
    
    endpoint_map = {
        "id": f"{CERTIFICATE_API_URL}/{identifier}",
        "number": f"{CERTIFICATE_API_URL}/number/{identifier}",
        "serial": f"{CERTIFICATE_API_URL}/serial/{identifier}"
    }
    
    url = endpoint_map.get(type.lower())
    if not url:
        return f"Error: Invalid type '{type}'. Must be 'id', 'number', or 'serial'."

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return f"No certificate found with {type}: {identifier}"
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching certificate details ({type}={identifier}): {e}")
        return f"Error connecting to certificate registry: {str(e)}"

@tool
def search_certificates(project_name: str = None, status: str = None):
    """
    Search or filter certificates by project name or status.
    Returns a list of matching certificates.
    """
    params = {}
    if project_name: params['project_name'] = project_name
    if status: params['status'] = status
    
    try:
        response = requests.get(CERTIFICATE_API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error searching certificates: {e}")
        return f"Error searching registry: {str(e)}"

@tool
def get_certificate_stats():
    """
    Get a statistical summary of all issued certificates (total tons offset, total certificates, etc.).
    """
    try:
        response = requests.get(f"{CERTIFICATE_API_URL}/stats/summary", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching certificate stats: {e}")
        return f"Error fetching stats: {str(e)}"
