# src/poe_search/gui/__init__.py
"""
Poe Search GUI Module
Modern PyQt6-based interface for managing Poe conversations
"""

import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QPushButton, QLabel, QProgressBar, QMessageBox, QStatusBar,
    QMenuBar, QFileDialog, QCheckBox, QComboBox, QTabWidget,
    QGroupBox, QFormLayout, QSpinBox, QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction, QPixmap

# Import our API client
from ..api.client import PoeApiClient, create_poe_client, Conversation, Message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncWorker(QThread):
    """Generic async worker for background tasks"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, coro_func, *args, **kwargs):
        super().__init__()
        self.coro_func = coro_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.coro_func(*self.args, **self.kwargs))
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class ConversationListWidget(QListWidget):
    """Enhanced conversation list with search and filtering"""
    
    conversation_selected = pyqtSignal(Conversation)
    
    def __init__(self):
        super().__init__()
        self.conversations = []
        self.filtered_conversations = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 8px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #3a3a3a;
                margin: 1px;
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
        """Populate with conversations"""
        self.conversations = conversations
        self.filtered_conversations = conversations.copy()
        self._refresh_display()
    
    def filter_conversations(self, query: str, bot_filter: str = "All"):
        """Filter conversations by query and bot"""
        if not query and bot_filter == "All":
            self.filtered_conversations = self.conversations.copy()
        else:
            self.filtered_conversations = []
            query_lower = query.lower()
            
            for conv in self.conversations:
                # Bot filter
                if bot_filter != "All" and conv.bot != bot_filter:
                    continue
                
                # Text search
                if query:
                    if (query_lower in conv.title.lower() or
                        query_lower in conv.bot.lower() or
                        any(query_lower in msg.content.lower() for msg in conv.messages)):
                        self.filtered_conversations.append(conv)
                else:
                    self.filtered_conversations.append(conv)
        
        self._refresh_display()
    
    def _refresh_display(self):
        """Refresh the display with filtered conversations"""
        self.clear()
        
        for conv in self.filtered_conversations:
            # Create rich display text
            title = conv.title[:50] + "..." if len(conv.title) > 50 else conv.title
            subtitle = f"{conv.bot} • {len(conv.messages)} messages • {conv.created_at.strftime('%Y-%m-%d')}"
            
            item = QListWidgetItem()
            item.setText(f"{title}\n{subtitle}")
            item.setData(Qt.ItemDataRole.UserRole, conv)
            
            # Color coding by bot
            if "claude" in conv.bot.lower():
                item.setBackground(Qt.GlobalColor.darkBlue)
            elif "gpt" in conv.bot.lower():
                item.setBackground(Qt.GlobalColor.darkGreen)
            
            self.addItem(item)
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle conversation selection"""
        conversation = item.data(Qt.ItemDataRole.UserRole)
        if conversation:
            self.conversation_selected.emit(conversation)

