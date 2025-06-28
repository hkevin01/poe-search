"""Integration tests for the complete application workflow."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from pathlib import Path

from poe_search.storage.database import Database
from poe_search.search.engine import SearchEngine
from poe_search.export.exporter import ConversationExporter


class TestDatabaseIntegration:
    """Test database operations with real SQLite database."""
    
    def test_database_creation_and_conversation_storage(self):
        """Test creating database and storing conversations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(f"sqlite:///{db_path}")
            
            # Test conversation data
            conversation = {
                "id": "test_conv_1",
                "bot": "GPT-4",
                "title": "Test Conversation",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:30:00Z",
                "message_count": 2,
                "messages": [
                    {
                        "id": "msg1",
                        "sender": "User",
                        "content": "Hello, can you help with Python?",
                        "timestamp": "2024-01-01T12:00:00Z",
                        "bot": "GPT-4"
                    },
                    {
                        "id": "msg2", 
                        "sender": "GPT-4",
                        "content": "Of course! I'd be happy to help with Python programming.",
                        "timestamp": "2024-01-01T12:01:00Z",
                        "bot": "GPT-4"
                    }
                ]
            }
            
            # Save conversation
            db.save_conversation(conversation)
            
            # Verify it was saved
            assert db.conversation_exists("test_conv_1")
            
            # Retrieve conversation
            retrieved = db.get_conversation("test_conv_1")
            assert retrieved is not None
            assert retrieved["id"] == "test_conv_1"
            assert retrieved["title"] == "Test Conversation"
            
            # Check messages were saved
            messages = db.get_messages("test_conv_1")
            assert len(messages) == 2
            assert messages[0]["content"] == "Hello, can you help with Python?"
    
    def test_search_engine_integration(self):
        """Test search engine with database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(f"sqlite:///{db_path}")
            search_engine = SearchEngine(db)
            
            # Add test conversations
            conversations = [
                {
                    "id": "conv1",
                    "bot": "GPT-4",
                    "title": "Python Programming Help",
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:30:00Z",
                    "message_count": 2,
                    "messages": [
                        {
                            "id": "msg1",
                            "sender": "User",
                            "content": "How do I create a class in Python?",
                            "timestamp": "2024-01-01T12:00:00Z",
                            "bot": "GPT-4"
                        }
                    ]
                },
                {
                    "id": "conv2",
                    "bot": "Claude",
                    "title": "Web Development Questions",
                    "created_at": "2024-01-02T10:00:00Z",
                    "updated_at": "2024-01-02T10:15:00Z",
                    "message_count": 1,
                    "messages": [
                        {
                            "id": "msg2",
                            "sender": "User", 
                            "content": "What is the best framework for web development?",
                            "timestamp": "2024-01-02T10:00:00Z",
                            "bot": "Claude"
                        }
                    ]
                }
            ]
            
            # Save conversations
            for conv in conversations:
                db.save_conversation(conv)
            
            # Test search
            results = search_engine.search("Python")
            assert len(results) == 1
            assert results[0]["id"] == "conv1"
            
            results = search_engine.search("web development")
            assert len(results) == 1
            assert results[0]["id"] == "conv2"
            
            # Test search with no results
            results = search_engine.search("nonexistent topic")
            assert len(results) == 0
    
    def test_export_integration(self):
        """Test exporting conversations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(f"sqlite:///{db_path}")
            exporter = ConversationExporter(db)
            
            # Add test conversation
            conversation = {
                "id": "export_test",
                "bot": "GPT-4",
                "title": "Export Test Conversation",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:30:00Z",
                "message_count": 1,
                "messages": [
                    {
                        "id": "msg1",
                        "sender": "User",
                        "content": "Test message for export",
                        "timestamp": "2024-01-01T12:00:00Z",
                        "bot": "GPT-4"
                    }
                ]
            }
            
            db.save_conversation(conversation)
            
            # Test JSON export
            json_path = os.path.join(temp_dir, "export.json")
            exporter.export_conversations_json(["export_test"], json_path)
            
            assert os.path.exists(json_path)
            
            # Read and verify exported data
            import json
            with open(json_path, 'r') as f:
                exported_data = json.load(f)
            
            assert len(exported_data) == 1
            assert exported_data[0]["id"] == "export_test"
            assert exported_data[0]["title"] == "Export Test Conversation"
    
    def test_category_update_integration(self):
        """Test updating conversation categories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(f"sqlite:///{db_path}")
            
            # Add conversation without category
            conversation = {
                "id": "category_test",
                "bot": "GPT-4", 
                "title": "Programming Question",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:30:00Z",
                "message_count": 1,
                "messages": []
            }
            
            db.save_conversation(conversation)
            
            # Update category
            db.update_conversation_category("category_test", "Technical")
            
            # Verify category was updated
            retrieved = db.get_conversation("category_test")
            assert retrieved["category"] == "Technical"


class TestAPIIntegration:
    """Test API integration with mocked Poe API."""
    
    @patch('poe_search.api.client.PoeApiClient')
    def test_conversation_sync_workflow(self, mock_api_client):
        """Test complete conversation sync workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(f"sqlite:///{db_path}")
            
            # Mock API responses
            mock_client = mock_api_client.return_value
            mock_client.get_conversation_ids.return_value = ["conv1", "conv2"]
            mock_client.get_conversation.side_effect = [
                {
                    "id": "conv1",
                    "bot": "GPT-4",
                    "title": "First Conversation",
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:30:00Z",
                    "message_count": 1,
                    "messages": [
                        {
                            "id": "msg1",
                            "sender": "User",
                            "content": "Hello",
                            "timestamp": "2024-01-01T12:00:00Z",
                            "bot": "GPT-4"
                        }
                    ]
                },
                {
                    "id": "conv2",
                    "bot": "Claude",
                    "title": "Second Conversation", 
                    "created_at": "2024-01-02T10:00:00Z",
                    "updated_at": "2024-01-02T10:15:00Z",
                    "message_count": 1,
                    "messages": [
                        {
                            "id": "msg2",
                            "sender": "User",
                            "content": "Hi there",
                            "timestamp": "2024-01-02T10:00:00Z",
                            "bot": "Claude"
                        }
                    ]
                }
            ]
            
            # Simulate sync process
            conversation_ids = mock_client.get_conversation_ids()
            
            for conv_id in conversation_ids:
                conversation_data = mock_client.get_conversation(conv_id)
                if conversation_data:
                    db.save_conversation(conversation_data)
            
            # Verify conversations were synced
            all_conversations = db.get_all_conversations()
            assert len(all_conversations) == 2
            
            conversation_1 = db.get_conversation("conv1")
            assert conversation_1["title"] == "First Conversation"
            
            conversation_2 = db.get_conversation("conv2") 
            assert conversation_2["title"] == "Second Conversation"


