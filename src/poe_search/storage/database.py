"""Database storage for conversations and metadata."""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class Database:
    """SQLite database for storing conversation data."""
    
    def __init__(self, database_url: str = "sqlite:///poe_search.db"):
        """Initialize database connection.
        
        Args:
            database_url: Database connection URL
        """
        # Extract path from URL (simple sqlite:/// handling)
        if database_url.startswith("sqlite:///"):
            self.db_path = database_url[10:]  # Remove "sqlite:///"
        else:
            self.db_path = database_url
        
        self.db_path = Path(self.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def _init_database(self):
        """Initialize database tables."""
        with self._get_connection() as conn:
            # Conversations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    bot TEXT NOT NULL,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    data TEXT,  -- JSON data
                    UNIQUE(id)
                )
            """)
            
            # Messages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,  -- 'user' or 'bot'
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    bot TEXT,
                    data TEXT,  -- JSON data
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id),
                    UNIQUE(id)
                )
            """)
            
            # Bots table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bots (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    display_name TEXT,
                    first_seen TEXT NOT NULL,
                    last_used TEXT,
                    conversation_count INTEGER DEFAULT 0,
                    message_count INTEGER DEFAULT 0,
                    data TEXT,  -- JSON data
                    UNIQUE(id)
                )
            """)
            
            # Search index for full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                    message_id UNINDEXED,
                    content,
                    conversation_id UNINDEXED,
                    bot UNINDEXED
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_bot ON conversations(bot)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_bot ON messages(bot)")
            
            conn.commit()
    
    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if conversation exists in database.
        
        Args:
            conversation_id: Conversation ID to check
            
        Returns:
            True if conversation exists
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            return cursor.fetchone() is not None
    
    def save_conversation(self, conversation: Dict[str, Any]) -> None:
        """Save conversation to database.
        
        Args:
            conversation: Conversation data
        """
        with self._get_connection() as conn:
            # Insert/update conversation
            conn.execute("""
                INSERT OR REPLACE INTO conversations 
                (id, bot, title, created_at, updated_at, message_count, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation["id"],
                conversation["bot"],
                conversation.get("title", ""),
                conversation["created_at"],
                conversation["updated_at"],
                conversation.get("message_count", 0),
                json.dumps(conversation),
            ))
            
            # Save messages
            messages = conversation.get("messages", [])
            for message in messages:
                self.save_message(message, conversation["id"], conn)
            
            # Update bot information
            self._update_bot_info(conversation["bot"], conn)
            
            conn.commit()
    
    def save_message(
        self,
        message: Dict[str, Any],
        conversation_id: str,
        conn: Optional[sqlite3.Connection] = None,
    ) -> None:
        """Save message to database.
        
        Args:
            message: Message data
            conversation_id: ID of conversation this message belongs to
            conn: Optional database connection
        """
        close_conn = conn is None
        if conn is None:
            conn = self._get_connection()
        
        try:
            # Insert/update message
            conn.execute("""
                INSERT OR REPLACE INTO messages 
                (id, conversation_id, role, content, timestamp, bot, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                message["id"],
                conversation_id,
                message["role"],
                message["content"],
                message["timestamp"],
                message.get("bot"),
                json.dumps(message),
            ))
            
            # Update FTS index
            conn.execute("""
                INSERT OR REPLACE INTO messages_fts 
                (message_id, content, conversation_id, bot)
                VALUES (?, ?, ?, ?)
            """, (
                message["id"],
                message["content"],
                conversation_id,
                message.get("bot", ""),
            ))
            
            if close_conn:
                conn.commit()
                
        finally:
            if close_conn:
                conn.close()
    
    def update_conversation(self, conversation: Dict[str, Any]) -> None:
        """Update existing conversation.
        
        Args:
            conversation: Updated conversation data
        """
        # For now, just save (which replaces)
        self.save_conversation(conversation)
    
    def get_conversations(
        self,
        bot: Optional[str] = None,
        days: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get conversations from database.
        
        Args:
            bot: Filter by bot
            days: Filter by days (from now)
            limit: Limit number of results
            
        Returns:
            List of conversations
        """
        query = "SELECT * FROM conversations WHERE 1=1"
        params = []
        
        if bot:
            query += " AND bot = ?"
            params.append(bot)
        
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            query += " AND created_at >= ?"
            params.append(cutoff_date)
        
        query += " ORDER BY updated_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            conversations = []
            for row in rows:
                conv_data = json.loads(row["data"]) if row["data"] else {}
                conv_data.update({
                    "id": row["id"],
                    "bot": row["bot"],
                    "title": row["title"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "message_count": row["message_count"],
                })
                conversations.append(conv_data)
            
            return conversations
    
    def search_messages(
        self,
        query: str,
        bot: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search messages using full-text search.
        
        Args:
            query: Search query
            bot: Filter by bot
            limit: Maximum results
            
        Returns:
            List of matching messages with conversation info
        """
        sql_query = """
            SELECT m.*, c.title as conversation_title, c.bot as conversation_bot
            FROM messages_fts fts
            JOIN messages m ON fts.message_id = m.id
            JOIN conversations c ON m.conversation_id = c.id
            WHERE messages_fts MATCH ?
        """
        params = [query]
        
        if bot:
            sql_query += " AND c.bot = ?"
            params.append(bot)
        
        sql_query += " ORDER BY rank LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.execute(sql_query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                message_data = json.loads(row["data"]) if row["data"] else {}
                message_data.update({
                    "id": row["id"],
                    "conversation_id": row["conversation_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "timestamp": row["timestamp"],
                    "bot": row["bot"],
                    "conversation_title": row["conversation_title"],
                    "conversation_bot": row["conversation_bot"],
                })
                results.append(message_data)
            
            return results
    
    def get_bots(self) -> List[Dict[str, Any]]:
        """Get all bots from database.
        
        Returns:
            List of bot information
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM bots 
                ORDER BY last_used DESC, conversation_count DESC
            """)
            rows = cursor.fetchall()
            
            bots = []
            for row in rows:
                bot_data = json.loads(row["data"]) if row["data"] else {}
                bot_data.update({
                    "id": row["id"],
                    "name": row["name"],
                    "display_name": row["display_name"],
                    "first_seen": row["first_seen"],
                    "last_used": row["last_used"],
                    "conversation_count": row["conversation_count"],
                    "message_count": row["message_count"],
                })
                bots.append(bot_data)
            
            return bots
    
    def get_analytics(self, period: str = "month") -> Dict[str, Any]:
        """Get usage analytics.
        
        Args:
            period: Analysis period (day, week, month, year)
            
        Returns:
            Analytics data
        """
        # Calculate date range
        now = datetime.now()
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)  # Default to month
        
        start_date_str = start_date.isoformat()
        
        with self._get_connection() as conn:
            # Total conversations
            cursor = conn.execute(
                "SELECT COUNT(*) FROM conversations WHERE created_at >= ?",
                (start_date_str,)
            )
            total_conversations = cursor.fetchone()[0]
            
            # Active bots
            cursor = conn.execute(
                "SELECT COUNT(DISTINCT bot) FROM conversations WHERE created_at >= ?",
                (start_date_str,)
            )
            active_bots = cursor.fetchone()[0]
            
            # Messages sent (user messages)
            cursor = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE role = 'user' AND timestamp >= ?",
                (start_date_str,)
            )
            messages_sent = cursor.fetchone()[0]
            
            # Average conversation length
            cursor = conn.execute("""
                SELECT AVG(message_count) FROM conversations 
                WHERE created_at >= ? AND message_count > 0
            """, (start_date_str,))
            avg_length_result = cursor.fetchone()[0]
            avg_conversation_length = avg_length_result if avg_length_result else 0
            
            return {
                "period": period,
                "start_date": start_date_str,
                "total_conversations": total_conversations,
                "active_bots": active_bots,
                "messages_sent": messages_sent,
                "avg_conversation_length": avg_conversation_length,
            }
    
    def _update_bot_info(self, bot_id: str, conn: sqlite3.Connection) -> None:
        """Update bot information in database.
        
        Args:
            bot_id: Bot identifier
            conn: Database connection
        """
        now = datetime.now().isoformat()
        
        # Get current bot info if exists
        cursor = conn.execute("SELECT * FROM bots WHERE id = ?", (bot_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing bot
            conn.execute("""
                UPDATE bots 
                SET last_used = ?,
                    conversation_count = (
                        SELECT COUNT(*) FROM conversations WHERE bot = ?
                    ),
                    message_count = (
                        SELECT COUNT(*) FROM messages WHERE bot = ?
                    )
                WHERE id = ?
            """, (now, bot_id, bot_id, bot_id))
        else:
            # Insert new bot
            conn.execute("""
                INSERT INTO bots 
                (id, name, display_name, first_seen, last_used, conversation_count, message_count, data)
                VALUES (?, ?, ?, ?, ?, 1, 0, ?)
            """, (
                bot_id,
                bot_id,  # Default name to ID
                bot_id.replace("_", " ").title(),  # Default display name
                now,
                now,
                json.dumps({"created": now}),
            ))
