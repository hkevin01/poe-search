"""
Background worker for syncing conversations from Poe.com.
"""

import logging
from typing import Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal
from ..client import PoeSearchClient
from ..storage.database_manager import DatabaseManager
from ..utils.config import load_config


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
            
            # Use the same approach as the successful GUI test
            config = load_config()
            
            # Create PoeSearchClient like the GUI does
            from pathlib import Path
            db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
            client = PoeSearchClient(config=config, database_url=f"sqlite:///{db_path}")
            
            # Get the underlying API client
            self._poe_client = client.api_client
            client_type = type(self._poe_client).__name__
            logger.info(f"Using API client: {client_type}")
            
            # Test connection
            self.status_update.emit("Testing connection...")
            try:
                user_info = self._poe_client.get_user_info()
                if not user_info:
                    self.error.emit("Failed to connect to Poe.com API")
                    return
                logger.info("API connection test successful")
            except Exception as e:
                logger.error(f"Connection test failed: {e}")
                self.error.emit(f"Failed to connect to Poe.com API: {str(e)}")
                return
                
            self.progress.emit(10)
            
            # Get conversations using the working client method
            self.status_update.emit("Fetching conversations...")
            
            try:
                logger.info("Fetching conversations using PoeSearchClient method")
                conversations = client.get_conversation_history(days=30, limit=100)
                logger.info(f"Retrieved {len(conversations)} conversations")
            except Exception as e:
                logger.error(f"Failed to fetch conversations: {e}")
                self.error.emit(f"Failed to fetch conversations: {str(e)}")
                return
            
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
