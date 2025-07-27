# Poe Search Project Structure
/
├── src/                           # Source code
│   └── poe_search/               # Main package
│       ├── __init__.py
│       ├── api/                  # API clients
│       │   ├── __init__.py
│       │   └── browser_client.py
│       ├── core/                 # Core functionality (NEW)
│       │   ├── __init__.py
│       │   ├── models.py         # Data models
│       │   ├── exceptions.py     # Custom exceptions
│       │   └── utils.py          # Utility functions
│       ├── gui/                  # GUI components (NEW)
│       │   ├── __init__.py
│       │   ├── main_window.py    # Main GUI
│       │   ├── dialogs.py        # Dialog windows
│       │   └── components.py     # Reusable components
│       └── services/             # Business logic (NEW)
│           ├── __init__.py
│           ├── search_service.py
│           └── export_service.py
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   ├── user_guide/               # User guides
│   └── development/              # Development docs
├── config/                       # Configuration
│   ├── default.json             # Default settings
│   └── poe_tokens.json          # User tokens
├── assets/                       # Static assets (NEW)
│   ├── icons/
│   ├── images/
│   └── styles/
├── scripts/                      # Utility scripts
├── logs/                         # Log files
├── .github/                      # GitHub workflows
│   └── workflows/
├── requirements/                 # Dependencies (NEW)
│   ├── base.txt
│   ├── dev.txt
│   └── test.txt
└── dist/                         # Build artifacts
