"""Main client for Poe Search functionality."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from poe_search.api.client import PoeAPIClient  # This is the main API client
from poe_search.export.exporter import ConversationExporter
from poe_search.search.engine import SearchEngine
from poe_search.storage.database import Database

logger = logging.getLogger(__name__)


class PoeSearchClient:
    """Main client for Poe Search functionality."""

    def __init__(
        self,
        token: Optional[str] = None,
        database_url: Optional[str] = None,
        config_path: Optional[Path] = None,
        config: Optional[Any] = None,
    ):
        """Initialize the Poe Search client.
        
        Args:
            token: Poe authentication token (legacy)
            database_url: Database connection URL
            config_path: Path to configuration file
            config: Configuration object (new format)
        """
        self.token = token
        self.database_url = database_url or "sqlite:///poe_search.db"
        self.config_path = config_path or Path.home() / ".poe-search"
        self.config = config
        
        # Initialize components
        self._api_client = None
        self._database = None
        self._search_engine = None
        self._exporter = None
    
    @property
    def api_client(self) -> PoeAPIClient:
        """Get the Poe API client."""
        if self._api_client is None:
            if self.config and hasattr(self.config, 'get_poe_tokens'):
                tokens = self.config.get_poe_tokens()
                p_b_token = tokens.get('p-b') if isinstance(tokens, dict) else tokens
                self._api_client = PoeAPIClient(token=p_b_token)
            else:
                token = self.token or ""
                self._api_client = PoeAPIClient(token=token)
        return self._api_client
    
    @property
    def database(self) -> Database:
        """Get the database instance."""
        if self._database is None:
            self._database = Database(self.database_url)
        return self._database
    
    @property
    def search_engine(self) -> SearchEngine:
        """Get the search engine instance."""
        if self._search_engine is None:
            self._search_engine = SearchEngine(self.database)
        return self._search_engine
    
    @property
    def exporter(self) -> ConversationExporter:
        """Get the conversation exporter."""
        if self._exporter is None:
            self._exporter = ConversationExporter(self.database)
        return self._exporter
    
    def get_api_type(self) -> str:
        """Get the current API type being used.
        
        Returns:
            "wrapper" or "official"
        """
        if self.config:
            return self.config.get_api_type()
        return "wrapper"
    
    def switch_api_type(self, api_type: str) -> bool:
        """Switch between API types.
        
        Args:
            api_type: "wrapper" or "official"
            
        Returns:
            True if switch was successful
        """
        if not self.config:
            logger.error("No configuration available for API type switch")
            return False
        
        try:
            self.config.set_api_type(api_type)
            # Reset API client to force recreation with new type
            self._api_client = None
            logger.info(f"Switched to {api_type} API")
            return True
        except Exception as e:
            logger.error(f"Failed to switch API type: {e}")
            return False
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Test the current API connection.
        
        Returns:
            Dictionary with test results
        """
        try:
            client = self.api_client
            
            # For wrapper client, try to get user info
            user_info = client.get_user_info()
            return {
                'success': bool(user_info),
                'api_type': 'wrapper',
                'user_info': user_info
            }
                
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'api_type': self.get_api_type()
            }
    
    def search(
        self,
        query: str,
        bot: Optional[str] = None,
        limit: int = 10,
        **filters: Any,
    ) -> List[Dict[str, Any]]:
        """Search conversations.
        
        Args:
            query: Search query
            bot: Filter by specific bot
            limit: Maximum number of results
            **filters: Additional search filters
            
        Returns:
            List of matching conversations
        """
        return self.search_engine.search(
            query=query,
            bot=bot,
            limit=limit,
            **filters,
        )
    
    def get_conversation_history(
        self,
        days: int = 7,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get conversation history.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of conversations
        """
        try:
            client = self.api_client
            
            # Use wrapper client for conversation history
            conversations = client.get_recent_conversations(days=days)
            return conversations[:limit]

        except Exception as e:
            logger.error(
                f"Failed to get conversation history: {e}"
            )
            return []
    
    def get_conversation(
        self, conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data or None if not found
        """
        try:
            client = self.api_client

            # Use wrapper client for conversation retrieval
            return client.get_conversation(
                conversation_id
            )

        except Exception as e:
            logger.error(
                "Failed to get conversation %s: %s",
                conversation_id,
                e,
            )
            return None
    
    def send_message(
        self,
        message: str,
        bot_name: str = "GPT-3.5-Turbo"
    ) -> Optional[str]:
        """Send a message to a bot (official API only).
        
        Args:
            message: Message to send
            bot_name: Name of the bot
            
        Returns:
            Bot response or None if failed
        """
        try:
            client = self.api_client

            # Message sending only supported with official API
            logger.warning(
                "Message sending only supported with official API"
            )
            return None

        except Exception as e:
            logger.error(
                f"Failed to send message: {e}"
            )
            return None
    
    def sync_conversations(self, days: int = 7) -> int:
        """Sync conversations to local database.
        
        Args:
            days: Number of days to sync
            
        Returns:
            Number of conversations synced
        """
        try:
            conversations = self.get_conversation_history(days=days)
            
            synced_count = 0
            for conv in conversations:
                try:
                    self.database.save_conversation(conv)
                    synced_count += 1
                except Exception as e:
                    logger.warning(
                        "Failed to store conversation %s: %s",
                        conv.get('id', 'unknown'),
                        e,
                    )
                    continue
            
            logger.info(f"Synced {synced_count} conversations")
            return synced_count
            
        except Exception as e:
            logger.error(f"Failed to sync conversations: {e}")
            return 0
    
    def sync(self, days: int = 7) -> Dict[str, int]:
        """Sync conversations from Poe.
        
        Args:
            days: Number of days to sync
            
        Returns:
            Statistics about synced data
        """
        logger.info(f"Syncing conversations from last {days} days")
        
        # Get recent conversations from API
        conversations = self.api_client.get_recent_conversations(days=days)
        
        # Store in database
        stats = {"new": 0, "updated": 0, "total": len(conversations)}
        
        for conversation in conversations:
            if self.database.conversation_exists(conversation["id"]):
                self.database.update_conversation(conversation)
                stats["updated"] += 1
            else:
                self.database.save_conversation(conversation)
                stats["new"] += 1
        
        logger.info(f"Sync complete: {stats}")
        return stats
    
    def get_conversations(
        self,
        bot: Optional[str] = None,
        days: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get conversations from local database.
        
        Args:
            bot: Filter by bot
            days: Filter by days
            limit: Limit results
            
        Returns:
            List of conversations
        """
        return self.database.get_conversations(
            bot=bot,
            days=days,
            limit=limit,
        )
    
    def export_conversations(
        self,
        output_path: str,
        format: str = "json",
        **filters: Any,
    ) -> None:
        """Export conversations to file.
        
        Args:
            output_path: Output file path
            format: Export format (json, csv, markdown)
            **filters: Filters for conversations to export
        """
        conversations = self.database.get_conversations(**filters)
        self.exporter.export(
            conversations=conversations,
            output_path=output_path,
            format=format,
        )
        logger.info(
            "Exported %d conversations to %s",
            len(conversations),
            output_path,
        )
    
    def get_bots(self) -> List[Dict[str, Any]]:
        """Get list of bots from database.
        
        Returns:
            List of bot information
        """
        return self.database.get_bots()
    
    def get_analytics(self, period: str = "month") -> Dict[str, Any]:
        """Get usage analytics.
        
        Args:
            period: Analysis period (day, week, month, year)
            
        Returns:
            Analytics data
        """
        return self.database.get_analytics(period=period)
