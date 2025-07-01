#!/usr/bin/env python3
"""Test script to fetch and print real Poe.com chat history using Selenium automation."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_config


def main():
    print("=== Real Poe.com Chat History Test ===\n")
    config = load_config()
    client = PoeAPIClient(token=config.get_poe_tokens())
    print("Fetching real chat history using browser automation...")
    conversations = client.get_true_chat_history(count=20)
    print(f"\nFetched {len(conversations)} real conversations:")
    for i, conv in enumerate(conversations, 1):
        print(f"{i}. {conv.get('title', 'Untitled')}")
        print(f"   Bot: {conv.get('bot', 'Unknown')}")
        print(f"   Created: {conv.get('createdAt', 'Unknown')}")
        print(f"   Updated: {conv.get('updatedAt', 'Unknown')}")
        print(f"   ID: {conv.get('id', 'Unknown')}")
        print()

if __name__ == "__main__":
    main() 