# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive project restructuring and modernization
- New core module with data models and utilities
- Enhanced error handling with custom exceptions
- Export service with multiple format support (JSON, CSV, TXT, Markdown)
- Improved browser client with better conversation extraction
- Development tools and CI/CD configuration

### Changed
- Moved GUI launcher to proper module structure
- Enhanced documentation with contributing guidelines
- Improved code organization and modularity
- Updated dependencies and development requirements

### Fixed
- Browser client conversation extraction reliability
- Token authentication handling
- Category classification accuracy

## [1.3.0] - 2024-01-20

### Added
- Enhanced GUI with PyQt6
- Advanced conversation categorization system
- Multi-format export functionality (JSON, CSV, TXT)
- Real-time sync progress tracking
- Category and bot filtering
- Search functionality with text matching
- Token management interface
- Conversation message viewer with rich formatting

### Changed
- Migrated from basic CLI to full GUI application
- Improved browser automation with multiple fallback strategies
- Enhanced error handling and user feedback
- Better conversation extraction with duplicate detection

### Fixed
- Authentication issues with Poe.com
- Browser automation stability
- Memory usage optimization
- UI responsiveness during sync operations

## [1.2.0] - 2024-01-15

### Added
- Browser-based conversation extraction using Selenium
- Automatic ChromeDriver management
- Rate limiting to respect Poe.com servers
- Configuration file support for tokens
- Basic conversation categorization

### Changed
- Replaced direct API calls with browser automation
- Improved extraction reliability
- Better handling of dynamic content

### Fixed
- Token validation issues
- Conversation parsing errors
- Browser compatibility problems

## [1.1.0] - 2024-01-10

### Added
- Initial GUI prototype
- Basic conversation list display
- Simple export functionality
- Token configuration interface

### Changed
- Improved code organization
- Better error messages
- Enhanced logging

### Fixed
- Various bug fixes and stability improvements

## [1.0.0] - 2024-01-05

### Added
- Initial release
- Basic conversation extraction from Poe.com
- Command-line interface
- JSON export functionality
- Token-based authentication
- Simple conversation search

### Security
- Secure token storage
- Local data processing (no cloud storage)

---

## Release Notes

### Version 1.3.0 Highlights
This major release introduces a complete GUI overhaul with PyQt6, bringing Poe Search from a command-line tool to a full-featured desktop application. Key improvements include:

- **Modern Interface**: Clean, intuitive GUI with dark/light theme support
- **Smart Categories**: Automatic conversation classification into Technical, Creative, Educational, Business, and Science categories
- **Enhanced Export**: Multiple export formats with customizable options
- **Real-time Feedback**: Progress tracking for all operations
- **Better Search**: Advanced filtering and search capabilities

### Migration Guide
If upgrading from version 1.2.x or earlier:

1. **Configuration**: Token configuration has moved to `config/poe_tokens.json`
2. **Launch Method**: Use `python gui_launcher.py` instead of CLI commands
3. **Export Format**: JSON export format has been enhanced with metadata
4. **Dependencies**: New dependencies include PyQt6 - run `pip install -r requirements.txt`

### Known Issues
- Some Poe.com UI changes may affect extraction reliability
- Large conversation exports may take significant time
- Browser automation requires Chrome/Chromium installation

### Compatibility
- **Python**: 3.9+ required
- **Operating Systems**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **Browsers**: Chrome 100+, Chromium 100+
