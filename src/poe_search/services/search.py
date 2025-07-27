"""
Search service for conversation content.
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ..core.models import Conversation, SearchResult


@dataclass
class SearchOptions:
    """Options for search operations."""
    case_sensitive: bool = False
    use_regex: bool = False
    search_messages: bool = True
    search_titles: bool = True
    max_results: Optional[int] = None


class SearchService:
    """Service for searching through conversations."""

    def __init__(self):
        self.last_search_query = ""
        self.last_search_results = []

    def search_conversations(
        self,
        conversations: List[Conversation],
        query: str,
        options: SearchOptions = None
    ) -> List[SearchResult]:
        """
        Search through conversations.

        Args:
            conversations: List of conversations to search
            query: Search query string
            options: Search options

        Returns:
            List of search results
        """
        if not query or not query.strip():
            return []

        if options is None:
            options = SearchOptions()

        # Cache the search
        self.last_search_query = query

        results = []

        for conv in conversations:
            result = self._search_single_conversation(conv, query, options)
            if result:
                results.append(result)

        # Sort by match score (highest first)
        results.sort(key=lambda x: x.match_score, reverse=True)

        # Limit results if specified
        if options.max_results:
            results = results[:options.max_results]

        self.last_search_results = results
        return results

    def _search_single_conversation(
        self,
        conversation: Conversation,
        query: str,
        options: SearchOptions
    ) -> Optional[SearchResult]:
        """
        Search within a single conversation.

        Args:
            conversation: Conversation to search
            query: Search query
            options: Search options

        Returns:
            SearchResult if matches found, None otherwise
        """
        matches = []
        match_score = 0.0
        matched_messages = []

        # Prepare query for searching
        search_query = query if options.case_sensitive else query.lower()

        # Search in title
        if options.search_titles:
            title = conversation.title
            search_title = title if options.case_sensitive else title.lower()

            if options.use_regex:
                try:
                    pattern = re.compile(search_query, re.IGNORECASE if not options.case_sensitive else 0)
                    if pattern.search(search_title):
                        matches.append(f"Title: {title}")
                        match_score += 2.0  # Title matches are weighted higher
                except re.error:
                    # Fallback to simple string search if regex is invalid
                    if search_query in search_title:
                        matches.append(f"Title: {title}")
                        match_score += 2.0
            else:
                if search_query in search_title:
                    matches.append(f"Title: {title}")
                    match_score += 2.0

        # Search in messages
        if options.search_messages and conversation.messages:
            for i, message in enumerate(conversation.messages):
                content = message.content
                search_content = content if options.case_sensitive else content.lower()

                match_found = False

                if options.use_regex:
                    try:
                        pattern = re.compile(search_query, re.IGNORECASE if not options.case_sensitive else 0)
                        if pattern.search(search_content):
                            match_found = True
                    except re.error:
                        # Fallback to simple string search
                        if search_query in search_content:
                            match_found = True
                else:
                    if search_query in search_content:
                        match_found = True

                if match_found:
                    # Extract snippet around the match
                    snippet = self._extract_snippet(content, query, options.case_sensitive)
                    matches.append(f"{message.role}: {snippet}")
                    matched_messages.append(i)
                    match_score += 1.0

        if matches:
            # Create snippet from first few matches
            snippet = "; ".join(matches[:3])
            if len(matches) > 3:
                snippet += f" ... (+{len(matches) - 3} more matches)"

            return SearchResult(
                conversation_id=conversation.id,
                title=conversation.title,
                snippet=snippet,
                match_score=min(match_score, 1.0),  # Normalize score
                matched_messages=matched_messages
            )

        return None

    def _extract_snippet(self, text: str, query: str, case_sensitive: bool = False) -> str:
        """
        Extract a snippet of text around the search query.

        Args:
            text: Text to extract snippet from
            query: Search query
            case_sensitive: Whether search is case sensitive

        Returns:
            Text snippet with context around the match
        """
        search_text = text if case_sensitive else text.lower()
        search_query = query if case_sensitive else query.lower()

        # Find the position of the match
        pos = search_text.find(search_query)
        if pos == -1:
            return text[:100] + "..." if len(text) > 100 else text

        # Extract context around the match
        context_length = 50
        start = max(0, pos - context_length)
        end = min(len(text), pos + len(query) + context_length)

        snippet = text[start:end]

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def filter_by_category(self, conversations: List[Conversation], category: str) -> List[Conversation]:
        """
        Filter conversations by category.

        Args:
            conversations: List of conversations to filter
            category: Category to filter by

        Returns:
            Filtered list of conversations
        """
        if not category or category == "All Categories":
            return conversations

        return [conv for conv in conversations if conv.category == category]

    def filter_by_bot(self, conversations: List[Conversation], bot_name: str) -> List[Conversation]:
        """
        Filter conversations by bot name.

        Args:
            conversations: List of conversations to filter
            bot_name: Bot name to filter by

        Returns:
            Filtered list of conversations
        """
        if not bot_name or bot_name == "All Bots":
            return conversations

        return [conv for conv in conversations if conv.bot == bot_name]

    def get_search_suggestions(self, conversations: List[Conversation], partial_query: str) -> List[str]:
        """
        Get search suggestions based on partial query.

        Args:
            conversations: Conversations to analyze for suggestions
            partial_query: Partial search query

        Returns:
            List of suggested search terms
        """
        if len(partial_query) < 2:
            return []

        suggestions = set()
        partial_lower = partial_query.lower()

        # Collect words from titles and messages
        words = set()
        for conv in conversations:
            # Add words from title
            title_words = conv.title.lower().split()
            words.update(title_words)

            # Add words from messages (first few only for performance)
            for message in conv.messages[:5]:
                message_words = message.content.lower().split()
                words.update(message_words[:20])  # Limit words per message

        # Find matching words
        for word in words:
            if (len(word) > 3 and
                partial_lower in word and
                word.startswith(partial_lower) and
                word.isalpha()):
                suggestions.add(word.capitalize())

        return sorted(list(suggestions))[:10]  # Return top 10 suggestions

    def get_popular_search_terms(self, conversations: List[Conversation]) -> List[str]:
        """
        Get popular search terms from conversations.

        Args:
            conversations: Conversations to analyze

        Returns:
            List of popular terms
        """
        word_freq = {}

        # Count word frequency
        for conv in conversations:
            # Count words in titles
            for word in conv.title.lower().split():
                if len(word) > 3 and word.isalpha():
                    word_freq[word] = word_freq.get(word, 0) + 2  # Title words get higher weight

            # Count words in first message of each conversation
            if conv.messages:
                for word in conv.messages[0].content.lower().split()[:50]:
                    if len(word) > 3 and word.isalpha():
                        word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top terms
        sorted_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [term.capitalize() for term, freq in sorted_terms[:20] if freq > 2]
