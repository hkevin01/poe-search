#!/usr/bin/env python3
"""
Project cleanup and organization script.

This script moves files to their proper locations according to the modern project structure.
"""

import shutil
from pathlib import Path


def organize_project():
    """Organize project files into proper structure."""
    project_root = Path(__file__).parent

    print("🧹 Organizing Poe Search project structure...")

    # Create necessary directories
    directories = [
        "archive",
        "docs",
        "docs/user_guide",
        "docs/development",
        "assets",
        "assets/icons",
        "assets/images",
        "logs",
        "dist",
        "tests/fixtures"
    ]

    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

    # Files to move to archive
    files_to_archive = [
        "gui_launcher.py",  # Will be replaced with compatibility wrapper
    ]

    # Move files to archive
    archive_dir = project_root / "archive"
    for file_name in files_to_archive:
        file_path = project_root / file_name
        if file_path.exists():
            archive_path = archive_dir / file_name
            if not archive_path.exists():  # Don't overwrite existing archives
                shutil.move(str(file_path), str(archive_path))
                print(f"📦 Archived: {file_name}")

    # Replace gui_launcher.py with compatibility wrapper
    new_launcher = project_root / "gui_launcher_new.py"
    old_launcher = project_root / "gui_launcher.py"

    if new_launcher.exists():
        shutil.move(str(new_launcher), str(old_launcher))
        print("✅ Updated gui_launcher.py with compatibility wrapper")

    # Move debug script to scripts directory
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    debug_script = project_root / "debug_browser_client.py"
    if debug_script.exists():
        new_location = scripts_dir / "debug_browser_client.py"
        if not new_location.exists():
            shutil.move(str(debug_script), str(new_location))
            print("📁 Moved debug_browser_client.py to scripts/")

    # Clean up temporary files
    temp_files = [
        ".pytest_cache",
        "__pycache__",
        "*.pyc",
        ".coverage",
        "htmlcov",
        ".mypy_cache"
    ]

    for pattern in temp_files:
        if pattern.startswith("."):
            # Handle directories
            temp_path = project_root / pattern
            if temp_path.exists() and temp_path.is_dir():
                shutil.rmtree(temp_path)
                print(f"🗑️  Removed: {pattern}")

    print("\n🎉 Project organization complete!")
    print("\nNew structure:")
    print("├── src/poe_search/          # Main application package")
    print("├── tests/                   # Test suite")
    print("├── docs/                    # Documentation")
    print("├── config/                  # Configuration files")
    print("├── scripts/                 # Utility scripts")
    print("├── archive/                 # Archived files")
    print("├── assets/                  # Static assets")
    print("├── requirements/            # Dependency files")
    print("└── logs/                    # Application logs")

    print("\n✅ Ready to use!")
    print("Run: python gui_launcher.py")


if __name__ == "__main__":
    organize_project()
