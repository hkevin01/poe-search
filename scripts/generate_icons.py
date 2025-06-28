#!/usr/bin/env python3
"""Generate application icons for Poe Search GUI."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication


def create_poe_search_icon(size: int = 32) -> QPixmap:
    """Create a Poe-themed search icon."""
    # Create a pixmap of the specified size
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Create a painter to draw the icon
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Poe brand colors: Purple (#7C3AED) and gradient
    poe_purple = QColor("#7C3AED")
    poe_dark = QColor("#5B21B6")
    poe_light = QColor("#A78BFA")
    
    # Scale factors based on size
    scale = size / 32.0
    
    # Draw magnifying glass (search symbol)
    # Glass circle
    painter.setPen(QPen(poe_purple, max(1, int(2 * scale))))
    painter.setBrush(QBrush(poe_light))
    painter.drawEllipse(
        int(8 * scale), int(8 * scale), 
        int(16 * scale), int(16 * scale)
    )
    
    # Handle
    painter.setPen(QPen(poe_purple, max(1, int(3 * scale))))
    painter.drawLine(
        int(20 * scale), int(20 * scale), 
        int(26 * scale), int(26 * scale)
    )
    
    # Add a small "P" for Poe in the center
    painter.setPen(QPen(poe_dark, max(1, int(1 * scale))))
    font_size = max(6, int(8 * scale))
    painter.setFont(QFont("Arial", font_size, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "P")
    
    painter.end()
    return pixmap


def create_app_icon(size: int = 128) -> QPixmap:
    """Create a larger application icon."""
    # Create a pixmap of the specified size
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Create a painter to draw the icon
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Poe brand colors
    poe_purple = QColor("#7C3AED")
    poe_dark = QColor("#5B21B6")
    poe_light = QColor("#A78BFA")
    poe_white = QColor("#FFFFFF")
    
    # Scale factors based on size
    scale = size / 128.0
    
    # Draw background circle with gradient effect
    painter.setPen(QPen(poe_purple, max(1, int(3 * scale))))
    painter.setBrush(QBrush(poe_purple))
    painter.drawEllipse(
        int(8 * scale), int(8 * scale), 
        int(112 * scale), int(112 * scale)
    )
    
    # Draw inner circle for depth
    painter.setPen(QPen(poe_light, max(1, int(2 * scale))))
    painter.setBrush(QBrush(poe_light))
    painter.drawEllipse(
        int(16 * scale), int(16 * scale), 
        int(96 * scale), int(96 * scale)
    )
    
    # Draw magnifying glass
    # Glass circle
    painter.setPen(QPen(poe_dark, max(1, int(4 * scale))))
    painter.setBrush(QBrush(poe_white))
    painter.drawEllipse(
        int(32 * scale), int(32 * scale), 
        int(48 * scale), int(48 * scale)
    )
    
    # Handle
    painter.setPen(QPen(poe_dark, max(1, int(6 * scale))))
    painter.drawLine(
        int(68 * scale), int(68 * scale), 
        int(88 * scale), int(88 * scale)
    )
    
    # Add "Poe" text
    painter.setPen(QPen(poe_dark, max(1, int(1 * scale))))
    font_size = max(12, int(16 * scale))
    painter.setFont(QFont("Arial", font_size, QFont.Weight.Bold))
    painter.drawText(
        int(0), int(90 * scale), int(128 * scale), int(30 * scale),
        Qt.AlignmentFlag.AlignCenter, "Poe"
    )
    
    painter.end()
    return pixmap


def main():
    """Generate all icons."""
    # Create QApplication for Qt operations
    _ = QApplication(sys.argv)
    
    # Create icons directory
    icons_dir = (
        Path(__file__).parent.parent / "src" / "poe_search" / 
        "gui" / "resources" / "icons"
    )
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate different sizes of tray icons
    tray_sizes = [16, 24, 32, 48]
    for size in tray_sizes:
        icon = create_poe_search_icon(size)
        icon_path = icons_dir / f"tray_icon_{size}x{size}.png"
        icon.save(str(icon_path), "PNG")
        print(f"Generated tray icon: {icon_path}")
    
    # Generate application icons
    app_sizes = [16, 32, 48, 64, 128, 256]
    for size in app_sizes:
        icon = create_app_icon(size)
        icon_path = icons_dir / f"app_icon_{size}x{size}.png"
        icon.save(str(icon_path), "PNG")
        print(f"Generated app icon: {icon_path}")
    
    # Create a default app icon
    default_icon = create_app_icon(128)
    default_icon_path = icons_dir / "app_icon.png"
    default_icon.save(str(default_icon_path), "PNG")
    print(f"Generated default app icon: {default_icon_path}")
    
    # Create a default tray icon
    default_tray_icon = create_poe_search_icon(32)
    default_tray_icon_path = icons_dir / "tray_icon.png"
    default_tray_icon.save(str(default_tray_icon_path), "PNG")
    print(f"Generated default tray icon: {default_tray_icon_path}")
    
    print("All icons generated successfully!")


if __name__ == "__main__":
    main() 