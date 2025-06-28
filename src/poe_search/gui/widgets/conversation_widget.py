"""Conversation viewer widget for displaying conversation details."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QTextCharFormat
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class MessageWidget(QFrame):
    """Widget for displaying a single message."""
    
    def __init__(self, message: Dict[str, Any], parent=None):
        """Initialize message widget."""
        super().__init__(parent)
        
        self.message = message
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the message UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Message header
        header_layout = QHBoxLayout()
        
        # Sender
        sender = self.message.get("sender", "Unknown")
        sender_label = QLabel(sender)
        sender_label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                font-size: 13px;
                color: #0078d4;
                padding: 2px 0;
            }
        """)
        header_layout.addWidget(sender_label)
        
        # Timestamp
        timestamp = self.message.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_text = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_text = timestamp
        else:
            time_text = "Unknown time"
        
        time_label = QLabel(time_text)
        time_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #888888;
                padding: 2px 0;
            }
        """)
        header_layout.addWidget(time_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Message content
        content = self.message.get("content", "")
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                line-height: 1.4;
                padding: 4px 0;
                color: #ffffff;
            }
        """)
        layout.addWidget(content_label)
        
        # Style the frame based on sender
        if sender.lower() in ["user", "human"]:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2b2b2b;
                    border: 1px solid #404040;
                    border-radius: 8px;
                    margin: 2px 0;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #323232;
                    border: 1px solid #505050;
                    border-radius: 8px;
                    margin: 2px 0;
                }
            """)


class ConversationWidget(QWidget):
    """Widget for viewing conversation details and messages."""
    
    # Signals
    category_changed = pyqtSignal(str, str)  # conversation_id, category
    export_requested = pyqtSignal(str)       # conversation_id
    
    def __init__(self, parent=None):
        """Initialize the conversation widget."""
        super().__init__(parent)
        
        self.current_conversation = None
        self.messages = []
        self.client = None
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Conversation info header
        info_group = self.create_conversation_info()
        layout.addWidget(info_group)
        
        # Messages area
        messages_group = self.create_messages_area()
        layout.addWidget(messages_group)
        
        # Show empty state initially
        self.show_empty_state()
        
    def create_conversation_info(self) -> QGroupBox:
        """Create conversation information header."""
        group = QGroupBox("Conversation Details")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                padding-top: 12px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Title and metadata row
        title_row = QHBoxLayout()
        
        self.title_label = QLabel("No conversation selected")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                padding: 4px 0;
            }
        """)
        title_row.addWidget(self.title_label)
        title_row.addStretch()
        
        # Category selector
        title_row.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Uncategorized", "Technical", "Medical", "Spiritual",
            "Political", "Educational", "Creative", "Personal", "Other"
        ])
        self.category_combo.setMinimumWidth(120)
        title_row.addWidget(self.category_combo)
        
        layout.addLayout(title_row)
        
        # Metadata row
        metadata_row = QHBoxLayout()
        
        self.bot_label = QLabel("Bot: -")
        self.bot_label.setStyleSheet("color: #888888; font-size: 12px;")
        metadata_row.addWidget(self.bot_label)
        
        self.message_count_label = QLabel("Messages: -")
        self.message_count_label.setStyleSheet("color: #888888; font-size: 12px;")
        metadata_row.addWidget(self.message_count_label)
        
        self.created_label = QLabel("Created: -")
        self.created_label.setStyleSheet("color: #888888; font-size: 12px;")
        metadata_row.addWidget(self.created_label)
        
        self.updated_label = QLabel("Updated: -")
        self.updated_label.setStyleSheet("color: #888888; font-size: 12px;")
        metadata_row.addWidget(self.updated_label)
        
        metadata_row.addStretch()
        
        # Action buttons
        self.export_button = QPushButton("Export")
        self.export_button.setMinimumHeight(32)
        self.export_button.setMinimumWidth(80)
        metadata_row.addWidget(self.export_button)
        
        layout.addLayout(metadata_row)
        
        return group
    
    def create_messages_area(self) -> QGroupBox:
        """Create the messages display area."""
        group = QGroupBox("Messages")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                padding-top: 12px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Messages scroll area
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Messages container widget
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()  # Push messages to top
        
        self.messages_scroll.setWidget(self.messages_container)
        layout.addWidget(self.messages_scroll)
        
        # Style the scroll area
        self.messages_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404040;
                border-radius: 8px;
                background-color: #2b2b2b;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        return group
    
    def setup_connections(self):
        """Set up signal connections."""
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        self.export_button.clicked.connect(self.on_export_requested)
    
    def show_empty_state(self):
        """Show empty state when no conversation is selected."""
        self.title_label.setText("No conversation selected")
        self.bot_label.setText("Bot: -")
        self.message_count_label.setText("Messages: -")
        self.created_label.setText("Created: -")
        self.updated_label.setText("Updated: -")
        self.category_combo.setCurrentText("Uncategorized")
        self.category_combo.setEnabled(False)
        self.export_button.setEnabled(False)
        
        # Clear messages
        self.clear_messages()
        
        # Show placeholder
        placeholder = QLabel("Select a conversation from the search results to view its details and messages.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
                padding: 40px;
            }
        """)
        self.messages_layout.addWidget(placeholder)
    
    def load_conversation(self, conversation: Dict[str, Any]):
        """Load and display a conversation."""
        self.current_conversation = conversation
        
        # Update header information
        title = conversation.get("title", "Untitled Conversation")
        self.title_label.setText(title)
        
        bot = conversation.get("bot", "Unknown")
        self.bot_label.setText(f"Bot: {bot}")
        
        message_count = conversation.get("message_count", 0)
        self.message_count_label.setText(f"Messages: {message_count}")
        
        # Format dates
        created_at = conversation.get("created_at", "")
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_text = dt.strftime("%Y-%m-%d %H:%M")
            except:
                created_text = created_at
        else:
            created_text = "Unknown"
        self.created_label.setText(f"Created: {created_text}")
        
        updated_at = conversation.get("updated_at", "")
        if updated_at:
            try:
                dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                updated_text = dt.strftime("%Y-%m-%d %H:%M")
            except:
                updated_text = updated_at
        else:
            updated_text = "Unknown"
        self.updated_label.setText(f"Updated: {updated_text}")
        
        # Set category
        category = conversation.get("category", "Uncategorized")
        self.category_combo.setCurrentText(category)
        self.category_combo.setEnabled(True)
        self.export_button.setEnabled(True)
        
        # Load messages
        messages = conversation.get("messages", [])
        self.load_messages(messages)
    
    def load_messages(self, messages: List[Dict[str, Any]]):
        """Load and display messages."""
        self.messages = messages
        self.clear_messages()
        
        if not messages:
            placeholder = QLabel("No messages in this conversation.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    padding: 20px;
                }
            """)
            self.messages_layout.addWidget(placeholder)
            return
        
        # Add message widgets
        for message in messages:
            message_widget = MessageWidget(message)
            self.messages_layout.addWidget(message_widget)
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def clear_messages(self):
        """Clear all message widgets."""
        while self.messages_layout.count() > 1:  # Keep the stretch item
            child = self.messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the messages."""
        scrollbar = self.messages_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_category_changed(self, category: str):
        """Handle category change."""
        if self.current_conversation:
            conversation_id = self.current_conversation.get("id")
            if conversation_id:
                self.category_changed.emit(conversation_id, category)
    
    def on_export_requested(self):
        """Handle export request."""
        if self.current_conversation:
            conversation_id = self.current_conversation.get("id")
            if conversation_id:
                self.export_requested.emit(conversation_id)
    
    def get_current_conversation_id(self) -> Optional[str]:
        """Get the current conversation ID."""
        if self.current_conversation:
            return self.current_conversation.get("id")
        return None

    def set_client(self, client):
        """Set the Poe Search client.
        
        Args:
            client: PoeSearchClient instance
        """
        self.client = client

    def refresh_data(self):
        """Refresh the conversation data."""
        if self.current_conversation and self.client:
            try:
                # Reload the current conversation from the database
                conversation_id = self.current_conversation.get("id")
                if conversation_id:
                    conversation = self.client.database.get_conversation(conversation_id)
                    if conversation:
                        self.load_conversation(conversation)
            except Exception as e:
                logger.error(f"Failed to refresh conversation data: {e}")
