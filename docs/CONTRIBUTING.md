# Contributing to Poe Search

Thank you for your interest in contributing to Poe Search! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows a Code of Conduct. By participating, you are expected to uphold this code. Please report any unacceptable behavior.

## Getting Started

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/poe-search.git
   cd poe-search
   ```

2. **Set up the development environment**:
   ```bash
   ./scripts/setup-dev.sh
   ```

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

4. **Run the tests**:
   ```bash
   pytest
   ```

### Project Structure

```
poe-search/
├── src/poe_search/           # Main package code
│   ├── cli/                  # Command line interface
│   ├── api/                  # Poe.com API client
│   ├── storage/              # Database and storage
│   ├── search/               # Search functionality
│   ├── export/               # Export utilities
│   └── utils/                # Common utilities
├── tests/                    # Test suite
├── docs/                     # Documentation
├── scripts/                  # Build and utility scripts
└── .github/                  # GitHub workflows
```

## Development Guidelines

### Code Style

- **Formatting**: Use Black with 120 character line length
- **Linting**: Follow Ruff rules (see `pyproject.toml`)
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Imports**: Use absolute imports, organize with isort

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use pytest fixtures for common test data
- Mock external dependencies (API calls, file system)
- Test both success and error cases

### Documentation

- Update documentation for new features
- Include docstrings for all public APIs
- Add examples for new CLI commands
- Update the changelog for notable changes

## Contribution Process

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS)
   - Error messages and stack traces

### Submitting Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the development guidelines

3. **Run the test suite**:
   ```bash
   pytest
   black .
   ruff check .
   mypy src/poe_search/
   ```

4. **Commit your changes**:
   ```bash
   git commit -m "Add feature: description of changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**:
   - Use the PR template
   - Link related issues
   - Describe the changes and motivation
   - Add screenshots for UI changes

### Pull Request Guidelines

- **One feature per PR**: Keep changes focused and atomic
- **Update tests**: Add or update tests for your changes
- **Update documentation**: Include relevant documentation updates
- **Check CI**: Ensure all automated checks pass
- **Respond to feedback**: Address review comments promptly

## Types of Contributions

### Bug Fixes
- Fix functionality that doesn't work as intended
- Improve error handling and user experience
- Add missing validations

### Features
- New CLI commands or options
- Additional export formats
- Enhanced search capabilities
- Performance improvements

### Documentation
- API documentation improvements
- Usage examples and tutorials
- Installation and setup guides
- FAQ and troubleshooting

### Infrastructure
- CI/CD improvements
- Development tooling
- Testing infrastructure
- Build and packaging

## Development Tips

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=poe_search

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Format code
black .

# Check linting
ruff check .

# Type checking
mypy src/poe_search/

# Run all checks
./scripts/build.sh
```

### Working with the Database

```bash
# Initialize a test database
python -c "from poe_search.storage.database import Database; Database('test.db')"

# Clean up test files
./scripts/clean.sh
```

## Release Process

1. **Update version** in `src/poe_search/__about__.py`
2. **Update CHANGELOG.md** with new version and changes
3. **Create a release PR** with version updates
4. **Tag the release** after merging:
   ```bash
   git tag v0.x.y
   git push origin v0.x.y
   ```
5. **GitHub Actions** will automatically build and publish

## Getting Help

- 💬 [GitHub Discussions](https://github.com/kevin/poe-search/discussions) for questions
- 🐛 [GitHub Issues](https://github.com/kevin/poe-search/issues) for bugs
- 📧 Email maintainers for security issues

## Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Added to the contributors section

Thank you for contributing to Poe Search! 🎉
