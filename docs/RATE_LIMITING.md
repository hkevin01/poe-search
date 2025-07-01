# Rate Limiting in Poe Search

This document describes the rate limiting system implemented in Poe Search to handle Poe.com's API restrictions and provide a smooth user experience.

## Overview

Poe.com has strict rate limiting on their API endpoints to prevent abuse and ensure fair usage. The Poe Search application implements a comprehensive rate limiting system that:

- **Respects Poe.com's limits** while maximizing data retrieval
- **Provides user control** over rate limiting behavior
- **Handles token cost prompts** when Poe.com requests payment
- **Offers configurable settings** for different usage patterns
- **Includes intelligent retry logic** with exponential backoff

## Features

### 1. Configurable Rate Limiting

Rate limiting can be enabled or disabled through the GUI settings:

- **Enable/Disable**: Toggle rate limiting on or off
- **Max Calls per Minute**: Configure the maximum API calls (1-20)
- **Retry Attempts**: Set retry attempts for failed calls (1-10)
- **Base Delay**: Configure base delay for exponential backoff (1-30 seconds)
- **Show Warnings**: Toggle rate limit warning messages
- **Prompt for Token Costs**: Enable/disable token cost prompt detection

### 2. Token Cost Prompt Detection

When Poe.com requests payment for additional tokens, the system:

- **Detects cost-related errors** in API responses
- **Logs detailed information** about the cost request
- **Provides user guidance** to visit Poe.com for token purchases
- **Continues operation** with available data

### 3. Intelligent Retry Logic

The system implements sophisticated retry mechanisms:

- **Exponential backoff**: Delays increase with each retry attempt
- **Jitter**: Random delays prevent thundering herd problems
- **Error classification**: Different handling for rate limits vs other errors
- **Configurable limits**: User-defined retry attempts and delays

## Configuration

### GUI Settings

Access rate limiting settings through the GUI:

1. Open the application
2. Go to **Settings** → **Advanced** tab
3. Find the **Rate Limiting** section
4. Configure your preferred settings

### Default Settings

```python
RateLimitSettings(
    enable_rate_limiting=True,      # Enable rate limiting
    max_calls_per_minute=8,         # Conservative limit
    retry_attempts=3,               # 3 retry attempts
    base_delay_seconds=5,           # 5 second base delay
    max_delay_seconds=60,           # 60 second max delay
    jitter_range=0.5,               # 0.5 second jitter
    show_rate_limit_warnings=True,  # Show warnings
    prompt_for_token_costs=True,    # Detect cost prompts
)
```

### Programmatic Configuration

```python
from poe_search.utils.config import RateLimitSettings

# Create custom rate limiting settings
rate_limit_settings = RateLimitSettings(
    enable_rate_limiting=True,
    max_calls_per_minute=10,        # Higher limit for power users
    retry_attempts=2,               # Fewer retries
    base_delay_seconds=2,           # Faster retries
    show_rate_limit_warnings=False, # Silent operation
    prompt_for_token_costs=True,    # Always detect costs
)

# Apply to configuration
config.rate_limit = rate_limit_settings
```

## Usage Scenarios

### 1. Conservative Usage (Default)

Best for most users who want to avoid rate limits:

```python
RateLimitSettings(
    enable_rate_limiting=True,
    max_calls_per_minute=5,         # Low limit
    retry_attempts=3,               # Standard retries
    base_delay_seconds=5,           # Standard delays
    show_rate_limit_warnings=True,  # Inform user
)
```

### 2. Power User Mode

For users who need faster data retrieval:

```python
RateLimitSettings(
    enable_rate_limiting=True,
    max_calls_per_minute=15,        # Higher limit
    retry_attempts=2,               # Fewer retries
    base_delay_seconds=2,           # Faster retries
    show_rate_limit_warnings=False, # Silent operation
)
```

### 3. Development/Testing

For development and testing scenarios:

```python
RateLimitSettings(
    enable_rate_limiting=False,     # Disable rate limiting
    prompt_for_token_costs=True,    # Still detect costs
)
```

## Error Handling

### Rate Limit Errors

