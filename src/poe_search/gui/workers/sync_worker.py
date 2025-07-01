"""Sync worker for synchronizing conversations with Poe."""

import logging
import random
import time
from typing import List, Optional

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
        
        # Define major bot IDs to sync from
        self.major_bots = [
            "a2",              # Claude (Anthropic)
            "chinchilla",      # ChatGPT (OpenAI)
            "capybara",        # Assistant (OpenAI)
            "beaver",          # GPT-4 (OpenAI)
            "claude-3-5-sonnet", # Claude 3.5 Sonnet
            "claude-3-opus",   # Claude 3 Opus
            "gemini-pro",      # Gemini Pro (Google)
            "llama-2-70b",     # Llama 2 70B
            "mistral-7b",      # Mistral 7B
        ]
        
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
                'total': 0,
                'bots_synced': 0
            }
            
            # Get conversations to sync
            if self.conversation_ids:
                conversations_to_sync = self.conversation_ids
                self.progress_updated.emit(10, "Using specified conversation IDs")
            else:
                # Get recent conversations from all major bots
                self.progress_updated.emit(5, "Fetching recent conversations from all bots...")
                conversations_to_sync = self.get_conversations_from_all_bots()
            
            total_conversations = len(conversations_to_sync)
            stats['total'] = total_conversations
            
            logger.info(f"Found {total_conversations} conversations to sync from {stats['bots_synced']} bots")
            
            if total_conversations == 0:
                self.progress_updated.emit(100, "No conversations to sync")
                self.sync_complete.emit(stats)
                return
            
            # Sync each conversation with rate limiting
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
                    
                    # Add delay between API calls to respect rate limits
                    if i > 0:  # Skip delay for first conversation
                        delay = random.uniform(1, 3)  # 1-3 seconds between calls
                        time.sleep(delay)
                    
                    # Check if conversation already exists
                    existing = None
                    try:
                        if hasattr(self.client.database, 'get_conversation'):
                            existing = self.client.database.get_conversation(
                                conversation_id
                            )
                    except Exception:
                        pass  # Conversation doesn't exist or error accessing
                    
                    # Fetch conversation data with retry logic
                    conversation_data = None
                    max_retries = 3
                    
                    for retry in range(max_retries):
                        try:
                            conversation_data = (
                                self.client.api_client.get_conversation(
                                    conversation_id
                                )
                            )
                            break  # Success, exit retry loop
                        except Exception as e:
                            error_msg = str(e).lower()
                            rate_limit_keywords = [
                                'rate limit', '429', 'too many requests'
                            ]
                            if any(keyword in error_msg for keyword in rate_limit_keywords):
                                if retry < max_retries - 1:
                                    # Exponential backoff for rate limits
                                    delay = min(5 * (2 ** retry), 30)  # 5, 10, 20s
                                    logger.warning(
                                        f"Rate limit hit, waiting {delay} seconds "
                                        f"before retry {retry + 1}"
                                    )
                                    time.sleep(delay)
                                    continue
                                else:
                                    logger.error(
                                        f"Rate limit exceeded for conversation "
                                        f"{conversation_id}"
                                    )
                                    stats['failed'] += 1
                                    break
                            else:
                                # Non-rate-limit error, don't retry
                                logger.error(
                                    f"Failed to fetch conversation "
                                    f"{conversation_id}: {e}"
                                )
                                stats['failed'] += 1
                                break
                    
                    if conversation_data:
                        # Save to database
                        try:
                            if existing:
                                if hasattr(self.client.database, 'update_conversation'):
                                    self.client.database.update_conversation(
                                        conversation_data
                                    )
                                else:
                                    self.client.database.save_conversation(
                                        conversation_data
                                    )
                                stats['updated'] += 1
                            else:
                                self.client.database.save_conversation(
                                    conversation_data
                                )
                                stats['new'] += 1
                        except Exception as e:
                            logger.error(
                                f"Failed to save conversation {conversation_id}: {e}"
                            )
                            stats['failed'] += 1
                            continue
                        
                        # Emit synced conversation
                        self.conversation_synced.emit(conversation_data)
                        
                        logger.debug(f"Synced conversation: {conversation_id}")
                    else:
                        if stats['failed'] == 0:  # Only increment if not already counted
                            stats['failed'] += 1
                        logger.warning(
                            f"Failed to fetch conversation: {conversation_id}"
                        )
                
                except Exception as e:
                    logger.error(f"Error syncing conversation {conversation_id}: {e}")
                    stats['failed'] += 1
                    continue
            
            # Final progress update
            self.progress_updated.emit(100, "Sync completed")
            
            # Emit completion signal
            self.sync_complete.emit(stats)
            
            logger.info(f"Sync completed: {stats}")
            
        except Exception as e:
            logger.error(f"Sync operation failed: {e}")
            self.error_occurred.emit(str(e))
    
    def get_conversations_from_all_bots(self) -> List[str]:
        """Get conversation IDs from all major bots."""
        all_conversation_ids = []
        
        for bot_id in self.major_bots:
            if self.should_stop:
                break
                
            try:
                logger.info(f"Fetching conversations for bot: {bot_id}")
                
                # Try to get conversations for this bot
                if hasattr(self.client.api_client, 'get_conversation_ids'):
                    bot_conversations = self.client.api_client.get_conversation_ids(
                        bot_id=bot_id, days=self.days
                    )
                elif hasattr(self.client.api_client, 'get_chat_history'):
                    # Fallback: get chat history for the bot
                    chat_history = self.client.api_client.get_chat_history(
                        bot_id, count=50
                    )
                    bot_conversations = []
                    if isinstance(chat_history, dict) and 'data' in chat_history:
                        bot_data = chat_history['data'].get(bot_id, [])
                        bot_conversations = [conv.get('id') for conv in bot_data if conv.get('id')]
                    else:
                        bot_conversations = []
                else:
                    logger.warning(f"No method to fetch conversations for bot {bot_id}")
                    continue
                
                if bot_conversations:
                    all_conversation_ids.extend(bot_conversations)
                    logger.info(f"Found {len(bot_conversations)} conversations for {bot_id}")
                else:
                    logger.info(f"No conversations found for bot {bot_id}")
                
                # Add delay between bots to respect rate limits
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                logger.warning(f"Failed to fetch conversations for bot {bot_id}: {e}")
                continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_conversations = []
        for conv_id in all_conversation_ids:
            if conv_id not in seen:
                seen.add(conv_id)
                unique_conversations.append(conv_id)
        
        logger.info(f"Total unique conversations found: {len(unique_conversations)}")
        return unique_conversations
