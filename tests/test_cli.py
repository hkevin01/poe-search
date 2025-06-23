"""Tests for CLI functionality."""

import pytest
import json
from click.testing import CliRunner
from unittest.mock import Mock, patch

from poe_search.cli import main


class TestCLI:
    """Test cases for CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_version_command(self):
        """Test --version command."""
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "poe-search" in result.output
    
    def test_help_command(self):
        """Test --help command."""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Poe Search" in result.output
        assert "search" in result.output
        assert "sync" in result.output
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_search_command(self, mock_client_class):
        """Test search command."""
        # Mock client and search results
        mock_client = Mock()
        mock_client.search.return_value = [
            {
                "id": "conv_123",
                "bot": "chinchilla",
                "preview": "This is about machine learning",
                "date": "2024-01-01",
            }
        ]
        mock_client_class.return_value = mock_client
        
        # Test search command
        result = self.runner.invoke(main, ["search", "machine learning"])
        
        assert result.exit_code == 0
        assert "Search Results" in result.output
        mock_client.search.assert_called_once_with(
            query="machine learning",
            bot=None,
            limit=10,
        )
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_search_command_with_options(self, mock_client_class):
        """Test search command with additional options."""
        mock_client = Mock()
        mock_client.search.return_value = []
        mock_client_class.return_value = mock_client
        
        # Test search with bot filter and limit
        result = self.runner.invoke(main, [
            "search", "python", 
            "--bot", "claude",
            "--limit", "5"
        ])
        
        assert result.exit_code == 0
        mock_client.search.assert_called_once_with(
            query="python",
            bot="claude",
            limit=5,
        )
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_search_no_results(self, mock_client_class):
        """Test search command with no results."""
        mock_client = Mock()
        mock_client.search.return_value = []
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(main, ["search", "nonexistent"])
        
        assert result.exit_code == 0
        assert "No conversations found" in result.output
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_sync_command(self, mock_client_class):
        """Test sync command."""
        mock_client = Mock()
        mock_client.sync.return_value = {
            "new": 5,
            "updated": 2,
            "total": 7,
        }
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(main, ["sync"])
        
        assert result.exit_code == 0
        assert "Sync completed" in result.output
        assert "New: 5" in result.output
        mock_client.sync.assert_called_once_with(days=7)
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_sync_command_with_days(self, mock_client_class):
        """Test sync command with custom days."""
        mock_client = Mock()
        mock_client.sync.return_value = {"new": 0, "updated": 0, "total": 0}
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(main, ["sync", "--days", "30"])
        
        assert result.exit_code == 0
        mock_client.sync.assert_called_once_with(days=30)
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_bots_list_command(self, mock_client_class):
        """Test bots list command."""
        mock_client = Mock()
        mock_client.get_bots.return_value = [
            {
                "name": "chinchilla",
                "display_name": "ChatGPT",
                "conversation_count": 10,
                "last_used": "2024-01-01",
            },
            {
                "name": "a2",
                "display_name": "Claude",
                "conversation_count": 5,
                "last_used": "2024-01-02",
            },
        ]
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(main, ["bots", "list"])
        
        assert result.exit_code == 0
        assert "Your Bots" in result.output
        assert "ChatGPT" in result.output
        assert "Claude" in result.output
        mock_client.get_bots.assert_called_once()
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_export_command(self, mock_client_class):
        """Test export command."""
        mock_client = Mock()
        mock_client.export_conversations = Mock()
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(main, [
            "export",
            "--format", "json",
            "--output", "test_export.json"
        ])
        
        assert result.exit_code == 0
        assert "exported to test_export.json" in result.output
        mock_client.export_conversations.assert_called_once_with(
            output_path="test_export.json",
            format="json",
        )
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_analytics_command(self, mock_client_class):
        """Test analytics command."""
        mock_client = Mock()
        mock_client.get_analytics.return_value = {
            "total_conversations": 25,
            "active_bots": 3,
            "messages_sent": 150,
            "avg_conversation_length": 6.0,
        }
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(main, ["analytics"])
        
        assert result.exit_code == 0
        assert "Analytics for the last month" in result.output
        assert "Total conversations: 25" in result.output
        assert "Active bots: 3" in result.output
        mock_client.get_analytics.assert_called_once_with(period="month")
    
    @patch('poe_search.cli.save_config')
    def test_config_set_token(self, mock_save_config):
        """Test config set-token command."""
        result = self.runner.invoke(main, ["config", "set-token", "test_token_123"])
        
        assert result.exit_code == 0
        assert "Token saved successfully" in result.output
        # Verify save_config was called (config content tested in mock)
        mock_save_config.assert_called_once()
    
    @patch('poe_search.cli.load_config')
    def test_config_show(self, mock_load_config):
        """Test config show command."""
        mock_load_config.return_value = {
            "token": "test_token_123",
            "database_url": "sqlite:///poe_search.db",
            "log_level": "INFO",
        }
        
        result = self.runner.invoke(main, ["config", "show"])
        
        assert result.exit_code == 0
        assert "Poe Search Configuration" in result.output
        assert "test_token_123..." in result.output  # Token should be truncated
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_search_json_output(self, mock_client_class):
        """Test search command with JSON output format."""
        mock_client = Mock()
        mock_client.search.return_value = [
            {
                "id": "conv_123",
                "bot": "chinchilla",
                "preview": "Test preview",
                "date": "2024-01-01",
            }
        ]
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(main, [
            "search", "test",
            "--format", "json"
        ])
        
        assert result.exit_code == 0
        # Should contain valid JSON
        try:
            json.loads(result.output.strip())
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
    
    @patch('poe_search.cli.PoeSearchClient')
    def test_error_handling(self, mock_client_class):
        """Test CLI error handling."""
        mock_client = Mock()
        mock_client.search.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(main, ["search", "test"])
        
        assert result.exit_code == 0  # CLI shouldn't crash
        assert "Search failed" in result.output