class TestGUIWorkflow:
    """Test complete GUI workflow scenarios."""
    
    def test_search_to_view_workflow(self, qapp):
        """Test workflow from search to viewing conversation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            
            # Mock the complete workflow
            with patch('poe_search.gui.main_window.PoeSearchClient') as mock_client_class:
                with patch('poe_search.storage.database.Database') as mock_db_class:
                    
                    # Set up mocks
                    mock_db = Mock()
                    mock_db_class.return_value = mock_db
                    
                    mock_client = Mock()
                    mock_client_class.return_value = mock_client
                    
                    # Mock search results
                    mock_db.get_all_conversations.return_value = [
                        {
                            "id": "conv1",
                            "title": "Test Conversation",
                            "bot": "GPT-4",
                            "category": "Technical",
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-01T12:30:00Z",
                            "message_count": 2
                        }
                    ]
                    
                    mock_db.get_conversation.return_value = {
                        "id": "conv1",
                        "title": "Test Conversation", 
                        "bot": "GPT-4",
                        "category": "Technical",
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:30:00Z",
                        "message_count": 2,
                        "messages": [
                            {
                                "id": "msg1",
                                "sender": "User",
                                "content": "Test message",
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        ]
                    }
                    
                    # Import here to avoid circular imports
                    from poe_search.gui.main_window import MainWindow
                    
                    # Create main window
                    config = {
                        "database_url": f"sqlite:///{db_path}",
                        "token": "test_token"
                    }
                    
                    window = MainWindow(config)
                    
                    # Test that components are initialized
                    assert window.search_widget is not None
                    assert window.conversation_widget is not None
                    assert window.category_widget is not None
                    assert window.analytics_widget is not None
    
    def test_categorization_workflow(self, qapp):
        """Test categorization workflow."""
        from poe_search.gui.widgets.category_widget import CategoryWidget, CategoryRule
        
        # Create widget
        widget = CategoryWidget()
        
        # Test conversations
        conversations = [
            {
                "id": "conv1",
                "title": "Python Programming Help",
                "category": "Uncategorized",
                "messages": [
                    {"content": "How do I write Python code?"}
                ]
            }
        ]
        
        widget.update_conversations(conversations)
        
        # Test category suggestion
        suggested = widget.suggest_category_for_conversation(conversations[0])
        assert suggested == "Technical"  # Should match programming keywords
    
    def test_export_workflow(self):
        """Test export workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(f"sqlite:///{db_path}")
            
            # Add test data
            conversation = {
                "id": "export_conv",
                "bot": "GPT-4",
                "title": "Export Test",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:30:00Z",
                "message_count": 1,
                "messages": [
                    {
                        "id": "msg1",
                        "sender": "User",
                        "content": "Test export message",
                        "timestamp": "2024-01-01T12:00:00Z",
                        "bot": "GPT-4"
                    }
                ]
            }
            
            db.save_conversation(conversation)
            
            # Test different export formats
            exporter = ConversationExporter(db)
            
            # JSON export
            json_path = os.path.join(temp_dir, "test.json")
            exporter.export_conversations_json(["export_conv"], json_path)
            assert os.path.exists(json_path)
            
            # CSV export
            csv_path = os.path.join(temp_dir, "test.csv")
            exporter.export_conversations_csv(["export_conv"], csv_path)
            assert os.path.exists(csv_path)
            
            # Markdown export
            md_path = os.path.join(temp_dir, "test.md")
            exporter.export_conversations_markdown(["export_conv"], md_path)
            assert os.path.exists(md_path)


