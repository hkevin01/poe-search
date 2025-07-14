...existing code from /home/kevin/Projects/poe-search/CHANGELOG.md...# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup with src-layout structure
- Command line interface with Click and Rich
- SQLite database with full-text search
- Poe.com API client integration
- Export functionality (JSON, CSV, Markdown)
- Search engine with fuzzy search capabilities
- Configuration management
- Comprehensive test suite
- Documentation with MkDocs
- GitHub Actions CI/CD
- Pre-commit hooks for code quality

### Features
- **Search**: Full-text search across conversations with filters
- **Sync**: Download and sync conversations from Poe.com
- **Export**: Export conversations in multiple formats
- **Analytics**: Usage statistics and insights
- **Bot Management**: Track conversations with different AI models
- **CLI**: Rich terminal interface with progress bars
- **Database**: Local SQLite storage with FTS5 search
- **API**: Python API for programmatic access

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Basic project structure
- Core functionality implementation
- Documentation setup
- Testing framework

### Technical Details
- Python 3.8+ support
- Modern packaging with pyproject.toml
- Type hints throughout codebase
- Comprehensive error handling
- Logging integration
- Rate limiting for API calls

### Dependencies
- click: Command line interface
- rich: Terminal formatting
- httpx: HTTP client
- sqlalchemy: Database ORM
- pydantic: Data validation
- pytest: Testing framework
- black: Code formatting
- ruff: Linting

---

## Release Notes Template

When creating a new release, use this template:

### [X.Y.Z] - YYYY-MM-DD

#### Added
- New features

#### Changed
- Changes to existing functionality

#### Deprecated
- Features marked for removal

#### Removed
- Removed features

#### Fixed
- Bug fixes

#### Security
- Security improvements
