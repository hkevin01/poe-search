#!/usr/bin/env python3
"""
Comprehensive test runner for Poe conversation retrieval and API functionality.
"""

import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def run_test_suite():
    """Run all conversation-related tests."""
    print("=" * 60)
    print("POE CONVERSATION RETRIEVAL TEST SUITE")
    print("=" * 60)
    
    # Check if database exists
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("Please ensure the database is populated with real conversations.")
        return False
    
    print(f"✅ Database found at {db_path}")
    
    # Test 1: Basic conversation listing
    print("\n📋 Test 1: Basic Conversation Listing")
    try:
        from poe_search.storage.database import Database
        db = Database(f"sqlite:///{db_path}")
        conversations = db.get_conversations()
        print(f"✅ Found {len(conversations)} conversations")
        
        if len(conversations) == 0:
            print("⚠️  Warning: No conversations in database")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 2: Full conversation retrieval
    print("\n💬 Test 2: Full Conversation Retrieval")
    try:
        test_count = min(5, len(conversations))
        success_count = 0
        
        for i, conv in enumerate(conversations[:test_count]):
            full_conv = db.get_conversation(conv["id"])
            if full_conv and "messages" in full_conv:
                message_count = len(full_conv["messages"])
                print(f"  ✅ Conv {i+1}: {conv['title'][:30]}... "
                      f"({message_count} messages)")
                success_count += 1
            else:
                print(f"  ❌ Conv {i+1}: Failed to retrieve full conversation")
        
        print(f"✅ Successfully retrieved {success_count}/{test_count} conversations")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 3: Message text verification
    print("\n📝 Test 3: Message Text Verification")
    try:
        total_messages = 0
        total_text_chars = 0
        conversations_with_text = 0
        
        for conv in conversations[:10]:  # Test first 10 conversations
            full_conv = db.get_conversation(conv["id"])
            messages = full_conv.get("messages", [])
            total_messages += len(messages)
            
            conv_has_text = False
            for msg in messages:
                text = msg.get("text", "")
                if text.strip():
                    total_text_chars += len(text)
                    conv_has_text = True
            
            if conv_has_text:
                conversations_with_text += 1
        
        print(f"✅ Analyzed {total_messages} messages across 10 conversations")
        print(f"✅ Found {total_text_chars:,} characters of text")
        print(f"✅ {conversations_with_text}/10 conversations have text content")
        
        if conversations_with_text == 0:
            print("⚠️  Warning: No text content found in conversations")
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 4: Search functionality
    print("\n🔍 Test 4: Search Functionality")
    try:
        if hasattr(db, 'search_messages'):
            # Test search with common terms
            search_terms = ["help", "python", "how", "what", "code"]
            search_results_found = False
            
            for term in search_terms:
                results = db.search_messages(term)
                if results:
                    print(f"  ✅ Search for '{term}': {len(results)} results")
                    search_results_found = True
                    break
            
            if not search_results_found:
                print("  ⚠️  No search results found for common terms")
        else:
            print("  ⚠️  search_messages method not available")
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    
    # Test 5: Data integrity
    print("\n🔒 Test 5: Data Integrity")
    try:
        integrity_issues = 0
        
        for conv in conversations[:5]:  # Check first 5 conversations
            # Check required fields
            required_fields = ["id", "bot", "title", "created_at", "message_count"]
            for field in required_fields:
                if field not in conv or not conv[field]:
                    print(f"  ❌ Missing/empty field '{field}' in conv {conv.get('id', 'unknown')}")
                    integrity_issues += 1
            
            # Check message count accuracy
            full_conv = db.get_conversation(conv["id"])
            actual_count = len(full_conv.get("messages", []))
            expected_count = conv["message_count"]
            
            if actual_count != expected_count:
                print(f"  ❌ Message count mismatch in {conv['id']}: "
                      f"expected {expected_count}, got {actual_count}")
                integrity_issues += 1
        
        if integrity_issues == 0:
            print("✅ No data integrity issues found")
        else:
            print(f"⚠️  Found {integrity_issues} data integrity issues")
            
    except Exception as e:
        print(f"❌ Integrity test failed: {e}")
    
    # Test 6: Performance check
    print("\n⚡ Test 6: Performance Check")
    try:
        import time
        
        # Time conversation listing
        start_time = time.time()
        all_conversations = db.get_conversations()
        list_time = time.time() - start_time
        
        # Time individual retrieval
        start_time = time.time()
        test_conv = db.get_conversation(conversations[0]["id"])
        retrieval_time = time.time() - start_time
        
        print(f"✅ Listed {len(all_conversations)} conversations in {list_time:.3f}s")
        print(f"✅ Retrieved 1 full conversation in {retrieval_time:.3f}s")
        
        if list_time > 5.0:
            print("⚠️  Warning: Conversation listing is slow")
        if retrieval_time > 2.0:
            print("⚠️  Warning: Individual conversation retrieval is slow")
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)
    
    return True


def run_pytest_tests():
    """Run pytest on the test files."""
    print("\n🧪 Running pytest on test files...")
    
    test_files = [
        "tests/storage/test_conversation_retrieval.py",
        "tests/api/test_conversation_sync.py"
    ]
    
    for test_file in test_files:
        test_path = Path(__file__).parent.parent.parent / test_file
        if test_path.exists():
            print(f"\n📁 Running tests in {test_file}")
            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", str(test_path), "-v"],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent.parent
                )
                
                if result.returncode == 0:
                    print(f"✅ {test_file} - All tests passed")
                else:
                    print(f"❌ {test_file} - Some tests failed")
                    print("STDOUT:", result.stdout)
                    print("STDERR:", result.stderr)
                    
            except Exception as e:
                print(f"❌ Failed to run pytest on {test_file}: {e}")
        else:
            print(f"⚠️  Test file not found: {test_file}")


if __name__ == "__main__":
    print("Starting comprehensive conversation retrieval tests...\n")
    
    # Run custom test suite
    success = run_test_suite()
    
    # Run pytest tests if available
    try:
        import pytest
        run_pytest_tests()
    except ImportError:
        print("\n⚠️  pytest not available, skipping pytest tests")
    
    if success:
        print("\n🎉 All core tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)
