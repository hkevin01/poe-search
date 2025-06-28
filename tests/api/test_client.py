"""Tests for API client functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

from poe_search.api.client import PoeAPIClient


class TestPoeAPIClient:
    """Test cases for the PoeAPIClient class."""
    
    def test_client_initialization(self):
        """Test client initializes with token."""
        client = PoeAPIClient("test_token")
        
        assert client.token == "test_token"
        assert client.base_url is not None
        assert client.session is not None
    
    @patch('poe_search.api.client.httpx.Client')
    def test_client_session_setup(self, mock_httpx):
        """Test HTTP client session setup."""
        mock_session = Mock()
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        
        # Verify session was created with correct headers
        mock_httpx.assert_called_once()
        call_kwargs = mock_httpx.call_args[1]
        assert "Authorization" in call_kwargs["headers"]
        assert call_kwargs["headers"]["Authorization"] == "Bearer test_token"
    
    @patch('poe_search.api.client.httpx.Client')
    def test_get_conversation_ids(self, mock_httpx):
        """Test getting conversation IDs."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "conversations": [
                {"id": "conv1", "title": "First Conversation"},
                {"id": "conv2", "title": "Second Conversation"}
            ]
        }
        mock_session.get.return_value = mock_response
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        conversation_ids = client.get_conversation_ids()
        
        assert conversation_ids == ["conv1", "conv2"]
        mock_session.get.assert_called_once()
    
    @patch('poe_search.api.client.httpx.Client')
    def test_get_conversation_details(self, mock_httpx):
        """Test getting conversation details."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "conv1",
            "title": "Test Conversation",
            "bot": "GPT-4",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:30:00Z",
            "messages": [
                {
                    "id": "msg1",
                    "sender": "User",
                    "content": "Hello",
                    "timestamp": "2024-01-01T12:00:00Z"
                },
                {
                    "id": "msg2",
                    "sender": "GPT-4",
                    "content": "Hi there!",
                    "timestamp": "2024-01-01T12:01:00Z"
                }
            ]
        }
        mock_session.get.return_value = mock_response
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        conversation = client.get_conversation("conv1")
        
        assert conversation["id"] == "conv1"
        assert conversation["title"] == "Test Conversation"
        assert len(conversation["messages"]) == 2
        mock_session.get.assert_called_once()
    
    @patch('poe_search.api.client.httpx.Client')
    def test_api_error_handling(self, mock_httpx):
        """Test API error handling."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_session.get.return_value = mock_response
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        conversation = client.get_conversation("nonexistent")
        
        assert conversation is None
    
    @patch('poe_search.api.client.httpx.Client')
    def test_authentication_error(self, mock_httpx):
        """Test authentication error handling."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_session.get.return_value = mock_response
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("invalid_token")
        
        with pytest.raises(Exception):  # Should raise authentication error
            client.get_conversation_ids()
    
    @patch('poe_search.api.client.httpx.Client')
    def test_rate_limiting(self, mock_httpx):
        """Test rate limiting handling."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_session.get.return_value = mock_response
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        
        # Should handle rate limiting gracefully
        result = client.get_conversation("conv1")
        assert result is None  # Or implement retry logic
    
    @patch('poe_search.api.client.httpx.Client')
    def test_get_conversation_info(self, mock_httpx):
        """Test getting basic conversation info."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "conv1",
            "title": "Test Conversation",
            "bot": "GPT-4",
            "updated_at": "2024-01-01T12:30:00Z",
            "message_count": 5
        }
        mock_session.get.return_value = mock_response
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        info = client.get_conversation_info("conv1")
        
        assert info["id"] == "conv1"
        assert info["message_count"] == 5
        assert "messages" not in info  # Should not include full messages
    
    @patch('poe_search.api.client.httpx.Client')
    def test_get_recent_conversation_ids(self, mock_httpx):
        """Test getting recent conversation IDs."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "conversations": [
                {
                    "id": "conv1",
                    "updated_at": "2024-01-02T12:00:00Z"
                },
                {
                    "id": "conv2", 
                    "updated_at": "2024-01-01T12:00:00Z"
                },
                {
                    "id": "conv3",
                    "updated_at": "2023-12-30T12:00:00Z"
                }
            ]
        }
        mock_session.get.return_value = mock_response
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        
        # Get conversations since Jan 1, 2024
        since_date = datetime(2024, 1, 1)
        recent_ids = client.get_recent_conversation_ids(since=since_date)
        
        # Should only return conv1 and conv2 (after Jan 1)
        assert len(recent_ids) == 2
        assert "conv1" in recent_ids
        assert "conv2" in recent_ids
        assert "conv3" not in recent_ids
    
    @patch('poe_search.api.client.httpx.Client')
    def test_pagination_handling(self, mock_httpx):
        """Test handling paginated API responses."""
        mock_session = Mock()
        
        # Mock first page
        mock_response_1 = Mock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {
            "conversations": [
                {"id": "conv1", "title": "First"},
                {"id": "conv2", "title": "Second"}
            ],
            "next_page": "page2_token"
        }
        
        # Mock second page
        mock_response_2 = Mock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            "conversations": [
                {"id": "conv3", "title": "Third"},
                {"id": "conv4", "title": "Fourth"}
            ],
            "next_page": None
        }
        
        mock_session.get.side_effect = [mock_response_1, mock_response_2]
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        conversation_ids = client.get_conversation_ids()
        
        # Should return all conversation IDs from both pages
        assert len(conversation_ids) == 4
        assert "conv1" in conversation_ids
        assert "conv4" in conversation_ids
        
        # Should have made two API calls
        assert mock_session.get.call_count == 2
    
    @patch('poe_search.api.client.httpx.Client')
    def test_connection_error_handling(self, mock_httpx):
        """Test handling connection errors."""
        mock_session = Mock()
        mock_session.get.side_effect = ConnectionError("Network error")
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        
        # Should handle connection errors gracefully
        result = client.get_conversation_ids()
        assert result == []  # Should return empty list on error
    
    @patch('poe_search.api.client.httpx.Client')
    def test_timeout_handling(self, mock_httpx):
        """Test handling request timeouts."""
        import httpx
        
        mock_session = Mock()
        mock_session.get.side_effect = httpx.TimeoutException("Request timeout")
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        
        # Should handle timeouts gracefully
        result = client.get_conversation("conv1")
        assert result is None
    
    def test_url_construction(self):
        """Test API URL construction."""
        client = PoeAPIClient("test_token")
        
        # Test conversation list URL
        list_url = client._build_url("conversations")
        assert "conversations" in list_url
        
        # Test specific conversation URL
        conv_url = client._build_url("conversations", "conv123")
        assert "conversations/conv123" in conv_url
    
    def test_headers_configuration(self):
        """Test HTTP headers configuration."""
        client = PoeAPIClient("test_token")
        
        headers = client._get_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token"
        assert "Content-Type" in headers
        assert "User-Agent" in headers


