# GitHub Copilot Instructions

## Project Overview
This is `poe-search`, a Python package for searching and organizing Poe.com conversations. The project follows modern Python packaging standards with a src-layout structure.

## Code Style & Standards
- **Code Style**: Black formatting (line length: 120)
- **Linting**: Ruff with strict settings
- **Type Checking**: MyPy for static type analysis
- **Import Style**: Absolute imports preferred
- **Docstrings**: Google-style docstrings

## Architecture
- **CLI**: Click-based command line interface with Rich for output
- **API Client**: HTTPx-based client for Poe.com API interaction
- **Storage**: SQLite database with SQLAlchemy ORM
- **Search**: Full-text search using SQLite FTS5
- **Export**: Multiple format support (JSON, CSV, Markdown)

## Key Components
1. `poe_search.cli` - Command line interface
2. `poe_search.api` - Poe.com API client
3. `poe_search.storage` - Database and data models
4. `poe_search.search` - Search engine and algorithms
5. `poe_search.export` - Data export functionality
6. `poe_search.utils` - Common utilities and helpers

## Development Guidelines
- Use type hints for all function parameters and return values
- Include comprehensive docstrings for all public methods
- Follow the repository's testing patterns using pytest
- Use dependency injection where appropriate
- Implement proper error handling with logging

## Common Patterns
- Database operations should use context managers
- API calls should include rate limiting and retry logic
- CLI commands should use Rich for user-friendly output
- Configuration should support both files and environment variables

## Testing
- Unit tests for all core functionality
- Integration tests for CLI commands
- Mock external API calls in tests
- Use pytest fixtures for common test data

## Security Considerations
- Never log or expose authentication tokens
- Sanitize all user inputs
- Use parameterized queries for database operations
- Implement proper rate limiting for API calls
