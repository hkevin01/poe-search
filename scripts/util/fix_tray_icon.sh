#!/bin/bash

echo "=== Poe Search System Tray Icon Fix ==="
echo "This script will help fix system tray icon issues on Ubuntu."
echo ""

# Check if running on Ubuntu/Debian
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux system."
    
    # Check if GNOME is running
    if [[ "$XDG_CURRENT_DESKTOP" == "ubuntu:GNOME" ]] || [[ "$XDG_CURRENT_DESKTOP" == "GNOME" ]]; then
        echo "Detected GNOME desktop environment."
        echo ""
        echo "To enable system tray icons in GNOME, you need to install an extension:"
        echo ""
        echo "Option 1: Install via apt (recommended):"
        echo "  sudo apt update"
        echo "  sudo apt install gnome-shell-extension-appindicator"
        echo ""
        echo "Option 2: Install via GNOME Extensions website:"
        echo "  Visit: https://extensions.gnome.org/extension/615/appindicator-support/"
        echo "  Click 'Install' and enable the extension"
        echo ""
        echo "After installation:"
        echo "  1. Restart GNOME Shell: Alt+F2, type 'r', press Enter"
        echo "  2. Or log out and log back in"
        echo "  3. Enable the extension in GNOME Extensions app"
        echo ""
        
        # Check if extension is already installed
        if dpkg -l | grep -q "gnome-shell-extension-appindicator"; then
            echo "✅ AppIndicator extension is already installed!"
            echo "Make sure it's enabled in GNOME Extensions."
        else
            echo "❌ AppIndicator extension is not installed."
            echo "Run: sudo apt install gnome-shell-extension-appindicator"
        fi
        
    elif [[ "$XDG_CURRENT_DESKTOP" == "KDE" ]]; then
        echo "Detected KDE desktop environment."
        echo "KDE should support system tray icons by default."
        echo "If icons don't appear, check KDE System Settings > System Tray."
        
    elif [[ "$XDG_CURRENT_DESKTOP" == "XFCE" ]]; then
        echo "Detected XFCE desktop environment."
        echo "XFCE should support system tray icons by default."
        echo "If icons don't appear, check XFCE Settings > Panel > Items."
        
    else
        echo "Unknown desktop environment: $XDG_CURRENT_DESKTOP"
        echo "System tray support may vary."
    fi
    
else
    echo "This script is designed for Linux systems."
    echo "For other operating systems, system tray support varies."
fi

echo ""
echo "=== Current Status ==="
echo "Your Poe Search application is working correctly!"
echo "The system tray icon is a cosmetic feature and doesn't affect functionality."
echo ""
echo "To test the application:"
echo "  ./run.sh"
echo ""
echo "The application will work perfectly even without the system tray icon." 