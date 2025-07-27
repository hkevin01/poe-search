# Troubleshooting Guide

## Common Issues

### Authentication Failed

**Symptoms:** Cannot sync conversations, authentication errors

**Solutions:**
1. Verify tokens are current and valid
2. Clear browser cache and get fresh tokens
3. Check if logged into Poe.com in browser

### No Conversations Found

**Symptoms:** Sync completes but no conversations appear

**Solutions:**
1. Ensure you have conversations in Poe.com history
2. Check if Poe.com interface has changed
3. Run with debug mode for detailed logging

### Browser Issues

**Symptoms:** Browser automation fails, crashes

**Solutions:**
1. Update Chrome/Chromium to latest version
2. Install/update ChromeDriver
3. Check firewall/antivirus settings
4. Run in non-headless mode for debugging

### Import Errors

**Symptoms:** Module not found errors when running

**Solutions:**
1. Verify virtual environment is activated
2. Install all required dependencies
3. Check Python path configuration

## Debug Mode

Run application with debug logging:
```bash
python gui_launcher.py --debug
```

Test browser client directly:
```bash
python scripts/development/debug_browser.py
```

## Getting Help

1. Check this troubleshooting guide
2. Review logs in `logs/` directory
3. Search existing GitHub issues
4. Create new issue with details:
   - OS and Python version
   - Error messages and logs
   - Steps to reproduce
