# Contributing to Poe Search

Thank you for your interest in contributing to Poe Search! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/poe-search.git
   cd poe-search
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements/dev.txt
   pip install -e .
   ```

4. **Verify Installation**
   ```bash
   pytest --version
   python -c "import poe_search; print('✅ Installation successful')"
   ```

## 🛠️ Development Workflow

### Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages
Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

feat(gui): add conversation search functionality
fix(api): handle authentication timeout errors
docs(readme): update installation instructions
test(core): add unit tests for conversation models
```

### Pull Request Process

1. **Before Starting**
   - Check existing issues and PRs
   - Create an issue for major changes
   - Discuss the approach in the issue

2. **Development**
   - Write tests for new functionality
   - Follow code style guidelines
   - Update documentation as needed
   - Test your changes thoroughly

3. **Submission**
   - Create a clear PR description
   - Reference related issues
   - Add screenshots for UI changes
   - Ensure all checks pass

## 📋 Code Standards

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Maximum line length: 200 characters (configured)
- Use type hints for all functions

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Sort imports
isort src/ tests/
```

### Testing Requirements
- Maintain 80%+ test coverage
- Write unit tests for all new functions
- Add integration tests for major features
- Use descriptive test names

```python
def test_conversation_extraction_with_valid_tokens():
    """Test that conversation extraction works with valid authentication."""
    pass
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/                    # Unit tests
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_services.py
├── integration/             # Integration tests
│   ├── test_browser_client.py
│   └── test_export_service.py
├── gui/                     # GUI tests
│   └── test_main_window.py
└── fixtures/                # Test data
    └── sample_conversations.json
```

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_models.py

# With coverage
pytest --cov=src/poe_search --cov-report=html

# GUI tests (requires display)
pytest tests/gui/ --gui

# Skip slow tests
pytest -m "not slow"
```

### Test Data
- Use fixtures for common test data
- Mock external services (Poe.com API)
- Create realistic but anonymized test conversations

## 📝 Documentation

### Required Documentation
- **Docstrings**: All public functions and classes
- **Type Hints**: All function parameters and returns
- **README Updates**: For new features
- **CHANGELOG**: For all changes

### Docstring Format
```python
def extract_conversations(limit: int, progress_callback: Optional[Callable] = None) -> List[Conversation]:
    """
    Extract conversations from Poe.com.

    Args:
        limit: Maximum number of conversations to extract
        progress_callback: Optional callback for progress updates

    Returns:
        List of extracted conversations

    Raises:
        AuthenticationError: If authentication fails
        ExtractionError: If extraction fails

    Example:
        >>> client = PoeApiClient(token="your_token")
        >>> conversations = client.extract_conversations(limit=10)
        >>> print(f"Found {len(conversations)} conversations")
    """
```

## 🐛 Bug Reports

### Before Reporting
- Search existing issues
- Try to reproduce the bug
- Test with latest version
- Check browser compatibility

### Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to...
2. Click on...
3. See error

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.11.0]
- Browser: [e.g., Chrome 120.0]
- Poe Search Version: [e.g., 1.3.0]

**Additional Context**
Screenshots, logs, etc.
```

## 💡 Feature Requests

### Guidelines
- Check existing feature requests
- Explain the use case clearly
- Consider implementation complexity
- Be open to alternative solutions

### Request Template
```markdown
**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should this work?

**Alternatives Considered**
What other approaches did you consider?

**Implementation Notes**
Technical considerations or constraints.
```

## 🏗️ Architecture Guidelines

### Code Organization
- Keep modules focused and cohesive
- Use dependency injection where appropriate
- Separate business logic from UI code
- Follow SOLID principles

### Error Handling
- Use custom exceptions from `core.exceptions`
- Provide helpful error messages
- Log errors with appropriate levels
- Graceful degradation when possible

### Performance Considerations
- Minimize API calls to Poe.com
- Use caching where appropriate
- Implement proper rate limiting
- Profile code for bottlenecks

## 🎯 Areas for Contribution

### High Priority
- [ ] Improve conversation extraction reliability
- [ ] Add more export formats (PDF, HTML)
- [ ] Enhance search functionality
- [ ] Better error handling and recovery

### Medium Priority
- [ ] Plugin system for custom extractors
- [ ] Conversation analytics and insights
- [ ] Performance optimizations
- [ ] Additional authentication methods

### Low Priority
- [ ] Web interface
- [ ] Mobile app
- [ ] Cloud sync
- [ ] Machine learning features

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Discord**: Real-time chat (coming soon)

### Code Reviews
- Be constructive and respectful
- Focus on code quality and maintainability
- Suggest improvements, don't just point out problems
- Ask questions if something is unclear

## 📜 License

By contributing to Poe Search, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Poe Search! 🎉
