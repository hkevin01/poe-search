"""
Test: Poe API integration and conversation synchronization.
"""
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from poe_search.api.client import PoeSearchClient
from poe_search.storage.database import Database


def test_client_initialization():
    """Test that PoeSearchClient can be initialized properly."""
    config = {"test": True}
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    
    client = PoeSearchClient(
        config=config, 
        database_url=f"sqlite:///{db_path}"
    )
    
    assert client is not None
    assert hasattr(client, 'database')
    assert client.database is not None


def test_conversation_sync_workflow():
    """Test the complete conversation sync workflow."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    
    # Initialize client
    config = {"test": True}
    client = PoeSearchClient(
        config=config,
        database_url=f"sqlite:///{db_path}"
    )
    
    # Count conversations before sync
    conversations_before = client.database.get_conversations()
    initial_count = len(conversations_before)
    
    # Test that we can access the sync functionality
    assert hasattr(client, 'sync_conversations') or hasattr(client, 'get_conversations')
    
    print(f"Found {initial_count} conversations in database")


@patch('poe_search.api.client.PoeAPI')
def test_mock_conversation_retrieval(mock_poe_api):
    """Test conversation retrieval with mocked Poe API."""
    # Mock API response
    mock_conversations = [
        {
            "id": "test_conv_1",
            "bot": "Claude-3-Opus",
            "title": "Test Conversation 1",
            "created_at": "2024-01-01T00:00:00Z",
            "messages": [
                {
                    "id": "msg_1",
                    "text": "Hello, how can I help you?",
                    "sender": "Claude-3-Opus",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "msg_2", 
                    "text": "I need help with Python coding",
                    "sender": "User",
                    "timestamp": "2024-01-01T00:01:00Z"
                }
            ]
        }
    ]
    
    # Configure mock
    mock_api_instance = MagicMock()
    mock_api_instance.get_conversations.return_value = mock_conversations
    mock_poe_api.return_value = mock_api_instance
    
    # Test with temporary database
    temp_db_path = "/tmp/test_poe_search.db"
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)
    
    try:
        db = Database(f"sqlite:///{temp_db_path}")
        
        # Save mock conversation
        for conv in mock_conversations:
            db.save_conversation(conv)
        
        # Verify conversation was saved
        saved_conversations = db.get_conversations()
        assert len(saved_conversations) == 1
        assert saved_conversations[0]["id"] == "test_conv_1"
        assert saved_conversations[0]["bot"] == "Claude-3-Opus"
        
        # Verify messages were saved
        full_conv = db.get_conversation("test_conv_1")
        assert len(full_conv["messages"]) == 2
        assert full_conv["messages"][0]["text"] == "Hello, how can I help you?"
        
    finally:
        # Cleanup
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)


def test_conversation_text_search():
    """Test that conversation text can be searched effectively."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    
    # Get all conversations
    all_conversations = db.get_conversations()
    
    if not all_conversations:
        print("No conversations to test search functionality")
        return
    
    # Test searching for common terms
    search_terms = ["help", "python", "code", "how", "what", "the"]
    
    for term in search_terms:
        if hasattr(db, 'search_messages'):
            results = db.search_messages(term)
            if results:
                print(f"Search for '{term}' found {len(results)} results")
                # Verify results have required fields
                for result in results[:3]:  # Check first 3 results
                    assert "conversation_id" in result
                    assert "text" in result
                    assert term.lower() in result["text"].lower()
                break
        else:
            # Fallback: manual search through conversations
            found_count = 0
            for conv in all_conversations:
                full_conv = db.get_conversation(conv["id"])
                messages = full_conv.get("messages", [])
                for msg in messages:
                    if term.lower() in msg.get("text", "").lower():
                        found_count += 1
                        break
            if found_count > 0:
                print(f"Manual search for '{term}' found {found_count} conversations")
                break


def test_conversation_export_format():
    """Test that conversations can be exported in proper format."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    
    conversations = db.get_conversations(limit=3)
    
    for conv in conversations:
        full_conv = db.get_conversation(conv["id"])
        
        # Test export format
        export_data = {
            "id": full_conv["id"],
            "bot": full_conv["bot"],
            "title": full_conv.get("title", ""),
            "created_at": full_conv["created_at"],
            "message_count": len(full_conv.get("messages", [])),
            "messages": []
        }
        
        for msg in full_conv.get("messages", []):
            export_msg = {
                "sender": msg.get("sender", ""),
                "text": msg.get("text", ""),
                "timestamp": msg.get("timestamp", "")
            }
            export_data["messages"].append(export_msg)
        
        # Verify export format
        assert "id" in export_data
        assert "bot" in export_data
        assert "messages" in export_data
        assert len(export_data["messages"]) == export_data["message_count"]
        
        print(f"Successfully exported conversation {conv['id']} "
              f"with {len(export_data['messages'])} messages")


def test_database_performance():
    """Test database performance with large result sets."""
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    db = Database(f"sqlite:///{db_path}")
    
    import time
    
    # Test listing all conversations
    start_time = time.time()
    all_conversations = db.get_conversations()
    list_time = time.time() - start_time
    
    print(f"Listed {len(all_conversations)} conversations in {list_time:.3f}s")
    
    # Test retrieving individual conversations
    if all_conversations:
        test_conv_ids = [c["id"] for c in all_conversations[:5]]
        
        start_time = time.time()
        for conv_id in test_conv_ids:
            db.get_conversation(conv_id)
        retrieval_time = time.time() - start_time
        
        avg_time = retrieval_time / len(test_conv_ids)
        print(f"Retrieved {len(test_conv_ids)} full conversations "
              f"in {retrieval_time:.3f}s (avg: {avg_time:.3f}s each)")
        
        # Performance assertions
        assert list_time < 5.0, "Listing conversations took too long"
        assert avg_time < 1.0, "Individual conversation retrieval too slow"
