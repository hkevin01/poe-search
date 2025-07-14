"""
Database manager for sync operations.

This module provides a simplified interface for database operations
used by the sync worker.
"""

import logging
from typing import Optional, Dict, Any
from .database import Database


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Simple database manager for sync operations."""
    
    def __init__(self, database_path: str):
        """
        Initialize the database manager.
        
        Args:
            database_path: Path to the database file
        """
        self.database = Database(f"sqlite:///{database_path}")
        
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            Conversation data if found, None otherwise
        """
        return self.database.get_conversation(conversation_id)
        
    def create_conversation(
        self, 
        conversation_id: str, 
        title: str, 
        created_at: str = None, 
        updated_at: str = None
    ):
        """
        Create a new conversation.
        
        Args:
            conversation_id: The conversation ID
            title: The conversation title
            created_at: Creation timestamp
            updated_at: Update timestamp
        """
        from datetime import datetime
        
        now = datetime.now().isoformat()
        conversation_data = {
            'id': conversation_id,
            'title': title,
            'bot': 'unknown',  # Will be updated when we have bot info
            'created_at': created_at or now,
            'updated_at': updated_at or now,
            'message_count': 0
        }
        
        self.database.save_conversation(conversation_data)
        
    def update_conversation(
        self, 
        conversation_id: str, 
        title: str = None, 
        updated_at: str = None
    ):
        """
        Update an existing conversation.
        
        Args:
            conversation_id: The conversation ID
            title: The new title (optional)
            updated_at: Update timestamp (optional)
        """
        existing = self.get_conversation_by_id(conversation_id)
        if not existing:
            logger.warning(f"Conversation {conversation_id} not found for update")
            return
            
        from datetime import datetime
        
        update_data = dict(existing)
        if title:
            update_data['title'] = title
        if updated_at:
            update_data['updated_at'] = updated_at
        else:
            update_data['updated_at'] = datetime.now().isoformat()
            
        self.database.update_conversation(update_data)
        
    def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get message by ID.
        
        Args:
            message_id: The message ID
            
        Returns:
            Message data if found, None otherwise
        """
        # The existing database doesn't have get_message_by_id
        # For now, we'll return None and rely on conversation-level deduplication
        return None
        
    def create_message(
        self, 
        message_id: str, 
        conversation_id: str, 
        content: str, 
        sender: str, 
        timestamp: str = None
    ):
        """
        Create a new message.
        
        Args:
            message_id: The message ID
            conversation_id: The conversation ID
            content: The message content
            sender: The message sender
            timestamp: The message timestamp
        """
        from datetime import datetime
        
        self.database.save_message(
            conversation_id=conversation_id,
            content=content,
            role=sender,
            timestamp=timestamp or datetime.now().isoformat(),
            metadata={'message_id': message_id}
        )
