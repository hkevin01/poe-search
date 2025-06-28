"""Sync worker for synchronizing conversations with Poe."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from PyQt6.QtCore import QThread, pyqtSignal

from poe_search.client import PoeSearchClient

logger = logging.getLogger(__name__)


class SyncWorker(QThread):
    """Worker thread for syncing conversations with Poe."""
    
    # Signals
    progress_updated = pyqtSignal(int, str)  # Progress percentage, status message
    conversation_synced = pyqtSignal(dict)  # Synced conversation data
    error_occurred = pyqtSignal(str)  # Error message
    sync_complete = pyqtSignal(dict)  # Sync statistics
    
    def __init__(self, client: PoeSearchClient, days: int = 7, 
                 conversation_ids: Optional[List[str]] = None):
        """Initialize sync worker.
        
        Args:
            client: Poe Search client
            days: Number of days to sync (recent conversations)
            conversation_ids: Specific conversation IDs to sync, or None for recent
        """
        super().__init__()
        
        self.client = client
        self.days = days
        self.conversation_ids = conversation_ids
        self.should_stop = False
        
    def stop(self):
        """Stop the sync operation."""
        self.should_stop = True
        
    def run(self):
        """Run the sync operation."""
        try:
            logger.info("Starting conversation sync")
            
            stats = {
                'new': 0,
                'updated': 0,
                'failed': 0,
                'total': 0
            }
            
            # Get conversations to sync
            if self.conversation_ids:
                conversations_to_sync = self.conversation_ids
                self.progress_updated.emit(10, "Using specified conversation IDs")
            else:
                # Get recent conversations based on days parameter
                self.progress_updated.emit(5, "Fetching recent conversations...")
                try:
                    # Use client's sync method if available
                    if hasattr(self.client, 'sync_recent_conversations'):
                        result = self.client.sync_recent_conversations(days=self.days)
                        self.sync_complete.emit(result)
                        return
                    
                    # Fallback: manual sync using API client
                    if hasattr(self.client.api_client, 'get_recent_conversation_ids'):
                        conversations_to_sync = self.client.api_client.get_recent_conversation_ids(days=self.days)
                    else:
                        # Last fallback: get all conversations
                        conversations_to_sync = self.client.api_client.get_conversation_ids()
                        
                except Exception as e:
                    self.error_occurred.emit(f"Failed to fetch conversation list: {e}")
                    return
            
            total_conversations = len(conversations_to_sync)
            stats['total'] = total_conversations
            
            logger.info(f"Found {total_conversations} conversations to sync")
            
            if total_conversations == 0:
                self.progress_updated.emit(100, "No conversations to sync")
                self.sync_complete.emit(stats)
                return
            
            # Sync each conversation
            for i, conversation_id in enumerate(conversations_to_sync):
                if self.should_stop:
                    break
                
                try:
                    # Update progress
                    progress = int((i / total_conversations) * 90) + 10
                    self.progress_updated.emit(
                        progress, 
                        f"Syncing conversation {i+1}/{total_conversations}"
                    )
                    
                    # Check if conversation already exists
                    existing = None
                    try:
                        if hasattr(self.client.database, 'get_conversation'):
                            existing = self.client.database.get_conversation(conversation_id)
                    except Exception:
                        pass  # Conversation doesn't exist or error accessing
                    
                    # Fetch conversation data
                    conversation_data = self.client.api_client.get_conversation(conversation_id)
                    
                    if conversation_data:
                        # Save to database
                        try:
                            if existing:
                                if hasattr(self.client.database, 'update_conversation'):
                                    self.client.database.update_conversation(conversation_data)
                                else:
                                    self.client.database.save_conversation(conversation_data)
                                stats['updated'] += 1
                            else:
                                self.client.database.save_conversation(conversation_data)
                                stats['new'] += 1
                        except Exception as e:
                            logger.error(f"Failed to save conversation {conversation_id}: {e}")
                            stats['failed'] += 1
                            continue
                        
                        # Emit synced conversation
                        self.conversation_synced.emit(conversation_data)
                        
                        logger.debug(f"Synced conversation: {conversation_id}")
                    else:
                        stats['failed'] += 1
                        logger.warning(f"Failed to fetch conversation: {conversation_id}")
                
                except Exception as e:
                    stats['failed'] += 1
                    logger.error(f"Error syncing conversation {conversation_id}: {e}")
                    
                    # Don't stop the entire sync for individual failures
                    continue
            
            # Final progress update
            self.progress_updated.emit(100, "Sync completed")
            
            logger.info(f"Sync completed: {stats['new']} new, {stats['updated']} updated, {stats['failed']} failed")
            
            # Emit completion signal
            self.sync_complete.emit(stats)
            
        except Exception as e:
            logger.error(f"Sync worker error: {e}")
            self.error_occurred.emit(str(e))
