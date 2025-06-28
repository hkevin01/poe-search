# Poe Search

A comprehensive tool for searching, organizing, and managing your Poe.com conversations and data with both CLI and modern GUI interfaces.

[![CI](https://github.com/kevin/poe-search/workflows/CI/badge.svg)](https://github.com/kevin/poe-search/actions)
[![Security](https://github.com/kevin/poe-search/workflows/Security%20Scan/badge.svg)](https://github.com/kevin/poe-search/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Features

- 🔍 **Search Conversations**: Search through your Poe.com conversation history with full-text search
- 🖥️ **Modern GUI**: Windows 11-style interface built with PyQt6 for intuitive conversation management
- 🏷️ **Smart Categories**: Auto-categorize conversations by topic (Technical, Medical, Spiritual, Political, etc.)
- 📊 **Analytics Dashboard**: Visual insights about your usage patterns and conversation trends
- 💾 **Local Storage**: SQLite database with FTS5 for fast, offline conversation access
- 🔄 **Export/Import**: Export conversations to JSON, CSV, or Markdown formats
- 🤖 **Bot Management**: Track conversations across different AI models (GPT-4, Claude, etc.)
- 🔐 **Privacy First**: All data processing happens locally on your machine
- ⚡ **Performance**: Optimized search and categorization with background workers

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Development](#development)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Standard Installation

```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
pip install -e .
```

### With GUI Support

```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
pip install -e ".[gui]"
```

### For Development

```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
pip install -e ".[dev,gui]"
```

### Using Make (Recommended for Development)

```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
make setup  # Sets up complete development environment
```

## 🚀 Quick Start

### Command Line Interface

1. **Set up your Poe token**:
   ```bash
   poe-search config set-token YOUR_POE_TOKEN
   ```

2. **Search your conversations**:
   ```bash
   poe-search search "machine learning"
   ```

3. **Export conversations**:
   ```bash
   poe-search export --format json --output conversations.json
   ```

### Graphical User Interface

1. **Launch the GUI**:
   ```bash
   # Using the installed script
   poe-search-gui
   
   # Or using make
   make gui
   
   # Or using the automation script
   python scripts/automation.py gui
   
   # Or directly
   python -m poe_search.gui
   ```

2. **Set up your token** in the GUI settings dialog

3. **Search, categorize, and manage** your conversations through the intuitive interface

## 🎨 GUI Features

The modern PyQt6-based GUI provides:

- **🔍 Search Tab**: Advanced search with filters for bot, category, date range, and regex support
- **💬 Conversation Tab**: View conversation details and messages in a readable format
- **🏷️ Categories Tab**: Manage conversation categories with auto-categorization rules
- **📊 Analytics Tab**: Visual dashboard with usage statistics and trends
- **🎨 Windows 11 Styling**: Modern dark theme following Windows 11 design principles
- **⚡ Background Processing**: Non-blocking search and sync operations
- **📱 Responsive Design**: Resizable interface that adapts to your screen

## ⚙️ Configuration

Create a `.env` file in your project root:

```env
POE_TOKEN=your_poe_token_here
DATABASE_URL=sqlite:///poe_search.db
LOG_LEVEL=INFO
```

## 🔑 Getting Your Poe Token

1. Log into [Poe](https://poe.com) in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage > Cookies > poe.com
4. Copy the value of the `p-b` cookie

## 📖 Usage

### Command Line Interface

```bash
# Search conversations
poe-search search "python programming" --bot claude --limit 10

# List all bots you've chatted with
poe-search bots list

# Export specific conversations
poe-search export --conversation-id 12345 --format markdown

# Sync latest conversations
poe-search sync --days 7

# Generate analytics
poe-search analytics --period month
```

### Python API

```python
from poe_search import PoeSearchClient

# Initialize client
client = PoeSearchClient(token="your_token")

# Search conversations
results = client.search("machine learning", limit=10)

# Get conversation history
conversations = client.get_conversations(bot="claude", days=30)

# Export data
client.export_conversations("output.json", format="json")
```

### Using Make Commands

```bash
# Run tests
make test

# Format code
make format

# Run linting
make lint

# Build package
make build

# Run GUI
make gui

# Run CLI with arguments
make cli ARGS='search "test"'

# Check dependencies
make deps-check

# Update dependencies
make deps-update
```

## 🏗️ Development

### Project Structure

```
poe-search/
├── src/poe_search/           # Main package (src-layout)
│   ├── api/                  # Poe.com API client
│   ├── cli/                  # Command-line interface
│   ├── gui/                  # Graphical user interface
│   ├── storage/              # Database and storage
│   ├── search/               # Search functionality
│   ├── export/               # Export utilities
│   └── utils/                # Common utilities
├── tests/                    # Comprehensive test suite
├── docs/                     # Documentation
├── scripts/                  # Automation scripts
├── .github/                  # GitHub workflows and templates
├── .copilot/                 # GitHub Copilot configuration
├── pyproject.toml           # Modern Python packaging
├── Makefile                 # Development automation
├── README.md                # Project overview
├── CHANGELOG.md             # Change tracking
├── CONTRIBUTING.md          # Contribution guidelines
├── SECURITY.md              # Security policy
├── WORKFLOW.md              # Development workflow
├── PROJECT_GOALS.md         # Project vision
└── PROJECT_STATUS.md        # Modernization status
```

### Development Setup

1. **Clone and setup**:
   ```bash
   git clone https://github.com/kevin/poe-search.git
   cd poe-search
   make setup
   ```

2. **Run tests**:
   ```bash
   make test
   ```

3. **Format code**:
   ```bash
   make format
   ```

4. **Run linting**:
   ```bash
   make lint
   ```

### Development Tools

- **Python 3.8+**: Modern Python with type hints
- **Black**: Code formatting (120 character lines)
- **Ruff**: Fast Python linter
- **MyPy**: Static type checking
- **pytest**: Testing framework with coverage
- **Pre-commit**: Automated quality checks
- **EditorConfig**: Consistent editor settings

### Automation Scripts

The project includes comprehensive automation:

- **`make`**: Unix-style automation commands
- **`scripts/automation.py`**: Python automation script
- **GitHub Actions**: CI/CD pipelines
- **Pre-commit hooks**: Automated quality checks

## 📚 Documentation

### Project Documentation

- **[PROJECT_GOALS.md](PROJECT_GOALS.md)**: Project vision and roadmap
- **[WORKFLOW.md](WORKFLOW.md)**: Development workflow and processes
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines
- **[SECURITY.md](SECURITY.md)**: Security policy and vulnerability reporting
- **[CHANGELOG.md](CHANGELOG.md)**: Detailed change tracking
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)**: Modernization status report

### API Documentation

- **MkDocs Site**: [https://poe-search.dev](https://poe-search.dev)
- **Code Documentation**: Comprehensive docstrings and type hints
- **Examples**: Usage examples in documentation

### Building Documentation

```bash
# Build documentation
make docs

# Serve documentation locally
make docs-serve
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. **Fork and clone** the repository
2. **Set up development environment**:
   ```bash
   make setup
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and run tests:
   ```bash
   make test
   make lint
   ```
5. **Submit a pull request**

### Development Workflow

- **Branching**: GitHub Flow with feature branches
- **Commits**: Conventional commit format
- **Code Review**: Required for all changes
- **Testing**: Comprehensive test suite
- **Documentation**: Updated for all changes

## 🔒 Security

### Security Policy

We take security seriously. Please see our [Security Policy](SECURITY.md) for:

- Vulnerability reporting procedures
- Security best practices
- Security features and measures
- Security contacts

### Security Features

- **Local Storage**: All data stored locally on your machine
- **Token Security**: Secure token handling and validation
- **Input Validation**: Comprehensive input sanitization
- **Dependency Scanning**: Automated security scanning
- **Code Scanning**: GitHub CodeQL integration

### Reporting Security Issues

**Please DO NOT create a public GitHub issue for security vulnerabilities.**

Instead, please report security vulnerabilities via:
- Email: [security@poe-search.dev](mailto:security@poe-search.dev)
- GitHub Security Advisories (if you have access)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Poe.com**: For providing the platform and API
- **Python Community**: For excellent tools and libraries
- **Contributors**: For their valuable contributions
- **Open Source**: For making this project possible

## 📞 Support

- **Documentation**: [https://poe-search.dev](https://poe-search.dev)
- **Issues**: [GitHub Issues](https://github.com/kevin/poe-search/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kevin/poe-search/discussions)
- **Security**: [security@poe-search.dev](mailto:security@poe-search.dev)

## 🚀 Roadmap

See [PROJECT_GOALS.md](PROJECT_GOALS.md) for our detailed roadmap and future plans.

### Upcoming Features

- 🔌 **Plugin System**: Extensible plugin architecture
- ☁️ **Cloud Sync**: Optional cloud synchronization
- 📱 **Mobile Support**: Mobile applications
- 🤖 **AI Integration**: Enhanced AI-powered features
- 🏢 **Enterprise Features**: Enterprise-grade capabilities

---

**Made with ❤️ by the Poe Search community**
