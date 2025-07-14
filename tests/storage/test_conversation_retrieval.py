"""
Test: Conversation retrieval and full text extraction from Poe Search database.
"""
from pathlib import Path
from poe_search.storage.database import Database


def test_conversation_listing():
    """Test that all conversations can be listed from the database."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    conversations = db.get_conversations()
    assert isinstance(conversations, list)
    assert len(conversations) > 0, "No conversations found in database!"
    # Check basic fields
    for conv in conversations:
        assert "id" in conv
        assert "bot" in conv
        assert "title" in conv
        assert "created_at" in conv
        assert "message_count" in conv


def test_full_conversation_text():
    """Test that full conversation text can be retrieved for each conversation."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    conversations = db.get_conversations()
    for conv in conversations:
        conv_id = conv["id"]
        full_conv = db.get_conversation(conv_id)
        assert full_conv is not None, f"Conversation {conv_id} not found!"
        assert "messages" in full_conv
        assert isinstance(full_conv["messages"], list)
        # Check that at least one message has text
        has_text = any(m.get("text") for m in full_conv["messages"])
        assert has_text, f"No message text found in conversation {conv_id}!"


def test_invalid_conversation_id():
    """Test retrieval with invalid conversation IDs."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    
    # Test with non-existent ID
    result = db.get_conversation("non_existent_id_12345")
    assert result is None
    
    # Test with empty string
    result = db.get_conversation("")
    assert result is None
    
    # Test with None
    result = db.get_conversation(None)
    assert result is None


def test_conversation_message_structure():
    """Test that conversation messages have proper structure."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    conversations = db.get_conversations(limit=5)  # Test first 5
    
    for conv in conversations:
        full_conv = db.get_conversation(conv["id"])
        messages = full_conv.get("messages", [])
        
        for msg in messages:
            # Check required message fields
            assert "id" in msg, f"Message missing ID in conv {conv['id']}"
            assert "text" in msg, f"Message missing text in conv {conv['id']}"
            assert "timestamp" in msg, f"Message missing timestamp in conv {conv['id']}"
            assert "sender" in msg, f"Message missing sender in conv {conv['id']}"
            
            # Validate message text is not empty
            assert msg["text"].strip(), f"Empty message text in conv {conv['id']}"


def test_conversation_filtering():
    """Test conversation filtering by bot and date range."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    
    # Get all conversations first
    all_conversations = db.get_conversations()
    
    # Test bot filtering
    if all_conversations:
        first_bot = all_conversations[0]["bot"]
        filtered_by_bot = db.get_conversations(bot=first_bot)
        assert len(filtered_by_bot) <= len(all_conversations)
        for conv in filtered_by_bot:
            assert conv["bot"] == first_bot
    
    # Test date filtering (last 30 days)
    recent_conversations = db.get_conversations(days=30)
    assert len(recent_conversations) <= len(all_conversations)
    
    # Test limit
    limited_conversations = db.get_conversations(limit=3)
    assert len(limited_conversations) <= min(3, len(all_conversations))


def test_empty_conversation_handling():
    """Test handling of conversations with no messages."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    conversations = db.get_conversations()
    
    for conv in conversations:
        full_conv = db.get_conversation(conv["id"])
        messages = full_conv.get("messages", [])
        
        if len(messages) == 0:
            # If we find an empty conversation, ensure it's handled gracefully
            assert conv["message_count"] == 0
            print(f"Found empty conversation: {conv['id']}")


def test_conversation_data_integrity():
    """Test data integrity of conversation fields."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    conversations = db.get_conversations()
    
    for conv in conversations:
        # Test ID format
        assert conv["id"], "Conversation ID should not be empty"
        assert isinstance(conv["id"], str), "Conversation ID should be string"
        
        # Test bot field
        assert conv["bot"], "Bot field should not be empty"
        assert isinstance(conv["bot"], str), "Bot should be string"
        
        # Test created_at format
        assert conv["created_at"], "created_at should not be empty"
        
        # Test message_count is non-negative
        assert conv["message_count"] >= 0, "Message count should be non-negative"
        
        # Verify message count matches actual messages
        full_conv = db.get_conversation(conv["id"])
        actual_count = len(full_conv.get("messages", []))
        expected_count = conv["message_count"]
        assert actual_count == expected_count, (
            f"Message count mismatch for {conv['id']}: "
            f"expected {expected_count}, got {actual_count}"
        )


def test_large_conversation_handling():
    """Test handling of conversations with many messages."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    conversations = db.get_conversations()
    
    # Find conversation with most messages
    largest_conv = max(conversations, key=lambda x: x["message_count"])
    
    if largest_conv["message_count"] > 10:  # Only test if we have large convs
        full_conv = db.get_conversation(largest_conv["id"])
        messages = full_conv.get("messages", [])
        
        # Ensure all messages are retrievable
        assert len(messages) == largest_conv["message_count"]
        
        # Test that text content is preserved
        total_chars = sum(len(msg.get("text", "")) for msg in messages)
        assert total_chars > 0, "Large conversation should have text content"
        
        print(f"Tested large conversation {largest_conv['id']} "
              f"with {len(messages)} messages")


def test_search_functionality():
    """Test that conversations can be searched by text content."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    
    # Get a sample conversation to extract search terms
    conversations = db.get_conversations(limit=1)
    if conversations:
        full_conv = db.get_conversation(conversations[0]["id"])
        messages = full_conv.get("messages", [])
        
        if messages and messages[0].get("text"):
            # Extract first word from first message for search
            first_text = messages[0]["text"]
            words = first_text.split()
            if words:
                search_term = words[0].lower()
                
                # Perform search using database method if available
                if hasattr(db, 'search_messages'):
                    results = db.search_messages(search_term)
                    assert isinstance(results, list)
                    # Should find at least the conversation we got the term from
                    found_ids = [r.get("conversation_id") for r in results]
                    assert conversations[0]["id"] in found_ids
