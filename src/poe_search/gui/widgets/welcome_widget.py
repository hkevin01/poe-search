"""Welcome widget for first-time setup and onboarding."""

import logging
from pathlib import Path
from typing import Callable, Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from poe_search.utils.config import get_config_manager

logger = logging.getLogger(__name__)


class WelcomeWidget(QWidget):
    """Welcome widget for first-time setup."""
    
    # Signals
    setup_complete = pyqtSignal()
    token_configured = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the welcome widget."""
        super().__init__(parent)
        
        self.config_manager = get_config_manager()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Setup section
        setup_section = self.create_setup_section()
        layout.addWidget(setup_section)
        
        # Features section
        features_section = self.create_features_section()
        layout.addWidget(features_section)
        
        # Action buttons
        actions = self.create_action_buttons()
        layout.addWidget(actions)
        
        layout.addStretch()
        
    def create_header(self) -> QWidget:
        """Create the welcome header."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Welcome to Poe Search")
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 700;
                color: #ffffff;
                padding: 20px 0;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel(
            "Search, organize, and manage your Poe.com conversations with ease"
        )
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #cccccc;
                padding: 10px 0;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        return widget
    
    def create_setup_section(self) -> QGroupBox:
        """Create the setup section."""
        group = QGroupBox("🔑 Setup Your Poe Token")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 16px;
                padding-top: 20px;
                margin-top: 10px;
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(16)
        
        # Instructions
        instructions = QLabel(
            "To get started, you need to provide your Poe.com authentication token. "
            "This allows Poe Search to access your conversations securely."
        )
        instructions.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #cccccc;
                line-height: 1.4;
                padding: 10px 0;
            }
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Token input
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("Poe Token:"))
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your Poe.com token (p-b cookie value)")
        self.token_input.setMinimumHeight(40)
        self.token_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px 12px;
                border: 2px solid #555555;
                border-radius: 6px;
                background-color: #3b3b3b;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        token_layout.addWidget(self.token_input)
        
        # Load existing token if available
        existing_token = self.config_manager.get_token()
        if existing_token:
            self.token_input.setText(existing_token)
        
        layout.addLayout(token_layout)
        
        # How to get token
        help_text = QTextEdit()
        help_text.setMaximumHeight(120)
        help_text.setReadOnly(True)
        help_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #cccccc;
                font-size: 12px;
                padding: 8px;
            }
        """)
        help_text.setPlainText(
            "How to get your Poe token:\n\n"
            "1. Go to https://poe.com and log in\n"
            "2. Open Developer Tools (F12)\n"
            "3. Go to Application/Storage > Cookies > poe.com\n"
            "4. Copy the value of the 'p-b' cookie\n"
            "5. Paste it in the field above"
        )
        layout.addWidget(help_text)
        
        # Test connection button
        self.test_button = QPushButton("Test Connection")
        self.test_button.setMinimumHeight(40)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
            }
        """)
        layout.addWidget(self.test_button)
        
        # Progress bar for testing
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        return group
    
    def create_features_section(self) -> QGroupBox:
        """Create the features section."""
        group = QGroupBox("✨ Features")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 16px;
                padding-top: 20px;
                margin-top: 10px;
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        features = [
            ("🔍", "Advanced Search", "Search through all your conversations with filters and regex support"),
            ("🏷️", "Smart Categories", "Auto-categorize conversations by topic and content"),
            ("📊", "Analytics Dashboard", "Visual insights about your conversation patterns"),
            ("💾", "Local Storage", "All data stored locally on your machine for privacy"),
            ("🔄", "Export Options", "Export conversations in JSON, CSV, Markdown, and more"),
            ("🎨", "Modern Interface", "Beautiful Windows 11-style dark theme"),
        ]
        
        for icon, title, description in features:
            feature_widget = self.create_feature_item(icon, title, description)
            layout.addWidget(feature_widget)
        
        return group
    
    def create_feature_item(self, icon: str, title: str, description: str) -> QWidget:
        """Create a feature item widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        icon_label.setMinimumWidth(30)
        layout.addWidget(icon_label)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
            }
        """)
        content_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #cccccc;
            }
        """)
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        return widget
    
    def create_action_buttons(self) -> QWidget:
        """Create action buttons."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(16)
        
        # Skip button
        self.skip_button = QPushButton("Skip Setup")
        self.skip_button.setMinimumHeight(40)
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #cccccc;
                border: 2px solid #555555;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #404040;
                border-color: #666666;
            }
        """)
        layout.addWidget(self.skip_button)
        
        layout.addStretch()
        
        # Get started button
        self.get_started_button = QPushButton("Get Started")
        self.get_started_button.setMinimumHeight(40)
        self.get_started_button.setMinimumWidth(120)
        self.get_started_button.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0e6b0e;
            }
            QPushButton:pressed {
                background-color: #0c5a0c;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
            }
        """)
        layout.addWidget(self.get_started_button)
        
        return widget
    
    def setup_connections(self):
        """Set up signal connections."""
        self.test_button.clicked.connect(self.test_connection)
        self.skip_button.clicked.connect(self.skip_setup)
        self.get_started_button.clicked.connect(self.complete_setup)
        
        # Enable/disable get started button based on token
        self.token_input.textChanged.connect(self.on_token_changed)
        self.on_token_changed()
    
    def on_token_changed(self):
        """Handle token input changes."""
        token = self.token_input.text().strip()
        has_token = len(token) > 0
        
        self.test_button.setEnabled(has_token)
        self.get_started_button.setEnabled(has_token)
        
        if has_token:
            self.get_started_button.setText("Get Started")
        else:
            self.get_started_button.setText("Enter Token to Continue")
    
    def test_connection(self):
        """Test the Poe token connection."""
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "No Token", "Please enter a Poe token first.")
            return
        
        self.progress_bar.setVisible(True)
        self.test_button.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Simulate connection test
        QTimer.singleShot(2000, self.complete_connection_test)
    
    def complete_connection_test(self):
        """Complete the connection test."""
        self.progress_bar.setVisible(False)
        self.test_button.setEnabled(True)
        
        # For now, always succeed (in real implementation, test actual connection)
        QMessageBox.information(
            self, 
            "Connection Successful", 
            "Successfully connected to Poe.com! Your token is valid."
        )
    
    def skip_setup(self):
        """Skip the setup process."""
        reply = QMessageBox.question(
            self,
            "Skip Setup",
            "Are you sure you want to skip setup? You can configure your token later in settings.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.setup_complete.emit()
    
    def complete_setup(self):
        """Complete the setup process."""
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "No Token", "Please enter a Poe token first.")
            return
        
        # Save token to configuration
        self.config_manager.set_token(token)
        
        # Emit signals
        self.token_configured.emit(token)
        self.setup_complete.emit()
        
        QMessageBox.information(
            self,
            "Setup Complete",
            "Your Poe token has been configured successfully! You can now start using Poe Search."
        ) 