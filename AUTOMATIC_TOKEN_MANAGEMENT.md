# Automatic Token Management System

## Overview

The Poe Search application now includes a sophisticated automatic token management system that handles Poe.com authentication tokens seamlessly. This system eliminates the need for manual token management by automatically checking token freshness on every application startup and prompting for refresh when needed.

## Key Features

### ✅ Automatic Token Checking
- **Token Age Monitoring**: Checks if tokens are older than a configurable threshold (default: 36 hours)
- **Freshness Validation**: Verifies tokens are recent enough for reliable API access
- **API Connectivity Testing**: Tests tokens against the actual Poe.com API to ensure they work

### ✅ Semi-Automated Refresh
- **Browser Cookie Extraction**: Automatically extracts `p-b` and `p-lat` tokens from Chrome, Firefox, and Edge
- **Interactive Formkey Input**: Prompts user for formkey (which requires manual network inspection)
- **Backup and Recovery**: Creates backups of old tokens before updating

### ✅ Graceful Error Handling
- **Non-Interactive Mode**: Can run without user interaction for automated systems
- **Fallback Mechanisms**: Falls back to mock data when tokens are unavailable
- **Clear Error Messages**: Provides helpful guidance when token refresh is needed

### ✅ Integration Ready
- **GUI Integration**: Automatically checks tokens when starting the GUI application
- **CLI Integration**: Includes token checking in CLI commands with optional skip flag
- **Library Integration**: Easy to integrate into any Python application

## How It Works

### 1. Startup Token Check

Every time you start the application, the token manager:

```python
from poe_search.utils.token_manager import ensure_tokens_on_startup

# This happens automatically on app startup
success, tokens = ensure_tokens_on_startup(
    interactive=True,      # Allow user prompts
    max_age_hours=36      # Tokens older than 36h need refresh
)

if success:
    # Application continues with fresh tokens
    print("✅ Ready to go!")
else:
    # User needs to refresh tokens
    print("❌ Please refresh your tokens")
```

### 2. Token Age Assessment

The system checks:
- **File modification time**: When were tokens last updated?
- **Age threshold**: Are they older than the configured maximum age?
- **API validity**: Do they actually work with Poe.com?

### 3. Automatic Refresh Process

When refresh is needed:

1. **Extract browser cookies** (automatic)
   - Scans Chrome, Firefox, Edge for `p-b` and `p-lat` tokens
   - Uses `browser-cookie3` library for secure extraction

2. **Request formkey** (manual step required)
   - Guides user through browser developer tools
   - Shows step-by-step instructions for finding formkey

3. **Validate and save**
   - Tests new tokens against Poe.com API
   - Backs up old tokens
   - Saves new tokens securely

### 4. Integration Points

The system integrates at key application entry points:

- **GUI**: `python -m poe_search.gui` - checks tokens before showing window
- **CLI**: `python -m poe_search.cli` - checks tokens before running commands
- **Scripts**: Any script can call `ensure_tokens_on_startup()`

## Usage Examples

### Basic Usage (Recommended)

```python
from poe_search.utils.token_manager import ensure_tokens_on_startup

def main():
    # Check tokens on startup
    success, tokens = ensure_tokens_on_startup()
    
    if not success:
        print("Failed to get fresh tokens")
        return
    
    # Your application logic here
    print("Application ready with fresh tokens!")

if __name__ == "__main__":
    main()
```

### Advanced Usage

```python
from poe_search.utils.token_manager import TokenManager

def advanced_token_management():
    manager = TokenManager()
    
    # Check token age
    age = manager.get_token_age()
    if age:
        hours = age.total_seconds() / 3600
        print(f"Tokens are {hours:.1f} hours old")
    
    # Check if fresh
    if manager.are_tokens_fresh(max_age_hours=24):
        print("Tokens are fresh!")
    else:
        print("Tokens need refresh")
    
    # Force refresh
    if manager.interactive_refresh():
        print("Tokens refreshed successfully")
```

### Non-Interactive Mode

```python
# For automated systems
success, tokens = ensure_tokens_on_startup(
    interactive=False,      # No user prompts
    max_age_hours=48       # More lenient age limit
)

if not success:
    # Log error and use fallback
    logger.error("Tokens need manual refresh")
    # Application can still run with mock data
```

## Configuration

### Token Age Limits

You can configure how often tokens need refresh:

```python
# Very strict - refresh daily
ensure_tokens_on_startup(max_age_hours=24)

# Default - refresh every 1.5 days
ensure_tokens_on_startup(max_age_hours=36)

# Lenient - refresh every 2 days
ensure_tokens_on_startup(max_age_hours=48)
```

### CLI Options

The CLI includes options for token management:

```bash
# Normal operation (checks tokens)
python -m poe_search.cli search "my query"

# Skip token check (for troubleshooting)
python -m poe_search.cli --skip-token-check search "my query"

# Verbose output
python -m poe_search.cli --verbose search "my query"
```

