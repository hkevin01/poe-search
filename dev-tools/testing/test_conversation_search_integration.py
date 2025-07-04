#!/usr/bin/env python3
"""
Test script for conversation search and listing functionality.

This script tests that:
1. Conversations can be listed from the database
2. Search functionality returns results
3. Various filtering and edge cases work correctly
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import the auto-installer
sys.path.insert(0, str(PROJECT_ROOT / "dev-tools" / "utilities"))
try:
    from auto_installer import ensure_dependencies
except ImportError:
    print("❌ Could not import auto_installer. "
          "Running without dependency check.")
    
    def ensure_dependencies(packages):
        return True


def main():
    """Run conversation search and listing tests."""
    print("🧪 Testing Conversation Search and Listing Functionality")
    print("=" * 60)
    
    # Ensure dependencies are installed
    required_packages = [
        "pytest>=7.0.0",
        "pytest-asyncio",
        "playwright",
        "python-dotenv",
        "rich",
        "aiosqlite"
    ]
    
    print("📦 Checking and installing dependencies...")
    if not ensure_dependencies(required_packages):
        print("❌ Failed to install required dependencies")
        return 1
    
    # Run the tests
    print("\n🧪 Running conversation search and listing tests...")
    print("-" * 40)
    
    try:
        import pytest

        # Get the test file path
        test_file = (PROJECT_ROOT.parent / "tests" /
                     "test_conversation_search.py")
        
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return 1
        
        # Run pytest with verbose output
        exit_code = pytest.main([
            str(test_file),
            "-v",
            "--tb=short",
            "--no-header",
            "-x"  # Stop on first failure
        ])
        
        print("\n" + "=" * 60)
        if exit_code == 0:
            print("✅ All conversation search and listing tests passed!")
            print("\n🎉 Search functionality verified:")
            print("   • Conversation listing works correctly")
            print("   • Message search returns results")
            print("   • Filtering by bot, date, and limit works")
            print("   • Edge cases are handled properly")
            print("   • Database robustness verified")
        else:
            print("❌ Some tests failed!")
            print("   Check the output above for details.")
        
        return exit_code
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are properly installed.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
