"""Tests for conversation search and listing functionality."""

import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from poe_search.storage.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    
    # Create database
    db = Database(f"sqlite:///{db_path}")
    
    yield db
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_conversations():
    """Sample conversations with varying content for testing."""
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    last_week = now - timedelta(days=7)
    
    return [
        {
            "id": "conv_001",
            "bot": "gpt-4",
            "title": "Python Programming Help",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "message_count": 3,
            "messages": [
                {
                    "id": "msg_001",
                    "conversation_id": "conv_001",
                    "role": "user",
                    "content": ("How do I implement a binary search "
                                "in Python?"),
                    "timestamp": now.isoformat(),
                    "bot": None
                },
                {
                    "id": "msg_002",
                    "conversation_id": "conv_001",
                    "role": "bot",
                    "content": ("Here's how to implement binary search "
                                "in Python: def binary_search(arr, target): "
                                "left, right = 0, len(arr) - 1..."),
                    "timestamp": now.isoformat(),
                    "bot": "gpt-4"
                },
                {
                    "id": "msg_003",
                    "conversation_id": "conv_001",
                    "role": "user",
                    "content": "Can you explain the time complexity?",
                    "timestamp": now.isoformat(),
                    "bot": None
                }
            ]
        },
        {
            "id": "conv_002",
            "bot": "claude-3",
            "title": "JavaScript Debugging",
            "created_at": yesterday.isoformat(),
            "updated_at": yesterday.isoformat(),
            "message_count": 2,
            "messages": [
                {
                    "id": "msg_004",
                    "conversation_id": "conv_002",
                    "role": "user",
                    "content": ("My JavaScript code has a syntax error. "
                                "Can you help?"),
                    "timestamp": yesterday.isoformat(),
                    "bot": None
                },
                {
                    "id": "msg_005",
                    "conversation_id": "conv_002",
                    "role": "bot",
                    "content": ("I'd be happy to help debug your JavaScript "
                                "code. Please share the code with the "
                                "syntax error."),
                    "timestamp": yesterday.isoformat(),
                    "bot": "claude-3"
                }
            ]
        },
        {
            "id": "conv_003",
            "bot": "gpt-4",
            "title": "Machine Learning Concepts",
            "created_at": last_week.isoformat(),
            "updated_at": last_week.isoformat(),
            "message_count": 4,
            "messages": [
                {
                    "id": "msg_006",
                    "conversation_id": "conv_003",
                    "role": "user",
                    "content": ("What is the difference between supervised "
                                "and unsupervised learning?"),
                    "timestamp": last_week.isoformat(),
                    "bot": None
                },
                {
                    "id": "msg_007",
                    "conversation_id": "conv_003",
                    "role": "bot",
                    "content": ("Supervised learning uses labeled data to "
                                "train models, while unsupervised learning "
                                "finds patterns in unlabeled data."),
                    "timestamp": last_week.isoformat(),
                    "bot": "gpt-4"
                },
                {
                    "id": "msg_008",
                    "conversation_id": "conv_003",
                    "role": "user",
                    "content": "Can you give examples of each?",
                    "timestamp": last_week.isoformat(),
                    "bot": None
                },
                {
                    "id": "msg_009",
                    "conversation_id": "conv_003",
                    "role": "bot",
                    "content": ("Examples of supervised learning include "
                                "classification and regression. Examples of "
                                "unsupervised learning include clustering "
                                "and dimensionality reduction."),
                    "timestamp": last_week.isoformat(),
                    "bot": "gpt-4"
                }
            ]
        },
        {
            "id": "conv_004",
            "bot": "chatgpt",
            "title": "Recipe Ideas",
            "created_at": (now - timedelta(days=3)).isoformat(),
            "updated_at": (now - timedelta(days=3)).isoformat(),
            "message_count": 2,
            "messages": [
                {
                    "id": "msg_010",
                    "conversation_id": "conv_004",
                    "role": "user",
                    "content": ("I need ideas for dinner tonight. "
                                "I have chicken and vegetables."),
                    "timestamp": (now - timedelta(days=3)).isoformat(),
                    "bot": None
                },
                {
                    "id": "msg_011",
                    "conversation_id": "conv_004",
                    "role": "bot",
                    "content": ("Here are some great dinner ideas with "
                                "chicken and vegetables: 1. Chicken stir-fry, "
                                "2. Roasted chicken with seasonal vegetables, "
                                "3. Chicken and vegetable soup."),
                    "timestamp": (now - timedelta(days=3)).isoformat(),
                    "bot": "chatgpt"
                }
            ]
        }
    ]


