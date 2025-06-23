"""Test configuration and fixtures."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock

from poe_search.storage.database import Database
from poe_search.api.client import PoeAPIClient


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    db = Database(f"sqlite:///{db_path}")
    yield db
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def mock_api_client():
    """Create a mock API client for testing."""
    client = Mock(spec=PoeAPIClient)
    client.token = "test_token"
    
    # Mock bot data
    client._bots = {
        "chinchilla": {"displayName": "ChatGPT", "id": "chinchilla"},
        "a2": {"displayName": "Claude-instant", "id": "a2"},
    }
    client._bot_names = {
        "chinchilla": "ChatGPT",
        "a2": "Claude-instant",
    }
    
    return client


@pytest.fixture
def sample_conversation():
    """Sample conversation data for testing."""
    return {
        "id": "conv_123",
        "bot": "chinchilla",
        "title": "Test Conversation",
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-01T11:00:00",
        "message_count": 4,
        "messages": [
            {
                "id": "msg_1",
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": "2024-01-01T10:00:00",
            },
            {
                "id": "msg_2",
                "role": "bot",
                "content": "I'm doing well, thank you! How can I help you today?",
                "timestamp": "2024-01-01T10:01:00",
                "bot": "chinchilla",
            },
            {
                "id": "msg_3",
                "role": "user",
                "content": "Can you explain machine learning?",
                "timestamp": "2024-01-01T10:02:00",
            },
            {
                "id": "msg_4",
                "role": "bot",
                "content": "Machine learning is a subset of artificial intelligence...",
                "timestamp": "2024-01-01T10:03:00",
                "bot": "chinchilla",
            },
        ],
    }


@pytest.fixture
def sample_conversations(sample_conversation):
    """Multiple sample conversations for testing."""
    conversations = [sample_conversation]
    
    # Add a second conversation
    conv2 = {
        "id": "conv_456",
        "bot": "a2",
        "title": "Python Programming",
        "created_at": "2024-01-02T10:00:00",
        "updated_at": "2024-01-02T11:00:00",
        "message_count": 2,
        "messages": [
            {
                "id": "msg_5",
                "role": "user",
                "content": "How do I use Python decorators?",
                "timestamp": "2024-01-02T10:00:00",
            },
            {
                "id": "msg_6",
                "role": "bot",
                "content": "Python decorators are a powerful feature that allows you to modify functions...",
                "timestamp": "2024-01-02T10:01:00",
                "bot": "a2",
            },
        ],
    }
    
    conversations.append(conv2)
    return conversations
