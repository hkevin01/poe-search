"""Conversation management for GUI."""

from typing import List, Dict, Any, Optional
from datetime import datetime

class ConversationManager:
    """Manages conversation data for the GUI."""
    
    def __init__(self):
        self.conversations = []
        self.filtered_conversations = []
    
    def set_conversations(self, conversations: List[Dict[str, Any]]):
        """Set the conversation list."""
        self.conversations = conversations
        self.filtered_conversations = conversations.copy()
    
    def get_conversations(self) -> List[Dict[str, Any]]:
        """Get filtered conversations."""
        return self.filtered_conversations
    
    def filter_conversations(self, search_text: str = "", bot_filter: str = "All Bots", 
                           date_filter: str = "All Time") -> List[Dict[str, Any]]:
        """Filter conversations based on criteria."""
        filtered = self.conversations.copy()
        
        # Text search
        if search_text:
            filtered = [
                conv for conv in filtered 
                if search_text.lower() in conv.get('title', '').lower()
            ]
        
        # Bot filter
        if bot_filter != "All Bots":
            bot_name = bot_filter.replace("🤖 ", "")
            filtered = [
                conv for conv in filtered 
                if conv.get('bot', 'Assistant') == bot_name
            ]
        
        self.filtered_conversations = filtered
        return filtered
    
    def get_conversation_by_id(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID."""
        for conv in self.conversations:
            if conv.get('id') == conv_id:
                return conv
        return None