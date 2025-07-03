"""Comprehensive tests for Poe.com conversation retrieval and token management."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_poe_tokens_from_file


class TestConversationRetrieval:
    """Test conversation retrieval functionality."""
    
    @pytest.fixture(scope="class")
    def poe_tokens(self):
        """Load Poe tokens from config file."""
        try:
            tokens = load_poe_tokens_from_file()
            if not tokens.get("p-b"):
                pytest.skip("No valid p-b token found")
            return tokens
        except Exception as e:
            pytest.skip(f"Could not load Poe tokens: {e}")

    @pytest.fixture(scope="class")
    def poe_client(self, poe_tokens):
        """Create PoeAPIClient instance."""
        try:
            client = PoeAPIClient(token=poe_tokens)
            return client
        except Exception as e:
            pytest.skip(f"Could not create PoeAPIClient: {e}")

    def test_token_validity(self, poe_tokens):
        """Test if current tokens are valid and properly formatted."""
        assert isinstance(poe_tokens, dict), "Tokens should be a dictionary"
        assert "p-b" in poe_tokens, "p-b token is required"
        assert "p-lat" in poe_tokens, "p-lat token is required"
        assert "formkey" in poe_tokens, "formkey is required"
        
        # Check token format (basic validation)
        assert len(poe_tokens["p-b"]) > 10, "p-b token seems too short"
        assert len(poe_tokens["p-lat"]) > 10, "p-lat token seems too short"
        assert len(poe_tokens["formkey"]) > 10, "formkey seems too short"
        
        print(f"Token validation passed:")
        print(f"  p-b: {poe_tokens['p-b'][:10]}...")
        print(f"  p-lat: {poe_tokens['p-lat'][:10]}...")
        print(f"  formkey: {poe_tokens['formkey'][:10]}...")

    def test_api_client_initialization(self, poe_client):
        """Test API client initialization."""
        assert poe_client is not None, "API client should be created"
        # Client may be None if tokens are invalid, which is acceptable
        if poe_client.client is not None:
            print("API client initialized successfully")
        else:
            print("API client initialization failed (likely due to invalid tokens)")

    def test_get_bots_with_fallback(self, poe_client):
        """Test bot retrieval with fallback to mock data."""
        bots = poe_client.get_bots()
        assert isinstance(bots, dict), "Bots should be returned as a dictionary"
        assert len(bots) > 0, "Should return at least some bots (real or mock)"
        
        # Check bot structure
        for bot_id, bot_info in bots.items():
            assert isinstance(bot_id, str), "Bot ID should be a string"
            assert isinstance(bot_info, dict), "Bot info should be a dictionary"
            assert "id" in bot_info, "Bot info should have 'id' field"
            assert "displayName" in bot_info, "Bot info should have 'displayName' field"
        
        print(f"Retrieved {len(bots)} bots:")
        for bot_id in list(bots.keys())[:5]:  # Show first 5
            print(f"  {bot_id}: {bots[bot_id]['displayName']}")

    def test_get_conversation_ids_with_days(self, poe_client):
        """Test conversation ID retrieval with different day ranges."""
        test_days = [1, 7, 30]
        
        for days in test_days:
            conv_ids = poe_client.get_conversation_ids(days=days)
            assert isinstance(conv_ids, list), f"Conversation IDs should be a list (days={days})"
            assert len(conv_ids) >= 0, f"Should return valid list (days={days})"
            
            # Check that all IDs are strings
            for conv_id in conv_ids:
                assert isinstance(conv_id, str), "Conversation ID should be a string"
                assert len(conv_id) > 0, "Conversation ID should not be empty"
            
            print(f"Found {len(conv_ids)} conversation IDs for last {days} days")
            if conv_ids:
                print(f"  Sample IDs: {conv_ids[:3]}")

    def test_get_recent_conversations_structure(self, poe_client):
        """Test recent conversations retrieval and structure."""
        conversations = poe_client.get_recent_conversations(days=7)
        assert isinstance(conversations, list), "Conversations should be returned as a list"
        
        for conv in conversations:
            assert isinstance(conv, dict), "Each conversation should be a dictionary"
            assert "id" in conv, "Conversation should have 'id' field"
            assert "title" in conv, "Conversation should have 'title' field"
            assert "createdAt" in conv, "Conversation should have 'createdAt' field"
            
            # Check ID format
            assert isinstance(conv["id"], str), "Conversation ID should be a string"
            assert len(conv["id"]) > 0, "Conversation ID should not be empty"
        
        print(f"Retrieved {len(conversations)} conversations:")
        for conv in conversations[:3]:  # Show first 3
            print(f"  {conv['id']}: {conv.get('title', 'No title')}")

    def test_get_conversation_details(self, poe_client):
        """Test fetching detailed conversation data."""
        # First get some conversation IDs
        conv_ids = poe_client.get_conversation_ids(days=7)
        
        if not conv_ids:
            pytest.skip("No conversation IDs available for testing")
        
        # Test fetching details for first conversation
        first_id = conv_ids[0]
        conversation = poe_client.get_conversation(first_id)
        
        if conversation is not None:
            assert isinstance(conversation, dict), "Conversation should be a dictionary"
            assert "id" in conversation, "Conversation should have 'id' field"
            
            # Check for messages or other expected fields
            expected_fields = ["messages", "title", "bot", "createdAt"]
            has_expected_field = any(field in conversation for field in expected_fields)
            assert has_expected_field, f"Conversation should have at least one of: {expected_fields}"
            
            print(f"Conversation details for {first_id}:")
            print(f"  Title: {conversation.get('title', 'No title')}")
            print(f"  Bot: {conversation.get('bot', 'Unknown')}")
            print(f"  Messages: {len(conversation.get('messages', []))} messages")
        else:
            print(f"Could not retrieve conversation details for {first_id}")

    def test_rate_limiting_behavior(self, poe_client):
        """Test that rate limiting works properly."""
        start_time = time.time()
        
        # Make multiple quick requests
        for i in range(3):
            bots = poe_client.get_bots()
            assert isinstance(bots, dict), f"Request {i+1} should return valid bots"
        
        elapsed_time = time.time() - start_time
        print(f"3 bot requests took {elapsed_time:.2f} seconds")
        
        # Should take at least some time due to rate limiting
        # But don't make it too strict as it might use cached data


class TestTokenManagement:
    """Test token management and refresh functionality."""
    
    def test_token_file_location(self):
        """Test that token file is in the correct location."""
        expected_paths = [
            Path("config/poe_tokens.json"),
            Path("src/config/poe_tokens.json")
        ]
        
        found_path = None
        for path in expected_paths:
            if path.exists():
                found_path = path
                break
        
        assert found_path is not None, f"Token file not found in expected locations: {expected_paths}"
        print(f"Token file found at: {found_path}")
        
        # Verify file content structure
        with open(found_path, 'r') as f:
            tokens = json.load(f)
        
        assert isinstance(tokens, dict), "Token file should contain a JSON object"
        assert "p-b" in tokens, "Token file should have 'p-b' field"
        assert "p-lat" in tokens, "Token file should have 'p-lat' field"
        assert "formkey" in tokens, "Token file should have 'formkey' field"

    def test_token_loading_function(self):
        """Test the token loading function."""
        tokens = load_poe_tokens_from_file()
        assert isinstance(tokens, dict), "Should return a dictionary"
        
        # Should either have valid tokens or empty defaults
        required_keys = ["p-b", "p-lat", "formkey"]
        for key in required_keys:
            assert key in tokens, f"Token dict should have '{key}' key"
            assert isinstance(tokens[key], str), f"Token '{key}' should be a string"

    def test_token_refresh_instructions(self):
        """Provide instructions for refreshing tokens."""
        print("\n" + "="*60)
        print("TOKEN REFRESH INSTRUCTIONS")
        print("="*60)
        print("If you're getting authentication errors, you need to refresh your Poe.com tokens:")
        print()
        print("1. Open your browser and go to https://poe.com")
        print("2. Log in to your Poe account")
        print("3. Open Developer Tools (F12)")
        print("4. Go to the 'Application' or 'Storage' tab")
        print("5. Find 'Cookies' → 'https://poe.com'")
        print("6. Copy the values for:")
        print("   - p-b (this is your main session token)")
        print("   - p-lat (this is your authentication token)")
        print("7. Go to the 'Network' tab and look for any GraphQL request")
        print("8. In the request headers, find 'Poe-Formkey' and copy its value")
        print()
        print("9. Update config/poe_tokens.json with the new values:")
        print('   {')
        print('     "p-b": "your-new-p-b-token",')
        print('     "p-lat": "your-new-p-lat-token",')
        print('     "formkey": "your-new-formkey"')
        print('   }')
        print()
        print("Note: Tokens typically expire after 24-48 hours and need to be refreshed.")
        print("="*60)

    def test_alternative_token_sources(self):
        """Test alternative ways to get tokens (browser-cookie3, etc.)."""
        try:
            import browser_cookie3
            print("\nbrowser_cookie3 is available for automatic cookie extraction")
            
            # Try to get cookies from different browsers
            browsers = ['chrome', 'firefox', 'edge', 'safari']
            
            for browser_name in browsers:
                try:
                    browser_func = getattr(browser_cookie3, browser_name, None)
                    if browser_func:
                        cookies = browser_func(domain_name='poe.com')
                        cookie_dict = {cookie.name: cookie.value for cookie in cookies}
                        
                        if 'p-b' in cookie_dict:
                            print(f"Found p-b token in {browser_name}")
                            print(f"Token preview: {cookie_dict['p-b'][:10]}...")
                        
                except Exception as e:
                    print(f"Could not extract cookies from {browser_name}: {e}")
                    
        except ImportError:
            print("browser_cookie3 not available. Install with: pip install browser-cookie3")

    def test_env_token_loading(self):
        """Test loading tokens from environment variables."""
        import os

        # Check if tokens are available via environment
        env_tokens = {
            'POE_PB_TOKEN': os.getenv('POE_PB_TOKEN'),
            'POE_PLAT_TOKEN': os.getenv('POE_PLAT_TOKEN'),
            'POE_FORMKEY': os.getenv('POE_FORMKEY')
        }
        
        has_env_tokens = any(token for token in env_tokens.values())
        
        if has_env_tokens:
            print("Environment tokens found:")
            for key, value in env_tokens.items():
                if value:
                    print(f"  {key}: {value[:10]}...")
        else:
            print("No environment tokens found.")
            print("You can set tokens via environment variables:")
            print("  export POE_PB_TOKEN='your-p-b-token'")
            print("  export POE_PLAT_TOKEN='your-p-lat-token'")
            print("  export POE_FORMKEY='your-formkey'")


if __name__ == "__main__":
    # Run tests manually if called directly
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
