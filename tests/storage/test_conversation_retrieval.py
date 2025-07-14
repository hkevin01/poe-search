"""
Test: Conversation retrieval and full text extraction from the Poe Search database.
"""
import pytest
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
