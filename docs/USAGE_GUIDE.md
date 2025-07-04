# How to Use Automatic Token Management

## Quick Start

The Poe Search application now automatically handles token management! Here's what you need to know:

### First Time Setup

1. **Install required dependencies** (if not already installed):
   ```bash
   pip install browser-cookie3
   ```

2. **Start any Poe Search application**:
   ```bash
   # GUI Application
   python -m poe_search.gui
   
   # CLI Application  
   python -m poe_search.cli search "my query"
   ```

3. **Follow the automatic token refresh prompts**:
   - The system will detect you need tokens
   - It will try to extract cookies from your browser automatically
   - You'll be prompted to provide the formkey manually
   - Tokens will be saved and validated

4. **You're done!** The application will use fresh tokens automatically.

## Daily Usage

### Normal Operation
- **Just start the app** - tokens are checked automatically
- **No manual intervention** needed for ~36 hours
- **Seamless experience** - app starts with fresh tokens

### When Tokens Expire (Every 1-2 Days)
The system will automatically detect expired tokens and prompt you:

1. **Automatic detection**: App detects tokens are >36 hours old
2. **Browser extraction**: Attempts to get p-b/p-lat cookies automatically  
3. **Manual formkey**: You provide formkey via browser dev tools
4. **Validation**: System tests tokens with Poe.com
5. **Ready to go**: App continues with fresh tokens

## Command Examples

### GUI Usage
```bash
# Normal startup (checks tokens automatically)
python -m poe_search.gui
```

### CLI Usage
```bash
# Normal commands (checks tokens automatically)
python -m poe_search.cli search "Claude conversations"
python -m poe_search.cli export --format json

# Skip token check (for troubleshooting)
python -m poe_search.cli --skip-token-check search "query"
```

### Manual Token Refresh
```bash
# Force refresh tokens manually
python scripts/refresh_tokens.py

# Or via token manager
python -c "
from poe_search.utils.token_manager import TokenManager
TokenManager().interactive_refresh()
"
```

## Integration in Your Code

### Basic Integration
```python
from poe_search.utils.token_manager import ensure_tokens_on_startup

def main():
    # Ensure tokens are fresh
    success, tokens = ensure_tokens_on_startup()
    
    if success:
        print("✅ Ready with fresh tokens!")
        # Your application logic here
    else:
        print("❌ Token refresh failed")
        return 1

if __name__ == "__main__":
    main()
```

### Advanced Configuration
```python
from poe_search.utils.token_manager import ensure_tokens_on_startup

# Custom age limit (12 hours instead of 36)
success, tokens = ensure_tokens_on_startup(max_age_hours=12)

# Non-interactive mode (for automation)  
success, tokens = ensure_tokens_on_startup(interactive=False)

# Very lenient (48 hours)
success, tokens = ensure_tokens_on_startup(max_age_hours=48)
```

### Manual Token Management
```python
from poe_search.utils.token_manager import TokenManager

manager = TokenManager()

# Check token age
age = manager.get_token_age()
if age:
    hours = age.total_seconds() / 3600
    print(f"Tokens are {hours:.1f} hours old")

# Check if fresh
if manager.are_tokens_fresh(max_age_hours=36):
    print("Tokens are fresh!")
else:
    print("Tokens need refresh")

# Force refresh
if manager.interactive_refresh():
    print("Refresh successful!")
```

## Troubleshooting

### "No tokens found"
```bash
# Run manual refresh
python scripts/refresh_tokens.py
```

### "browser-cookie3 not installed"
```bash
pip install browser-cookie3
```

### "Tokens too old" 
- This is normal every 1-2 days
- Follow the interactive refresh prompts
- Or run: `python scripts/refresh_tokens.py`

### GUI won't start
```bash
# Check what's wrong
python -m poe_search.gui

# If token issues, run:
python scripts/refresh_tokens.py
```

### CLI fails
```bash
# Skip token check temporarily
python -m poe_search.cli --skip-token-check search "query"

# Then refresh tokens
python scripts/refresh_tokens.py
```

### Automation/Background Services
```python
# Use non-interactive mode
success, tokens = ensure_tokens_on_startup(
    interactive=False,
    max_age_hours=48  # More lenient for background
)

if not success:
    # Log error, send notification, etc.
    logger.error("Tokens need manual refresh")
    send_admin_alert("Poe tokens expired")
```

## Configuration

### Token Age Limits
- **24 hours**: Very strict, daily refresh
- **36 hours**: Default, refresh every ~1.5 days  
- **48 hours**: Lenient, refresh every 2 days

### File Locations
Tokens are stored at:
- `config/poe_tokens.json` (project directory)
- `src/config/poe_tokens.json` (development)
- `~/.poe-search/poe_tokens.json` (user home)

Backups are stored at:
- `config/token_backups/poe_tokens_YYYYMMDD_HHMMSS.json`

## Security Notes

### ✅ What's Automatic
- Token age checking
- Browser cookie extraction (p-b, p-lat)
- Token validation
- Backup creation

### 🔒 What Requires Manual Input
- **Formkey**: Must be extracted manually via browser dev tools
- **Initial setup**: First-time token creation
- **Permission**: User confirms token refresh

### 🛡️ Security Features
- Local storage only (no cloud/remote storage)
- Automatic backup of previous tokens
- No logging of sensitive token values
- Manual formkey input for security

## Benefits

### For Users
- **No daily token management** - automatic refresh when needed
- **Clear prompts** - step-by-step guidance when refresh needed
- **Seamless experience** - apps just work with fresh tokens
- **Secure** - manual approval for sensitive formkey

### For Developers
- **Easy integration** - single function call
- **Robust error handling** - graceful fallbacks
- **Configurable** - adjustable age limits and modes
- **Well documented** - comprehensive examples

### For Operations
- **Automated monitoring** - automatic staleness detection
- **Backup system** - previous tokens preserved
- **Audit trail** - clear logging of token activities
- **Non-interactive support** - works in automation

## What's New

This automatic token management system replaces the previous manual process:

### Before (Manual)
1. Run application
2. Get API errors
3. Manually run `python scripts/refresh_tokens.py`
4. Follow manual steps to get all 3 tokens
5. Restart application
6. Repeat every 1-2 days

### Now (Automatic)  
1. Run application
2. System automatically detects token age
3. System prompts for refresh if needed (semi-automated)
4. Application starts with fresh tokens
5. Minimal user intervention

The system maintains security by requiring manual formkey input while automating everything else that can be safely automated.

## Next Steps

1. **Try it out**: Start any Poe Search application
2. **Test refresh**: Wait for tokens to expire or force refresh
3. **Integrate**: Use `ensure_tokens_on_startup()` in your code
4. **Customize**: Adjust age limits and modes as needed

The automatic token management system makes Poe Search truly production-ready for daily use!
