"""
Background worker for syncing conversations from Poe.com.
"""

import logging
from typing import Optional, List, Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal
from ..api.client_factory import create_poe_client
from ..storage.database import DatabaseManager


logger = logging.getLogger(__name__)


class SyncWorker(QThread):
    """Background worker for syncing conversations from Poe.com."""
    
    # Signals
    progress = pyqtSignal(int)  # Progress percentage (0-100)
    status_update = pyqtSignal(str)  # Status message
    error = pyqtSignal(str)  # Error message
    finished = pyqtSignal()  # Sync completed successfully
    conversation_synced = pyqtSignal(dict)  # Individual conversation synced
    
    def __init__(self, db_manager: DatabaseManager, credentials: Dict[str, str]):
        """
        Initialize the sync worker.
        
        Args:
            db_manager: Database manager instance
            credentials: Dictionary with 'formkey' and 'p_b_cookie'
        """
        super().__init__()
        self.db_manager = db_manager
        self.credentials = credentials
        self.should_stop = False
        self._poe_client = None
        
    def stop(self):
        """Stop the sync process."""
        self.should_stop = True
        logger.info("Sync worker stop requested")
        
    def run(self):
        """Main sync process."""
        try:
            logger.info("Starting conversation sync")
            self.status_update.emit("Initializing Poe client...")
            self.progress.emit(0)
            
            # Create Poe client
            self._poe_client = create_poe_client(
                formkey=self.credentials['formkey'],
                p_b_cookie=self.credentials['p_b_cookie']
            )
            
            # Test connection
            self.status_update.emit("Testing connection...")
            if not self._poe_client.test_connection():
                self.error.emit("Failed to connect to Poe.com API")
                return
                
            self.progress.emit(10)
            
            # Get conversations
            self.status_update.emit("Fetching conversations...")
            conversations = self._poe_client.get_conversations()
            
            if not conversations:
                self.status_update.emit("No conversations found")
                self.progress.emit(100)
                self.finished.emit()
                return
                
            logger.info(f"Found {len(conversations)} conversations")
            self.progress.emit(20)
            
            # Sync each conversation
            total_conversations = len(conversations)
            for i, conversation in enumerate(conversations):
                if self.should_stop:
                    logger.info("Sync stopped by user")
                    return
                    
                self._sync_conversation(conversation)
                
                # Update progress
                progress = 20 + int((i + 1) / total_conversations * 70)
                self.progress.emit(progress)
                
                # Emit signal for individual conversation
                self.conversation_synced.emit(conversation)
                
            self.status_update.emit(f"Sync completed! {total_conversations} conversations synced")
            self.progress.emit(100)
            self.finished.emit()
            
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
            
    def _sync_conversation(self, conversation: Dict[str, Any]):
        """
        Sync a single conversation to the database.
        
        Args:
            conversation: Conversation data from Poe API
        """
        try:
            # Extract conversation info
            conversation_id = conversation.get('id')
            title = conversation.get('title', 'Untitled')
            created_at = conversation.get('created_at')
            updated_at = conversation.get('updated_at')
            
            if not conversation_id:
                logger.warning("Conversation missing ID, skipping")
                return
                
            # Check if conversation already exists
            existing = self.db_manager.get_conversation_by_id(conversation_id)
            if existing:
                # Update existing conversation
                self.db_manager.update_conversation(
                    conversation_id=conversation_id,
                    title=title,
                    updated_at=updated_at
                )
                logger.debug(f"Updated conversation: {title}")
            else:
                # Create new conversation
                self.db_manager.create_conversation(
                    conversation_id=conversation_id,
                    title=title,
                    created_at=created_at,
                    updated_at=updated_at
                )
                logger.debug(f"Created conversation: {title}")
                
            # Sync messages for this conversation
            self._sync_conversation_messages(conversation)
            
        except Exception as e:
            logger.error(f"Failed to sync conversation {conversation.get('id', 'unknown')}: {e}")
            
    def _sync_conversation_messages(self, conversation: Dict[str, Any]):
        """
        Sync messages for a conversation.
        
        Args:
            conversation: Conversation data from Poe API
        """
        try:
            conversation_id = conversation.get('id')
            messages = conversation.get('messages', [])
            
            for message in messages:
                message_id = message.get('id')
                content = message.get('text', '')
                sender = message.get('author', 'unknown')
                timestamp = message.get('created_at')
                
                if not message_id:
                    continue
                    
                # Check if message already exists
                existing = self.db_manager.get_message_by_id(message_id)
                if not existing:
                    # Create new message
                    self.db_manager.create_message(
                        message_id=message_id,
                        conversation_id=conversation_id,
                        content=content,
                        sender=sender,
                        timestamp=timestamp
                    )
                    
        except Exception as e:
            logger.error(f"Failed to sync messages for conversation {conversation.get('id', 'unknown')}: {e}")
