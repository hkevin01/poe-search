"""
Data models for Poe Search application.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ConversationCategory(Enum):
    """Enumeration of conversation categories."""
    TECHNICAL = "Technical"
    CREATIVE = "Creative"
    EDUCATIONAL = "Educational"
    BUSINESS = "Business"
    SCIENCE = "Science"
    GENERAL = "General"
    CLAUDE_CONVERSATIONS = "Claude Conversations"
    GPT_CONVERSATIONS = "GPT Conversations"
    GEMINI_CONVERSATIONS = "Gemini Conversations"


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None
    bot_name: Optional[str] = None
    message_id: Optional[str] = None
    extraction_method: Optional[str] = None

    def __post_init__(self):
        """Validate message data after initialization."""
        if self.role not in ['user', 'assistant', 'system']:
            raise ValueError(f"Invalid message role: {self.role}")
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")


@dataclass
class Conversation:
    """Represents a conversation with metadata and messages."""
    id: str
    title: str
    bot: str
    category: str
    url: str
    method: str
    extracted_at: str
    messages: List[Message] = field(default_factory=list)

    def __post_init__(self):
        """Validate conversation data after initialization."""
        if not self.id or not self.id.strip():
            raise ValueError("Conversation ID cannot be empty")
        if not self.title or not self.title.strip():
            raise ValueError("Conversation title cannot be empty")

    @property
    def message_count(self) -> int:
        """Get the number of messages in this conversation."""
        return len(self.messages)

    @property
    def user_message_count(self) -> int:
        """Get the number of user messages."""
        return sum(1 for msg in self.messages if msg.role == 'user')

    @property
    def assistant_message_count(self) -> int:
        """Get the number of assistant messages."""
        return sum(1 for msg in self.messages if msg.role == 'assistant')

    def add_message(self, message: Message) -> None:
        """Add a message to this conversation."""
        if not isinstance(message, Message):
            raise TypeError("Expected Message instance")
        self.messages.append(message)

    def get_text_preview(self, max_length: int = 100) -> str:
        """Get a text preview of the conversation."""
        if not self.messages:
            return self.title[:max_length]

        first_message = self.messages[0]
        preview = f"{self.title}: {first_message.content}"
        return preview[:max_length] + "..." if len(preview) > max_length else preview

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'bot': self.bot,
            'category': self.category,
            'url': self.url,
            'method': self.method,
            'extracted_at': self.extracted_at,
            'messages': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp,
                    'bot_name': msg.bot_name,
                    'message_id': msg.message_id,
                    'extraction_method': msg.extraction_method
                }
                for msg in self.messages
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary."""
        messages = [
            Message(
                role=msg_data['role'],
                content=msg_data['content'],
                timestamp=msg_data.get('timestamp'),
                bot_name=msg_data.get('bot_name'),
                message_id=msg_data.get('message_id'),
                extraction_method=msg_data.get('extraction_method')
            )
            for msg_data in data.get('messages', [])
        ]

        return cls(
            id=data['id'],
            title=data['title'],
            bot=data['bot'],
            category=data['category'],
            url=data['url'],
            method=data['method'],
            extracted_at=data['extracted_at'],
            messages=messages
        )


@dataclass
class SearchResult:
    """Represents a search result."""
    conversation_id: str
    title: str
    snippet: str
    match_score: float
    matched_messages: List[int] = field(default_factory=list)

    def __post_init__(self):
        """Validate search result data."""
        if not self.conversation_id:
            raise ValueError("Conversation ID cannot be empty")
        if self.match_score < 0 or self.match_score > 1:
            raise ValueError("Match score must be between 0 and 1")


@dataclass
class ExportOptions:
    """Options for exporting conversations."""
    format: str  # 'json', 'txt', 'csv', 'markdown'
    include_metadata: bool = True
    include_timestamps: bool = True
    max_conversations: Optional[int] = None
    date_range: Optional[tuple] = None
    categories: Optional[List[str]] = None

    def __post_init__(self):
        """Validate export options."""
        valid_formats = ['json', 'txt', 'csv', 'markdown']
        if self.format not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of: {valid_formats}")


@dataclass
class SyncProgress:
    """Represents sync progress information."""
    message: str
    percentage: int
    total_conversations: int = 0
    processed_conversations: int = 0
    errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate progress data."""
        if not 0 <= self.percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")
