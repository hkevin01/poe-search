"""Tests for database functionality."""

import pytest
import json
from datetime import datetime, timedelta

from poe_search.storage.database import Database


class TestDatabase:
    """Test cases for Database class."""
    
    def test_database_initialization(self, temp_db):
        """Test database initialization and table creation."""
        # Database should be initialized with tables
        with temp_db._get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert "conversations" in tables
            assert "messages" in tables
            assert "bots" in tables
            assert "messages_fts" in tables
    
    def test_conversation_exists(self, temp_db, sample_conversation):
        """Test conversation existence check."""
        # Initially should not exist
        assert not temp_db.conversation_exists("conv_123")
        
        # Save conversation
        temp_db.save_conversation(sample_conversation)
        
        # Now should exist
        assert temp_db.conversation_exists("conv_123")
    
    def test_save_conversation(self, temp_db, sample_conversation):
        """Test saving a conversation."""
        temp_db.save_conversation(sample_conversation)
        
        # Check conversation was saved
        with temp_db._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM conversations WHERE id = ?", ("conv_123",))
            row = cursor.fetchone()
            
            assert row is not None
            assert row["id"] == "conv_123"
            assert row["bot"] == "chinchilla"
            assert row["title"] == "Test Conversation"
            assert row["message_count"] == 4
        
        # Check messages were saved
        with temp_db._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = ?", ("conv_123",))
            count = cursor.fetchone()[0]
            assert count == 4
        
        # Check FTS index was populated
        with temp_db._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messages_fts WHERE conversation_id = ?", ("conv_123",))
            count = cursor.fetchone()[0]
            assert count == 4
    
    def test_get_conversations(self, temp_db, sample_conversations):
        """Test retrieving conversations."""
        # Save test data
        for conv in sample_conversations:
            temp_db.save_conversation(conv)
        
        # Get all conversations
        conversations = temp_db.get_conversations()
        assert len(conversations) == 2
        
        # Test filtering by bot
        chinchilla_convs = temp_db.get_conversations(bot="chinchilla")
        assert len(chinchilla_convs) == 1
        assert chinchilla_convs[0]["bot"] == "chinchilla"
        
        # Test limit
        limited_convs = temp_db.get_conversations(limit=1)
        assert len(limited_convs) == 1
    
    def test_search_messages(self, temp_db, sample_conversations):
        """Test full-text search of messages."""
        # Save test data
        for conv in sample_conversations:
            temp_db.save_conversation(conv)
        
        # Search for "machine learning"
        results = temp_db.search_messages("machine learning")
        assert len(results) > 0
        
        # Check that results contain the search term
        found_match = False
        for result in results:
            if "machine learning" in result["content"].lower():
                found_match = True
                break
        assert found_match
        
        # Search with bot filter
        results = temp_db.search_messages("Python", bot="a2")
        assert len(results) > 0
        assert all(result["conversation_bot"] == "a2" for result in results)
    
    def test_get_bots(self, temp_db, sample_conversations):
        """Test retrieving bot information."""
        # Save test data
        for conv in sample_conversations:
            temp_db.save_conversation(conv)
        
        # Get bots
        bots = temp_db.get_bots()
        assert len(bots) == 2
        
        # Check bot data
        bot_names = [bot["name"] for bot in bots]
        assert "chinchilla" in bot_names
        assert "a2" in bot_names
        
        # Check conversation counts
        for bot in bots:
            assert bot["conversation_count"] >= 1
    
    def test_get_analytics(self, temp_db, sample_conversations):
        """Test analytics generation."""
        # Save test data
        for conv in sample_conversations:
            temp_db.save_conversation(conv)
        
        # Get analytics
        analytics = temp_db.get_analytics(period="month")
        
        assert analytics["total_conversations"] == 2
        assert analytics["active_bots"] == 2
        assert analytics["messages_sent"] == 2  # 2 user messages
        assert analytics["avg_conversation_length"] == 3.0  # (4+2)/2
    
    def test_update_conversation(self, temp_db, sample_conversation):
        """Test updating an existing conversation."""
        # Save initial conversation
        temp_db.save_conversation(sample_conversation)
        
        # Modify and update
        sample_conversation["title"] = "Updated Title"
        sample_conversation["message_count"] = 5
        temp_db.update_conversation(sample_conversation)
        
        # Check update
        conversations = temp_db.get_conversations()
        assert len(conversations) == 1
        assert conversations[0]["title"] == "Updated Title"
    
    def test_bot_info_update(self, temp_db, sample_conversation):
        """Test bot information is updated correctly."""
        temp_db.save_conversation(sample_conversation)
        
        # Check bot was created/updated
        with temp_db._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM bots WHERE id = ?", ("chinchilla",))
            bot_row = cursor.fetchone()
            
            assert bot_row is not None
            assert bot_row["conversation_count"] == 1
            assert bot_row["display_name"] == "Chinchilla"  # Auto-generated from ID
    
    def test_date_filtering(self, temp_db):
        """Test filtering conversations by date."""
        # Create conversations with different dates
        old_conv = {
            "id": "old_conv",
            "bot": "chinchilla",
            "title": "Old Conversation",
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "message_count": 1,
            "messages": [],
        }
        
        recent_conv = {
            "id": "recent_conv",
            "bot": "chinchilla",
            "title": "Recent Conversation",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 1,
            "messages": [],
        }
        
        temp_db.save_conversation(old_conv)
        temp_db.save_conversation(recent_conv)
        
        # Test filtering by days
        recent_conversations = temp_db.get_conversations(days=5)
        assert len(recent_conversations) == 1
        assert recent_conversations[0]["id"] == "recent_conv"
