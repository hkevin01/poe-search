"""
Test suite for Poe Search.

This package contains comprehensive tests for the Poe Search application:
- unit/: Unit tests for individual components
- integration/: Integration tests for component interactions
- gui/: GUI tests for the PyQt6 interface
- fixtures/: Test data and mock objects
"""

import pytest
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures"

# Test configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "gui: marks tests as GUI tests (require display)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
