"""Tests for utility functions."""

import pytest
from datetime import datetime
from pathlib import Path

from poe_search.utils.helpers import (
    generate_id,
    clean_text,
    truncate_text,
    format_timestamp,
    extract_keywords,
    validate_token,
    sanitize_filename,
    parse_size,
    format_size,
)


class TestHelpers:
    """Test cases for utility helper functions."""
    
    def test_generate_id(self):
        """Test ID generation."""
        # Test basic ID generation
        id1 = generate_id("test content")
        assert len(id1) == 8  # MD5 hash truncated to 8 chars
        assert isinstance(id1, str)
        
        # Test with prefix
        id2 = generate_id("test content", prefix="msg")
        assert id2.startswith("msg_")
        assert len(id2) == 12  # "msg_" + 8 chars
        
        # Same content should generate same ID
        id3 = generate_id("test content")
        assert id1 == id3
    
    def test_clean_text(self):
        """Test text cleaning."""
        # Test basic cleaning
        cleaned = clean_text("  hello   world  ")
        assert cleaned == "hello world"
        
        # Test empty text
        assert clean_text("") == ""
        assert clean_text(None) == ""
        
        # Test control character removal
        text_with_controls = "hello\x00\x08world\x1f"
        cleaned = clean_text(text_with_controls)
        assert cleaned == "hello world"
        
        # Test newline normalization
        multiline = "line1\n\n  line2\t\tline3"
        cleaned = clean_text(multiline)
        assert cleaned == "line1 line2 line3"
    
    def test_truncate_text(self):
        """Test text truncation."""
        # Test normal truncation
        long_text = "This is a very long text that should be truncated"
        truncated = truncate_text(long_text, max_length=20)
        assert len(truncated) <= 20
        assert truncated.endswith("...")
        
        # Test short text (no truncation)
        short_text = "Short"
        truncated = truncate_text(short_text, max_length=20)
        assert truncated == "Short"
        
        # Test custom suffix
        truncated = truncate_text(long_text, max_length=20, suffix="***")
        assert truncated.endswith("***")
        
        # Test empty text
        assert truncate_text("", max_length=10) == ""
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        # Test datetime object
        dt = datetime(2024, 1, 1, 12, 30, 45)
        formatted = format_timestamp(dt)
        assert formatted == "2024-01-01 12:30:45"
        
        # Test ISO string
        iso_string = "2024-01-01T12:30:45"
        formatted = format_timestamp(iso_string)
        assert "2024-01-01" in formatted
        
        # Test Unix timestamp
        timestamp = 1704110445.0  # 2024-01-01 12:00:45 UTC
        formatted = format_timestamp(timestamp)
        assert "2024-01-01" in formatted
        
        # Test custom format
        formatted = format_timestamp(dt, format_str="%Y/%m/%d")
        assert formatted == "2024/01/01"
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "Machine learning and artificial intelligence are fascinating topics in computer science."
        
        keywords = extract_keywords(text)
        assert len(keywords) > 0
        assert "machine" in keywords
        assert "learning" in keywords
        assert "artificial" in keywords
        assert "intelligence" in keywords
        
        # Test minimum length filter
        keywords = extract_keywords(text, min_length=5)
        assert "machine" in keywords
        assert "and" not in keywords  # Too short
        
        # Test max keywords limit
        keywords = extract_keywords(text, max_keywords=3)
        assert len(keywords) <= 3
        
        # Test empty text
        assert extract_keywords("") == []
        assert extract_keywords(None) == []
    
    def test_validate_token(self):
        """Test token validation."""
        # Valid tokens
        assert validate_token("abcd1234567890abcdef1234567890")
        assert validate_token("valid-token-with-dashes_and_underscores")
        
        # Invalid tokens
        assert not validate_token("")  # Empty
        assert not validate_token("short")  # Too short
        assert not validate_token("invalid token with spaces")  # Spaces
        assert not validate_token("invalid@token#with$symbols")  # Special chars
        assert not validate_token(None)  # None
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test basic sanitization
        filename = 'test<file>name'
        sanitized = sanitize_filename(filename)
        assert "<" not in sanitized
        assert ">" not in sanitized
        
        # Test all invalid characters
        invalid_filename = 'file<>:"/\\|?*name'
        sanitized = sanitize_filename(invalid_filename)
        assert all(char not in sanitized for char in '<>:"/\\|?*')
        
        # Test leading/trailing dots and spaces
        filename = "  .filename.  "
        sanitized = sanitize_filename(filename)
        assert not sanitized.startswith(".")
        assert not sanitized.endswith(".")
        
        # Test empty filename
        sanitized = sanitize_filename("")
        assert sanitized == "untitled"
        
        # Test very long filename
        long_filename = "a" * 300
        sanitized = sanitize_filename(long_filename)
        assert len(sanitized) <= 255
    
    def test_parse_size(self):
        """Test size string parsing."""
        # Test various units
        assert parse_size("100B") == 100
        assert parse_size("1KB") == 1024
        assert parse_size("1MB") == 1024 ** 2
        assert parse_size("1GB") == 1024 ** 3
        assert parse_size("1TB") == 1024 ** 4
        
        # Test decimal values
        assert parse_size("1.5KB") == int(1.5 * 1024)
        
        # Test without unit (defaults to bytes)
        assert parse_size("100") == 100
        
        # Test case insensitive
        assert parse_size("1kb") == 1024
        assert parse_size("1mb") == 1024 ** 2
        
        # Test invalid formats
        with pytest.raises(ValueError):
            parse_size("invalid")
        
        with pytest.raises(ValueError):
            parse_size("100XB")  # Invalid unit
    
    def test_format_size(self):
        """Test size formatting."""
        # Test bytes
        assert format_size(0) == "0 B"
        assert format_size(512) == "512 B"
        
        # Test KB
        assert format_size(1024) == "1.0 KB"
        assert format_size(1536) == "1.5 KB"
        
        # Test MB
        assert format_size(1024 ** 2) == "1.0 MB"
        assert format_size(int(2.5 * 1024 ** 2)) == "2.5 MB"
        
        # Test GB
        assert format_size(1024 ** 3) == "1.0 GB"
        
        # Test TB
        assert format_size(1024 ** 4) == "1.0 TB"
        
        # Test large numbers
        very_large = 5 * 1024 ** 4
        formatted = format_size(very_large)
        assert "TB" in formatted
