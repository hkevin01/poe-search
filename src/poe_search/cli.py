import sys
import os
from poe_search.api.browser_client import PoeApiClient
from poe_search.models.conversation import Conversation, Message
from poe_search.database.manager import DatabaseManager
from datetime import datetime
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), '../../poe_search.db')

def fetch_and_store():
    print("Launching browser and fetching conversations...")
    client = PoeApiClient()
    conversations_raw = client.get_conversations()
    print(f"Found {len(conversations_raw)} conversations.")
    conversations = []
    for conv in conversations_raw:
        conv_id = conv.get('id') or str(uuid.uuid4())
        messages_raw = client.get_conversation_messages(conv_id)
        messages = []
        for i, msg in enumerate(messages_raw):
            messages.append(Message(
                id=f"{conv_id}-{i}",
                role=msg.get('role', 'user'),
                content=msg.get('content', ''),
                timestamp=datetime.now(),
                bot_name=conv.get('bot')
            ))
        conversations.append(Conversation(
            id=conv_id,
            title=conv.get('title', 'Untitled'),
            bot=conv.get('bot', 'Unknown'),
            messages=messages,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            category=conv.get('category')
        ))
    client.close()
    db = DatabaseManager(DB_PATH)
    db.save_conversations(conversations)
    print(f"Saved {len(conversations)} conversations to database.")

def list_conversations():
    db = DatabaseManager(DB_PATH)
    conversations = db.get_all_conversations()
    for conv in conversations:
        print(f"{conv.id}: {conv.title} ({conv.bot}) - {len(conv.messages)} messages")

def show_conversation(conversation_id: str):
    db = DatabaseManager(DB_PATH)
    conversations = db.get_all_conversations()
    for conv in conversations:
        if conv.id == conversation_id:
            print(f"=== {conv.title} ({conv.bot}) ===")
            for msg in conv.messages:
                print(f"[{msg.role}] {msg.content}\n")
            return
    print(f"Conversation {conversation_id} not found.")

def search_conversations(query: str):
    db = DatabaseManager(DB_PATH)
    # Placeholder: implement real FTS5 search in manager.py for better results
    conversations = db.get_all_conversations()
    found = [conv for conv in conversations if query.lower() in conv.title.lower()]
    for conv in found:
        print(f"{conv.id}: {conv.title} ({conv.bot}) - {len(conv.messages)} messages")
    if not found:
        print("No conversations found matching query.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m poe_search.cli [fetch|list|show <id>|search <query>]")
        return
    cmd = sys.argv[1]
    if cmd == "fetch":
        fetch_and_store()
    elif cmd == "list":
        list_conversations()
    elif cmd == "show" and len(sys.argv) > 2:
        show_conversation(sys.argv[2])
    elif cmd == "search" and len(sys.argv) > 2:
        search_conversations(" ".join(sys.argv[2:]))
    else:
        print("Unknown command. Use 'fetch', 'list', 'show <id>', or 'search <query>'.")

if __name__ == "__main__":
    main()
