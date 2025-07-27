# API Reference

## Core Classes

### PoeApiClient

Browser-based client for interacting with Poe.com.

```python
from poe_search.api.clients import PoeApiClient

client = PoeApiClient(token="your_token")
conversations = client.get_conversations(limit=50)
```

### ExportService

Service for exporting conversations in various formats.

```python
from poe_search.services import ExportService

service = ExportService()
service.export_conversations(conversations, output_path, options)
```

### SearchService

Service for searching through conversations.

```python
from poe_search.services import SearchService

search = SearchService()
results = search.search_conversations(conversations, "python")
```

## Data Models

### Conversation

Represents a conversation with metadata and messages.

### Message

Represents a single message within a conversation.

### SearchResult

Represents a search result with match information.
