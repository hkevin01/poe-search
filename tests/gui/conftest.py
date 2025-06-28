"""Test configuration for GUI tests."""

import pytest
import sys
from unittest.mock import Mock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing GUI components."""
    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar)
    
    yield app
    
    # Clean up
    if app:
        app.quit()


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "database_url": "sqlite:///:memory:",
        "token": "test_token",
        "logging": {
            "level": "DEBUG",
            "format": "%(message)s"
        }
    }


@pytest.fixture
def mock_database():
    """Mock database for testing."""
    db = Mock()
    db.get_all_conversations.return_value = []
    db.get_conversation.return_value = None
    db.conversation_exists.return_value = False
    db.save_conversation.return_value = None
    return db


@pytest.fixture
def mock_client():
    """Mock Poe client for testing."""
    client = Mock()
    client.get_conversations.return_value = []
    client.get_conversation.return_value = None
    client.search.return_value = []
    return client


@pytest.fixture
def sample_conversations():
    """Sample conversation data for testing."""
    return [
        {
            "id": "conv1",
            "title": "Python Programming Help",
            "bot": "GPT-4",
            "category": "Technical",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:30:00Z",
            "message_count": 5,
            "messages": [
                {
                    "id": "msg1",
                    "sender": "User",
                    "content": "How do I create a class in Python?",
                    "timestamp": "2024-01-01T12:00:00Z"
                },
                {
                    "id": "msg2",
                    "sender": "GPT-4",
                    "content": "To create a class in Python, use the 'class' keyword...",
                    "timestamp": "2024-01-01T12:01:00Z"
                }
            ]
        },
        {
            "id": "conv2",
            "title": "Health Question",
            "bot": "Claude",
            "category": "Medical",
            "created_at": "2024-01-02T10:00:00Z",
            "updated_at": "2024-01-02T10:15:00Z",
            "message_count": 3,
            "messages": [
                {
                    "id": "msg3",
                    "sender": "User",
                    "content": "What are the symptoms of flu?",
                    "timestamp": "2024-01-02T10:00:00Z"
                }
            ]
        }
    ]
