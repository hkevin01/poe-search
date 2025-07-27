#!/usr/bin/env python3
"""
Execute comprehensive repository organization.

This script runs the complete repository organization following
modern best practices and industry standards.
"""

import sys
from pathlib import Path

def main():
    """Execute comprehensive organization."""
    print("🚀 Starting Comprehensive Repository Organization")
    print("=" * 60)

    try:
        # Import and run the comprehensive organizer
        from comprehensive_organization import RepositoryOrganizer

        organizer = RepositoryOrganizer()
        organizer.organize_repository()

        print("\n✅ Organization Complete!")
        print("\n🎯 Next Steps:")
        print("1. Run: python -m pytest tests/")
        print("2. Test: python gui_launcher.py")
        print("3. Check: python -c 'from poe_search import Conversation'")
        print("4. Review: ORGANIZATION_REPORT.md")

        return 0

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory")
        return 1

    except Exception as e:
        print(f"❌ Organization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
