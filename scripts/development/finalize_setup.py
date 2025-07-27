#!/usr/bin/env python3
"""
Final project organization script.

Moves all test files and completes the project structure organization.
"""

import shutil
from pathlib import Path
import os


def show_current_test_files():
    """Show current test files in root directory."""
    project_root = Path(__file__).parent

    print("🔍 Scanning for test files in root directory...")

    # Find test files
    test_files = list(project_root.glob("test*.py"))

    if test_files:
        print(f"\n📋 Found {len(test_files)} test files to organize:")
        for file_path in test_files:
            print(f"  - {file_path.name}")
        return test_files
    else:
        print("ℹ️  No test*.py files found in root directory")
        return []


def move_specific_test_files():
    """Move specific test files to appropriate directories."""
    project_root = Path(__file__).parent
    moves_made = 0

    # Specific file movements based on content/purpose
    file_movements = {
        # Add specific test files if they exist
        # Format: "filename.py": "destination_directory"
    }

    # Find all test*.py files and categorize them
    test_files = list(project_root.glob("test*.py"))

    for test_file in test_files:
        # Determine destination based on filename patterns
        filename = test_file.name.lower()

        if any(pattern in filename for pattern in ['gui', 'window', 'dialog', 'widget', 'qt']):
            destination = "tests/gui"
        elif any(pattern in filename for pattern in ['integration', 'browser', 'client', 'api', 'e2e']):
            destination = "tests/integration"
        else:
            destination = "tests/unit"

        # Create destination directory
        dest_dir = project_root / destination
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Move file
        dest_file = dest_dir / test_file.name

        if not dest_file.exists():
            try:
                shutil.move(str(test_file), str(dest_file))
                print(f"📁 Moved {test_file.name} → {destination}/")
                moves_made += 1
            except Exception as e:
                print(f"❌ Error moving {test_file.name}: {e}")
        else:
            print(f"⚠️  {test_file.name} already exists in {destination}/")

    return moves_made


def organize_other_loose_files():
    """Organize other loose files in root directory."""
    project_root = Path(__file__).parent

    print("\n🧹 Organizing other loose files...")

    # Files to move to scripts directory
    script_files = [
        "debug_browser_client.py",
        "organize_project.py",
        "move_test_files.py",
    ]

    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    moves_made = 0
    for script_file in script_files:
        source = project_root / script_file
        destination = scripts_dir / script_file

        if source.exists() and not destination.exists():
            try:
                shutil.move(str(source), str(destination))
                print(f"📁 Moved {script_file} → scripts/")
                moves_made += 1
            except Exception as e:
                print(f"❌ Error moving {script_file}: {e}")

    # Files to archive
    archive_candidates = [
        "gui_launcher_new.py",
        "*.pyc",
        "*.pyo",
    ]

    archive_dir = project_root / "archive"
    archive_dir.mkdir(exist_ok=True)

    for pattern in archive_candidates:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                archive_path = archive_dir / file_path.name
                if not archive_path.exists():
                    try:
                        shutil.move(str(file_path), str(archive_path))
                        print(f"📦 Archived {file_path.name}")
                        moves_made += 1
                    except Exception as e:
                        print(f"❌ Error archiving {file_path.name}: {e}")

    return moves_made


def clean_temporary_files():
    """Clean up temporary files and directories."""
    project_root = Path(__file__).parent

    print("\n🗑️  Cleaning temporary files...")

    temp_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        ".mypy_cache",
        "*.egg-info",
    ]

    cleaned = 0
    for pattern in temp_patterns:
        for path in project_root.rglob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"🗑️  Removed directory: {path.relative_to(project_root)}")
                else:
                    path.unlink()
                    print(f"🗑️  Removed file: {path.relative_to(project_root)}")
                cleaned += 1
            except Exception as e:
                print(f"⚠️  Could not remove {path}: {e}")

    return cleaned


def show_final_structure():
    """Show the final project structure."""
    project_root = Path(__file__).parent

    print("\n🎯 Final Project Structure:")
    print("poe-search/")

    # Show main directories
    directories = [
        "src/poe_search/",
        "tests/",
        "config/",
        "scripts/",
        "docs/",
        "archive/",
        "assets/",
        "requirements/",
        ".github/workflows/",
    ]

    for directory in directories:
        dir_path = project_root / directory
        if dir_path.exists():
            print(f"├── {directory}")

            # Show key files in each directory
            if directory == "src/poe_search/":
                subdirs = ["api/", "core/", "gui/", "services/"]
                for subdir in subdirs:
                    subdir_path = dir_path / subdir
                    if subdir_path.exists():
                        print(f"│   ├── {subdir}")
                        # Show key files
                        for py_file in subdir_path.glob("*.py"):
                            if py_file.name != "__init__.py":
                                print(f"│   │   └── {py_file.name}")

            elif directory == "tests/":
                subdirs = ["unit/", "integration/", "gui/", "fixtures/"]
                for subdir in subdirs:
                    subdir_path = dir_path / subdir
                    if subdir_path.exists():
                        print(f"│   ├── {subdir}")
                        # Count test files
                        test_files = list(subdir_path.glob("test*.py"))
                        if test_files:
                            print(f"│   │   └── {len(test_files)} test files")

    # Show root files
    important_root_files = [
        "gui_launcher.py",
        "pyproject.toml",
        "README.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
    ]

    print("├── Root files:")
    for filename in important_root_files:
        file_path = project_root / filename
        if file_path.exists():
            print(f"│   ├── {filename}")


def main():
    """Main organization function."""
    print("🎯 Final Project Organization")
    print("=" * 50)

    # Show current state
    current_test_files = show_current_test_files()

    # Move test files
    print("\n📁 Moving test files to proper directories...")
    test_moves = move_specific_test_files()

    # Organize other files
    other_moves = organize_other_loose_files()

    # Clean temporary files
    cleaned = clean_temporary_files()

    # Show final structure
    show_final_structure()

    # Summary
    print(f"\n✅ Organization Complete!")
    print(f"   📁 Test files moved: {test_moves}")
    print(f"   📁 Other files organized: {other_moves}")
    print(f"   🗑️  Temporary files cleaned: {cleaned}")

    print(f"\n🚀 Ready to use!")
    print(f"   Run tests: pytest tests/")
    print(f"   Launch GUI: python gui_launcher.py")
    print(f"   Debug browser: python scripts/debug_browser_client.py")


if __name__ == "__main__":
    main()