When rate limits are hit:

1. **Detection**: System detects rate limit errors from Poe.com
2. **Backoff**: Implements exponential backoff with jitter
3. **Retry**: Attempts the request again after delay
4. **Fallback**: Uses cached data if available
5. **Notification**: Logs warnings (if enabled)

### Token Cost Errors

When Poe.com requests payment:

1. **Detection**: Identifies cost-related error messages
2. **Logging**: Records detailed cost information
3. **Guidance**: Provides user with Poe.com link
4. **Continuation**: Continues with available data
5. **Notification**: Logs cost prompt details

### Other API Errors

For non-rate-limit errors:

1. **Classification**: Determines error type
2. **Retry Logic**: Applies shorter retry delays
3. **Fallback**: Uses mock data if available
4. **Logging**: Records error details

## Monitoring and Logging

### Log Levels

- **INFO**: Normal rate limiting operations
- **WARNING**: Rate limits hit, retries attempted
- **ERROR**: Rate limits exceeded, failures

### Key Log Messages

```
Rate limit reached. Waiting 45.2 seconds...
Rate limit hit (attempt 2/4). Waiting 10.5 seconds before retry...
Token cost prompt detected: Payment required for additional tokens
Rate limit exceeded after 4 attempts
```

### Performance Metrics

The system tracks:

- **API call frequency**: Calls per minute
- **Retry success rate**: Successful retries vs failures
- **Average response times**: With and without rate limiting
- **Error distribution**: Rate limits vs other errors

## Best Practices

### 1. Start Conservative

Begin with default settings and adjust based on your needs:

```python
# Start with defaults
config.rate_limit.enable_rate_limiting = True
config.rate_limit.max_calls_per_minute = 8
```

### 2. Monitor Usage

Watch for rate limit warnings and adjust accordingly:

```python
# If you see frequent warnings, reduce the limit
config.rate_limit.max_calls_per_minute = 5
```

### 3. Handle Token Costs

Always enable token cost detection:

```python
config.rate_limit.prompt_for_token_costs = True
```

### 4. Use Appropriate Delays

Balance speed vs reliability:

```python
# For reliability
config.rate_limit.base_delay_seconds = 5
config.rate_limit.retry_attempts = 3

# For speed (if you have good connectivity)
config.rate_limit.base_delay_seconds = 2
config.rate_limit.retry_attempts = 2
```

## Troubleshooting

### Common Issues

1. **Frequent Rate Limits**
   - Reduce `max_calls_per_minute`
   - Increase `base_delay_seconds`
   - Check your internet connection

2. **Slow Performance**
   - Increase `max_calls_per_minute` (cautiously)
   - Reduce `base_delay_seconds`
   - Consider disabling rate limiting for testing

3. **Token Cost Prompts**
   - Visit https://poe.com to purchase tokens
   - Check your Poe.com subscription status
   - Verify your cookies are current

### Debug Mode

Enable debug logging for detailed rate limiting information:

```python
config.log_level = "DEBUG"
config.enable_debug_mode = True
```

### Testing Rate Limiting

Use the test script to verify your settings:

```bash
python scripts/test_rate_limiting_features.py
```

## Integration with GUI

The rate limiting settings are fully integrated into the GUI:

1. **Settings Dialog**: Advanced tab contains all rate limiting options
2. **Real-time Updates**: Changes apply immediately
3. **Persistent Storage**: Settings are saved to configuration file
4. **Validation**: GUI validates input ranges and values

## Future Enhancements

Planned improvements to the rate limiting system:

1. **Adaptive Rate Limiting**: Automatically adjust based on success rates
2. **User-specific Limits**: Different limits for different user types
3. **Advanced Analytics**: Detailed usage statistics and recommendations
4. **Integration with Poe.com**: Direct token purchase integration
5. **Machine Learning**: Predict optimal rate limiting parameters

## Conclusion

The rate limiting system in Poe Search provides a robust, configurable solution for handling Poe.com's API restrictions while maximizing data retrieval efficiency. Users can customize the behavior to match their usage patterns and requirements, ensuring a smooth and reliable experience. 