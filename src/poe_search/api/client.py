"""API client for Poe.com using poe-api-wrapper."""

import os
import json
import logging
import requests
import time
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from urllib.parse import unquote

# Load environment variables from .env if present
load_dotenv()

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("poe_search.api.client")

# Helper to load Poe token from JSON config if env not set
POE_TOKEN = os.environ.get("POE_TOKEN")
if not POE_TOKEN:
    # Try config files relative to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
    config_paths = [
        os.path.join(project_root, 'config', 'poe_tokens.json'),
        os.path.join(project_root, 'config', 'secrets.json'),
    ]
    for path in config_paths:
        try:
            with open(path) as f:
                data = json.load(f)
                POE_TOKEN = unquote(data.get("p-b", ""))
                logger.info(f"Loaded POE_TOKEN from {path}")
                break
        except Exception:
            continue
    if not POE_TOKEN:
        logger.error("POE_TOKEN environment variable not set and could not load from JSON config.")
        raise RuntimeError("POE_TOKEN required for Poe API access.")

GRAPHQL_ENDPOINT = "https://poe.com/api/gql_POST"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PoeSearchBot/1.0; +https://github.com/hkevin01/poe-search)",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Cookie": f"p-b={POE_TOKEN}",
    "Origin": "https://poe.com",
    "Referer": "https://poe.com/",
}

RATE_LIMIT = int(os.environ.get("RATE_LIMIT_REQUESTS_PER_MINUTE", 30))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", 3))
RETRY_BACKOFF = 2  # seconds

class PoeAPIClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or POE_TOKEN
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        # Update headers with the actual token
        if self.token:
            self.session.headers.update({"Cookie": f"p-b={self.token}"})

    def _graphql(self, query: str, variables: dict, retry: int = 0) -> Any:
        payload = {
            "query": query,
            "variables": variables,
        }
        try:
            response = self.session.post(GRAPHQL_ENDPOINT, json=payload, timeout=15)
            if response.status_code == 429:
                logger.warning("Rate limited by Poe.com, sleeping before retry...")
                if retry < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF * (retry + 1))
                    return self._graphql(query, variables, retry + 1)
                else:
                    logger.error("Max retries exceeded for rate limiting.")
                    raise Exception("Rate limited and retries exhausted.")
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                logger.error(f"Poe.com GraphQL error: {data['errors']}")
                raise Exception(f"Poe.com error: {data['errors']}")
            return data.get("data")
        except requests.RequestException as e:
            logger.error(f"Network error contacting Poe.com: {e}")
            if retry < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF * (retry + 1))
                return self._graphql(query, variables, retry + 1)
            raise

    def test_connection(self) -> bool:
        """Test if the API connection is working."""
        try:
            # Simple query to test connection
            gql_query = """
            query {
                viewer {
                    id
                }
            }
            """
            data = self._graphql(gql_query, {})
            return data is not None and "viewer" in data
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def search(self, query: str, limit: int = 10, bot: Optional[str] = None, category: Optional[str] = None, date_range: Optional[str] = None) -> List[Dict]:
        gql_query = """
        query SearchMessages($query: String!, $limit: Int) {
            messageSearch(query: $query, limit: $limit) {
                id
                message
                conversationId
                bot
                createdAt
                category
            }
        }
        """
        variables = {"query": query, "limit": limit}
        logger.info(f"Searching Poe messages: query={query}, limit={limit}, bot={bot}, category={category}, date_range={date_range}")
        data = self._graphql(gql_query, variables)
        results = data.get("messageSearch", [])
        logger.info(f"Found {len(results)} results.")
        return results

    def get_conversation(self, conversation_id: str) -> Dict:
        gql_query = """
        query GetConversation($id: ID!) {
            conversation(id: $id) {
                id
                title
                messages {
                    id
                    message
                    author
                    createdAt
                }
            }
        }
        """
        variables = {"id": conversation_id}
        logger.info(f"Fetching conversation: {conversation_id}")
        data = self._graphql(gql_query, variables)
        return data.get("conversation", {})

    def get_conversation_history(self, days: int = 30, limit: int = 100) -> List[Dict]:
        """Get conversation history for the specified number of days."""
        gql_query = """
        query GetConversationHistory($limit: Int) {
            conversations(limit: $limit) {
                id
                title
                createdAt
                messageCount
            }
        }
        """
        variables = {"limit": limit}
        logger.info(f"Fetching conversation history: days={days}, limit={limit}")
        data = self._graphql(gql_query, variables)
        conversations = data.get("conversations", [])
        logger.info(f"Found {len(conversations)} conversations.")
        return conversations

    def export_conversations(self, output_file: str, format: str = "json"):
        gql_query = """
        query AllConversations {
            conversations {
                id
                title
                createdAt
                messages {
                    id
                    message
                    author
                    createdAt
                }
            }
        }
        """
        logger.info(f"Exporting all conversations to {output_file} in {format} format")
        data = self._graphql(gql_query, {})
        conversations = data.get("conversations", [])
        import json, csv
        if format == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(conversations, f, ensure_ascii=False, indent=2)
        elif format == "csv":
            with open(output_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "title", "createdAt", "messageCount"])
                for conv in conversations:
                    writer.writerow([conv["id"], conv["title"], conv["createdAt"], len(conv.get("messages", []))])
        else:
            logger.error("Unsupported export format.")
            raise ValueError("Unsupported format for export: use 'json' or 'csv'")
        logger.info("Export complete.")

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get user information."""
        try:
            gql_query = """
            query {
                viewer {
                    id
                    displayName
                    email
                }
            }
            """
            data = self._graphql(gql_query, {})
            return data.get("viewer")
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None

    def get_recent_conversations(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent conversations (alias for get_conversation_history)."""
        return self.get_conversation_history(days=days)

# Example usage (for CLI or scripts)
if __name__ == "__main__":
    import sys
    client = PoeAPIClient()
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "search":
            results = client.search(" ".join(sys.argv[2:]))
            print(results)
        elif len(sys.argv) > 1 and sys.argv[1] == "export":
            client.export_conversations("poe_conversations.json", format="json")
        elif len(sys.argv) > 1 and sys.argv[1] == "test":
            if client.test_connection():
                print("✅ Connection test passed")
            else:
                print("❌ Connection test failed")
        else:
            print("Usage: python client.py [search <query> | export | test]")
    except Exception as ex:
        logger.error(f"Operation failed: {ex}")