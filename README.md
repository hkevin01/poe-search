# Poe Search

A comprehensive tool for searching, organizing, and managing your Poe.com conversations and data.

## Features

- 🔍 **Search Conversations**: Search through your Poe.com conversation history
- 📊 **Data Organization**: Organize and categorize your chats and responses
- 💾 **Local Storage**: Store conversations locally for offline access
- 🔄 **Export/Import**: Export conversations to various formats (JSON, CSV, Markdown)
- 🤖 **Bot Management**: Track and organize conversations with different AI models
- 📈 **Analytics**: Generate insights about your usage patterns
- 🔐 **Privacy First**: All data processing happens locally

## Installation

### From Source

```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
pip install -e .
```

### For Development

```bash
git clone https://github.com/kevin/poe-search.git
cd poe-search
pip install -e ".[dev]"
```

## Quick Start

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

## Configuration

Create a `.env` file in your project root:

```env
POE_TOKEN=your_poe_token_here
DATABASE_URL=sqlite:///poe_search.db
LOG_LEVEL=INFO
```

## Getting Your Poe Token

1. Log into [Poe](https://poe.com) in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage > Cookies > poe.com
4. Copy the value of the `p-b` cookie

## Usage

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

## Project Structure

```
poe-search/
├── src/poe_search/           # Main package
│   ├── __init__.py
│   ├── __about__.py
│   ├── cli/                  # Command line interface
│   ├── api/                  # Poe API client
│   ├── storage/              # Data storage and database
│   ├── search/               # Search functionality
│   ├── export/               # Export utilities
│   └── utils/                # Common utilities
├── tests/                    # Test suite
├── docs/                     # Documentation
├── scripts/                  # Shell scripts
├── .github/                  # GitHub workflows
└── .copilot/                 # GitHub Copilot configuration
```

## Features in Detail

### Search Capabilities
- Full-text search across all conversations
- Filter by bot type, date range, conversation length
- Search within specific conversations
- Regex pattern matching
- Fuzzy search for typos

### Data Organization
- Automatic conversation categorization
- Tag and label system
- Conversation threading
- Bot usage analytics
- Export to multiple formats

### Privacy & Security
- Local data storage
- Optional encryption
- Token management
- Rate limiting
- Respect for Poe's terms of service

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/kevin/poe-search.git
cd poe-search

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
black .
ruff check .
mypy src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for personal use and educational purposes. Please respect Poe's terms of service and rate limits. The authors are not responsible for any misuse of this tool.

## Acknowledgments

- Inspired by the [poe-api](https://github.com/ading2210/poe-api) project
- Built with modern Python tools and best practices
- Community contributions and feedback

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/kevin/poe-search/issues)
- 💬 [Discussions](https://github.com/kevin/poe-search/discussions)
- 📧 Email: your-email@example.com