class ConversationViewer(QTextBrowser):
    """Enhanced conversation viewer with rich formatting"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.setOpenExternalLinks(True)
        self.setStyleSheet("""
            QTextBrowser {
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
    
    def display_conversation(self, conversation: Conversation):
        """Display conversation with enhanced formatting"""
        if not conversation:
            self.setHtml("<p>Select a conversation to view messages.</p>")
            return
        
        html = self._generate_conversation_html(conversation)
        self.setHtml(html)
        self.moveCursor(self.textCursor().Start)  # Scroll to top
    
    def _generate_conversation_html(self, conversation: Conversation) -> str:
        """Generate rich HTML for conversation display"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                    line-height: 1.6;
                    color: #ffffff;
                    background-color: #1e1e1e;
                    margin: 0;
                    padding: 20px;
                }}
                .header {{
                    border-bottom: 2px solid #404040;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .title {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #0078d4;
                    margin-bottom: 10px;
                }}
                .meta {{
                    color: #888;
                    font-size: 14px;
                }}
                .message {{
                    margin-bottom: 25px;
                    padding: 20px;
                    border-radius: 12px;
                    border-left: 4px solid;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }}
                .user-message {{
                    background: linear-gradient(135deg, #2a2a2a, #323232);
                    border-left-color: #0078d4;
                }}
                .assistant-message {{
                    background: linear-gradient(135deg, #252525, #2d2d2d);
                    border-left-color: #00b294;
                }}
                .message-header {{
                    font-weight: bold;
                    margin-bottom: 12px;
                    font-size: 15px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .user-header {{ color: #0078d4; }}
                .assistant-header {{ color: #00b294; }}
                .message-content {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .timestamp {{
                    color: #666;
                    font-size: 12px;
                }}
                .stats {{
                    background-color: #2a2a2a;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">{self._escape_html(conversation.title)}</div>
                <div class="meta">
                    Bot: <strong>{conversation.bot}</strong> • 
                    Messages: <strong>{len(conversation.messages)}</strong> • 
                    Created: <strong>{conversation.created_at.strftime('%Y-%m-%d %H:%M')}</strong>
                </div>
            </div>
            
            <div class="stats">
                📊 <strong>Conversation Statistics:</strong><br>
                Total Messages: {len(conversation.messages)} • 
                User Messages: {len([m for m in conversation.messages if m.role == 'user'])} • 
                Assistant Responses: {len([m for m in conversation.messages if m.role == 'assistant'])} • 
                Total Characters: {sum(len(m.content) for m in conversation.messages):,}
            </div>
        """
        
        # Add messages
        for i, message in enumerate(conversation.messages):
            role_class = "user" if message.role == "user" else "assistant"
            role_display = "You" if message.role == "user" else (message.bot_name or "Assistant")
            
            html += f"""
            <div class="message {role_class}-message">
                <div class="message-header {role_class}-header">
                    <span>🎯 {role_display}</span>
                    <span class="timestamp">{message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="message-content">{self._escape_html(message.content)}</div>
            </div>
            """
        
        html += "</body></html>"
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        import html
        return html.escape(text)

class PoeSearchMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.poe_client = None
        self.conversations = []
        self.settings = QSettings("PoeSearch", "MainApp")
        self.worker = None
        
        self.setup_ui()
        self.setup_connections()
        self.load_settings()
        self.apply_theme()
    
    def setup_ui(self):
        """Set up the complete user interface"""
        self.setWindowTitle("Poe Search - Advanced Chat Manager")
        self.setGeometry(100, 100, 1600, 900)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Main chat view tab
        self.create_chat_view_tab()
        
        # Settings tab
        self.create_settings_tab()
        
        # Analytics tab (placeholder)
        self.create_analytics_tab()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Configure your Poe token and click Sync")
    
    def create_chat_view_tab(self):
        """Create the main chat viewing interface"""
        chat_widget = QWidget()
        self.tab_widget.addTab(chat_widget, "💬 Conversations")
        
        layout = QVBoxLayout(chat_widget)
        
        # Top toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Search + Conversation List
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Conversation Viewer
        self.conversation_viewer = ConversationViewer()
        splitter.addWidget(self.conversation_viewer)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
    
    def create_toolbar(self):
        """Create the top toolbar"""
        toolbar_widget = QGroupBox("Connection & Sync")
        toolbar_layout = QFormLayout(toolbar_widget)
        
        # Token input
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText("Enter your Poe p-b cookie value...")
        toolbar_layout.addRow("Poe Token:", self.token_input)
        
        # Controls row
        controls_layout = QHBoxLayout()
        
        self.sync_button = QPushButton("🔄 Sync Conversations")
        self.sync_button.clicked.connect(self.sync_conversations)
        controls_layout.addWidget(self.sync_button)
        
        self.headless_checkbox = QCheckBox("Headless Mode")
        controls_layout.addWidget(self.headless_checkbox)
        
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setRange(10, 500)
        self.limit_spinbox.setValue(100)
        controls_layout.addWidget(QLabel("Limit:"))
        controls_layout.addWidget(self.limit_spinbox)
        
        toolbar_layout.addRow("Controls:", controls_layout)
        
        return toolbar_widget
    
    def create_left_panel(self):
        """Create the left panel with search and conversation list"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Search section
        search_group = QGroupBox("🔍 Search & Filter")
        search_layout = QFormLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search conversations...")
        self.search_input.textChanged.connect(self.filter_conversations)
        search_layout.addRow("Search:", self.search_input)
        
        self.bot_filter = QComboBox()
        self.bot_filter.addItem("All")
        self.bot_filter.currentTextChanged.connect(self.filter_conversations)
        search_layout.addRow("Bot:", self.bot_filter)
        
        left_layout.addWidget(search_group)
        
        # Conversation list
        self.conversation_list = ConversationListWidget()
        left_layout.addWidget(self.conversation_list)
        
        return left_widget
    
    def create_settings_tab(self):
        """Create settings configuration tab"""
        settings_widget = QWidget()
        self.tab_widget.addTab(settings_widget, "⚙️ Settings")
        
        layout = QVBoxLayout(settings_widget)
        
        # Connection settings
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QFormLayout(conn_group)
        
        self.rate_limit_spinbox = QSpinBox()
        self.rate_limit_spinbox.setRange(1, 10)
        self.rate_limit_spinbox.setValue(2)
        conn_layout.addRow("Rate Limit (seconds):", self.rate_limit_spinbox)
        
        layout.addWidget(conn_group)
        layout.addStretch()
    
    def create_analytics_tab(self):
        """Create analytics and insights tab"""
        analytics_widget = QWidget()
        self.tab_widget.addTab(analytics_widget, "📊 Analytics")
        
        layout = QVBoxLayout(analytics_widget)
        
        info_label = QLabel("📊 Analytics and insights will be displayed here.\n\n"
                           "Coming soon:\n"
                           "• Conversation trends\n"
                           "• Bot usage statistics\n"
                           "• Message frequency analysis\n"
                           "• Export reports")
        info_label.setStyleSheet("font-size: 14px; padding: 20px;")
        layout.addWidget(info_label)
        layout.addStretch()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        export_action = QAction('&Export Conversations...', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_conversations)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        refresh_action = QAction('&Refresh Conversations', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.sync_conversations)
        tools_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_connections(self):
        """Set up signal connections"""
        self.conversation_list.conversation_selected.connect(self.display_conversation)
    
    def load_settings(self):
        """Load saved settings"""
        token = self.settings.value("poe_token", "")
        if token:
            self.token_input.setText(token)
        
        headless = self.settings.value("headless_mode", False, type=bool)
        self.headless_checkbox.setChecked(headless)
        
        limit = self.settings.value("conversation_limit", 100, type=int)
        self.limit_spinbox.setValue(limit)
    
    def save_settings(self):
        """Save current settings"""
        self.settings.setValue("poe_token", self.token_input.text())
        self.settings.setValue("headless_mode", self.headless_checkbox.isChecked())
        self.settings.setValue("conversation_limit", self.limit_spinbox.value())
    
    def apply_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #2a2a2a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
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
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
    
    def sync_conversations(self):
        """Start conversation sync"""
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Warning", "Please enter your Poe token first.")
            return
        
        self.save_settings()
        
        # Create client
        headless = self.headless_checkbox.isChecked()
        rate_limit = self.rate_limit_spinbox.value()
        self.poe_client = create_poe_client(token, headless=headless, rate_limit=rate_limit)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.sync_button.setEnabled(False)
        self.status_bar.showMessage("🔄 Connecting to Poe...")
        
        # Start worker
        limit = self.limit_spinbox.value()
        self.worker = AsyncWorker(self._sync_conversations_async, limit)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_sync_finished)
        self.worker.error.connect(self.on_sync_error)
        self.worker.start()
    
    async def _sync_conversations_async(self, limit: int):
        """Async conversation sync"""
        # Connect
        connected = await self.poe_client.connect()
        if not connected:
            raise Exception("Failed to connect to Poe")
        
        # Fetch conversations
        conversations = await self.poe_client.get_conversations(limit)
        
        # Fetch messages for first few conversations
        for i, conv in enumerate(conversations[:10]):  # Limit for performance
            if conv.messages:  # Skip if already has messages
                continue
                
            messages = await self.poe_client.get_conversation_messages(conv.id)
            conv.messages = messages
        
        return conversations
    
    def update_progress(self, value: int, message: str):
        """Update progress display"""
        if value >= 0:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(value)
        self.status_bar.showMessage(message)
    
    def on_sync_finished(self, conversations: List[Conversation]):
        """Handle successful sync"""
        self.conversations = conversations
        self.conversation_list.populate_conversations(conversations)
        
        # Update bot filter
        bots = set(conv.bot for conv in conversations)
        self.bot_filter.clear()
        self.bot_filter.addItem("All")
        for bot in sorted(bots):
            self.bot_filter.addItem(bot)
        
        self.progress_bar.setVisible(False)
        self.sync_button.setEnabled(True)
        
        count = len(conversations)
        self.status_bar.showMessage(f"✅ Loaded {count} conversations")
        
        logger.info(f"Successfully synced {count} conversations")
    
    def on_sync_error(self, error_message: str):
        """Handle sync error"""
        self.progress_bar.setVisible(False)
        self.sync_button.setEnabled(True)
        self.status_bar.showMessage(f"❌ Sync failed: {error_message}")
        
        QMessageBox.critical(self, "Sync Error", f"Failed to sync conversations:\n\n{error_message}")
        logger.error(f"Sync error: {error_message}")
    
    def display_conversation(self, conversation: Conversation):
        """Display selected conversation"""
        self.conversation_viewer.display_conversation(conversation)
        self.status_bar.showMessage(f"Viewing: {conversation.title}")
    
    def filter_conversations(self):
        """Filter conversations based on search criteria"""
        query = self.search_input.text()
        bot_filter = self.bot_filter.currentText()
        self.conversation_list.filter_conversations(query, bot_filter)
        
        count = len(self.conversation_list.filtered_conversations)
        self.status_bar.showMessage(f"Showing {count} conversations")
    
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
                export_data = [conv.to_dict() for conv in self.conversations]
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(
                    self, "Success", 
                    f"Exported {len(self.conversations)} conversations to {filename}"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Poe Search",
            "<h3>Poe Search</h3>"
            "<p>Advanced conversation manager for Poe.com</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>🔍 Search and filter conversations</li>"
            "<li>💬 View conversation history</li>"
            "<li>📊 Analytics and insights</li>"
            "<li>📄 Export capabilities</li>"
            "</ul>"
            "<p><b>Version:</b> 1.0.0</p>"
        )
    
    def closeEvent(self, event):
        """Handle application close"""
        self.save_settings()
        
        if self.poe_client:
            self.poe_client.disconnect()
        
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Poe Search")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = PoeSearchMainWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())