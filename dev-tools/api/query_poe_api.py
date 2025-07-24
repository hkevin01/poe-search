"""Simple script to query Poe.com Official API using an API key."""

import requests
import os

API_KEY = os.environ.get("POE_API_KEY") or "your-official-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def query_poe(prompt, bot="ChatGPT"):
    response = requests.post(
        "https://api.poe.com/v1/query",
        headers=headers,
        json={
            "query": prompt,
            "bot": bot
        }
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Enter your question: ")
    result = query_poe(prompt)
    print(result)
