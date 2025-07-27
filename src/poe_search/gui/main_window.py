#!/usr/bin/env python3
"""
Main GUI application for Poe Search.

Modern PyQt6-based interface for managing and searching Poe.com conversations.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6 import QtCore
except ImportError:
    print("❌ PyQt6 not found. Please install with: pip install PyQt6")
    sys.exit(1)

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from poe_search.api.browser_client import PoeApiClient
from poe_search.core.utils import safe_json_load, safe_json_save, get_project_root


class PoeSearchGUI:
    """Main GUI application for Poe Search."""

    def __init__(self):
        """Initialize the GUI application."""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Poe Search")
        self.app.setApplicationVersion("1.3.0")

        # Initialize data
        self.conversations = []
        self.filtered_conversations = []
        self.current_conversation = None
        self.client = None
        self.loaded_tokens = {}

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Setup UI
        self.setup_ui()
        self.load_settings()
        self.update_display()

    def setup_ui(self):
        """Setup the user interface."""
        # Create main window
        self.window = QMainWindow()
        self.window.setWindowTitle("🔍 Poe Search - Enhanced AI Conversation Manager")
        self.window.setGeometry(100, 100, 1400, 900)

        # Create central widget
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout(central_widget)

        # Create left panel (conversation list)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # Create right panel (conversation viewer)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)

        # Create status bar
        self.status_bar = self.window.statusBar()
        self.status_bar.showMessage("Ready")

        # Apply styling
        self.apply_theme()

    def create_left_panel(self):
        """Create the left panel with conversation list and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("📋 Conversations")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Search and filters
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search conversations...")
        self.search_input.textChanged.connect(self.filter_conversations)
        search_layout.addWidget(self.search_input)

        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "All Categories", "Technical", "Creative", "Educational",
            "Business", "Science", "General", "Claude Conversations",
            "GPT Conversations", "Gemini Conversations"
        ])
        self.category_filter.currentTextChanged.connect(self.filter_conversations)
        search_layout.addWidget(self.category_filter)

        layout.addLayout(search_layout)

        # Sync controls
        sync_layout = QHBoxLayout()

        self.sync_button = QPushButton("🚀 Enhanced Sync")
        self.sync_button.clicked.connect(self.start_sync)
        sync_layout.addWidget(self.sync_button)

        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setRange(1, 1000)
        self.limit_spinbox.setValue(50)
        self.limit_spinbox.setSuffix(" conversations")
        sync_layout.addWidget(self.limit_spinbox)

        layout.addLayout(sync_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Conversation list
        self.conversation_list = QListWidget()
        self.conversation_list.itemClicked.connect(self.on_conversation_selected)
        layout.addWidget(self.conversation_list)

        # Statistics
        self.stats_label = QLabel("No conversations loaded")
        self.stats_label.setStyleSheet("color: gray; padding: 5px;")
        layout.addWidget(self.stats_label)

        return panel

    def create_right_panel(self):
        """Create the right panel with conversation viewer and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Conversation header
        self.conv_header = QLabel("Select a conversation to view")
        self.conv_header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; border-bottom: 1px solid gray;")
        layout.addWidget(self.conv_header)

        # Action buttons
        button_layout = QHBoxLayout()

        self.open_browser_btn = QPushButton("🌐 Open in Browser")
        self.open_browser_btn.clicked.connect(self.open_conversation_in_browser)
        self.open_browser_btn.setEnabled(False)
        button_layout.addWidget(self.open_browser_btn)

        self.export_conv_btn = QPushButton("📤 Export")
        self.export_conv_btn.clicked.connect(self.export_current_conversation)
        self.export_conv_btn.setEnabled(False)
        button_layout.addWidget(self.export_conv_btn)

        self.copy_conv_btn = QPushButton("📋 Copy")
        self.copy_conv_btn.clicked.connect(self.copy_conversation)
        self.copy_conv_btn.setEnabled(False)
        button_layout.addWidget(self.copy_conv_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Message viewer
        self.message_viewer = QTextEdit()
        self.message_viewer.setReadOnly(True)
        layout.addWidget(self.message_viewer)

        return panel

    def apply_theme(self):
        """Apply dark theme to the application."""
        dark_style = """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QListWidget {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                padding: 6px;
                border-radius: 4px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """
        self.app.setStyleSheet(dark_style)

    def load_settings(self):
        """Load application settings and tokens."""
        config_dir = get_project_root() / "config"

        # Load tokens
        tokens_file = config_dir / "poe_tokens.json"
        self.loaded_tokens = safe_json_load(tokens_file, {})

        if self.loaded_tokens:
            self.logger.info(f"Loaded tokens: {list(self.loaded_tokens.keys())}")

    def start_sync(self):
        """Start the conversation sync process."""
        if not self.loaded_tokens.get('p-b'):
            QMessageBox.warning(
                self.window,
                "No Tokens",
                "Please configure your Poe.com tokens in config/poe_tokens.json"
            )
            return

        # Setup UI for sync
        self.sync_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and start sync thread
        self.sync_thread = SyncThread(
            token=self.loaded_tokens.get('p-b'),
            lat_token=self.loaded_tokens.get('p-lat'),
            limit=self.limit_spinbox.value()
        )
        self.sync_thread.progress.connect(self.update_sync_progress)
        self.sync_thread.finished.connect(self.sync_finished)
        self.sync_thread.error.connect(self.sync_error)
        self.sync_thread.start()

    def update_sync_progress(self, message: str, percentage: int):
        """Update sync progress display."""
        self.progress_bar.setValue(percentage)
        self.status_bar.showMessage(message)

    def sync_finished(self, conversations: List[Dict[str, Any]]):
        """Handle sync completion."""
        self.conversations = conversations
        self.populate_conversation_list()
        self.update_display()

        # Reset UI
        self.sync_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"✅ Synced {len(conversations)} conversations")

    def sync_error(self, error_message: str):
        """Handle sync error."""
        QMessageBox.critical(self.window, "Sync Error", f"Failed to sync conversations:\n{error_message}")

        # Reset UI
        self.sync_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("❌ Sync failed")

    def populate_conversation_list(self):
        """Populate the conversation list widget."""
        self.conversation_list.clear()

        for conv in self.filtered_conversations or self.conversations:
            item = QListWidgetItem()

            # Create display text
            title = conv.get('title', 'Unknown')[:50]
            bot = conv.get('bot', 'Assistant')
            category = conv.get('category', 'General')

            display_text = f"{title}\n🤖 {bot} | 📂 {category}"
            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, conv)

            self.conversation_list.addItem(item)

    def filter_conversations(self):
        """Filter conversations based on search and category."""
        search_text = self.search_input.text().lower()
        category_filter = self.category_filter.currentText()

        if not search_text and category_filter == "All Categories":
            self.filtered_conversations = self.conversations
        else:
            self.filtered_conversations = []

            for conv in self.conversations:
                # Text search
                if search_text:
                    title = conv.get('title', '').lower()
                    bot = conv.get('bot', '').lower()
                    if search_text not in title and search_text not in bot:
                        continue

                # Category filter
                if category_filter != "All Categories":
                    if conv.get('category') != category_filter:
                        continue

                self.filtered_conversations.append(conv)

        self.populate_conversation_list()
        self.update_display()

    def update_display(self):
        """Update the display with current data."""
        count = len(self.filtered_conversations or self.conversations)
        total = len(self.conversations)

        if self.filtered_conversations and len(self.filtered_conversations) != total:
            self.stats_label.setText(f"Showing {count} of {total} conversations")
        else:
            self.stats_label.setText(f"{total} conversations loaded")

    def on_conversation_selected(self, item):
        """Handle conversation selection."""
        conversation = item.data(Qt.ItemDataRole.UserRole)
        if not conversation:
            return

        self.current_conversation = conversation

        # Update header
        title = conversation.get('title', 'Unknown Conversation')[:50]
        bot = conversation.get('bot', 'Assistant')
        category = conversation.get('category', 'General')

        self.conv_header.setText(f"📝 {title} | 🤖 {bot} | 📂 {category}")

        # Enable action buttons
        self.open_browser_btn.setEnabled(True)
        self.export_conv_btn.setEnabled(True)
        self.copy_conv_btn.setEnabled(True)

        # Display conversation content
        self.display_conversation_content(conversation)

    def display_conversation_content(self, conversation):
        """Display conversation content in the viewer."""
        messages = conversation.get('messages', [])

        if not messages:
            self.message_viewer.setHtml("""
                <div style='text-align: center; padding: 20px; color: #888;'>
                    <h3>📭 No messages loaded</h3>
                    <p>This conversation doesn't have message content loaded yet.</p>
                    <p>Message content would be loaded by clicking "Load Messages" button.</p>
                </div>
            """)
            return

        # Create HTML content
        html_content = """
        <style>
            body { font-family: 'Segoe UI', sans-serif; line-height: 1.6; margin: 0; padding: 10px; background: #1e1e1e; color: #fff; }
            .message { margin: 10px 0; padding: 12px; border-radius: 8px; }
            .user { background: #0078d4; color: white; margin-left: 20px; }
            .assistant { background: #2a2a2a; border: 1px solid #404040; margin-right: 20px; }
            .role { font-weight: bold; margin-bottom: 5px; }
            .content { white-space: pre-wrap; }
            .timestamp { font-size: 0.8em; opacity: 0.7; margin-top: 5px; }
        </style>
        <body>
        """

        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')

            role_icon = "👤" if role == "user" else "🤖"
            css_class = role

            html_content += f"""
            <div class="message {css_class}">
                <div class="role">{role_icon} {role.title()}</div>
                <div class="content">{content}</div>
                <div class="timestamp">{timestamp}</div>
            </div>
            """

        html_content += "</body>"
        self.message_viewer.setHtml(html_content)

    def open_conversation_in_browser(self):
        """Open current conversation in browser."""
        if not self.current_conversation:
            return

        url = self.current_conversation.get('url')
        if url and url != 'No direct URL':
            import webbrowser
            webbrowser.open(url)
            self.status_bar.showMessage(f"🌐 Opened conversation in browser")
        else:
            QMessageBox.warning(self.window, "No URL", "This conversation doesn't have a direct URL")

    def export_current_conversation(self):
        """Export current conversation to file."""
        if not self.current_conversation:
            QMessageBox.warning(self.window, "No Selection", "Please select a conversation first")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self.window,
            "Export Conversation",
            f"conversation_{self.current_conversation.get('id', 'unknown')}.json",
            "JSON Files (*.json);;Text Files (*.txt)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    if filename.endswith('.json'):
                        json.dump(self.current_conversation, f, indent=2, ensure_ascii=False)
                    else:
                        # Text export
                        f.write(f"Title: {self.current_conversation.get('title', 'Unknown')}\n")
                        f.write(f"Bot: {self.current_conversation.get('bot', 'Assistant')}\n")
                        f.write(f"Category: {self.current_conversation.get('category', 'General')}\n")
                        f.write(f"URL: {self.current_conversation.get('url', 'N/A')}\n\n")

                        messages = self.current_conversation.get('messages', [])
                        for msg in messages:
                            f.write(f"{msg.get('role', 'unknown').upper()}: {msg.get('content', '')}\n\n")

                QMessageBox.information(self.window, "Success", f"✅ Exported to {filename}")
                self.status_bar.showMessage(f"✅ Exported conversation")

            except Exception as e:
                QMessageBox.critical(self.window, "Export Error", f"Failed to export: {str(e)}")

    def copy_conversation(self):
        """Copy current conversation to clipboard."""
        if not self.current_conversation:
            return

        try:
            content = f"Title: {self.current_conversation.get('title', 'Unknown')}\n"
            content += f"Bot: {self.current_conversation.get('bot', 'Assistant')}\n"
            content += f"Category: {self.current_conversation.get('category', 'General')}\n\n"

            messages = self.current_conversation.get('messages', [])
            for msg in messages:
                content += f"{msg.get('role', 'unknown').upper()}: {msg.get('content', '')}\n\n"

            clipboard = QApplication.clipboard()
            clipboard.setText(content)

            self.status_bar.showMessage("📋 Conversation copied to clipboard")

        except Exception as e:
            QMessageBox.warning(self.window, "Copy Error", f"Failed to copy: {str(e)}")

    def run(self):
        """Run the GUI application."""
        self.window.show()
        return self.app.exec()


class SyncThread(QThread):
    """Thread for background conversation synchronization."""

    progress = pyqtSignal(str, int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, token: str, lat_token: Optional[str] = None, limit: int = 50):
        super().__init__()
        self.token = token
        self.lat_token = lat_token
        self.limit = limit

    def run(self):
        """Run the sync process."""
        try:
            with PoeApiClient(token=self.token, lat_token=self.lat_token, headless=True) as client:
                conversations = client.get_conversations(
                    limit=self.limit,
                    progress_callback=self.progress.emit
                )
                self.finished.emit(conversations)
        except Exception as e:
            self.error.emit(str(e))


def run_gui():
    """Run the GUI application."""
    gui = PoeSearchGUI()
    return gui.run()


def main():
    """Main entry point."""
    return run_gui()


if __name__ == "__main__":
    sys.exit(main())
