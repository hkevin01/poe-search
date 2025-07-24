import sqlite3
from typing import List
from datetime import datetime
from ..models.conversation import Conversation

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                bot TEXT,
                created_at TEXT,
                updated_at TEXT,
                category TEXT
            )
        ''')
        c.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS messages USING fts5(
                id,
                conversation_id,
                role,
                content,
                timestamp,
                bot_name
            )
        ''')
        conn.commit()
        conn.close()

    def save_conversations(self, conversations: List[Conversation]):
        """Save conversations to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for conv in conversations:
            c.execute('''
                INSERT OR REPLACE INTO conversations (id, title, bot, created_at, updated_at, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (conv.id, conv.title, conv.bot, conv.created_at.isoformat(), conv.updated_at.isoformat(), conv.category))
            for msg in conv.messages:
                c.execute('''
                    INSERT INTO messages (id, conversation_id, role, content, timestamp, bot_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (msg.id, conv.id, msg.role, msg.content, msg.timestamp.isoformat(), msg.bot_name))
        conn.commit()
        conn.close()

    def search_conversations(self, query: str) -> List[Conversation]:
        """Search using FTS5"""
        return []

    def get_all_conversations(self) -> List[Conversation]:
        """Get all conversations for display"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, title, bot, created_at, updated_at, category FROM conversations')
        rows = c.fetchall()
        conversations = []
        for row in rows:
            conv_id, title, bot, created_at, updated_at, category = row
            # Get messages for this conversation
            c.execute('SELECT id, role, content, timestamp, bot_name FROM messages WHERE conversation_id = ?', (conv_id,))
            msg_rows = c.fetchall()
            from ..models.conversation import Message, Conversation
            messages = [
                Message(
                    id=msg_id,
                    role=role,
                    content=content,
                    timestamp=datetime.fromisoformat(timestamp),
                    bot_name=bot_name
                ) for msg_id, role, content, timestamp, bot_name in msg_rows
            ]
            conversations.append(
                Conversation(
                    id=conv_id,
                    title=title,
                    bot=bot,
                    messages=messages,
                    created_at=datetime.fromisoformat(created_at),
                    updated_at=datetime.fromisoformat(updated_at),
                    category=category
                )
            )
        conn.close()
        return conversations
