# Performance Guide

## Performance Benchmarks

### Conversation Sync
- Small dataset (< 100 conversations): 1-2 minutes
- Medium dataset (100-500 conversations): 3-8 minutes
- Large dataset (500+ conversations): 10+ minutes

### Search Performance
- Text search: < 100ms for 1000 conversations
- Regex search: < 500ms for 1000 conversations
- Category filtering: < 50ms

## Optimization Guidelines

### Memory Usage
- Application uses ~50-100MB base memory
- Each conversation adds ~1-5KB memory
- Large datasets may require 200-500MB

### Disk Usage
- Conversations stored as JSON (~1-10KB per conversation)
- Logs rotate automatically (max 10MB)
- Temporary files cleaned on startup

### Network Usage
- Respects Poe.com rate limits (1-2 requests/second)
- Uses browser automation to avoid API limits
- Minimizes network requests through caching

## Performance Monitoring

### Built-in Metrics
- Sync progress and timing
- Search response times
- Memory usage indicators

### Profiling
```bash
# Profile application startup
python -m cProfile gui_launcher.py

# Monitor memory usage
python -m memory_profiler gui_launcher.py
```

## Optimization Tips

1. **Sync in smaller batches** for better responsiveness
2. **Use category filters** to reduce search scope
3. **Regular cleanup** of old logs and temporary files
4. **Close unused conversations** to free memory
5. **Restart application** periodically for long sessions
