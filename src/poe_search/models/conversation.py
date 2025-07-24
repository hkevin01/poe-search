from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Message:
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    bot_name: Optional[str] = None

@dataclass
class Conversation:
    id: str
    title: str
    bot: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    category: Optional[str] = None