class TestPoeAPIClientIntegration:
    """Integration tests for PoeAPIClient."""
    
    @patch('poe_search.api.client.httpx.Client')
    def test_full_sync_workflow(self, mock_httpx):
        """Test complete sync workflow."""
        mock_session = Mock()
        
        # Mock conversation list response
        list_response = Mock()
        list_response.status_code = 200
        list_response.json.return_value = {
            "conversations": [
                {"id": "conv1", "title": "First"},
                {"id": "conv2", "title": "Second"}
            ]
        }
        
        # Mock individual conversation responses
        conv1_response = Mock()
        conv1_response.status_code = 200
        conv1_response.json.return_value = {
            "id": "conv1",
            "title": "First Conversation",
            "bot": "GPT-4",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:30:00Z",
            "messages": [
                {
                    "id": "msg1",
                    "sender": "User",
                    "content": "Hello",
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            ]
        }
        
        conv2_response = Mock()
        conv2_response.status_code = 200
        conv2_response.json.return_value = {
            "id": "conv2",
            "title": "Second Conversation",
            "bot": "Claude",
            "created_at": "2024-01-02T10:00:00Z", 
            "updated_at": "2024-01-02T10:15:00Z",
            "messages": [
                {
                    "id": "msg2",
                    "sender": "User",
                    "content": "Hi there",
                    "timestamp": "2024-01-02T10:00:00Z"
                }
            ]
        }
        
        mock_session.get.side_effect = [list_response, conv1_response, conv2_response]
        mock_httpx.return_value = mock_session
        
        client = PoeAPIClient("test_token")
        
        # Get conversation IDs
        conversation_ids = client.get_conversation_ids()
        assert len(conversation_ids) == 2
        
        # Get each conversation
        conversations = []
        for conv_id in conversation_ids:
            conv_data = client.get_conversation(conv_id)
            if conv_data:
                conversations.append(conv_data)
        
        assert len(conversations) == 2
        assert conversations[0]["id"] == "conv1"
        assert conversations[1]["id"] == "conv2"
        
        # Verify correct number of API calls
        assert mock_session.get.call_count == 3  # 1 list + 2 individual
