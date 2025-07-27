"""
Utility functions for Poe Search application.
"""

import re
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: The filename to sanitize
        max_length: Maximum length of the filename

    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)

    # Trim whitespace and dots
    sanitized = sanitized.strip(' .')

    # Ensure not empty
    if not sanitized:
        sanitized = 'untitled'

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def format_timestamp(timestamp: str, format_type: str = 'human') -> str:
    """
    Format a timestamp string for display.

    Args:
        timestamp: ISO timestamp string
        format_type: 'human', 'short', or 'iso'

    Returns:
        Formatted timestamp string
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

        if format_type == 'human':
            now = datetime.now(dt.tzinfo)
            diff = now - dt

            if diff.days > 30:
                return dt.strftime('%Y-%m-%d')
            elif diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hours ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago"
            else:
                return "Just now"

        elif format_type == 'short':
            return dt.strftime('%m/%d %H:%M')
        else:  # iso
            return dt.isoformat()

    except (ValueError, TypeError):
        return timestamp or 'Unknown'


def extract_text_preview(text: str, max_length: int = 100) -> str:
    """
    Extract a preview of text content.

    Args:
        text: The text to preview
        max_length: Maximum length of preview

    Returns:
        Text preview with ellipsis if truncated
    """
    if not text or not text.strip():
        return ''

    # Clean whitespace
    cleaned = ' '.join(text.split())

    if len(cleaned) <= max_length:
        return cleaned

    # Find a good breaking point
    truncated = cleaned[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > max_length * 0.8:  # If space is reasonably close to end
        return cleaned[:last_space] + '...'
    else:
        return truncated + '...'


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def safe_json_load(file_path: Path, default: Any = None) -> Any:
    """
    Safely load JSON from a file with error handling.

    Args:
        file_path: Path to JSON file
        default: Default value if loading fails

    Returns:
        Loaded JSON data or default value
    """
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"Warning: Failed to load {file_path}: {e}")

    return default


def safe_json_save(data: Any, file_path: Path) -> bool:
    """
    Safely save data to JSON file with error handling.

    Args:
        data: Data to save
        file_path: Path to save file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError, TypeError) as e:
        print(f"Error: Failed to save {file_path}: {e}")
        return False


def get_file_size_human(file_path: Path) -> str:
    """
    Get human-readable file size.

    Args:
        file_path: Path to file

    Returns:
        Human-readable file size string
    """
    try:
        size = file_path.stat().st_size

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    except (OSError, IOError):
        return "Unknown"


def extract_conversation_id(url: str) -> Optional[str]:
    """
    Extract conversation ID from Poe.com URL.

    Args:
        url: Poe.com URL

    Returns:
        Conversation ID if found, None otherwise
    """
    if not url:
        return None

    # Pattern for Poe.com chat URLs
    pattern = r'/(?:chat|c)/([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)

    return match.group(1) if match else None


def ensure_directory(path: Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        True if directory exists or was created successfully
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, IOError):
        return False


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to project root
    """
    # Start from current file and go up until we find pyproject.toml
    current = Path(__file__).parent

    while current != current.parent:
        if (current / 'pyproject.toml').exists():
            return current
        current = current.parent

    # Fallback to parent of src directory
    return Path(__file__).parent.parent.parent


def create_backup_filename(original_path: Path) -> Path:
    """
    Create a backup filename with timestamp.

    Args:
        original_path: Original file path

    Returns:
        Backup file path with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    stem = original_path.stem
    suffix = original_path.suffix

    backup_name = f"{stem}_backup_{timestamp}{suffix}"
    return original_path.parent / backup_name
