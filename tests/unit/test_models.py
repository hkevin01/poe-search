"""
Unit tests for core models.
"""

import pytest
from datetime import datetime

from poe_search.core.models import Conversation, Message, ConversationCategory


class TestMessage:
    """Test cases for Message model."""

    def test_message_creation_valid(self):
        """Test creating a valid message."""
        message = Message(
            role="user",
            content="Hello, how are you?",
            timestamp="2024-01-20T10:30:00Z"
        )

        assert message.role == "user"
        assert message.content == "Hello, how are you?"
        assert message.timestamp == "2024-01-20T10:30:00Z"

    def test_message_invalid_role(self):
        """Test message creation with invalid role."""
        with pytest.raises(ValueError, match="Invalid message role"):
            Message(role="invalid", content="Test content")

    def test_message_empty_content(self):
        """Test message creation with empty content."""
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message(role="user", content="")

        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message(role="user", content="   ")


class TestConversation:
    """Test cases for Conversation model."""

    def test_conversation_creation_valid(self):
        """Test creating a valid conversation."""
        conversation = Conversation(
            id="test_123",
            title="Test Conversation",
            bot="Claude",
            category="Technical",
            url="https://poe.com/chat/test_123",
            method="test_method",
            extracted_at=datetime.now().isoformat()
        )

        assert conversation.id == "test_123"
        assert conversation.title == "Test Conversation"
        assert conversation.message_count == 0

    def test_conversation_empty_id(self):
        """Test conversation creation with empty ID."""
        with pytest.raises(ValueError, match="Conversation ID cannot be empty"):
            Conversation(
                id="",
                title="Test",
                bot="Claude",
                category="General",
                url="https://poe.com",
                method="test",
                extracted_at=datetime.now().isoformat()
            )

    def test_add_message(self):
        """Test adding messages to conversation."""
        conversation = Conversation(
            id="test_123",
            title="Test",
            bot="Claude",
            category="General",
            url="https://poe.com",
            method="test",
            extracted_at=datetime.now().isoformat()
        )

        message = Message(role="user", content="Hello")
        conversation.add_message(message)

        assert conversation.message_count == 1
        assert conversation.user_message_count == 1
        assert conversation.assistant_message_count == 0

    def test_to_dict_conversion(self):
        """Test conversation to dictionary conversion."""
        conversation = Conversation(
            id="test_123",
            title="Test",
            bot="Claude",
            category="General",
            url="https://poe.com",
            method="test",
            extracted_at="2024-01-20T10:30:00Z"
        )

        message = Message(role="user", content="Hello")
        conversation.add_message(message)

        data = conversation.to_dict()

        assert data["id"] == "test_123"
        assert data["title"] == "Test"
        assert len(data["messages"]) == 1
        assert data["messages"][0]["role"] == "user"

    def test_from_dict_creation(self):
        """Test creating conversation from dictionary."""
        data = {
            "id": "test_123",
            "title": "Test",
            "bot": "Claude",
            "category": "General",
            "url": "https://poe.com",
            "method": "test",
            "extracted_at": "2024-01-20T10:30:00Z",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                    "timestamp": "2024-01-20T10:30:00Z"
                }
            ]
        }

        conversation = Conversation.from_dict(data)

        assert conversation.id == "test_123"
        assert conversation.message_count == 1
        assert conversation.messages[0].role == "user"


class TestConversationCategory:
    """Test cases for ConversationCategory enum."""

    def test_category_values(self):
        """Test category enum values."""
        assert ConversationCategory.TECHNICAL.value == "Technical"
        assert ConversationCategory.CREATIVE.value == "Creative"
        assert ConversationCategory.GENERAL.value == "General"

    def test_category_membership(self):
        """Test category membership."""
        categories = list(ConversationCategory)

        assert ConversationCategory.TECHNICAL in categories
        assert ConversationCategory.GPT_CONVERSATIONS in categories
        assert len(categories) == 9  # Total number of categories
