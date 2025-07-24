# src/poe_search/gui/main_window.py
import sys
import asyncio
from typing import List, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
    QLabel, QComboBox, QProgressBar, QMessageBox, QStatusBar,
    QMenuBar, QMenu, QFileDialog, QCheckBox, QApplication  # ← Added this import
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QAction


from ..api.client import create_poe_client, PoeApiClient
from ..models.conversation import Conversation, Message
from ..database.manager import DatabaseManager
from ..utils.logger import get_logger
from ..config.settings import get_config

logger = get_logger(__name__)

class ConversationSyncThread(QThread):
    """Background thread for syncing conversations"""
    progress_update = pyqtSignal(int, str)
    conversations_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, poe_client: PoeApiClient, limit: int = 50):
        super().__init__()
        self.poe_client = poe_client
        self.limit = limit
        
    def run(self):
        try:
            self.progress_update.emit(0, "Connecting to Poe...")
            
            # Connect to Poe
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            connected = loop.run_until_complete(self.poe_client.connect())
            if not connected:
                self.error_occurred.emit("Failed to connect to Poe. Please check your token.")
                return
            
            self.progress_update.emit(25, "Fetching conversations...")
            
            # Fetch conversations
            conversations = loop.run_until_complete(
                self.poe_client.get_conversations(self.limit)
            )
            
            self.progress_update.emit(75, "Loading messages...")
            
            # Fetch messages for first few conversations
            for i, conv in enumerate(conversations[:5]):  # Limit to first 5 for speed
                messages = loop.run_until_complete(
                    self.poe_client.get_conversation_messages(conv.id)
                )
                conv.messages = messages
                
                progress = 75 + (i + 1) * 5  # 75% to 100%
                self.progress_update.emit(progress, f"Loaded messages for {conv.title[:30]}...")
            
            self.progress_update.emit(100, "Complete!")
            self.conversations_loaded.emit(conversations)
            
        except Exception as e:
            logger.error(f"Error in sync thread: {e}")
            self.error_occurred.emit(f"Sync failed: {str(e)}")

class ChatListWidget(QListWidget):
    """Custom list widget for displaying conversations"""
    
    conversation_selected = pyqtSignal(Conversation)
    
    def __init__(self):
        super().__init__()
        self.conversations = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #404040;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
        """)
        
        self.itemClicked.connect(self._on_item_clicked)
    
    def populate_conversations(self, conversations: List[Conversation]):
        """Populate the list with conversations"""
        self.clear()
        self.conversations = conversations
        
        for conv in conversations:
            # Create display text
            title = conv.title[:50] + "..." if len(conv.title) > 50 else conv.title
            subtitle = f"{conv.bot} • {len(conv.messages)} messages"
            display_text = f"{title}\n{subtitle}"
            
            # Create list item
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, conv.id)
            
            # Add to list
            self.addItem(item)
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle conversation selection"""
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        
        # Find conversation object
        conversation = None
        for conv in self.conversations:
            if conv.id == conv_id:
                conversation = conv
                break
        
        if conversation:
            self.conversation_selected.emit(conversation)

