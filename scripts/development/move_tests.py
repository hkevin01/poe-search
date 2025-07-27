#!/usr/bin/env python3
"""
Move test files from root to proper test directories.
"""

import shutil
from pathlib import Path
import re


def move_test_files():
    """Move test files from root to proper test structure."""
    project_root = Path(__file__).parent

    print("🧪 Moving test files to proper test structure...")

    # Ensure test directories exist
    test_dirs = [
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/gui",
        "tests/fixtures"
    ]

    for test_dir in test_dirs:
        dir_path = project_root / test_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Ensured directory exists: {test_dir}")

    # Find all test*.py files in root
    test_files = list(project_root.glob("test*.py"))

    if not test_files:
        print("ℹ️  No test*.py files found in root directory")
        return

    print(f"\n📋 Found {len(test_files)} test files to move:")
    for file_path in test_files:
        print(f"  - {file_path.name}")

    # Move files based on their type/content
    for test_file in test_files:
        destination = categorize_test_file(test_file, project_root)

        if destination:
            destination_path = project_root / destination / test_file.name

            # Don't overwrite existing files
            if destination_path.exists():
                print(f"⚠️  Skipping {test_file.name} - already exists in {destination}")
                continue

            try:
                shutil.move(str(test_file), str(destination_path))
                print(f"📁 Moved {test_file.name} → {destination}/")
            except Exception as e:
                print(f"❌ Error moving {test_file.name}: {e}")
        else:
            print(f"⚠️  Could not categorize {test_file.name} - leaving in root")

    print("\n🎉 Test file organization complete!")


def categorize_test_file(file_path: Path, project_root: Path) -> str:
    """
    Categorize test file to determine destination directory.

    Args:
        file_path: Path to the test file
        project_root: Project root directory

    Returns:
        Destination directory relative to project root
    """
    file_name = file_path.name.lower()

    try:
        # Read file content to analyze
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        content = ""

    # GUI tests - check for PyQt, GUI, window, etc.
    gui_indicators = [
        'pyqt', 'qtwidgets', 'qapplication', 'qmainwindow',
        'gui', 'window', 'dialog', 'widget'
    ]

    if any(indicator in content.lower() for indicator in gui_indicators):
        return "tests/gui"

    # Integration tests - check for multiple components, API calls, browser, etc.
    integration_indicators = [
        'browser_client', 'poeapiclient', 'selenium', 'webdriver',
        'integration', 'end_to_end', 'e2e', 'full_test'
    ]

    if any(indicator in content.lower() for indicator in integration_indicators):
        return "tests/integration"

    # Check filename patterns
    if any(pattern in file_name for pattern in ['integration', 'e2e', 'browser', 'api']):
        return "tests/integration"

    if any(pattern in file_name for pattern in ['gui', 'window', 'dialog', 'widget']):
        return "tests/gui"

    # Default to unit tests
    return "tests/unit"


def create_test_init_files():
    """Create __init__.py files in test directories."""
    project_root = Path(__file__).parent

    test_dirs = ["tests", "tests/unit", "tests/integration", "tests/gui"]

    for test_dir in test_dirs:
        init_file = project_root / test_dir / "__init__.py"
        if not init_file.exists():
            init_content = f'"""\n{test_dir.split("/")[-1].title()} tests for Poe Search.\n"""\n'
            with open(init_file, 'w') as f:
                f.write(init_content)
            print(f"✅ Created {test_dir}/__init__.py")


def create_test_fixtures():
    """Create sample test fixtures."""
    project_root = Path(__file__).parent
    fixtures_dir = project_root / "tests" / "fixtures"

    # Sample conversation data
    sample_conversation = {
        "export_info": {
            "timestamp": "2024-01-20T10:30:00Z",
            "total_conversations": 2,
            "format": "json"
        },
        "conversations": [
            {
                "id": "test_conv_1",
                "title": "Python Programming Help",
                "bot": "Claude",
                "category": "Technical",
                "url": "https://poe.com/chat/test_conv_1",
                "method": "test_method",
                "extracted_at": "2024-01-20T10:30:00Z",
                "messages": [
                    {
                        "role": "user",
                        "content": "How do I handle exceptions in Python?",
                        "timestamp": "2024-01-20T10:30:00Z"
                    },
                    {
                        "role": "assistant",
                        "content": "In Python, you handle exceptions using try-except blocks...",
                        "timestamp": "2024-01-20T10:31:00Z"
                    }
                ]
            },
            {
                "id": "test_conv_2",
                "title": "Creative Writing Ideas",
                "bot": "GPT-4",
                "category": "Creative",
                "url": "https://poe.com/chat/test_conv_2",
                "method": "test_method",
                "extracted_at": "2024-01-20T11:00:00Z",
                "messages": [
                    {
                        "role": "user",
                        "content": "Give me some creative writing prompts",
                        "timestamp": "2024-01-20T11:00:00Z"
                    }
                ]
            }
        ]
    }

    fixture_file = fixtures_dir / "sample_conversations.json"
    if not fixture_file.exists():
        import json
        with open(fixture_file, 'w', encoding='utf-8') as f:
            json.dump(sample_conversation, f, indent=2, ensure_ascii=False)
        print(f"✅ Created test fixture: {fixture_file}")


def update_test_imports():
    """Update imports in moved test files."""
    project_root = Path(__file__).parent

    # Find all test files in test directories
    test_files = []
    for test_dir in ["tests/unit", "tests/integration", "tests/gui"]:
        test_files.extend((project_root / test_dir).glob("test*.py"))

    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update relative imports to absolute imports
            # This is a simple pattern - you might need to adjust based on actual imports
            updated_content = content

            # Replace common import patterns
            import_replacements = [
                (r'from poe_search\.', r'from poe_search.'),  # Already correct
                (r'import poe_search\.', r'import poe_search.'),  # Already correct
                # Add more patterns as needed
            ]

            # Only write if content changed
            if updated_content != content:
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"✅ Updated imports in {test_file.name}")

        except Exception as e:
            print(f"⚠️  Could not update imports in {test_file.name}: {e}")


if __name__ == "__main__":
    move_test_files()
    create_test_init_files()
    create_test_fixtures()
    update_test_imports()

    print("\n🎯 Test organization complete!")
    print("\nTest structure:")
    print("tests/")
    print("├── __init__.py")
    print("├── unit/           # Unit tests")
    print("│   ├── __init__.py")
    print("│   └── test_*.py")
    print("├── integration/    # Integration tests")
    print("│   ├── __init__.py")
    print("│   └── test_*.py")
    print("├── gui/           # GUI tests")
    print("│   ├── __init__.py")
    print("│   └── test_*.py")
    print("└── fixtures/      # Test data")
    print("    └── sample_conversations.json")

    print("\n✅ Ready to run tests with: pytest tests/")