@pytest.fixture
def populated_db(temp_db, sample_conversations):
    """Database populated with sample conversations."""
    for conv in sample_conversations:
        temp_db.save_conversation(conv)
    return temp_db


class TestConversationListing:
    """Test conversation listing functionality."""
    
    def test_get_all_conversations(self, populated_db):
        """Test getting all conversations."""
        conversations = populated_db.get_conversations()
        
        assert len(conversations) == 4
        # Should be ordered by updated_at DESC
        assert conversations[0]["id"] == "conv_001"  # Most recent
        assert conversations[1]["id"] == "conv_004"  # 3 days ago
        assert conversations[2]["id"] == "conv_002"  # Yesterday
        assert conversations[3]["id"] == "conv_003"  # Last week
    
    def test_get_conversations_by_bot(self, populated_db):
        """Test filtering conversations by bot."""
        # Filter by gpt-4
        gpt4_conversations = populated_db.get_conversations(bot="gpt-4")
        assert len(gpt4_conversations) == 2
        assert all(conv["bot"] == "gpt-4" for conv in gpt4_conversations)
        
        # Filter by claude-3
        claude_conversations = populated_db.get_conversations(bot="claude-3")
        assert len(claude_conversations) == 1
        assert claude_conversations[0]["bot"] == "claude-3"
        
        # Filter by non-existent bot
        none_conversations = populated_db.get_conversations(
            bot="non-existent"
        )
        assert len(none_conversations) == 0
    
    def test_get_conversations_by_date_range(self, populated_db):
        """Test filtering conversations by date range."""
        # Get conversations from last 2 days
        recent_conversations = populated_db.get_conversations(days=2)
        # conv_001 (today) and conv_002 (yesterday)
        assert len(recent_conversations) == 2
        
        # Get conversations from last week
        week_conversations = populated_db.get_conversations(days=7)
        # All except conv_003 (8 days ago)
        assert len(week_conversations) == 3
        
        # Get conversations from last month
        month_conversations = populated_db.get_conversations(days=30)
        assert len(month_conversations) == 4  # All conversations
    
    def test_get_conversations_with_limit(self, populated_db):
        """Test limiting the number of conversations returned."""
        # Get only 2 conversations
        limited_conversations = populated_db.get_conversations(limit=2)
        assert len(limited_conversations) == 2
        # Should get the 2 most recent
        assert limited_conversations[0]["id"] == "conv_001"
        assert limited_conversations[1]["id"] == "conv_004"
    
    def test_get_conversations_combined_filters(self, populated_db):
        """Test combining multiple filters."""
        # Get gpt-4 conversations from last 2 days, limit 1
        filtered_conversations = populated_db.get_conversations(
            bot="gpt-4",
            days=2,
            limit=1
        )
        assert len(filtered_conversations) == 1
        assert filtered_conversations[0]["id"] == "conv_001"
        assert filtered_conversations[0]["bot"] == "gpt-4"
    
    def test_get_single_conversation(self, populated_db):
        """Test getting a single conversation by ID."""
        conversation = populated_db.get_conversation("conv_001")
        
        assert conversation is not None
        assert conversation["id"] == "conv_001"
        assert conversation["title"] == "Python Programming Help"
        assert conversation["bot"] == "gpt-4"
        assert conversation["message_count"] == 3
    
    def test_get_nonexistent_conversation(self, populated_db):
        """Test getting a conversation that doesn't exist."""
        conversation = populated_db.get_conversation("nonexistent")
        assert conversation is None


