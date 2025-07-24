#!/bin/bash
# VS Code Global Settings Optimizer - Prevents freezing and performance issues

echo "Setting up VS Code global settings to prevent freezing and improve performance..."

# VS Code user settings directory
VSCODE_USER_DIR="$HOME/.config/Code/User"
SETTINGS_FILE="$VSCODE_USER_DIR/settings.json"

# Create directory if it doesn't exist
mkdir -p "$VSCODE_USER_DIR"

# Backup existing settings if they exist
if [ -f "$SETTINGS_FILE" ]; then
    echo "Backing up existing settings to settings.json.backup..."
    cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup"
fi

# Create optimized global settings
cat > "$SETTINGS_FILE" << 'EOF'
{
    // Terminal settings to prevent freezing
    "terminal.integrated.cwd": "${workspaceFolder}",
    "terminal.integrated.defaultLocation": "editor",
    "terminal.integrated.enablePersistentSessions": false,
    "terminal.integrated.persistentSessionReviveProcess": "never",
    "terminal.integrated.enableMultiLinePasteWarning": "never",
    "terminal.integrated.shellIntegration.enabled": false,
    "terminal.integrated.detectLocale": "off",
    "terminal.integrated.inheritEnv": false,
    "terminal.integrated.confirmOnExit": "never",
    "terminal.integrated.confirmOnKill": "never",
    "terminal.integrated.fastScrollSensitivity": 5,
    "terminal.integrated.scrollback": 1000,
    
    // Performance optimizations
    "workbench.startupEditor": "none",
    "extensions.autoUpdate": false,
    "extensions.autoCheckUpdates": false,
    "telemetry.telemetryLevel": "off",
    "update.mode": "none",
    "workbench.enableExperiments": false,
    "workbench.settings.enableNaturalLanguageSearch": false,
    
    // Git optimizations to prevent freezing
    "git.autorefresh": false,
    "git.autoRepositoryDetection": false,
    "git.autoStash": false,
    "git.autofetch": false,
    "git.enabled": true,
    "git.scanRepositories": [],
    "scm.autoReveal": false,
    
    // File watching optimizations
    "files.watcherExclude": {
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true,
        "**/node_modules/*/**": true,
        "**/.hg/store/**": true,
        "**/logs/**": true,
        "**/__pycache__/**": true,
        "**/.pytest_cache/**": true,
        "**/.venv/**": true,
        "**/venv/**": true,
        "**/env/**": true,
        "**/.env/**": true,
        "**/dist/**": true,
        "**/build/**": true,
        "**/*.log": true,
        "**/tmp/**": true,
        "**/temp/**": true
    },
    
    // Search optimizations
    "search.exclude": {
        "**/logs/**": true,
        "**/__pycache__/**": true,
        "**/.pytest_cache/**": true,
        "**/.venv/**": true,
        "**/venv/**": true,
        "**/env/**": true,
        "**/.env/**": true,
        "**/node_modules/**": true,
        "**/dist/**": true,
        "**/build/**": true,
        "**/*.log": true
    },
    
    // Editor performance
    "editor.minimap.enabled": false,
    "editor.codeLens": false,
    "editor.hover.delay": 1000,
    "editor.quickSuggestions": {
        "other": false,
        "comments": false,
        "strings": false
    },
    
    // Python specific optimizations
    "python.analysis.autoImportCompletions": false,
    "python.analysis.diagnosticMode": "openFilesOnly",
    "python.analysis.indexing": false,
    
    // Disable problematic extensions auto-loading
    "workbench.tree.enableStickyScroll": false,
    "workbench.list.smoothScrolling": false,
    "workbench.tree.renderIndentGuides": "none"
}
EOF

echo "✅ Global VS Code settings have been optimized!"
echo "📍 Settings file: $SETTINGS_FILE"
echo ""
echo "Changes made:"
echo "  - Disabled persistent terminal sessions"
echo "  - Disabled shell integration"
echo "  - Optimized file watching"
echo "  - Disabled auto-updates and telemetry" 
echo "  - Optimized Git integration"
echo "  - Reduced editor overhead"
echo ""
echo "These settings will prevent VS Code from freezing on directory changes and improve overall performance."
echo "If you need to restore previous settings, they are backed up as settings.json.backup"
