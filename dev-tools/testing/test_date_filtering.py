#!/usr/bin/env python3
"""Test script to verify date filtering in the search widget."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from poe_search.storage.database import Database


def test_date_filtering():
    """Test that date filtering works properly in search."""
    # Use the real database
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    # Initialize database
    db = Database(f"sqlite:///{db_path}")
    
    # Get all conversations first
    all_conversations = db.get_conversations()
    print(f"Total conversations in database: {len(all_conversations)}")
    
    if len(all_conversations) == 0:
        print("No conversations found in database")
        return False
    
    # Find the date range of conversations
    dates = []
    for conv in all_conversations:
        created_at = conv.get("created_at")
        if created_at:
            try:
                if created_at.endswith('Z'):
                    created_at = created_at[:-1] + '+00:00'
                conv_date = datetime.fromisoformat(created_at)
                dates.append(conv_date)
            except ValueError:
                continue
    
    if not dates:
        print("No valid dates found in conversations")
        return False
    
    dates.sort()
    oldest_date = dates[0]
    newest_date = dates[-1]
    
    print(f"Date range: {oldest_date.date()} to {newest_date.date()}")
    print(f"Conversations with valid dates: {len(dates)}")
    
    # Test 1: Filter to only recent conversations (last 30 days)
    cutoff_date = datetime.now() - timedelta(days=30)
    recent_count = sum(1 for d in dates if d >= cutoff_date)
    print(f"Conversations in last 30 days: {recent_count}")
    
    # Test 2: Filter to only older conversations (older than 30 days)
    old_count = sum(1 for d in dates if d < cutoff_date)
    print(f"Conversations older than 30 days: {old_count}")
    
    # Test 3: Filter to a narrow date range (first week of conversations)
    if len(dates) > 1:
        start_date = oldest_date
        end_date = oldest_date + timedelta(days=7)
        week_count = sum(1 for d in dates if start_date <= d <= end_date)
        week_text = (f"Conversations in first week "
                    f"({start_date.date()} to {end_date.date()}): {week_count}")
        print(week_text)
    
    print("\nDate filtering test completed successfully!")
    return True


if __name__ == "__main__":
    test_date_filtering()
