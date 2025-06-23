"""Common utilities and helper functions."""

import hashlib
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


def generate_id(content: str, prefix: str = "") -> str:
    """Generate a unique ID based on content.
    
    Args:
        content: Content to hash
        prefix: Optional prefix for the ID
        
    Returns:
        Generated ID
    """
    hash_object = hashlib.md5(content.encode())
    hash_hex = hash_object.hexdigest()[:8]
    
    if prefix:
        return f"{prefix}_{hash_hex}"
    return hash_hex


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_timestamp(timestamp: Union[str, datetime, float], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to string.
    
    Args:
        timestamp: Timestamp to format
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if isinstance(timestamp, str):
        try:
            # Try to parse ISO format
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return timestamp  # Return as-is if can't parse
    elif isinstance(timestamp, float):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        return str(timestamp)
    
    return dt.strftime(format_str)


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        max_keywords: Maximum number of keywords
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Simple keyword extraction
    # In a more advanced implementation, you could use NLP libraries
    
    # Remove punctuation and split into words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter by length
    words = [word for word in words if len(word) >= min_length]
    
    # Remove common stop words
    stop_words = {
        "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
        "by", "from", "up", "about", "into", "through", "during", "before",
        "after", "above", "below", "between", "among", "this", "that", "these",
        "those", "is", "are", "was", "were", "be", "been", "being", "have",
        "has", "had", "do", "does", "did", "will", "would", "could", "should",
        "may", "might", "must", "can", "cannot", "shall", "what", "where",
        "when", "why", "how", "who", "which", "whose", "whom", "not", "very",
        "just", "now", "then", "here", "there", "also", "too", "only", "well",
        "back", "still", "way", "even", "new", "old", "good", "great", "small",
        "large", "own", "other", "many", "much", "more", "most", "some", "any",
        "all", "both", "each", "few", "little", "long", "right", "left", "high",
        "low", "next", "last", "first", "second", "same", "different"
    }
    
    words = [word for word in words if word not in stop_words]
    
    # Count frequency and sort
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, count in sorted_words[:max_keywords]]
    
    return keywords


def validate_token(token: str) -> bool:
    """Validate Poe authentication token format.
    
    Args:
        token: Token to validate
        
    Returns:
        True if token format is valid
    """
    if not token:
        return False
    
    # Basic validation - Poe tokens are typically long alphanumeric strings
    if len(token) < 20:
        return False
    
    # Check if it contains only valid characters
    if not re.match(r'^[a-zA-Z0-9\-_]+$', token):
        return False
    
    return True


def rate_limit(last_call_time: float, min_interval: float) -> None:
    """Apply rate limiting with minimum interval.
    
    Args:
        last_call_time: Timestamp of last call
        min_interval: Minimum interval between calls
    """
    elapsed = time.time() - last_call_time
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to be safe for filesystem.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:252] + "..."
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def parse_size(size_str: str) -> int:
    """Parse size string to bytes.
    
    Args:
        size_str: Size string like "10MB", "1GB"
        
    Returns:
        Size in bytes
    """
    size_str = size_str.upper().strip()
    
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }
    
    # Extract number and unit
    match = re.match(r'(\d+(?:\.\d+)?)\s*([A-Z]+)?', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    number = float(match.group(1))
    unit = match.group(2) or 'B'
    
    if unit not in units:
        raise ValueError(f"Unknown size unit: {unit}")
    
    return int(number * units[unit])


def format_size(size_bytes: int) -> str:
    """Format size in bytes to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"