class TestPerformanceIntegration:
    """Test performance with larger datasets."""
    
    def test_large_dataset_search(self):
        """Test search performance with many conversations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = Database(f"sqlite:///{db_path}")
            search_engine = SearchEngine(db)
            
            # Generate test conversations
            num_conversations = 100
            
            for i in range(num_conversations):
                conversation = {
                    "id": f"conv_{i}",
                    "bot": "GPT-4" if i % 2 == 0 else "Claude",
                    "title": f"Test Conversation {i}",
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:30:00Z",
                    "message_count": 1,
                    "messages": [
                        {
                            "id": f"msg_{i}",
                            "sender": "User",
                            "content": f"This is test message {i} about topic {i % 10}",
                            "timestamp": "2024-01-01T12:00:00Z",
                            "bot": "GPT-4" if i % 2 == 0 else "Claude"
                        }
                    ]
                }
                
                db.save_conversation(conversation)
            
            # Test search performance
            import time
            
            start_time = time.time()
            results = search_engine.search("test")
            search_time = time.time() - start_time
            
            # Should find results quickly
            assert len(results) > 0
            assert search_time < 1.0  # Should complete within 1 second
            
            # Test specific search
            results = search_engine.search("topic 5")
            topic_5_results = [r for r in results if "topic 5" in r.get("title", "") or 
                             any("topic 5" in msg.get("content", "") for msg in r.get("messages", []))]
            assert len(topic_5_results) >= 1
