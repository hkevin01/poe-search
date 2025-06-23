"""Main client for Poe Search functionality."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from poe_search.api.client import PoeAPIClient
from poe_search.storage.database import Database
from poe_search.search.engine import SearchEngine
from poe_search.export.exporter import ConversationExporter

logger = logging.getLogger(__name__)


class PoeSearchClient:
    """Main client for Poe Search functionality."""

    def __init__(
        self,
        token: Optional[str] = None,
        database_url: Optional[str] = None,
        config_path: Optional[Path] = None,
    ):
        """Initialize the Poe Search client.
        
        Args:
            token: Poe authentication token
            database_url: Database connection URL
            config_path: Path to configuration file
        """
        self.token = token
        self.database_url = database_url or "sqlite:///poe_search.db"
        self.config_path = config_path or Path.home() / ".poe-search"
        
        # Initialize components
        self._api_client = None
        self._database = None
        self._search_engine = None
        self._exporter = None
    
    @property
    def api_client(self) -> PoeAPIClient:
        """Get the Poe API client."""
        if self._api_client is None:
            self._api_client = PoeAPIClient(token=self.token)
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
        logger.info(f"Exported {len(conversations)} conversations to {output_path}")
    
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
