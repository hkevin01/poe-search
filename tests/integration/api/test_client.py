"""Tests for the main client functionality."""

import pytest
from unittest.mock import Mock, patch

from poe_search.client import PoeSearchClient


class TestPoeSearchClient:
    """Test cases for PoeSearchClient."""
    
    def test_client_initialization(self):
        """Test client initialization with default parameters."""
        client = PoeSearchClient(token="test_token")
        
        assert client.token == "test_token"
        assert client.database_url == "sqlite:///poe_search.db"
        assert client._api_client is None  # Lazy loading
        assert client._database is None  # Lazy loading
    
    def test_client_initialization_with_custom_params(self):
        """Test client initialization with custom parameters."""
        client = PoeSearchClient(
            token="test_token",
            database_url="sqlite:///custom.db",
        )
        
        assert client.token == "test_token"
        assert client.database_url == "sqlite:///custom.db"
    
    @patch('poe_search.client.PoeAPIClient')
    def test_api_client_property(self, mock_api_client_class):
        """Test lazy loading of API client."""
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        client = PoeSearchClient(token="test_token")
        
        # First access should create the client
        api_client = client.api_client
        assert api_client == mock_api_client
        mock_api_client_class.assert_called_once_with(token="test_token")
        
        # Second access should return the same instance
        api_client2 = client.api_client
        assert api_client2 == api_client
        assert mock_api_client_class.call_count == 1
    
    @patch('poe_search.client.Database')
    def test_database_property(self, mock_database_class):
        """Test lazy loading of database."""
        mock_database = Mock()
        mock_database_class.return_value = mock_database
        
        client = PoeSearchClient(token="test_token")
        
        # First access should create the database
        database = client.database
        assert database == mock_database
        mock_database_class.assert_called_once_with("sqlite:///poe_search.db")
        
        # Second access should return the same instance
        database2 = client.database
        assert database2 == database
        assert mock_database_class.call_count == 1
    
    def test_search(self, temp_db, sample_conversations):
        """Test search functionality."""
        # Setup test data
        for conv in sample_conversations:
            temp_db.save_conversation(conv)
        
        client = PoeSearchClient(token="test_token")
        client._database = temp_db
        
        # Test search
        results = client.search("machine learning", limit=5)
        
        assert len(results) > 0
        assert any("machine learning" in str(result).lower() for result in results)
    
    @patch('poe_search.client.PoeAPIClient')
    def test_sync(self, mock_api_client_class, temp_db, sample_conversations):
        """Test sync functionality."""
        mock_api_client = Mock()
        mock_api_client.get_recent_conversations.return_value = sample_conversations
        mock_api_client_class.return_value = mock_api_client
        
        client = PoeSearchClient(token="test_token")
        client._database = temp_db
        
        # Test sync
        stats = client.sync(days=7)
        
        assert stats["new"] == len(sample_conversations)
        assert stats["updated"] == 0
        assert stats["total"] == len(sample_conversations)
        
        mock_api_client.get_recent_conversations.assert_called_once_with(days=7)
    
    def test_get_conversations(self, temp_db, sample_conversations):
        """Test get_conversations functionality."""
        # Setup test data
        for conv in sample_conversations:
            temp_db.save_conversation(conv)
        
        client = PoeSearchClient(token="test_token")
        client._database = temp_db
        
        # Test get all conversations
        conversations = client.get_conversations()
        assert len(conversations) == len(sample_conversations)
        
        # Test filter by bot
        chinchilla_convs = client.get_conversations(bot="chinchilla")
        assert len(chinchilla_convs) == 1
        assert chinchilla_convs[0]["bot"] == "chinchilla"
    
    def test_get_bots(self, temp_db, sample_conversations):
        """Test get_bots functionality."""
        # Setup test data
        for conv in sample_conversations:
            temp_db.save_conversation(conv)
        
        client = PoeSearchClient(token="test_token")
        client._database = temp_db
        
        # Test get bots
        bots = client.get_bots()
        
        assert len(bots) == 2  # chinchilla and a2
        bot_names = [bot["name"] for bot in bots]
        assert "chinchilla" in bot_names
        assert "a2" in bot_names
    
    def test_get_analytics(self, temp_db, sample_conversations):
        """Test get_analytics functionality."""
        # Setup test data
        for conv in sample_conversations:
            temp_db.save_conversation(conv)
        
        client = PoeSearchClient(token="test_token")
        client._database = temp_db
        
        # Test analytics
        analytics = client.get_analytics(period="month")
        
        assert "total_conversations" in analytics
        assert "active_bots" in analytics
        assert "messages_sent" in analytics
        assert analytics["period"] == "month"
