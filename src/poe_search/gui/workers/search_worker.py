"""Search worker for performing background searches."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QThread, pyqtSignal

from poe_search.search.engine import SearchEngine
from poe_search.storage.database import Database

logger = logging.getLogger(__name__)


class SearchWorker(QThread):
    """Worker thread for performing conversation searches."""
    
    # Signals
    progress = pyqtSignal(int)  # Progress percentage
    results_ready = pyqtSignal(list)  # Search results
    error = pyqtSignal(str)  # Error message
    finished = pyqtSignal()  # Search completed
    
    def __init__(self, search_params: Dict[str, Any], database: Database):
        """Initialize search worker.
        
        Args:
            search_params: Search parameters
            database: Database instance
        """
        super().__init__()
        
        self.search_params = search_params
        self.database = database
        self.search_engine = SearchEngine(database)
        self.should_stop = False
        
    def run(self):
        """Run the search operation."""
        try:
            logger.info(f"Starting search with params: {self.search_params}")
            
            # Extract search parameters
            query = self.search_params.get("query", "")
            bot = self.search_params.get("bot", "All Bots")
            category = self.search_params.get("category", "All Categories")
            date_from = self.search_params.get("date_from")
            date_to = self.search_params.get("date_to")
            use_regex = self.search_params.get("use_regex", False)
            case_sensitive = self.search_params.get("case_sensitive", False)
            
            # Update progress
            self.progress.emit(10)
            
            if self.should_stop:
                return
            
            # Perform search
            if query:
                # Text search
                results = self.search_engine.search(
                    query=query,
                    use_regex=use_regex,
                    case_sensitive=case_sensitive
                )
            else:
                # Get all conversations
                results = self.database.get_conversations()
            
            self.progress.emit(50)
            
            if self.should_stop:
                return
            
            # Apply additional filters
            filtered_results = self.apply_filters(results, bot, category, date_from, date_to)
            
            self.progress.emit(80)
            
            if self.should_stop:
                return
            
            # Sort results by relevance/date
            sorted_results = self.sort_results(filtered_results)
            
            self.progress.emit(100)
            
            # Emit results
            self.results_ready.emit(sorted_results)
            
            logger.info(f"Search completed: {len(sorted_results)} results found")
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            self.error.emit(str(e))
        finally:
            self.finished.emit()
    
    def apply_filters(self, conversations: List[Dict[str, Any]], 
                     bot_filter: str, category_filter: str,
                     date_from: Optional[datetime], date_to: Optional[datetime]) -> List[Dict[str, Any]]:
        """Apply additional filters to search results."""
        filtered = conversations
        
        # Bot filter
        if bot_filter and bot_filter != "All Bots":
            filtered = [conv for conv in filtered if conv.get("bot") == bot_filter]
        
        # Category filter
        if category_filter and category_filter != "All Categories":
            filtered = [conv for conv in filtered 
                       if conv.get("category", "Uncategorized") == category_filter]
        
        # Date filters
        if date_from or date_to:
            date_filtered = []
            for conv in filtered:
                conv_date = self.parse_date(conv.get("created_at"))
                if conv_date:
                    if date_from and conv_date < date_from:
                        continue
                    if date_to and conv_date > date_to:
                        continue
                    date_filtered.append(conv)
            filtered = date_filtered
        
        return filtered
    
    def parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        try:
            # Handle ISO format with Z timezone
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                # Try other common formats
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
    
    def sort_results(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort search results by relevance and date."""
        # Sort by updated_at descending (most recent first)
        def sort_key(conv):
            updated_at = self.parse_date(conv.get("updated_at"))
            return updated_at if updated_at else datetime.min
        
        return sorted(conversations, key=sort_key, reverse=True)
    
    def stop(self):
        """Stop the search operation."""
        self.should_stop = True
        logger.info("Search operation stopped")


class QuickSearchWorker(QThread):
    """Worker thread for quick/incremental searches."""
    
    # Signals
    results_ready = pyqtSignal(list)  # Quick search results
    error = pyqtSignal(str)  # Error message
    
    def __init__(self, query: str, database: Database, limit: int = 50):
        """Initialize quick search worker.
        
        Args:
            query: Search query
            database: Database instance
            limit: Maximum number of results
        """
        super().__init__()
        
        self.query = query
        self.database = database
        self.limit = limit
        self.search_engine = SearchEngine(database)
        
    def run(self):
        """Run the quick search operation."""
        try:
            if not self.query or len(self.query) < 2:
                self.results_ready.emit([])
                return
            
            # Perform quick search
            results = self.search_engine.search(
                query=self.query,
                limit=self.limit
            )
            
            # Sort by relevance
            sorted_results = sorted(results, key=lambda x: x.get("message_count", 0), reverse=True)
            
            self.results_ready.emit(sorted_results[:self.limit])
            
        except Exception as e:
            logger.error(f"Quick search error: {e}")
            self.error.emit(str(e))