class TestMessageSearch:
    """Test message search functionality."""
    
    def test_search_messages_basic(self, populated_db):
        """Test basic message search."""
        results = populated_db.search_messages("Python")
        
        assert len(results) >= 1
        # Should find the message about binary search in Python
        python_result = next(
            (r for r in results if "binary search" in r["content"]),
            None
        )
        assert python_result is not None
        assert python_result["conversation_id"] == "conv_001"
        assert python_result["conversation_title"] == "Python Programming Help"
    
    def test_search_messages_javascript(self, populated_db):
        """Test searching for JavaScript-related messages."""
        results = populated_db.search_messages("JavaScript")
        
        assert len(results) >= 1
        js_result = next(
            (r for r in results if "JavaScript" in r["content"]),
            None
        )
        assert js_result is not None
        assert js_result["conversation_id"] == "conv_002"
        assert js_result["conversation_title"] == "JavaScript Debugging"
    
    def test_search_messages_with_bot_filter(self, populated_db):
        """Test searching messages filtered by bot."""
        # Search for learning content from gpt-4 only
        results = populated_db.search_messages("learning", bot="gpt-4")
        
        assert len(results) >= 1
        # All results should be from gpt-4 conversations
        for result in results:
            assert result["conversation_bot"] == "gpt-4"
    
    def test_search_messages_with_limit(self, populated_db):
        """Test limiting search results."""
        # Search with a limit
        results = populated_db.search_messages("the", limit=2)
        assert len(results) <= 2
    
    def test_search_messages_case_insensitive(self, populated_db):
        """Test that search is case insensitive."""
        # Search for both cases
        lower_results = populated_db.search_messages("python")
        upper_results = populated_db.search_messages("PYTHON")
        mixed_results = populated_db.search_messages("Python")
        
        # Should return the same results (may vary in order due to ranking)
        assert len(lower_results) == len(upper_results) == len(mixed_results)
    
    def test_search_messages_no_results(self, populated_db):
        """Test search with no matching results."""
        results = populated_db.search_messages("xyznothingmatches")
        assert len(results) == 0
    
    def test_search_messages_complex_query(self, populated_db):
        """Test search with complex queries."""
        # Search for multiple terms
        results = populated_db.search_messages("supervised unsupervised")
        
        # Should find the machine learning conversation
        assert len(results) >= 1
        ml_result = next(
            (r for r in results if "conv_003" == r["conversation_id"]),
            None
        )
        assert ml_result is not None
    
    def test_search_messages_result_structure(self, populated_db):
        """Test that search results have the correct structure."""
        results = populated_db.search_messages("help")
        
        if results:  # If there are results
            result = results[0]
            # Check required fields
            required_fields = [
                "id", "conversation_id", "role", "content", "timestamp",
                "bot", "conversation_title", "conversation_bot"
            ]
            for field in required_fields:
                assert field in result
            
            # Check that conversation_id matches a known conversation
            expected_convs = ["conv_001", "conv_002", "conv_003", "conv_004"]
            assert result["conversation_id"] in expected_convs


class TestEmptyDatabase:
    """Test behavior with empty database."""
    
    def test_get_conversations_empty_db(self, temp_db):
        """Test getting conversations from empty database."""
        conversations = temp_db.get_conversations()
        assert len(conversations) == 0
    
    def test_search_messages_empty_db(self, temp_db):
        """Test searching messages in empty database."""
        results = temp_db.search_messages("anything")
        assert len(results) == 0
    
    def test_get_single_conversation_empty_db(self, temp_db):
        """Test getting single conversation from empty database."""
        conversation = temp_db.get_conversation("nonexistent")
        assert conversation is None


class TestBotListing:
    """Test bot listing functionality."""
    
    def test_get_bots(self, populated_db):
        """Test getting all bots."""
        bots = populated_db.get_bots()
        
        # Should have at least the bots from our test data
        bot_names = [bot["name"] for bot in bots]
        expected_bots = ["gpt-4", "claude-3", "chatgpt"]
        
        for expected_bot in expected_bots:
            assert expected_bot in bot_names
    
    def test_get_bots_empty_db(self, temp_db):
        """Test getting bots from empty database."""
        bots = temp_db.get_bots()
        assert len(bots) == 0


class TestDatabaseRobustness:
    """Test database robustness and edge cases."""
    
    def test_conversation_exists_edge_cases(self, temp_db):
        """Test conversation_exists with edge cases."""
        # Test with None
        assert not temp_db.conversation_exists("")
        
        # Test with very long ID
        long_id = "x" * 1000
        assert not temp_db.conversation_exists(long_id)
    
    def test_search_with_special_characters(self, populated_db):
        """Test search with special characters."""
        # These should not crash the search
        special_queries = ["'", '"', "\\", "%", "_", "(", ")", "[", "]"]
        
        for query in special_queries:
            try:
                results = populated_db.search_messages(query)
                # Should return a list (possibly empty)
                assert isinstance(results, list)
            except Exception as e:
                msg = f"Search with special character '{query}' failed: {e}"
                pytest.fail(msg)
    
    def test_get_conversations_with_invalid_params(self, populated_db):
        """Test get_conversations with invalid parameters."""
        # These should not crash
        conversations = populated_db.get_conversations(days=-1)
        assert isinstance(conversations, list)
        
        conversations = populated_db.get_conversations(limit=0)
        assert isinstance(conversations, list)
        
        conversations = populated_db.get_conversations(limit=-1)
        assert isinstance(conversations, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
