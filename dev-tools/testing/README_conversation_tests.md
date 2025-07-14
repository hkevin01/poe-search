# Poe Conversation Retrieval Tests

This directory contains comprehensive tests for verifying Poe conversation retrieval and database functionality.

## Test Files

### 1. Core Database Tests
- **`tests/storage/test_conversation_retrieval.py`** - pytest-compatible tests for database operations
- **`tests/api/test_conversation_sync.py`** - API integration and sync tests

### 2. Quick Test Scripts
- **`quick_conversation_test.py`** - Fast verification of basic conversation retrieval
- **`test_conversation_comprehensive.py`** - Full test suite with performance and integrity checks
- **`test_conversation_integration.sh`** - Integration test that verifies the entire workflow

## Running the Tests

### Quick Test (Recommended)
```bash
# From project root
python dev-tools/testing/quick_conversation_test.py
```

### Comprehensive Test Suite
```bash
# From project root
python dev-tools/testing/test_conversation_comprehensive.py
```

### Integration Test (Tests run.sh compatibility)
```bash
# From project root
./dev-tools/testing/test_conversation_integration.sh
```

### Pytest Tests
```bash
# From project root
python -m pytest tests/storage/test_conversation_retrieval.py -v
python -m pytest tests/api/test_conversation_sync.py -v
```

## What These Tests Verify

### Database Operations
- ✅ Conversation listing from database
- ✅ Full conversation retrieval by ID
- ✅ Message text extraction
- ✅ Data integrity (required fields, message counts)
- ✅ Database performance
- ✅ Error handling for invalid IDs

### API Integration  
- ✅ Client initialization
- ✅ Conversation sync workflow
- ✅ Mocked API responses
- ✅ Export format validation

### Edge Cases
- ✅ Empty conversations
- ✅ Missing fields
- ✅ Invalid conversation IDs
- ✅ Large conversation handling
- ✅ Search functionality

### Performance
- ✅ Conversation listing speed
- ✅ Individual retrieval speed
- ✅ Large dataset handling

## Prerequisites

1. **Database**: Ensure `data/poe_search.db` exists and contains real Poe conversations
2. **Virtual Environment**: `.venv` or `venv` directory with dependencies installed
3. **Source Code**: All source code in `src/` directory

## Expected Results

When all tests pass, you should see:
- Total conversation count
- Successful message retrieval
- Text content verification
- Performance metrics
- Data integrity confirmation

## Troubleshooting

### "No conversations found"
- Check that `data/poe_search.db` exists
- Verify the database contains real conversation data
- Run the import script to populate with real data

### Import errors
- Ensure virtual environment is activated
- Check that `src/` directory contains the poe_search package
- Verify all dependencies are installed

### Performance issues
- Large databases (>1000 conversations) may take longer
- Consider using `limit` parameter for faster testing
- Check available system memory

## Integration with run.sh

The `test_conversation_integration.sh` script specifically tests that:
- The `run.sh` script can find all required modules
- Database access works through the GUI components
- Virtual environment activation succeeds
- Python path is set correctly

This ensures that conversation retrieval will work when the GUI is started via `./run.sh`.