class ChatViewerWidget(QTextEdit):
    """Widget for displaying conversation messages"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        
        # Set font
        font = QFont("Segoe UI", 11)
        self.setFont(font)
    
    def display_conversation(self, conversation: Conversation):
        """Display a conversation with proper formatting"""
        if not conversation or not conversation.messages:
            self.setText("No messages to display.")
            return
        
        html_content = self._format_conversation_html(conversation)
        self.setHtml(html_content)
    
    def _format_conversation_html(self, conversation: Conversation) -> str:
        """Format conversation as HTML"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #ffffff;
                    background-color: #1e1e1e;
                    margin: 0;
                    padding: 20px;
                }}
                .conversation-header {{
                    border-bottom: 2px solid #404040;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .conversation-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #0078d4;
                    margin-bottom: 5px;
                }}
                .conversation-meta {{
                    color: #888888;
                    font-size: 12px;
                }}
                .message {{
                    margin-bottom: 20px;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid;
                }}
                .user-message {{
                    background-color: #2a2a2a;
                    border-left-color: #0078d4;
                }}
                .assistant-message {{
                    background-color: #252525;
                    border-left-color: #00b294;
                }}
                .message-role {{
                    font-weight: bold;
                    margin-bottom: 8px;
                    font-size: 13px;
                }}
                .user-role {{ color: #0078d4; }}
                .assistant-role {{ color: #00b294; }}
                .message-content {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
                .timestamp {{
                    color: #666666;
                    font-size: 11px;
                    margin-top: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="conversation-header">
                <div class="conversation-title">{conversation.title}</div>
                <div class="conversation-meta">
                    Bot: {conversation.bot} • 
                    Messages: {len(conversation.messages)} • 
                    Created: {conversation.created_at.strftime('%Y-%m-%d %H:%M')}
                </div>
            </div>
        """
        
        # Add messages
        for message in conversation.messages:
            role_class = "user" if message.role == "user" else "assistant"
            role_display = "You" if message.role == "user" else (message.bot_name or "Assistant")
            
            html += f"""
            <div class="message {role_class}-message">
                <div class="message-role {role_class}-role">{role_display}</div>
                <div class="message-content">{self._escape_html(message.content)}</div>
                <div class="timestamp">{message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            """
        
        html += "</body></html>"
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        import html
        return html.escape(text)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.poe_client = None
        self.db_manager = None
        self.conversations = []
        self.settings = QSettings("PoeSearch", "MainApp")
        
        self.setup_ui()
        self.setup_connections()
        self.load_settings()
        
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("Poe Search - Chat Viewer")
        self.setGeometry(100, 100, 1400, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        
        # Top toolbar
        toolbar_layout = QHBoxLayout()
        
        # Token input
        toolbar_layout.addWidget(QLabel("Poe Token:"))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your p-b cookie value...")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        toolbar_layout.addWidget(self.token_input)
        
        # Sync button
        self.sync_button = QPushButton("🔄 Sync Conversations")
        self.sync_button.clicked.connect(self.sync_conversations)
        toolbar_layout.addWidget(self.sync_button)
        
        # Headless checkbox
        self.headless_checkbox = QCheckBox("Headless Mode")
        toolbar_layout.addWidget(self.headless_checkbox)
        
        layout.addLayout(toolbar_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Chat list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search conversations...")
        self.search_input.textChanged.connect(self.filter_conversations)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # Chat list
        self.chat_list = ChatListWidget()
        left_layout.addWidget(self.chat_list)
        
        # Right panel: Chat viewer
        self.chat_viewer = ChatViewerWidget()
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self.chat_viewer)
        splitter.setStretchFactor(0, 1)  # Left panel
        splitter.setStretchFactor(1, 2)  # Right panel wider
        
        layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Enter your Poe token and click Sync")
        
        # Apply dark theme
        self.apply_dark_theme()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        export_action = QAction('Export Conversations', self)
        export_action.triggered.connect(self.export_conversations)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        
        config_action = QAction('Configuration', self)
        config_action.triggered.connect(self.open_settings)
        settings_menu.addAction(config_action)
    
    def setup_connections(self):
        """Set up signal connections"""
        self.chat_list.conversation_selected.connect(self.display_conversation)
    
    def load_settings(self):
        """Load saved settings"""
        # Load token (encrypted in real implementation)
        saved_token = self.settings.value("poe_token", "")
        if saved_token:
            self.token_input.setText(saved_token)
        
        # Load headless preference
        headless = self.settings.value("headless_mode", False, type=bool)
        self.headless_checkbox.setChecked(headless)
    
    def save_settings(self):
        """Save current settings"""
        self.settings.setValue("poe_token", self.token_input.text())
        self.settings.setValue("headless_mode", self.headless_checkbox.isChecked())
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-bottom: 1px solid #404040;
            }
            QMenuBar::item:selected {
                background-color: #404040;
            }
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-top: 1px solid #404040;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #3c3c3c;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
    
    def sync_conversations(self):
        """Start syncing conversations from Poe"""
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Warning", "Please enter your Poe token first.")
            return
        
        # Save settings
        self.save_settings()
        
        # Create Poe client
        headless = self.headless_checkbox.isChecked()
        self.poe_client = create_poe_client(token, headless=headless)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.sync_button.setEnabled(False)
        
        # Start sync thread
        self.sync_thread = ConversationSyncThread(self.poe_client, limit=50)
        self.sync_thread.progress_update.connect(self.update_progress)
        self.sync_thread.conversations_loaded.connect(self.on_conversations_loaded)
        self.sync_thread.error_occurred.connect(self.on_sync_error)
        self.sync_thread.start()
    
    def update_progress(self, value: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_bar.showMessage(message)
    
    def on_conversations_loaded(self, conversations: List[Conversation]):
        """Handle successful conversation loading"""
        self.conversations = conversations
        self.chat_list.populate_conversations(conversations)
        
        self.progress_bar.setVisible(False)
        self.sync_button.setEnabled(True)
        
        count = len(conversations)
        self.status_bar.showMessage(f"✅ Loaded {count} conversations")
        
        logger.info(f"Successfully loaded {count} conversations")
    
    def on_sync_error(self, error_message: str):
        """Handle sync error"""
        self.progress_bar.setVisible(False)
        self.sync_button.setEnabled(True)
        self.status_bar.showMessage(f"❌ {error_message}")
        
        QMessageBox.critical(self, "Sync Error", error_message)
        logger.error(f"Sync error: {error_message}")
    
    def display_conversation(self, conversation: Conversation):
        """Display selected conversation"""
        self.chat_viewer.display_conversation(conversation)
        self.status_bar.showMessage(f"Viewing: {conversation.title}")
    
    def filter_conversations(self, search_text: str):
        """Filter conversations based on search text"""
        if not search_text:
            self.chat_list.populate_conversations(self.conversations)
            return
        
        # Simple text search
        filtered = []
        search_lower = search_text.lower()
        
        for conv in self.conversations:
            if (search_lower in conv.title.lower() or 
                search_lower in conv.bot.lower() or
                any(search_lower in msg.content.lower() for msg in conv.messages)):
                filtered.append(conv)
        
        self.chat_list.populate_conversations(filtered)
        self.status_bar.showMessage(f"Found {len(filtered)} matching conversations")
    
    def export_conversations(self):
        """Export conversations to file"""
        if not self.conversations:
            QMessageBox.information(self, "Info", "No conversations to export. Sync first.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Conversations", "poe_conversations.json", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                import json
                export_data = []
                for conv in self.conversations:
                    export_data.append({
                        'id': conv.id,
                        'title': conv.title,
                        'bot': conv.bot,
                        'created_at': conv.created_at.isoformat(),
                        'messages': [
                            {
                                'role': msg.role,
                                'content': msg.content,
                                'timestamp': msg.timestamp.isoformat()
                            }
                            for msg in conv.messages
                        ]
                    })
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Success", f"Exported {len(self.conversations)} conversations to {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def open_settings(self):
        """Open settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet.")
    
    def closeEvent(self, event):
        """Handle application close"""
        self.save_settings()
        
        if self.poe_client:
            self.poe_client.disconnect()
        
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Poe Search")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())