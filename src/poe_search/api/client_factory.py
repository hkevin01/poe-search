"""
Factory for creating Poe API clients.
"""

import logging
from .direct_client import DirectPoeClient


logger = logging.getLogger(__name__)


def create_poe_client(formkey: str, p_b_cookie: str) -> DirectPoeClient:
    """
    Create a Poe API client with the given credentials.
    
    Args:
        formkey: The formkey from Poe.com
        p_b_cookie: The p-b cookie from Poe.com
        
    Returns:
        DirectPoeClient: Configured client instance
    """
    logger.info("Creating Poe API client")
    
    return DirectPoeClient(
        formkey=formkey,
        token=p_b_cookie
    )
