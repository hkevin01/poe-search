# Development Setup

## Prerequisites

- Python 3.9+
- Chrome/Chromium browser
- Git

## Setup Steps

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd poe-search
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Development Dependencies**
   ```bash
   pip install -r requirements/dev.txt
   pre-commit install
   ```

3. **Configure IDE**
   - Set Python interpreter to `venv/bin/python`
   - Configure paths for `src/` directory
   - Install recommended extensions

4. **Run Tests**
   ```bash
   pytest tests/
   ```

5. **Code Quality**
   ```bash
   black src/ tests/
   flake8 src/ tests/
   mypy src/poe_search
   ```

## Development Workflow

1. Create feature branch
2. Make changes
3. Run tests and linting
4. Commit with conventional commits
5. Push and create PR

## Testing

- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- GUI tests: `pytest tests/gui/`
- All tests: `pytest tests/`

## Debugging

Use the debug script for browser client issues:
```bash
python scripts/development/debug_browser.py
```
