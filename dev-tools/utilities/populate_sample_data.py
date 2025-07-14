#!/usr/bin/env python3
"""
Populate database with sample conversation data for testing.
This creates sample conversations to test search functionality.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from poe_search.storage.database import Database

# Set up logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "populate_sample_data.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def create_sample_conversations():
    """Create sample conversation data."""
    base_time = datetime.now() - timedelta(days=1)
    
    conversations = [
        {
            "id": "conv_001",
            "bot": "claude-3-5-sonnet",
            "title": "Python Web Development Discussion",
            "created_at": base_time.isoformat(),
            "updated_at": (base_time + timedelta(minutes=30)).isoformat(),
            "message_count": 6,
            "messages": [
                {
                    "id": "msg_001_1",
                    "role": "user",
                    "content": "I want to learn Python web development. Where should I start?",
                    "timestamp": base_time.isoformat(),
                },
                {
                    "id": "msg_001_2", 
                    "role": "bot",
                    "content": "Great choice! For Python web development, I'd recommend starting with Flask or Django. Flask is lighter and easier to learn, while Django is more feature-complete for larger applications.",
                    "timestamp": (base_time + timedelta(minutes=1)).isoformat(),
                    "bot": "claude-3-5-sonnet",
                },
                {
                    "id": "msg_001_3",
                    "role": "user", 
                    "content": "What about FastAPI? I've heard it's modern and fast.",
                    "timestamp": (base_time + timedelta(minutes=5)).isoformat(),
                },
                {
                    "id": "msg_001_4",
                    "role": "bot",
                    "content": "FastAPI is excellent! It's built for modern Python with automatic API documentation, type hints, and async support. Perfect for building REST APIs and microservices.",
                    "timestamp": (base_time + timedelta(minutes=6)).isoformat(),
                    "bot": "claude-3-5-sonnet",
                },
                {
                    "id": "msg_001_5",
                    "role": "user",
                    "content": "Can you show me a simple FastAPI example?",
                    "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
                },
                {
                    "id": "msg_001_6",
                    "role": "bot",
                    "content": "Here's a simple FastAPI example:\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}\n\n@app.get('/items/{item_id}')\ndef read_item(item_id: int, q: str = None):\n    return {'item_id': item_id, 'q': q}\n```",
                    "timestamp": (base_time + timedelta(minutes=12)).isoformat(),
                    "bot": "claude-3-5-sonnet",
                },
            ],
        },
        {
            "id": "conv_002",
            "bot": "chinchilla",
            "title": "JavaScript React Tutorial",
            "created_at": (base_time + timedelta(hours=2)).isoformat(),
            "updated_at": (base_time + timedelta(hours=2, minutes=45)).isoformat(),
            "message_count": 4,
            "messages": [
                {
                    "id": "msg_002_1",
                    "role": "user",
                    "content": "I'm new to React. Can you explain components and props?",
                    "timestamp": (base_time + timedelta(hours=2)).isoformat(),
                },
                {
                    "id": "msg_002_2",
                    "role": "bot",
                    "content": "React components are reusable pieces of UI. Props (properties) are how you pass data to components. Think of components as functions that return JSX, and props as the function parameters.",
                    "timestamp": (base_time + timedelta(hours=2, minutes=1)).isoformat(),
                    "bot": "chinchilla",
                },
                {
                    "id": "msg_002_3",
                    "role": "user",
                    "content": "Can you show me a simple component example?",
                    "timestamp": (base_time + timedelta(hours=2, minutes=5)).isoformat(),
                },
                {
                    "id": "msg_002_4",
                    "role": "bot",
                    "content": "Here's a simple React component:\n\n```jsx\nfunction Greeting({name}) {\n  return <h1>Hello, {name}!</h1>;\n}\n\n// Usage:\n<Greeting name='Alice' />\n```\n\nThe `name` prop is passed to the component and displayed in the heading.",
                    "timestamp": (base_time + timedelta(hours=2, minutes=7)).isoformat(),
                    "bot": "chinchilla",
                },
            ],
        },
        {
            "id": "conv_003",
            "bot": "a2",
            "title": "Database Design Best Practices",
            "created_at": (base_time + timedelta(hours=4)).isoformat(),
            "updated_at": (base_time + timedelta(hours=4, minutes=20)).isoformat(),
            "message_count": 4,
            "messages": [
                {
                    "id": "msg_003_1",
                    "role": "user",
                    "content": "What are the key principles of good database design?",
                    "timestamp": (base_time + timedelta(hours=4)).isoformat(),
                },
                {
                    "id": "msg_003_2",
                    "role": "bot",
                    "content": "Key database design principles include: 1) Normalization to eliminate redundancy, 2) Proper indexing for performance, 3) Consistent naming conventions, 4) Appropriate data types, and 5) Well-defined relationships between tables.",
                    "timestamp": (base_time + timedelta(hours=4, minutes=1)).isoformat(),
                    "bot": "a2",
                },
                {
                    "id": "msg_003_3",
                    "role": "user",
                    "content": "Can you explain normalization in simple terms?",
                    "timestamp": (base_time + timedelta(hours=4, minutes=10)).isoformat(),
                },
                {
                    "id": "msg_003_4",
                    "role": "bot",
                    "content": "Normalization means organizing data to reduce duplication. Instead of storing customer info in every order, you create separate customer and order tables linked by ID. This saves space and ensures consistency.",
                    "timestamp": (base_time + timedelta(hours=4, minutes=12)).isoformat(),
                    "bot": "a2",
                },
            ],
        },
        {
            "id": "conv_004",
            "bot": "gemini-pro",
            "title": "Machine Learning Introduction",
            "created_at": (base_time + timedelta(hours=6)).isoformat(),
            "updated_at": (base_time + timedelta(hours=6, minutes=35)).isoformat(),
            "message_count": 6,
            "messages": [
                {
                    "id": "msg_004_1",
                    "role": "user",
                    "content": "I want to get started with machine learning. What should I know?",
                    "timestamp": (base_time + timedelta(hours=6)).isoformat(),
                },
                {
                    "id": "msg_004_2",
                    "role": "bot",
                    "content": "Machine learning is about training algorithms to find patterns in data. You'll need basic math (statistics, linear algebra), Python programming, and familiarity with libraries like scikit-learn, pandas, and numpy.",
                    "timestamp": (base_time + timedelta(hours=6, minutes=2)).isoformat(),
                    "bot": "gemini-pro",
                },
                {
                    "id": "msg_004_3",
                    "role": "user",
                    "content": "What are the main types of machine learning?",
                    "timestamp": (base_time + timedelta(hours=6, minutes=10)).isoformat(),
                },
                {
                    "id": "msg_004_4",
                    "role": "bot",
                    "content": "There are three main types: 1) Supervised learning (with labeled data), 2) Unsupervised learning (finding patterns in unlabeled data), and 3) Reinforcement learning (learning through rewards and penalties).",
                    "timestamp": (base_time + timedelta(hours=6, minutes=12)).isoformat(),
                    "bot": "gemini-pro",
                },
                {
                    "id": "msg_004_5",
                    "role": "user",
                    "content": "Can you give me an example of supervised learning?",
                    "timestamp": (base_time + timedelta(hours=6, minutes=20)).isoformat(),
                },
                {
                    "id": "msg_004_6",
                    "role": "bot",
                    "content": "Email spam detection is a classic example. You train a model with thousands of emails labeled as 'spam' or 'not spam'. The model learns to identify spam patterns and can then classify new emails automatically.",
                    "timestamp": (base_time + timedelta(hours=6, minutes=22)).isoformat(),
                    "bot": "gemini-pro",
                },
            ],
        },
    ]
    
    return conversations


def populate_database(db_path, conversations):
    """Populate database with sample conversations."""
    logger.info(f"Populating database: {db_path}")
    
    db = Database(str(db_path))
    
    for conv in conversations:
        logger.info(f"Adding conversation: {conv['title']}")
        db.save_conversation(conv)
    
    # Verify data was saved
    all_conversations = db.get_conversations()
    logger.info(f"Database now contains {len(all_conversations)} conversations")
    
    # Test search functionality
    search_results = db.search_messages("Python")
    logger.info(f"Search for 'Python' returned {len(search_results)} results")
    
    search_results = db.search_messages("React")
    logger.info(f"Search for 'React' returned {len(search_results)} results")
    
    search_results = db.search_messages("machine learning")
    logger.info(f"Search for 'machine learning' returned {len(search_results)} results")


def main():
    """Populate all databases with sample data."""
    logger.info("=== POPULATING DATABASES WITH SAMPLE DATA ===")
    
    # Create sample data
    conversations = create_sample_conversations()
    logger.info(f"Created {len(conversations)} sample conversations")
    
    # Populate all database files
    db_files = [
        project_root / "data" / "poe_search.db",
        project_root / "data" / "my_conversations.db",
        project_root / "data" / "test_conversations.db"
    ]
    
    for db_file in db_files:
        populate_database(db_file, conversations)
    
    logger.info("=== SAMPLE DATA POPULATION COMPLETE ===")
    logger.info(f"Log saved to: {log_file}")


if __name__ == "__main__":
    main()
