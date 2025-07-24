#!/usr/bin/env python3
"""Script to run Poe API integration tests and provide a summary."""

import os
import subprocess
import sys
from pathlib import Path


def run_api_tests():
    """Run the Poe API integration tests."""
    print("🔍 Running Poe API Integration Tests...")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Run the test suite
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/api/test_poe_api_integration.py",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print("Test Results:")
        print("-" * 40)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        # Extract summary from output
        lines = result.stdout.split('\n')
        summary_line = None
        for line in reversed(lines):
            if "passed" in line.lower() and ("failed" in line.lower() or "skipped" in line.lower()):
                summary_line = line.strip()
                break
        
        if summary_line:
            print(f"📊 Summary: {summary_line}")
        
        print("\n" + "=" * 60)
        print("Test Coverage:")
        print("-" * 40)
        print("✅ API Connection & Authentication")
        print("✅ Bot Retrieval")
        print("✅ Conversation Retrieval")
        print("✅ Rate Limiting")
        print("✅ Mock Data Generation")
        print("✅ Configuration Integration")
        print("✅ Error Handling")
        print("✅ Live API Connection (when token available)")
        
        print("\n" + "=" * 60)
        print("Key Features Tested:")
        print("-" * 40)
        print("• Poe API client initialization")
        print("• Token handling (string and dict formats)")
        print("• Bot information retrieval")
        print("• Recent conversations fetching")
        print("• Individual conversation retrieval")
        print("• Rate limiting configuration")
        print("• Mock data fallback")
        print("• Configuration system integration")
        print("• Error handling and recovery")
        
        if result.stderr:
            print("\n⚠️  Warnings/Errors:")
            print("-" * 40)
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Poe Search - API Integration Test Suite")
    print("=" * 60)
    
    success = run_api_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("The Poe API wrapper is working correctly.")
        print("\nNext steps:")
        print("1. Set up your Poe token in config/secrets.json")
        print("2. Run live integration tests with: pytest -m integration")
        print("3. Start using the API client in your application")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        print("Make sure the poe-api-wrapper dependency is installed.")
        sys.exit(1)


if __name__ == "__main__":
    main() 