## Token Storage

### File Locations

Tokens are stored in JSON format at:
- `config/poe_tokens.json` (project directory)
- `src/config/poe_tokens.json` (development)
- `~/.poe-search/poe_tokens.json` (user home)

### File Format

```json
{
  "p-b": "your-p-b-cookie-value",
  "p-lat": "your-p-lat-cookie-value", 
  "formkey": "your-formkey-value"
}
```

### Backup System

Old tokens are automatically backed up to:
- `config/token_backups/poe_tokens_YYYYMMDD_HHMMSS.json`

## Security Considerations

### ✅ Secure Storage
- Tokens stored in local files only
- No transmission to external servers
- Automatic backup of previous tokens

### ✅ Minimal Exposure
- Browser cookie extraction uses secure system APIs
- Formkey requires manual input (user controls exposure)
- No logging of sensitive token values

### ⚠️ Manual Step Required
- **Formkey extraction cannot be fully automated** due to Poe.com's security model
- Users must manually inspect network requests to get formkey
- This is intentional and unavoidable due to how Poe.com's authentication works

## Troubleshooting

### Common Issues

#### "No tokens found"
```bash
# Run manual refresh
python scripts/refresh_tokens.py
```

#### "Tokens are too old"
```bash
# Check token age
python test_token_management.py
```

#### "browser-cookie3 not installed"
```bash
pip install browser-cookie3
```

#### GUI/CLI won't start
```bash
# Skip token check temporarily
python -m poe_search.cli --skip-token-check
python -m poe_search.gui  # Will prompt for tokens
```

### Manual Token Refresh

If automatic refresh fails:

1. **Run the refresh script**:
   ```bash
   python scripts/refresh_tokens.py
   ```

2. **Or use the token manager directly**:
   ```bash
   python -c "from poe_search.utils.token_manager import TokenManager; TokenManager().interactive_refresh()"
   ```

### Debug Mode

Enable verbose logging to troubleshoot:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from poe_search.utils.token_manager import ensure_tokens_on_startup
ensure_tokens_on_startup()
```

## Integration Examples

### GUI Application

```python
# src/poe_search/gui/__main__.py
from poe_search.utils.token_manager import ensure_tokens_on_startup

def main():
    app = QApplication(sys.argv)
    
    # Check tokens before showing GUI
    success, _ = ensure_tokens_on_startup()
    if not success:
        # Show error dialog and exit
        QMessageBox.critical(None, "Token Error", 
                           "Please refresh your Poe.com tokens")
        sys.exit(1)
    
    # Continue with GUI...
    window = MainWindow()
    window.show()
    app.exec()
```

### CLI Application

```python
# src/poe_search/cli/__init__.py
@click.option("--skip-token-check", is_flag=True)
def main(skip_token_check: bool):
    if not skip_token_check:
        success, _ = ensure_tokens_on_startup()
        if not success:
            click.echo("❌ Token refresh required")
            sys.exit(1)
    
    # Continue with CLI logic...
```

### Background Service

```python
# For automated sync services
def background_sync():
    # Use non-interactive mode
    success, tokens = ensure_tokens_on_startup(
        interactive=False,
        max_age_hours=48  # More lenient for background
    )
    
    if success:
        # Run sync with fresh tokens
        sync_conversations()
    else:
        # Log error, use fallback, notify admin
        logger.error("Tokens need manual refresh")
        send_admin_notification()
```

## Benefits

### For Users
- **Seamless Experience**: No manual token management required
- **Automatic Refresh**: Prompted only when needed (every 1-2 days)
- **Clear Instructions**: Step-by-step guidance when refresh is needed
- **Always Working**: Applications always have fresh tokens

### For Developers
- **Easy Integration**: Single function call to ensure fresh tokens
- **Robust Error Handling**: Graceful fallbacks and clear error messages
- **Configurable**: Adjustable age limits and interactive modes
- **Well Tested**: Comprehensive test suite and validation

### For Operations
- **Automated Monitoring**: Automatic token age checking
- **Backup System**: Previous tokens are preserved
- **Logging**: Clear audit trail of token refresh activities
- **Non-Interactive Mode**: Works in automated environments

## Future Enhancements

### Potential Improvements
- **Official API Support**: Integration with official Poe API when available
- **Token Rotation**: Automatic rotation before expiration
- **Cloud Storage**: Optional secure cloud-based token storage
- **Team Sharing**: Secure token sharing for team environments

### Current Limitations
- **Formkey Manual Step**: Cannot be fully automated due to Poe.com security
- **Browser Dependency**: Cookie extraction requires supported browsers
- **Local Storage Only**: Tokens stored locally (by design for security)

## Conclusion

The automatic token management system makes Poe Search truly production-ready by eliminating the manual token refresh burden. Users can focus on searching and organizing their conversations while the system handles authentication seamlessly in the background.

The system strikes the right balance between automation and security, automating what can be safely automated while requiring manual input only for the security-sensitive formkey step.
