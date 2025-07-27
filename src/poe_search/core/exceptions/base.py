"""
Custom exceptions for Poe Search application.
"""


class PoeSearchError(Exception):
    """Base exception for all Poe Search related errors."""

    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self):
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class AuthenticationError(PoeSearchError):
    """Raised when authentication with Poe.com fails."""
    pass


class ExtractionError(PoeSearchError):
    """Raised when conversation extraction fails."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when the authentication token has expired."""
    pass


class RateLimitError(PoeSearchError):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class ValidationError(PoeSearchError):
    """Raised when data validation fails."""
    pass


class ConfigurationError(PoeSearchError):
    """Raised when configuration is invalid or missing."""
    pass


class ExportError(PoeSearchError):
    """Raised when export operations fail."""
    pass


class ImportError(PoeSearchError):
    """Raised when import operations fail."""
    pass


class SearchError(PoeSearchError):
    """Raised when search operations fail."""
    pass


class BrowserError(PoeSearchError):
    """Raised when browser automation fails."""
    pass
