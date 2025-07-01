# Poe.com API Integration Guide

This document explains how to integrate with Poe.com API for any project, including the required information, setup steps, and code examples.

## Overview

Poe.com provides access to various AI models through their API. To integrate with Poe.com, you need to authenticate using browser cookies and use the `poe-api-wrapper` library.

## Required Information

### 1. Authentication Cookies

You need to extract the following cookies from your browser when logged into Poe.com:

- **`p-b`**: Primary authentication token (required)
- **`p-lat`**: Secondary authentication token (optional but recommended)
- **`formkey`**: Form key for additional security (optional)

### 2. How to Extract Cookies

#### Method 1: Browser Developer Tools
1. Go to [poe.com](https://poe.com) and log in
2. Open Developer Tools (F12)
3. Go to Application/Storage → Cookies → poe.com
4. Copy the values for `p-b`, `p-lat`, and `formkey`

#### Method 2: Browser Extension
1. Install a cookie export extension (e.g., "Cookie Editor")
2. Navigate to poe.com
3. Export cookies and find the required values

#### Method 3: Network Tab
1. Open Developer Tools → Network tab
2. Refresh poe.com
3. Look for any request to poe.com
4. Copy cookies from the request headers

### 3. Dependencies

Install the required Python package:
```bash
pip install poe-api-wrapper
```

## Basic Integration

### 1. Simple Example

```python
from poe_api_wrapper import PoeApi

# Your cookies from browser
tokens = {
    "p-b": "your_p_b_cookie_value_here",
    "p-lat": "your_p_lat_cookie_value_here",
    "formkey": "your_formkey_value_here"  # optional
}

# Initialize client
client = PoeApi(tokens)

# Test connection
try:
    settings = client.get_settings()
    print("✅ Connected successfully!")
    print(f"Subscription: {settings.get('subscription', {}).get('planType', 'Unknown')}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### 2. Get Available Bots

```python
# Get list of available bots
try:
    bots = client.get_available_bots()
    print(f"Found {len(bots)} bots")
    for bot in bots:
        print(f"- {bot.get('displayName', 'Unknown')} ({bot.get('id', 'Unknown')})")
except Exception as e:
    print(f"Failed to get bots: {e}")
```

### 3. Get Chat History

```python
# Get recent conversations for a specific bot
bot_id = "a2"  # Claude
try:
    response = client.get_chat_history(bot_id, count=10)
    
    # Extract conversations from response
    if isinstance(response, dict) and 'data' in response:
        conversations = response['data'].get(bot_id, [])
        print(f"Found {len(conversations)} conversations")
        
        for conv in conversations:
            print(f"- {conv.get('title', 'Untitled')} (ID: {conv.get('chatId')})")
except Exception as e:
    print(f"Failed to get chat history: {e}")
```

### 4. Get Messages from a Conversation

```python
# Get messages from a specific conversation
bot_id = "a2"
chat_id = "your_chat_id_here"

try:
    messages = client.get_message_history(bot_id, chat_id, count=50)
    
    if hasattr(messages, '__iter__'):
        messages = list(messages)
        print(f"Found {len(messages)} messages")
        
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get('role', 'unknown')
                text = msg.get('text', '')[:100] + "..." if len(msg.get('text', '')) > 100 else msg.get('text', '')
                print(f"[{role}] {text}")
except Exception as e:
    print(f"Failed to get messages: {e}")
```

## Advanced Integration

### 1. Rate Limiting

The Poe API has rate limits. Implement proper delays between requests:

```python
import time
import random

def safe_api_call(func, *args, **kwargs):
    """Wrapper for API calls with rate limiting"""
    try:
        result = func(*args, **kwargs)
        # Add random delay between requests
        time.sleep(random.uniform(1, 3))
        return result
    except Exception as e:
        print(f"API call failed: {e}")
        # Add longer delay on failure
        time.sleep(random.uniform(5, 10))
        return None
```

### 2. Error Handling

```python
def robust_poe_call(client, method, *args, **kwargs):
    """Robust wrapper for Poe API calls with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if 'rate limit' in error_msg or '429' in error_msg:
                wait_time = (2 ** attempt) * 5  # Exponential backoff
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            elif attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2)
            else:
                raise e
```

### 3. Complete Example with Error Handling

```python
import time
import random
from poe_api_wrapper import PoeApi

class PoeClient:
    def __init__(self, tokens):
        self.client = PoeApi(tokens)
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1:  # Minimum 1 second between requests
            time.sleep(1 - time_since_last)
        self.last_request_time = time.time()
    
    def get_conversations(self, bot_id, count=20):
        """Get conversations for a bot with error handling"""
        self._rate_limit()
        
        try:
            response = self.client.get_chat_history(bot_id, count=count)
            
            if isinstance(response, dict) and 'data' in response:
                return response['data'].get(bot_id, [])
            else:
                print(f"Unexpected response format for {bot_id}")
                return []
                
        except Exception as e:
            print(f"Failed to get conversations for {bot_id}: {e}")
            return []
    
    def get_all_conversations(self, bot_ids=None):
        """Get conversations from multiple bots"""
        if bot_ids is None:
            bot_ids = ["a2", "chinchilla", "capybara", "beaver", "claude-3-5-sonnet"]
        
        all_conversations = []
        
        for bot_id in bot_ids:
            conversations = self.get_conversations(bot_id)
            for conv in conversations:
                if isinstance(conv, dict):
                    conv['bot_id'] = bot_id
                    all_conversations.append(conv)
            
            # Add delay between bots
            time.sleep(random.uniform(1, 3))
        
        return all_conversations

# Usage
tokens = {
    "p-b": "your_p_b_cookie_value_here",
    "p-lat": "your_p_lat_cookie_value_here"
}

poe_client = PoeClient(tokens)
conversations = poe_client.get_all_conversations()

for conv in conversations[:5]:  # Show first 5
    print(f"- {conv.get('title', 'Untitled')} (Bot: {conv.get('bot_id')})")
```

## Common Bot IDs

Here are some common bot IDs you can use:

- `"a2"` - Claude (Anthropic)
- `"chinchilla"` - ChatGPT (OpenAI)
- `"capybara"` - Assistant (OpenAI)
- `"beaver"` - GPT-4 (OpenAI)
- `"claude-3-5-sonnet"` - Claude 3.5 Sonnet
- `"claude-3-opus"` - Claude 3 Opus
- `"gemini-pro"` - Gemini Pro (Google)
- `"llama-2-70b"` - Llama 2 70B
- `"mistral-7b"` - Mistral 7B

## Response Format

### Chat History Response
```json
{
  "data": {
    "bot_id": [
      {
        "chatId": 123456789,
        "chatCode": "abc123def456",
        "id": "Q2hhdDoxMjM0NTY3ODk=",
        "title": "Conversation Title"
      }
    ]
  },
  "cursor": null
}
```

### Settings Response
```json
{
  "subscription": {
    "isActive": true,
    "planType": "yearly",
    "id": "U3Vic2NyaXB0aW9uOjA=",
    "purchaseType": "web",
    "isComplimentary": false,
    "expiresTime": 1770596307000000,
    "willCancelAtPeriodEnd": true,
    "isFreeTrial": false
  },
  "messagePointInfo": {
    "messagePointResetTime": 1752192090000000,
    "messagePointBalance": 4652677,
    "totalMessagePointAllotment": 5000000,
    "id": "TWVzc2FnZVBvaW50SW5mbzow"
  }
}
```

## Troubleshooting

### Common Issues

1. **"PersistedQueryNotFound" Error**
   - Some API endpoints may have changed
   - Try using different bot IDs
   - Check if the poe-api-wrapper is up to date

2. **Authentication Failures**
   - Ensure cookies are fresh and valid
   - Re-extract cookies from browser
   - Check if you're logged into Poe.com

3. **Rate Limiting**
   - Implement proper delays between requests
   - Use exponential backoff on failures
   - Respect the API limits

4. **Empty Responses**
   - Some bots may not have conversations
   - Try different bot IDs
   - Check if the response format has changed

### Debug Tips

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test connection
try:
    settings = client.get_settings()
    print("Connection successful")
    print(f"Settings: {settings}")
except Exception as e:
    print(f"Connection failed: {e}")
    import traceback
    traceback.print_exc()
```

## Security Considerations

1. **Never commit cookies to version control**
2. **Store cookies securely** (environment variables, encrypted files)
3. **Rotate cookies regularly**
4. **Use HTTPS for all API calls**
5. **Implement proper error handling**

## Example Configuration File

Create a `config.json` file (never commit this to version control):

```json
{
  "poe_tokens": {
    "p-b": "your_p_b_cookie_value_here",
    "p-lat": "your_p_lat_cookie_value_here",
    "formkey": "your_formkey_value_here"
  },
  "rate_limiting": {
    "min_delay": 1,
    "max_delay": 3,
    "retry_attempts": 3
  }
}
```

Load it securely:

```python
import json
import os

def load_config():
    config_path = os.getenv('POE_CONFIG_PATH', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

config = load_config()
tokens = config['poe_tokens']
```

## Conclusion

This guide provides everything you need to integrate with Poe.com API in another project. Remember to:

1. Extract fresh cookies from your browser
2. Install the poe-api-wrapper library
3. Implement proper rate limiting and error handling
4. Store credentials securely
5. Test thoroughly before deploying

For more advanced features, refer to the [poe-api-wrapper documentation](https://github.com/snowby666/poe-api-wrapper). 