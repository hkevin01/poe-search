"""
Authentication tests for Poe Search API.

Tests authentication mechanisms, token validation, and session management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from poe_search.api.clients.browser_client import PoeApiClient
from poe_search.core.exceptions.base import AuthenticationError


class TestAuthenticationFlow:
    """Test authentication flow and token management."""

    @pytest.fixture
    def valid_tokens(self):
        """Valid test tokens."""
        return {
            'p-b': 'AG58MLIXFnbOh98QAv4YHA==',
            'p-lat': '87OepyV2QcF9TkiuqhaFyWZgROH+Vp00g0QZLwZEMg=='
        }

    @pytest.fixture
    def invalid_tokens(self):
        """Invalid test tokens."""
        return {
            'p-b': 'invalid_token_123',
            'p-lat': 'invalid_lat_token_456'
        }

    @pytest.fixture
    def mock_driver(self):
        """Mock WebDriver for testing."""
        driver = Mock()
        driver.get = Mock()
        driver.quit = Mock()
        driver.find_elements = Mock()
        driver.execute_script = Mock()
        return driver

    def test_token_validation_format(self, valid_tokens, invalid_tokens):
        """Test token format validation."""
        # Valid tokens should not raise errors during initialization
        client = PoeApiClient(token=valid_tokens['p-b'])
        assert client.token == valid_tokens['p-b']

        # Empty token should raise error
        with pytest.raises(ValueError, match="Token cannot be empty"):
            PoeApiClient(token="")

        with pytest.raises(ValueError, match="Token cannot be empty"):
            PoeApiClient(token=None)

    @patch('poe_search.api.clients.browser_client.webdriver.Chrome')
    def test_successful_authentication(self, mock_chrome, valid_tokens, mock_driver):
        """Test successful authentication flow."""
        # Setup mock driver
        mock_chrome.return_value = mock_driver
        mock_driver.find_elements.return_value = [Mock()]  # Auth indicator found

        client = PoeApiClient(token=valid_tokens['p-b'], headless=True)

        with client:
            result = client.authenticate()
            assert result is True

            # Verify browser setup
            mock_chrome.assert_called_once()
            mock_driver.get.assert_called()

    @patch('poe_search.api.clients.browser_client.webdriver.Chrome')
    def test_failed_authentication(self, mock_chrome, invalid_tokens, mock_driver):
        """Test failed authentication flow."""
        # Setup mock driver for failed auth
        mock_chrome.return_value = mock_driver
        mock_driver.find_elements.return_value = []  # No auth indicator

        with pytest.raises(AuthenticationError, match="Authentication failed"):
            client = PoeApiClient(token=invalid_tokens['p-b'], headless=True)
            with client:
                client.authenticate()

    @patch('poe_search.api.clients.browser_client.webdriver.Chrome')
    def test_token_expiration_handling(self, mock_chrome, valid_tokens, mock_driver):
        """Test handling of expired tokens."""
        mock_chrome.return_value = mock_driver

        # Mock expired token scenario
        mock_driver.find_elements.side_effect = [
            [],  # First call: no auth indicator (expired)
            [Mock()],  # Second call: would succeed with new token
        ]

        client = PoeApiClient(token=valid_tokens['p-b'], headless=True)

        with pytest.raises(AuthenticationError):
            with client:
                client.authenticate()

    @patch('poe_search.api.clients.browser_client.webdriver.Chrome')
    def test_network_error_during_auth(self, mock_chrome, valid_tokens, mock_driver):
        """Test network errors during authentication."""
        mock_chrome.return_value = mock_driver

        # Mock network error
        from selenium.common.exceptions import WebDriverException
        mock_driver.get.side_effect = WebDriverException("Network error")

        client = PoeApiClient(token=valid_tokens['p-b'], headless=True)

        with pytest.raises(AuthenticationError, match="Network error during authentication"):
            with client:
                client.authenticate()

    def test_token_storage_security(self, valid_tokens):
        """Test that tokens are handled securely."""
        client = PoeApiClient(token=valid_tokens['p-b'])

        # Token should not appear in string representation
        client_str = str(client)
        assert valid_tokens['p-b'] not in client_str
        assert "***" in client_str or "masked" in client_str.lower()

        # Token should not appear in repr
        client_repr = repr(client)
        assert valid_tokens['p-b'] not in client_repr

    @patch('poe_search.api.clients.browser_client.webdriver.Chrome')
    def test_session_management(self, mock_chrome, valid_tokens, mock_driver):
        """Test session management and cleanup."""
        mock_chrome.return_value = mock_driver
        mock_driver.find_elements.return_value = [Mock()]

        client = PoeApiClient(token=valid_tokens['p-b'], headless=True)

        # Test context manager behavior
        with client:
            assert client.driver is not None
            client.authenticate()

        # Driver should be closed after context exit
        mock_driver.quit.assert_called_once()

    @patch('poe_search.api.clients.browser_client.webdriver.Chrome')
    def test_concurrent_authentication_attempts(self, mock_chrome, valid_tokens, mock_driver):
        """Test handling of concurrent authentication attempts."""
        mock_chrome.return_value = mock_driver
        mock_driver.find_elements.return_value = [Mock()]

        client = PoeApiClient(token=valid_tokens['p-b'], headless=True)

        with client:
            # First authentication should succeed
            result1 = client.authenticate()
            assert result1 is True

            # Second authentication should use cached result
            result2 = client.authenticate()
            assert result2 is True

            # Should not make additional browser calls
            assert mock_driver.get.call_count <= 2

    def test_token_config_loading(self, tmp_path, valid_tokens):
        """Test loading tokens from configuration file."""
        # Create temporary config file
        config_file = tmp_path / "tokens.json"
        import json
        with open(config_file, 'w') as f:
            json.dump(valid_tokens, f)

        # Test loading from config
        from poe_search.utils.common import safe_json_load
        loaded_tokens = safe_json_load(config_file)

        assert loaded_tokens['p-b'] == valid_tokens['p-b']
        assert loaded_tokens['p-lat'] == valid_tokens['p-lat']

    @patch('poe_search.api.clients.browser_client.webdriver.Chrome')
    def test_authentication_retry_logic(self, mock_chrome, valid_tokens, mock_driver):
        """Test authentication retry logic."""
        mock_chrome.return_value = mock_driver

        # Mock intermittent failure then success
        mock_driver.find_elements.side_effect = [
            [],  # First attempt fails
            [],  # Second attempt fails
            [Mock()],  # Third attempt succeeds
        ]

        client = PoeApiClient(token=valid_tokens['p-b'], headless=True, max_retries=3)

        with client:
            result = client.authenticate()
            assert result is True
            assert mock_driver.find_elements.call_count == 3

    @patch('poe_search.api.clients.browser_client.webdriver.Chrome')
    def test_browser_options_configuration(self, mock_chrome, valid_tokens):
        """Test browser options are configured correctly."""
        client = PoeApiClient(token=valid_tokens['p-b'], headless=True)

        with client:
            # Verify Chrome was called with correct options
            mock_chrome.assert_called_once()
            call_args = mock_chrome.call_args

            # Should have options configured
            assert 'options' in call_args.kwargs or len(call_args.args) > 0


class TestTokenValidation:
    """Test token validation and security measures."""

    def test_token_format_validation(self):
        """Test various token format validations."""
        # Valid base64-like tokens should work
        valid_tokens = [
            'AG58MLIXFnbOh98QAv4YHA==',
            '87OepyV2QcF9TkiuqhaFyWZgROH+Vp00g0QZLwZEMg=='
        ]

        for token in valid_tokens:
            client = PoeApiClient(token=token)
            assert client.token == token

    def test_invalid_token_formats(self):
        """Test rejection of invalid token formats."""
        invalid_tokens = [
            '',  # Empty
            '   ',  # Whitespace only
            'short',  # Too short
            'invalid characters!@#$%',  # Invalid characters
        ]

        for token in invalid_tokens:
            with pytest.raises((ValueError, AuthenticationError)):
                PoeApiClient(token=token)

    def test_token_sanitization(self):
        """Test that tokens are properly sanitized."""
        token_with_whitespace = '  AG58MLIXFnbOh98QAv4YHA==  '
        client = PoeApiClient(token=token_with_whitespace)

        # Token should be stripped of whitespace
        assert client.token == token_with_whitespace.strip()

    def test_sensitive_data_handling(self):
        """Test that sensitive data is properly handled."""
        token = 'AG58MLIXFnbOh98QAv4YHA=='
        client = PoeApiClient(token=token)

        # Sensitive data should not appear in logs or string representations
        import logging
        with patch('logging.Logger.info') as mock_log:
            client._log_auth_attempt()

            # Check that actual token doesn't appear in log calls
            for call in mock_log.call_args_list:
                for arg in call[0]:
                    assert token not in str(arg)


@pytest.mark.integration
class TestAuthenticationIntegration:
    """Integration tests for authentication (require real network access)."""

    @pytest.mark.skip(reason="Requires real tokens and network access")
    def test_real_authentication_flow(self):
        """Test authentication with real Poe.com (manual test only)."""
        # This would test actual authentication but requires real tokens
        # Only run manually when needed for debugging
        pass

    @pytest.mark.skip(reason="Requires real tokens and network access")
    def test_rate_limiting_compliance(self):
        """Test that authentication respects rate limits."""
        # This would test rate limiting behavior with real requests
        pass
