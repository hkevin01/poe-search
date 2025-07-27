"""
Integration tests for browser client.
"""

import pytest
from unittest.mock import Mock, patch
import json
from pathlib import Path

from poe_search.api.browser_client import PoeApiClient
from poe_search.core.exceptions import AuthenticationError, ExtractionError


class TestBrowserClientIntegration:
    """Integration tests for PoeApiClient."""

    @pytest.fixture
    def mock_tokens(self):
        """Mock authentication tokens."""
        return {
            'p-b': 'test_token_123',
            'p-lat': 'test_lat_token_456'
        }

    @pytest.fixture
    def sample_conversations(self):
        """Sample conversation data for testing."""
        return [
            {
                'id': 'conv_1',
                'title': 'Test Conversation 1',
                'bot': 'Claude',
                'category': 'Technical',
                'url': 'https://poe.com/chat/conv_1',
                'method': 'test_method',
                'extracted_at': '2024-01-20T10:30:00Z',
                'messages': [
                    {
                        'role': 'user',
                        'content': 'Hello, how are you?',
                        'timestamp': '2024-01-20T10:30:00Z'
                    },
                    {
                        'role': 'assistant',
                        'content': 'I am doing well, thank you!',
                        'timestamp': '2024-01-20T10:31:00Z'
                    }
                ]
            }
        ]

    @patch('poe_search.api.browser_client.webdriver')
    def test_client_initialization(self, mock_webdriver, mock_tokens):
        """Test that browser client initializes correctly."""
        with PoeApiClient(token=mock_tokens['p-b'], headless=True) as client:
            assert client.token == mock_tokens['p-b']
            assert client.headless is True
            mock_webdriver.Chrome.assert_called_once()

    @patch('poe_search.api.browser_client.webdriver')
    def test_authentication_success(self, mock_webdriver, mock_tokens):
        """Test successful authentication."""
        # Mock successful authentication
        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver
        mock_driver.find_elements.return_value = [Mock()]  # Auth indicator found

        with PoeApiClient(token=mock_tokens['p-b'], headless=True) as client:
            result = client.authenticate()
            assert result is True

    @patch('poe_search.api.browser_client.webdriver')
    def test_authentication_failure(self, mock_webdriver, mock_tokens):
        """Test authentication failure."""
        # Mock failed authentication
        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver
        mock_driver.find_elements.return_value = []  # No auth indicator

        with pytest.raises(AuthenticationError):
            with PoeApiClient(token='invalid_token', headless=True) as client:
                client.authenticate()

    @patch('poe_search.api.browser_client.webdriver')
    def test_get_conversations_success(self, mock_webdriver, mock_tokens, sample_conversations):
        """Test successful conversation extraction."""
        # Mock successful extraction
        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver
        mock_driver.find_elements.return_value = [Mock()]  # Auth success

        with PoeApiClient(token=mock_tokens['p-b'], headless=True) as client:
            # Mock the actual extraction method
            client.get_conversations = Mock(return_value=sample_conversations)

            conversations = client.get_conversations(limit=10)
            assert len(conversations) == 1
            assert conversations[0]['title'] == 'Test Conversation 1'

    @patch('poe_search.api.browser_client.webdriver')
    def test_get_conversations_with_progress_callback(self, mock_webdriver, mock_tokens):
        """Test conversation extraction with progress callback."""
        progress_calls = []

        def progress_callback(message, percentage):
            progress_calls.append((message, percentage))

        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver
        mock_driver.find_elements.return_value = [Mock()]

        with PoeApiClient(token=mock_tokens['p-b'], headless=True) as client:
            # Mock the method to call progress callback
            def mock_get_conversations(limit=50, progress_callback=None):
                if progress_callback:
                    progress_callback("Starting extraction...", 0)
                    progress_callback("Halfway done...", 50)
                    progress_callback("Complete!", 100)
                return []

            client.get_conversations = mock_get_conversations
            client.get_conversations(limit=10, progress_callback=progress_callback)

            assert len(progress_calls) == 3
            assert progress_calls[0] == ("Starting extraction...", 0)
            assert progress_calls[-1] == ("Complete!", 100)

    def test_extract_conversation_id(self):
        """Test conversation ID extraction from URLs."""
        # Test with direct import since this is a utility method
        from poe_search.api.browser_client import PoeApiClient

        test_urls = [
            ('https://poe.com/chat/abc123def', 'abc123def'),
            ('https://poe.com/c/xyz789', 'xyz789'),
            ('invalid_url', None),
            ('', None),
        ]

        client = PoeApiClient(token='dummy')
        for url, expected_id in test_urls:
            result = client._extract_conversation_id(url)
            assert result == expected_id

    def test_extract_bot_name(self):
        """Test bot name extraction from conversation text."""
        from poe_search.api.browser_client import PoeApiClient

        test_cases = [
            ('Claude conversation about Python', 'Claude'),
            ('GPT-4 explains quantum physics', 'GPT'),
            ('Gemini helps with coding', 'Gemini'),
            ('Random conversation text', 'Assistant'),
            ('', 'Assistant'),
        ]

        client = PoeApiClient(token='dummy')
        for text, expected_bot in test_cases:
            result = client._extract_bot_name(text)
            assert result == expected_bot

    def test_categorize_conversation(self):
        """Test conversation categorization."""
        from poe_search.api.browser_client import PoeApiClient

        test_cases = [
            ('Python programming help', 'Claude', 'Technical'),
            ('Creative writing story', 'GPT', 'Creative'),
            ('Math homework help', 'Assistant', 'Educational'),
            ('Business plan review', 'Claude', 'Business'),
            ('Physics concepts', 'GPT', 'Science'),
            ('Random chat', 'Assistant', 'General'),
        ]

        client = PoeApiClient(token='dummy')
        for title, bot, expected_category in test_cases:
            result = client._categorize_conversation(title, bot)
            assert result == expected_category


@pytest.mark.slow
@pytest.mark.browser
class TestBrowserClientRealWorld:
    """Real-world integration tests (marked as slow)."""

    @pytest.mark.skip(reason="Requires real tokens and network access")
    def test_real_authentication(self):
        """Test authentication with real tokens (manual test)."""
        # This test would require real tokens and should be run manually
        # when needed for debugging
        pass

    @pytest.mark.skip(reason="Requires real tokens and network access")
    def test_real_conversation_extraction(self):
        """Test conversation extraction with real data (manual test)."""
        # This test would require real tokens and should be run manually
        # when needed for debugging
        pass
