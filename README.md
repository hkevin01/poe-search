# Poe Search 🔍

> **A comprehensive tool for searching, organizing, and managing your Poe.com conversations with modern GUI and CLI interfaces**

[![CI](https://github.com/kevin/poe-search/workflows/CI/badge.svg)](https://github.com/kevin/poe-search/actions)
[![Security](https://github.com/kevin/poe-search/workflows/Security%20Scan/badge.svg)](https://github.com/kevin/poe-search/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-blue.svg)](https://sqlite.org/)

---

## 🎯 Overview

Poe Search transforms your Poe.com conversation history into a searchable, organized knowledge base. With both command-line and modern graphical interfaces, it provides powerful tools for managing AI conversations, extracting insights, and maintaining your digital knowledge repository.

## ✨ Key Features

### 🔍 **Intelligent Search**
- **Full-text search** across all conversation history
- **Advanced filtering** by bot, category, date range, and regex patterns
- **SQLite FTS5** for lightning-fast local searches
- **Context preservation** with conversation threading

### 🖥️ **Modern Interface**
- **PyQt6 GUI** with Windows 11-inspired design
- **Dark theme** optimized for long reading sessions
- **System tray integration** for background operation
- **Responsive design** that adapts to any screen size

### 🏷️ **Smart Organization**
- **Auto-categorization** by topic (Technical, Medical, Creative, etc.)
- **Bot management** across different AI models (GPT-4, Claude, Gemini)
- **Conversation tagging** and custom metadata
- **Export/Import** in JSON, CSV, and Markdown formats

### 📊 **Analytics & Insights**
- **Usage patterns** and conversation trends
- **Bot comparison** and preference analysis
- **Token cost tracking** and budget monitoring
- **Visual dashboards** with interactive charts

### 🛡️ **Privacy & Performance**
- **Local-first** - all processing happens on your machine
- **Rate limiting** with intelligent backoff strategies
- **Background workers** for non-blocking operations
- **Configurable settings** for optimal performance

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [🛠️ Installation](#️-installation)
- [🎨 GUI Features](#-gui-features)
- [💻 Usage Examples](#-usage-examples)
- [⚙️ Configuration](#️-configuration)
- [📁 Project Structure](#-project-structure)
- [🧪 Development](#-development)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [🔒 Security](#-security)
- [📄 License](#-license)

## � Quick Start

### 1️⃣ **Get Your Poe Token**
```bash
# Visit poe.com → Developer Tools (F12) → Application → Cookies → poe.com
# Copy the 'p-b' cookie value
```

### 2️⃣ **Install & Run**
```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
pip install -e ".[gui]"      # Install with GUI support
poe-search-gui               # Launch the application
```

### 3️⃣ **Start Exploring**
- **Configure** your Poe token in the settings
- **Search** through your conversation history
- **Categorize** conversations automatically
- **Export** your data in multiple formats

---

## 🛠️ Installation Options

### 🎯 **Quick Install (Recommended)**
```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
pip install -e ".[gui]"      # Includes GUI and all dependencies
```

### 🔧 **Development Setup**
```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
pip install -e ".[dev,gui]"  # Includes development tools
pre-commit install           # Set up git hooks
```

### ⚙️ **Using Make (Advanced)**
   ```bash
make setup                   # Complete development environment
make install                 # Standard installation
make gui                     # Launch GUI directly
```

### 📦 **Package Options**
- **Base**: `pip install -e .` (CLI only)
- **GUI**: `pip install -e ".[gui]"` (Includes PyQt6)
- **Development**: `pip install -e ".[dev]"` (Testing & linting)
- **Complete**: `pip install -e ".[dev,gui]"` (Everything)

### 🧪 **Prerequisites**
- Python 3.8+ 
- Git
- Virtual environment (recommended)

## 🎨 GUI Features

<div align="center">

| **Feature** | **Description** |
|-------------|-----------------|
| 🔍 **Search Tab** | Advanced search with filters, regex support, and real-time results |
| 💬 **Conversation View** | Clean, readable conversation display with message threading |
| 🏷️ **Category Manager** | Auto-categorization with custom rules and manual tagging |
| 📊 **Analytics Dashboard** | Visual insights, usage trends, and bot comparison charts |
| ⚙️ **Settings Panel** | Token management, sync preferences, and UI customization |
| 🌙 **Dark Theme** | Modern Windows 11-inspired design optimized for readability |
| 📱 **Responsive Layout** | Adaptive interface that scales to any screen size |
| 🔔 **System Tray** | Background operation with minimal system impact |

</div>

### **Launch Options**
```bash
poe-search-gui               # Primary launcher
make gui                     # Via make system
python -m poe_search.gui     # Direct module execution
./run.sh                     # Shell script launcher
```

---

## 💻 Usage Examples

### 🖥️ **Command Line Interface**

```bash
# Configure authentication
poe-search config set-token YOUR_POE_TOKEN

# Search conversations
poe-search search "machine learning" --bot claude --limit 10

# Advanced search with filters
poe-search search "python" --category technical --days 30 --regex

# Export conversations
poe-search export --format json --output ml_conversations.json
poe-search export --conversation-id 12345 --format markdown

# Sync recent conversations
poe-search sync --days 7 --verbose

# Analytics and insights
poe-search analytics --period month --bot all
poe-search bots list --usage-stats
```

### 🐍 **Python API**

```python
from poe_search import PoeSearchClient, SearchFilters

# Initialize client
client = PoeSearchClient(token="your_token")

# Simple search
results = client.search("machine learning", limit=10)

# Advanced search with filters
filters = SearchFilters(
    bot="claude",
    category="technical", 
    date_range="last_week",
    include_system_messages=False
)
results = client.search("python programming", filters=filters)

# Get conversation details
conversation = client.get_conversation("conv_12345")
messages = conversation.messages

# Export and analytics
client.export_conversations("output.json", format="json")
stats = client.get_usage_analytics(period="month")
```

### 🎯 **Common Workflows**

```bash
# Daily routine: sync and search
poe-search sync --days 1
poe-search search "today's work" --days 1

# Project research: export specific topics
poe-search search "AI ethics" --export research_notes.md

# Bot comparison: analyze different models
poe-search analytics --bot claude,gpt4,gemini --compare

# Backup: export all conversations
poe-search export --all --format json --output backup_$(date +%Y%m%d).json
```

---

## ⚙️ Configuration

### � **Getting Your Poe Token**
1. Visit [poe.com](https://poe.com) and log in
2. Open Developer Tools (`F12`)
3. Navigate to **Application** → **Cookies** → **poe.com**
4. Copy the value of the `p-b` cookie

### 📄 **Environment Configuration**
Create a `.env` file in your project root:
```env
POE_TOKEN=your_poe_token_here
DATABASE_URL=sqlite:///data/poe_search.db
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS_PER_MINUTE=30
MAX_RETRIES=3
```

### ⚙️ **Advanced Settings**
Configuration files in `config/`:
- `config.yaml` - Main application settings
- `rate_limits.yaml` - API rate limiting configuration  
- `categories.yaml` - Auto-categorization rules
- `export_templates/` - Custom export formats

### 🔧 **Runtime Configuration**
```bash
# Set token via CLI
poe-search config set-token YOUR_TOKEN

# Configure rate limiting
poe-search config set rate-limit 30

# Set default export format
poe-search config set export-format markdown
```

---

## �📁 Project Structure

<div align="center">

| **Directory** | **Purpose** | **Contents** |
|---------------|-------------|--------------|
| `src/poe_search/` | 🏗️ Core application | GUI, CLI, API, database modules |
| `scripts/` | 🔧 Automation | Build, test, deployment scripts |
| `config/` | ⚙️ Configuration | YAML configs, templates, tokens |
| `dev-tools/` | 🧪 Development | Testing, debugging, utilities |
| `data/` | 💾 Runtime data | SQLite databases, backups |
| `logs/` | 📊 Logging | Application and error logs |
| `docs/` | 📚 Documentation | User guides, API docs, tutorials |
| `tests/` | 🧪 Testing | Unit, integration, API tests |

</div>

```
poe-search/                   # 🏠 Project root
├── src/poe_search/           # 🎯 Main application source
│   ├── gui/                  # 🖥️ PyQt6 GUI components
│   ├── cli/                  # 💻 Command-line interface
│   ├── api/                  # 🌐 Poe.com API client
│   ├── database/             # 🗄️ SQLite database management
│   └── utils/                # 🔧 Utilities and helpers
├── scripts/                  # 🚀 Automation scripts
│   ├── build.sh             # 📦 Build automation
│   ├── run_tests.sh          # 🧪 Test runner
│   └── deploy.sh             # 🚀 Deployment script
├── config/                   # ⚙️ Configuration files
│   ├── config.yaml           # 🔧 Main settings
│   ├── categories.yaml       # 🏷️ Auto-categorization rules
│   └── export_templates/     # 📄 Export format templates
├── dev-tools/                # 🛠️ Development utilities
│   ├── testing/              # 🧪 Test scripts and validation
│   ├── debug/                # 🐛 Debugging tools and demos  
│   └── utilities/            # 🔧 Development helpers
├── data/                     # 💾 Runtime data (gitignored)
│   ├── *.db                  # 🗄️ SQLite databases
│   └── *.json                # 💾 Backup files
├── logs/                     # 📊 Application logs (gitignored)
├── docs/                     # 📚 Documentation
│   ├── user-guide/           # 👤 User documentation
│   ├── api/                  # 🔗 API reference
│   └── development/          # 👨‍💻 Developer guides
└── tests/                    # 🧪 Unit and integration tests
    ├── unit/                 # 🔬 Unit tests
    ├── integration/          # 🔗 Integration tests
    └── api/                  # 🌐 API tests
```

### 🎯 **Clean Organization Benefits**
- ✅ **Root directory** kept minimal and professional
- ✅ **Development tools** organized in `dev-tools/`
- ✅ **Runtime data** isolated in `data/` directory
- ✅ **Configuration** centralized in `config/`
- ✅ **Documentation** structured in `docs/`
- ✅ **Logs** collected in dedicated `logs/` directory

---

## 🧪 Development

### 🚀 **Quick Setup**
```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
make setup                   # Complete development environment
```

### 🔧 **Available Commands**
```bash
make install                 # Install package in development mode
make test                    # Run all tests with coverage
make lint                    # Run code linting and formatting
make docs                    # Build documentation
make clean                   # Clean build artifacts
make gui                     # Launch GUI for testing
```

### 🧪 **Testing**
```bash
# Run all tests
pytest tests/ -v --cov=src/poe_search

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/api/            # API tests only

# Run tests with different markers
pytest -m "not slow"         # Skip slow tests
pytest -m "gui"              # GUI tests only
```

### 📊 **Code Quality**
```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/poe_search/

# Security scanning
bandit -r src/

# Pre-commit hooks
pre-commit run --all-files
```

### 🔄 **Development Workflow**
1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Make changes** with tests and documentation
3. **Run quality checks**: `make lint test`
4. **Commit changes**: Git hooks will run automatically
5. **Submit pull request** with clear description

---

## 📚 Documentation

### 📖 **Available Documentation**

| **Document** | **Purpose** | **Location** |
|--------------|-------------|--------------|
| 👤 **User Guide** | Getting started and basic usage | [`docs/user-guide/`](docs/user-guide/) |
| 🔗 **API Reference** | Complete API documentation | [`docs/api/`](docs/api/) |
| 👨‍💻 **Development Guide** | Contributing and development setup | [`docs/development/`](docs/development/) |
| 🏗️ **Architecture** | System design and structure | [`docs/architecture.md`](docs/architecture.md) |
| ❓ **FAQ** | Frequently asked questions | [`docs/faq.md`](docs/faq.md) |
| 🚀 **Examples** | Code samples and tutorials | [`docs/examples/`](docs/examples/) |

### 🔗 **Quick Links**
- [**Installation Guide**](docs/user-guide/installation.md)
- [**Configuration Reference**](docs/user-guide/configuration.md)
- [**CLI Commands**](docs/user-guide/cli-reference.md)
- [**GUI Tutorial**](docs/user-guide/gui-tutorial.md)
- [**API Examples**](docs/examples/api-usage.md)
- [**Troubleshooting**](docs/user-guide/troubleshooting.md)

### 📝 **Building Documentation**
```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
make docs

# Serve documentation locally
mkdocs serve
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### 🎯 **Quick Contribution Steps**
1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/poe-search.git`
3. **Setup** development environment: `make setup`
4. **Create** feature branch: `git checkout -b feature/amazing-feature`
5. **Make** your changes with tests and documentation
6. **Test** your changes: `make test lint`
7. **Commit** your changes: `git commit -m 'Add amazing feature'`
8. **Push** to your branch: `git push origin feature/amazing-feature`
9. **Submit** a Pull Request

### 💡 **Contribution Ideas**
- 🐛 **Bug fixes** and error handling improvements
- ✨ **New features** for search and categorization
- 📱 **UI/UX improvements** for the GUI
- 📚 **Documentation** enhancements and examples
- 🧪 **Test coverage** improvements
- 🌐 **Internationalization** support
- 🚀 **Performance optimizations**

### 📋 **Code Standards**
- Follow **PEP 8** style guidelines
- Write **comprehensive tests** for new features
- Include **docstrings** for all public functions
- Update **documentation** for user-facing changes
- Use **type hints** for better code clarity

---

## 🔒 Security

### 🛡️ **Security Measures**
- **Local data processing** - no data sent to external servers
- **Token encryption** at rest using system keyring
- **Rate limiting** to prevent API abuse
- **Input validation** and sanitization
- **Secure database** with parameterized queries

### 🚨 **Reporting Security Issues**
If you discover a security vulnerability, please send an email to **security@poe-search.dev** instead of using the public issue tracker.

### 🔐 **Best Practices**
- Store tokens securely using the built-in configuration system
- Keep your Poe token private and never commit it to version control
- Regularly update the application to get security fixes
- Use virtual environments to isolate dependencies

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### 🎉 **Acknowledgments**
- Built with ❤️ using **PyQt6** for the modern GUI
- Powered by **SQLite** with **FTS5** for fast search
- Inspired by the need for better **AI conversation management**
- Thanks to the **open source community** for excellent tools and libraries

---

<div align="center">

**⭐ Star this project if you find it useful!**

[🐛 Report Bug](https://github.com/kevin/poe-search/issues) • [✨ Request Feature](https://github.com/kevin/poe-search/issues) • [💬 Discussions](https://github.com/kevin/poe-search/discussions)

Made with ❤️ by the Poe Search community

</div>