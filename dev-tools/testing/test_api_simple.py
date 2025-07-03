"""Simple test to check if our API client works without hanging."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_poe_tokens_from_file


def test_simple_api():
    print("Loading tokens...")
    tokens = load_poe_tokens_from_file()
    print(f"Tokens loaded: {bool(tokens.get('p-b'))}")
    
    print("Creating API client...")
    client = PoeAPIClient(token=tokens)
    print(f"Client created: {client.client is not None}")
    
    print("Testing get_bots() with timeout...")
    try:
        bots = client.get_bots()
        print(f"Bots fetched: {len(bots)} bots")
        print(f"Bot IDs: {list(bots.keys())[:3]}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_api()
    print(f"Test {'PASSED' if success else 'FAILED'}")
