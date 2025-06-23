"""Search engine for finding conversations and messages."""

import re
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from poe_search.storage.database import Database

logger = logging.getLogger(__name__)


class SearchEngine:
    """Search engine for conversations and messages."""
    
    def __init__(self, database: Database):
        """Initialize search engine.
        
        Args:
            database: Database instance
        """
        self.database = database
    
    def search(
        self,
        query: str,
        bot: Optional[str] = None,
        limit: int = 10,
        **filters: Any,
    ) -> List[Dict[str, Any]]:
        """Search conversations and messages.
        
        Args:
            query: Search query
            bot: Filter by specific bot
            limit: Maximum number of results
            **filters: Additional search filters
            
        Returns:
            List of search results
        """
        logger.info(f"Searching for: '{query}' with filters: {filters}")
        
        # Perform full-text search on messages
        message_results = self.database.search_messages(
            query=query,
            bot=bot,
            limit=limit * 2,  # Get more messages, then deduplicate conversations
        )
        
        # Group by conversation and create result entries
        conversation_results = {}
        
        for message in message_results:
            conv_id = message["conversation_id"]
            
            if conv_id not in conversation_results:
                conversation_results[conv_id] = {
                    "id": conv_id,
                    "bot": message["conversation_bot"],
                    "title": message["conversation_title"],
                    "preview": self._generate_preview(message["content"], query),
                    "date": message["timestamp"][:10],  # Just the date part
                    "matches": [message],
                    "score": self._calculate_relevance_score(message["content"], query),
                }
            else:
                # Add additional match to existing conversation
                conversation_results[conv_id]["matches"].append(message)
                # Update score with additional match
                additional_score = self._calculate_relevance_score(message["content"], query)
                conversation_results[conv_id]["score"] += additional_score * 0.5  # Diminishing returns
        
        # Convert to list and sort by relevance score
        results = list(conversation_results.values())
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply additional filters
        results = self._apply_filters(results, filters)
        
        return results[:limit]
    
    def search_conversations(
        self,
        query: str,
        bot: Optional[str] = None,
        limit: int = 10,
        **filters: Any,
    ) -> List[Dict[str, Any]]:
        """Search conversation titles and metadata.
        
        Args:
            query: Search query
            bot: Filter by specific bot
            limit: Maximum number of results
            **filters: Additional search filters
            
        Returns:
            List of matching conversations
        """
        # Get all conversations and filter by title/content
        conversations = self.database.get_conversations(bot=bot, limit=limit * 5)
        
        # Simple text matching for now
        query_lower = query.lower()
        matching_conversations = []
        
        for conv in conversations:
            score = 0
            
            # Check title match
            if conv.get("title") and query_lower in conv["title"].lower():
                score += 10
            
            # Check if any message content matches (simple approach)
            for message in conv.get("messages", []):
                if query_lower in message.get("content", "").lower():
                    score += 1
            
            if score > 0:
                conv["score"] = score
                conv["preview"] = conv.get("title", "No title")
                conv["date"] = conv["created_at"][:10]
                matching_conversations.append(conv)
        
        # Sort by score and apply filters
        matching_conversations.sort(key=lambda x: x["score"], reverse=True)
        matching_conversations = self._apply_filters(matching_conversations, filters)
        
        return matching_conversations[:limit]
    
    def fuzzy_search(
        self,
        query: str,
        threshold: float = 0.6,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Perform fuzzy search for typos and similar terms.
        
        Args:
            query: Search query
            threshold: Similarity threshold (0.0 to 1.0)
            **kwargs: Additional search parameters
            
        Returns:
            List of fuzzy search results
        """
        # For now, implement simple fuzzy search
        # In a more advanced implementation, you could use libraries like fuzzywuzzy
        
        # Generate variations of the query
        query_variations = [
            query,
            query.lower(),
            query.upper(),
            query.capitalize(),
        ]
        
        # Add some common typo patterns
        if len(query) > 3:
            # Character swaps
            for i in range(len(query) - 1):
                swapped = list(query)
                swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
                query_variations.append("".join(swapped))
        
        all_results = []
        
        for variation in query_variations:
            try:
                results = self.search(variation, **kwargs)
                all_results.extend(results)
            except Exception as e:
                logger.debug(f"Fuzzy search variation '{variation}' failed: {e}")
                continue
        
        # Deduplicate by conversation ID
        seen_convs = set()
        unique_results = []
        
        for result in all_results:
            if result["id"] not in seen_convs:
                seen_convs.add(result["id"])
                unique_results.append(result)
        
        return unique_results
    
    def search_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        bot: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search conversations within a date range.
        
        Args:
            start_date: Start date for search
            end_date: End date for search
            bot: Filter by specific bot
            limit: Maximum number of results
            
        Returns:
            List of conversations in date range
        """
        conversations = self.database.get_conversations(bot=bot, limit=limit * 2)
        
        filtered_conversations = []
        
        for conv in conversations:
            conv_date = datetime.fromisoformat(conv["created_at"].replace("Z", "+00:00"))
            
            if start_date <= conv_date <= end_date:
                conv["preview"] = conv.get("title", "No title")
                conv["date"] = conv["created_at"][:10]
                filtered_conversations.append(conv)
        
        return filtered_conversations[:limit]
    
    def _generate_preview(self, content: str, query: str, max_length: int = 100) -> str:
        """Generate a preview snippet highlighting the search query.
        
        Args:
            content: Message content
            query: Search query
            max_length: Maximum preview length
            
        Returns:
            Preview text with query context
        """
        if not content or not query:
            return content[:max_length] if content else ""
        
        # Find the position of the query in the content (case-insensitive)
        query_lower = query.lower()
        content_lower = content.lower()
        
        query_pos = content_lower.find(query_lower)
        
        if query_pos == -1:
            # Query not found exactly, just return the beginning
            return content[:max_length] + ("..." if len(content) > max_length else "")
        
        # Calculate preview window around the query
        context_length = (max_length - len(query)) // 2
        start_pos = max(0, query_pos - context_length)
        end_pos = min(len(content), query_pos + len(query) + context_length)
        
        preview = content[start_pos:end_pos]
        
        # Add ellipsis if truncated
        if start_pos > 0:
            preview = "..." + preview
        if end_pos < len(content):
            preview = preview + "..."
        
        return preview
    
    def _calculate_relevance_score(self, content: str, query: str) -> float:
        """Calculate relevance score for a piece of content.
        
        Args:
            content: Content to score
            query: Search query
            
        Returns:
            Relevance score (higher is more relevant)
        """
        if not content or not query:
            return 0.0
        
        content_lower = content.lower()
        query_lower = query.lower()
        
        score = 0.0
        
        # Exact phrase match (highest score)
        if query_lower in content_lower:
            score += 10.0
        
        # Individual word matches
        query_words = query_lower.split()
        content_words = content_lower.split()
        
        for word in query_words:
            if word in content_words:
                score += 2.0
            else:
                # Partial word matches
                for content_word in content_words:
                    if word in content_word or content_word in word:
                        score += 0.5
        
        # Length penalty (prefer shorter, more focused content)
        length_penalty = min(1.0, 100.0 / len(content)) if content else 0
        score *= length_penalty
        
        return score
    
    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Apply additional filters to search results.
        
        Args:
            results: List of search results
            filters: Filter criteria
            
        Returns:
            Filtered results
        """
        filtered_results = results
        
        # Date range filter
        if "days" in filters:
            cutoff_date = datetime.now() - timedelta(days=filters["days"])
            cutoff_str = cutoff_date.isoformat()
            
            filtered_results = [
                result for result in filtered_results
                if result.get("date", "") >= cutoff_str[:10]
            ]
        
        # Minimum score filter
        if "min_score" in filters:
            min_score = filters["min_score"]
            filtered_results = [
                result for result in filtered_results
                if result.get("score", 0) >= min_score
            ]
        
        # Conversation length filter
        if "min_messages" in filters:
            min_messages = filters["min_messages"]
            filtered_results = [
                result for result in filtered_results
                if len(result.get("matches", [])) >= min_messages
            ]
        
        return filtered_results
