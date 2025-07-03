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
- 🛡️ **Rate Limiting**: Intelligent rate limiting with exponential backoff to handle Poe.com API limits gracefully
- 🎨 **Modern GUI**: Clean, intuitive interface built with PyQt6
- 🔧 **Configurable Settings**: Customize search, sync, and rate limiting preferences
- 🛡️ **Rate Limiting**: Intelligent rate limiting with user-configurable settings
- 💰 **Token Cost Detection**: Automatic detection and handling of Poe.com token cost prompts
- 🔔 **System Tray**: Minimize to system tray for background operation

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

## 📁 Project Structure

```
poe-search/
├── src/poe_search/           # Main application source code
│   ├── gui/                  # PyQt6 GUI components
│   ├── cli/                  # Command-line interface
│   ├── api/                  # Poe.com API client
│   ├── database/             # SQLite database management
│   └── utils/                # Utilities and helpers
├── scripts/                  # Automation and utility scripts
├── config/                   # Configuration files
│   └── poe_tokens.json      # Authentication tokens (gitignored)
├── dev-tools/               # Development utilities (organized)
│   ├── testing/             # Test scripts and validation
│   ├── debug/               # Debugging tools and demos  
│   └── utilities/           # Development helper scripts
├── data/                    # Runtime data (gitignored)
│   ├── *.db                 # SQLite databases
│   └── *.json               # Backup files
├── logs/                    # Application logs (gitignored)
├── docs/                    # Documentation
└── tests/                   # Unit and integration tests
```

### Clean Organization

The project has been organized to keep the root directory clean:
- **Development files** moved to `dev-tools/` with sub-categorization
- **Runtime data** isolated in `data/` directory
- **Log files** collected in `logs/` directory
- **Configuration** kept in dedicated `config/` directory