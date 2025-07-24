#!/usr/bin/env python3
"""Direct test of Poe.com tokens and chat history endpoint."""

import requests
import json
from pathlib import Path
from poe_search.utils.config import load_config

# Poe.com GraphQL endpoint
POE_GQL_URL = "https://poe.com/api/gql_POST"

# Example GraphQL query for chat history (may need to be updated if Poe.com changes)
CHAT_HISTORY_QUERY = {
    "operationName": "ChatListPaginationQuery",
    "variables": {"first": 5},
    "query": "query ChatListPaginationQuery($first: Int) { chatList(first: $first) { edges { node { chatId title lastMessage { text } bot { id displayName } } } } }"
}

def get_tokens():
    config = load_config()
    tokens = config.get_poe_tokens()
    return tokens

def main():
    tokens = get_tokens()
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Cookie": f"p-b={tokens.get('p-b','')}; p-lat={tokens.get('p-lat','')}; formkey={tokens.get('formkey','')}"
    }
    print("\n===== SENDING DIRECT REQUEST TO POE.COM =====")
    print(f"Headers: {headers}")
    print(f"GraphQL Query: {json.dumps(CHAT_HISTORY_QUERY)}")
    print("============================================\n")
    response = requests.post(POE_GQL_URL, headers=headers, json=CHAT_HISTORY_QUERY)
    print(f"Status code: {response.status_code}")
    print("\n===== FULL RAW RESPONSE =====")
    print(response.text)
    print("===== END RAW RESPONSE =====\n")
    try:
        data = response.json()
        # Try to parse chat titles
        chats = data.get('data', {}).get('chatList', {}).get('edges', [])
        print("\nParsed last 5 chat titles:")
        for i, edge in enumerate(chats, 1):
            node = edge.get('node', {})
            title = node.get('title', 'Untitled')
            bot = node.get('bot', {}).get('displayName', 'Unknown bot')
            chat_id = node.get('chatId', 'Unknown ID')
            print(f"{i}. {title} (Bot: {bot}, ID: {chat_id})")
        if not chats:
            print("No chats found in response.")
    except Exception as e:
        print(f"Failed to parse JSON or extract chats: {e}")

if __name__ == "__main__":
    main() 