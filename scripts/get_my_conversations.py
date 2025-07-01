#!/usr/bin/env python3
"""Script to retrieve and display your Poe conversations using the working method."""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.storage.database import Database
from poe_search.utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConversationRetriever:
    """Class to retrieve conversations using the working method."""
    
    def __init__(self):
        """Initialize the retriever."""
        self.config = None
        self.client = None
        self.database = None
        
        # Known bot IDs that work
        self.known_bots = [
            ("capybara", "Sage"),
            ("chinchilla", "ChatGPT"),
            ("a2", "Claude"),
            ("beaver", "GPT-4"),
            ("acouchy", "Claude+"),
            ("agouti", "ChatGPT"),
            ("llama_2_70b", "Llama"),
            ("gemini_pro", "Gemini"),
            ("mixtral_8x7b", "Mixtral"),
            ("claude_3_5_sonnet", "Claude 3.5 Sonnet"),
            ("claude_3_5_haiku", "Claude 3.5 Haiku"),
            ("gpt_4o", "GPT-4o"),
            ("gpt_4o_mini", "GPT-4o Mini"),
        ]
    
    def setup(self):
        """Set up the retriever."""
        print("🔧 Setting up conversation retriever...")
        
        try:
            # Load configuration
            self.config = load_config()
            print("✅ Configuration loaded")
            
            # Initialize database
            self.database = Database("sqlite:///my_conversations.db")
            print("✅ Database initialized")
            
            # Initialize wrapper client
            if self.config.has_valid_tokens():
                tokens = self.config.get_poe_tokens()
                self.client = PoeAPIClient(token=tokens, config=self.config)
                print("✅ Wrapper client initialized")
                return True
            else:
                print("❌ No valid tokens for wrapper client")
                return False
                
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def get_conversations_from_bot(self, bot_id: str, bot_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversations from a specific bot."""
        print(f"🤖 Getting conversations from {bot_name} ({bot_id})...")
        
        try:
            # Get chat history for this bot
            response = self.client.client.get_chat_history(bot_id, count=limit)
            
            if not response or not isinstance(response, dict) or 'data' not in response:
                print(f"   ⚠️  No data for {bot_name}")
                return []
            
            bot_data = response['data'].get(bot_id, [])
            if not bot_data:
                print(f"   ⚠️  No conversations for {bot_name}")
                return []
            
            print(f"   ✅ Found {len(bot_data)} conversations")
            
            # Convert to our format
            conversations = []
            for conv in bot_data:
                conversation = {
                    "id": str(conv.get("chatId", "")),
                    "title": conv.get("title", f"Conversation with {bot_name}"),
                    "createdAt": conv.get("createdAt", datetime.now().isoformat()),
                    "updatedAt": conv.get("updatedAt", datetime.now().isoformat()),
                    "messageCount": conv.get("messageCount", 0),
                    "bot": {
                        "id": bot_id,
                        "displayName": bot_name
                    }
                }
                conversations.append(conversation)
            
            return conversations
            
        except Exception as e:
            print(f"   ❌ Failed to get conversations from {bot_name}: {e}")
            return []
    
    def get_all_conversations(self, limit_per_bot: int = 20) -> List[Dict[str, Any]]:
        """Get conversations from all known bots."""
        print(f"\n📋 Getting conversations from all bots (limit: {limit_per_bot} per bot)...")
        
        all_conversations = []
        
        for bot_id, bot_name in self.known_bots:
            try:
                conversations = self.get_conversations_from_bot(bot_id, bot_name, limit_per_bot)
                all_conversations.extend(conversations)
                
                # Add small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Failed to get conversations from {bot_name}: {e}")
                continue
        
        # Sort by updated date (most recent first)
        all_conversations.sort(key=lambda x: x.get('updatedAt', ''), reverse=True)
        
        print(f"\n📊 Total conversations found: {len(all_conversations)}")
        return all_conversations
    
    def get_conversation_details(self, conversation_id: str, bot_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed conversation with messages."""
        print(f"📖 Getting details for conversation {conversation_id}...")
        
        try:
            # Get message history
            messages = self.client.client.get_message_history(bot_id, conversation_id, count=100)
            
            if not messages:
                print(f"   ⚠️  No messages found for conversation {conversation_id}")
                return None
            
            # Convert messages to our format
            formatted_messages = []
            for msg in messages:
                formatted_message = {
                    "id": str(msg.get("id", "")),
                    "text": msg.get("text", ""),
                    "role": msg.get("role", "unknown"),
                    "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                    "author": msg.get("author", "unknown")
                }
                formatted_messages.append(formatted_message)
            
            print(f"   ✅ Found {len(formatted_messages)} messages")
            return {
                "id": conversation_id,
                "messages": formatted_messages
            }
            
        except Exception as e:
            print(f"   ❌ Failed to get conversation details: {e}")
            return None
    
    def display_conversation_summary(self, conversations: List[Dict[str, Any]]):
        """Display a summary of conversations."""
        print(f"\n{'='*80}")
        print("📊 CONVERSATION SUMMARY")
        print(f"{'='*80}")
        
        if not conversations:
            print("❌ No conversations found")
            return
        
        # Group by bot
        bot_conversations = {}
        for conv in conversations:
            bot_name = conv.get('bot', {}).get('displayName', 'Unknown')
            if bot_name not in bot_conversations:
                bot_conversations[bot_name] = []
            bot_conversations[bot_name].append(conv)
        
        # Display summary by bot
        for bot_name, convs in bot_conversations.items():
            print(f"\n🤖 {bot_name}: {len(convs)} conversations")
            
            # Show recent conversations
            recent_convs = sorted(convs, key=lambda x: x.get('updatedAt', ''), reverse=True)[:5]
            for conv in recent_convs:
                title = conv.get('title', 'Untitled')
                message_count = conv.get('messageCount', 0)
                updated_at = conv.get('updatedAt', '')
                
                # Format date
                try:
                    date_obj = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = updated_at
                
                print(f"   📝 {title} ({message_count} messages) - {date_str}")
        
        # Show total stats
        total_messages = sum(conv.get('messageCount', 0) for conv in conversations)
        print(f"\n📈 Total Statistics:")
        print(f"   📋 Total conversations: {len(conversations)}")
        print(f"   💬 Total messages: {total_messages}")
        print(f"   🤖 Bots used: {len(bot_conversations)}")
    
    def save_conversations_to_file(self, conversations: List[Dict[str, Any]], filename: str = None):
        """Save conversations to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"my_conversations_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, default=str)
            print(f"\n💾 Conversations saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save conversations: {e}")
    
    def store_in_database(self, conversations: List[Dict[str, Any]]):
        """Store conversations in the database."""
        print(f"\n💾 Storing conversations in database...")
        
        try:
            # Clear existing data
            self.database.clear_conversations()
            print("🗑️  Cleared existing data")
            
            # Store conversations
            stored_count = 0
            for conv in conversations:
                try:
                    self.database.store_conversation(conv)
                    stored_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to store conversation {conv.get('id', 'unknown')}: {e}")
                    continue
            
            print(f"✅ Stored {stored_count} conversations in database")
            
            # Test retrieval
            retrieved = self.database.get_all_conversations()
            print(f"📖 Retrieved {len(retrieved)} conversations from database")
            
        except Exception as e:
            print(f"❌ Database operation failed: {e}")
    
    def run(self, limit_per_bot: int = 20, save_to_file: bool = True, store_in_db: bool = True):
        """Run the conversation retrieval process."""
        print("🚀 Starting conversation retrieval...")
        
        if not self.setup():
            print("❌ Setup failed, aborting")
            return
        
        # Get all conversations
        conversations = self.get_all_conversations(limit_per_bot)
        
        if not conversations:
            print("❌ No conversations found")
            return
        
        # Display summary
        self.display_conversation_summary(conversations)
        
        # Save to file if requested
        if save_to_file:
            self.save_conversations_to_file(conversations)
        
        # Store in database if requested
        if store_in_db:
            self.store_in_database(conversations)
        
        print(f"\n✅ Conversation retrieval completed!")
        print(f"📊 Found {len(conversations)} conversations across all bots")


def main():
    """Main function."""
    print("🎯 Poe Search - My Conversations Retriever")
    print("=" * 50)
    
    # Parse command line arguments
    limit_per_bot = 20
    if len(sys.argv) > 1:
        try:
            limit_per_bot = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  Invalid limit '{sys.argv[1]}', using default: {limit_per_bot}")
    
    # Run the retriever
    retriever = ConversationRetriever()
    retriever.run(limit_per_bot=limit_per_bot)


if __name__ == "__main__":
    main() 