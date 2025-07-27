"""
Poe Search - Enhanced AI Conversation Manager

A comprehensive tool for searching and managing conversations from Poe.com
"""

__version__ = "1.3.0"
__author__ = "Kevin Hao"
__license__ = "MIT"

from .api.browser_client import PoeApiClient

__all__ = ['PoeApiClient']
