#!/usr/bin/env python3
"""
Enhanced GUI Launcher for Poe Search
Fixed styling and layout issues
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def setup_logging():
    """Setup logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(project_root / "logs" / "gui.log", mode='a')
        ]
    )
    # Create logs directory if it doesn't exist
    (project_root / "logs").mkdir(exist_ok=True)

def load_poe_tokens() -> Dict[str, str]:
    """Load Poe tokens from secure config file"""
    config_file = project_root / "config" / "poe_tokens.json"
    
    try:
        if config_file.exists():
            with open(config_file, 'r') as f:
                tokens = json.load(f)
                print(f"✅ Loaded tokens from {config_file}")
                return tokens
        else:
            print(f"⚠️ Token config file not found: {config_file}")
            return {}
    except Exception as e:
        print(f"❌ Error loading tokens: {e}")
        return {}

def save_poe_tokens(tokens: Dict[str, str]) -> bool:
    """Save Poe tokens to secure config file"""
    config_file = project_root / "config" / "poe_tokens.json"
    
    try:
        # Create config directory if it doesn't exist
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print(f"✅ Saved tokens to {config_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")
        return False

def check_dependencies():
    """Check all required dependencies"""
    missing = []
    
    # Check PyQt6
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 found")
    except ImportError:
        missing.append("PyQt6")
        print("❌ PyQt6 not found")
    
    # Check Selenium (optional)
    try:
        import selenium
        print("✅ Selenium found")
    except ImportError:
        print("⚠️ Selenium not found (required for real Poe integration)")
    
    # Check our API client
    try:
        from poe_search.api.client import PoeAPIClient
        print("✅ API client found")
    except ImportError as e:
        print(f"❌ API client not found: {e}")
        missing.append("poe_search.api.client")
    
    return missing

class FullFeaturedMainWindow:
    """Complete main window with all Poe Search features"""
    
    def __init__(self):
        from PyQt6.QtWidgets import (
            QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
            QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
            QLabel, QProgressBar, QMessageBox, QStatusBar, QMenuBar, QTabWidget,
            QGroupBox, QFormLayout, QComboBox, QCheckBox, QSpinBox, QTextBrowser,
            QFileDialog, QScrollArea, QFrame, QApplication
        )
        from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QTimer
        from PyQt6.QtGui import QFont, QIcon, QAction, QPixmap
        
        # Store all PyQt6 classes
        self.QMainWindow = QMainWindow
        self.QWidget = QWidget
        self.QVBoxLayout = QVBoxLayout
        self.QHBoxLayout = QHBoxLayout
        self.QSplitter = QSplitter
        self.QListWidget = QListWidget
        self.QListWidgetItem = QListWidgetItem
        self.QTextEdit = QTextEdit
        self.QLineEdit = QLineEdit
        self.QPushButton = QPushButton
        self.QLabel = QLabel
        self.QProgressBar = QProgressBar
        self.QMessageBox = QMessageBox
        self.QStatusBar = QStatusBar
        self.QTabWidget = QTabWidget
        self.QGroupBox = QGroupBox
        self.QFormLayout = QFormLayout
        self.QComboBox = QComboBox
        self.QCheckBox = QCheckBox
        self.QSpinBox = QSpinBox
        self.QTextBrowser = QTextBrowser
        self.QFileDialog = QFileDialog
        self.QScrollArea = QScrollArea
        self.QFrame = QFrame
        self.QApplication = QApplication
        self.Qt = Qt
        self.QSettings = QSettings
        
        # Import our components
        from poe_search.api.client import PoeAPIClient, Conversation, Message
        self.PoeAPIClient = PoeAPIClient
        self.Conversation = Conversation
        self.Message = Message
        
        self.poe_client = None
        self.conversations = []
        self.current_conversation = None
        self.loaded_tokens = {}
        
    def create_window(self):
        """Create the complete main window"""
        self.window = self.QMainWindow()
        self.window.setWindowTitle("🔍 Poe Search - Advanced AI Conversation Manager")
        self.window.setGeometry(50, 50, 1400, 900)
        self.window.setMinimumSize(1200, 800)
        
        # Load tokens from config file
        self.loaded_tokens = load_poe_tokens()
        
        # Apply comprehensive styling FIRST
        self.apply_advanced_styling()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main widget and layout
        main_widget = self.QWidget()
        self.window.setCentralWidget(main_widget)
        main_layout = self.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Header section
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create tabbed interface
        self.tab_widget = self.QTabWidget()
        self.tab_widget.setTabPosition(self.QTabWidget.TabPosition.North)
        main_layout.addWidget(self.tab_widget)
        
        # Tab 1: Main conversation browser
        self.create_conversation_tab()
        
        # Tab 2: Advanced search
        self.create_search_tab()
        
        # Tab 3: Analytics dashboard
        self.create_analytics_tab()
        
        # Tab 4: Settings and configuration
        self.create_settings_tab()
        
        # Status bar
        self.status_bar = self.QStatusBar()
        self.window.setStatusBar(self.status_bar)
        
        # Set initial status based on token availability
        if self.loaded_tokens.get('p-b'):
            self.status_bar.showMessage("🔑 Token loaded from config - Ready to sync!")
        else:
            self.status_bar.showMessage("🚀 Ready - Configure your Poe token to begin")
        
        return self.window
    
    def create_header(self):
        """Create the application header"""
        header_frame = self.QFrame()
        header_frame.setFixedHeight(100)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4, stop:1 #106ebe);
                border-radius: 12px;
                margin: 5px;
            }
        """)
        
        header_layout = self.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 20, 25, 20)
        header_layout.setSpacing(20)
        
        # Logo and title section
        title_section = self.QWidget()
        title_layout = self.QVBoxLayout(title_section)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        
        title_label = self.QLabel("🔍 Poe Search")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                background: transparent;
                margin: 0;
                padding: 0;
            }
        """)
        title_layout.addWidget(title_label)
        
        subtitle_label = self.QLabel("Advanced AI Conversation Manager")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                background: transparent;
                margin: 0;
                padding: 0;
            }
        """)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(title_section)
        header_layout.addStretch()
        
        # Stats section
        stats_section = self.QWidget()
        stats_layout = self.QVBoxLayout(stats_section)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(5)
        stats_layout.setAlignment(self.Qt.AlignmentFlag.AlignRight)
        
        self.stats_label = self.QLabel("📊 0 conversations loaded")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                margin: 0;
                padding: 0;
            }
        """)
        stats_layout.addWidget(self.stats_label)
        
        # Show token status in header
        token_status = "🔑 Token loaded" if self.loaded_tokens.get('p-b') else "⚪ No token"
        self.status_label = self.QLabel(token_status)
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                background: transparent;
                margin: 0;
                padding: 0;
            }
        """)
        stats_layout.addWidget(self.status_label)
        
        header_layout.addWidget(stats_section)
        
        return header_frame
    
    def create_conversation_tab(self):
        """Create the main conversation viewing tab"""
        conv_widget = self.QWidget()
        self.tab_widget.addTab(conv_widget, "💬 Conversations")
        
        layout = self.QVBoxLayout(conv_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Connection toolbar
        toolbar = self.create_connection_toolbar()
        layout.addWidget(toolbar)
        
        # Progress bar
        self.progress_bar = self.QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(25)
        layout.addWidget(self.progress_bar)
        
        # Main content area
        content_splitter = self.QSplitter(self.Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(8)
        
        # Left panel: conversation list
        left_panel = self.create_conversation_list_panel()
        left_panel.setMinimumWidth(400)
        content_splitter.addWidget(left_panel)
        
        # Right panel: message viewer
        right_panel = self.create_message_viewer_panel()
        right_panel.setMinimumWidth(600)
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 2)
        content_splitter.setSizes([450, 750])
        
        layout.addWidget(content_splitter)
    
    def create_connection_toolbar(self):
        """Create connection and sync toolbar"""
        toolbar_group = self.QGroupBox("🔗 Connection & Sync")
        toolbar_group.setMaximumHeight(200)
        toolbar_layout = self.QFormLayout(toolbar_group)
        toolbar_layout.setSpacing(10)
        toolbar_layout.setContentsMargins(20, 25, 20, 20)
        
        # Token source selection
        token_source_layout = self.QHBoxLayout()
        self.token_source_combo = self.QComboBox()
        self.token_source_combo.addItem("📁 Use Config File")
        self.token_source_combo.addItem("✏️ Manual Entry")
        self.token_source_combo.setFixedHeight(35)
        self.token_source_combo.currentTextChanged.connect(self.on_token_source_changed)
        token_source_layout.addWidget(self.token_source_combo)
        token_source_layout.addStretch()
        
        toolbar_layout.addRow("🔑 Token Source:", token_source_layout)
        
        # Token input (initially hidden if config file has token)
        token_input_layout = self.QHBoxLayout()
        self.token_input = self.QLineEdit()
        self.token_input.setEchoMode(self.QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText("Enter your Poe p-b cookie token...")
        self.token_input.setFixedHeight(35)
        token_input_layout.addWidget(self.token_input)
        
        show_token_btn = self.QPushButton("👁️")
        show_token_btn.setFixedSize(40, 35)
        show_token_btn.clicked.connect(self.toggle_token_visibility)
        token_input_layout.addWidget(show_token_btn)
        
        self.token_input_row = self.QWidget()
        self.token_input_row.setLayout(token_input_layout)
        toolbar_layout.addRow("🔐 Manual Token:", self.token_input_row)
        
        # Token status display
        self.token_status_label = self.QLabel()
        self.update_token_status_display()
        toolbar_layout.addRow("📊 Token Status:", self.token_status_label)
        
        # Control buttons
        controls_layout = self.QHBoxLayout()
        controls_layout.setSpacing(10)
        
        self.sync_button = self.QPushButton("🔄 Sync Conversations")
        self.sync_button.setFixedHeight(40)
        self.sync_button.clicked.connect(self.sync_conversations)
        controls_layout.addWidget(self.sync_button)
        
        self.test_connection_btn = self.QPushButton("🧪 Test Connection")
        self.test_connection_btn.setFixedHeight(40)
        self.test_connection_btn.clicked.connect(self.test_connection)
        controls_layout.addWidget(self.test_connection_btn)
        
        self.save_token_btn = self.QPushButton("💾 Save Token")
        self.save_token_btn.setFixedHeight(40)
        self.save_token_btn.clicked.connect(self.save_current_token)
        controls_layout.addWidget(self.save_token_btn)
        
        self.headless_checkbox = self.QCheckBox("Headless Browser")
        self.headless_checkbox.setChecked(True)
        controls_layout.addWidget(self.headless_checkbox)
        
        controls_layout.addStretch()
        
        toolbar_layout.addRow("🎛️ Controls:", controls_layout)
        
        # Set initial visibility based on whether we have a config token
        self.on_token_source_changed()
        
        return toolbar_group
    
    def update_token_status_display(self):
        """Update the token status display"""
        if self.loaded_tokens.get('p-b'):
            masked_token = self.loaded_tokens['p-b'][:8] + "..." + self.loaded_tokens['p-b'][-8:]
            status_text = f"✅ Config: {masked_token}"
            self.token_status_label.setText(status_text)
            self.token_status_label.setStyleSheet("color: #00b294; font-weight: bold; font-size: 13px;")
        else:
            self.token_status_label.setText("❌ No token found in config")
            self.token_status_label.setStyleSheet("color: #d13438; font-weight: bold; font-size: 13px;")
    
    def on_token_source_changed(self):
        """Handle token source selection change"""
        source = self.token_source_combo.currentText()
        
        if "Config File" in source:
            # Hide manual input if we have a config token
            self.token_input_row.setVisible(not bool(self.loaded_tokens.get('p-b')))
            if self.loaded_tokens.get('p-b'):
                self.status_label.setText("🔑 Using config token")
        else:
            # Show manual input
            self.token_input_row.setVisible(True)
            self.status_label.setText("✏️ Manual entry mode")
    
    def get_current_token(self) -> str:
        """Get the current token based on selected source"""
        source = self.token_source_combo.currentText()
        
        if "Config File" in source and self.loaded_tokens.get('p-b'):
            return self.loaded_tokens['p-b']
        else:
            return self.token_input.text().strip()
    
    def save_current_token(self):
        """Save current manual token to config file"""
        token = self.token_input.text().strip()
        if not token:
            self.QMessageBox.warning(self.window, "Warning", "Please enter a token first.")
            return
        
        # Update the loaded tokens
        self.loaded_tokens['p-b'] = token
        
        # Save to file
        if save_poe_tokens(self.loaded_tokens):
            self.QMessageBox.information(self.window, "Token Saved", 
                "✅ Token saved to config file successfully!")
            self.update_token_status_display()
            self.status_label.setText("🔑 Token saved to config")
        else:
            self.QMessageBox.warning(self.window, "Save Error", 
                "❌ Failed to save token to config file.")
    
    def create_conversation_list_panel(self):
        """Create the conversation list with search and filters"""
        panel_widget = self.QWidget()
        panel_layout = self.QVBoxLayout(panel_widget)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(15)
        
        # Search and filter section
        search_group = self.QGroupBox("🔍 Search & Filter")
        search_group.setMaximumHeight(200)
        search_layout = self.QFormLayout(search_group)
        search_layout.setSpacing(10)
        search_layout.setContentsMargins(15, 25, 15, 15)
        
        # Search input
        self.search_input = self.QLineEdit()
        self.search_input.setPlaceholderText("Search conversations...")
        self.search_input.setFixedHeight(35)
        self.search_input.textChanged.connect(self.filter_conversations)
        search_layout.addRow("🔎 Search:", self.search_input)
        
        # Bot filter
        self.bot_filter = self.QComboBox()
        self.bot_filter.addItem("All Bots")
        self.bot_filter.setFixedHeight(35)
        self.bot_filter.currentTextChanged.connect(self.filter_conversations)
        search_layout.addRow("🤖 Bot:", self.bot_filter)
        
        # Date filter
        self.date_filter = self.QComboBox()
        self.date_filter.addItems(["All Time", "Today", "This Week", "This Month", "Last 3 Months"])
        self.date_filter.setFixedHeight(35)
        self.date_filter.currentTextChanged.connect(self.filter_conversations)
        search_layout.addRow("📅 Date:", self.date_filter)
        
        panel_layout.addWidget(search_group)
        
        # Conversation list
        list_group = self.QGroupBox("💬 Conversations")
        list_layout = self.QVBoxLayout(list_group)
        list_layout.setContentsMargins(15, 25, 15, 15)
        list_layout.setSpacing(10)
        
        self.conversation_list = self.QListWidget()
        self.conversation_list.setAlternatingRowColors(True)
        self.conversation_list.itemClicked.connect(self.on_conversation_selected)
        list_layout.addWidget(self.conversation_list)
        
        # List stats
        self.list_stats = self.QLabel("📊 0 conversations")
        self.list_stats.setStyleSheet("color: #888; font-size: 13px; padding: 5px;")
        list_layout.addWidget(self.list_stats)
        
        panel_layout.addWidget(list_group)
        
        return panel_widget
    
    def create_message_viewer_panel(self):
        """Create the message viewing panel"""
        panel_widget = self.QWidget()
        panel_layout = self.QVBoxLayout(panel_widget)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(15)
        
        # Conversation header
        self.conv_header = self.QLabel("Select a conversation to view messages")
        self.conv_header.setFixedHeight(60)
        self.conv_header.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #0078d4;
                padding: 15px 20px;
                background-color: #2a2a2a;
                border-radius: 10px;
                border: 1px solid #404040;
            }
        """)
        panel_layout.addWidget(self.conv_header)
        
        # Message viewer
        self.message_viewer = self.QTextBrowser()
        self.message_viewer.setOpenExternalLinks(True)
        panel_layout.addWidget(self.message_viewer)
        
        # Action buttons
        actions_layout = self.QHBoxLayout()
        actions_layout.setSpacing(10)
        
        self.export_conv_btn = self.QPushButton("📄 Export Conversation")
        self.export_conv_btn.setFixedHeight(40)
        self.export_conv_btn.clicked.connect(self.export_current_conversation)
        self.export_conv_btn.setEnabled(False)
        actions_layout.addWidget(self.export_conv_btn)
        
        self.copy_conv_btn = self.QPushButton("📋 Copy to Clipboard")
        self.copy_conv_btn.setFixedHeight(40)
        self.copy_conv_btn.clicked.connect(self.copy_conversation)
        self.copy_conv_btn.setEnabled(False)
        actions_layout.addWidget(self.copy_conv_btn)
        
        actions_layout.addStretch()
        
        panel_layout.addLayout(actions_layout)
        
        return panel_widget
    
    def create_search_tab(self):
        """Create advanced search tab"""
        search_widget = self.QWidget()
        self.tab_widget.addTab(search_widget, "🔍 Advanced Search")
        
        layout = self.QVBoxLayout(search_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Advanced search form
        search_form_group = self.QGroupBox("🔍 Advanced Search Options")
        search_form_layout = self.QFormLayout(search_form_group)
        search_form_layout.setSpacing(10)
        search_form_layout.setContentsMargins(20, 25, 20, 20)
        
        # Search query
        self.advanced_search_input = self.QLineEdit()
        self.advanced_search_input.setPlaceholderText("Enter search query...")
        self.advanced_search_input.setFixedHeight(35)
        search_form_layout.addRow("🔎 Query:", self.advanced_search_input)
        
        # Search options
        search_options_layout = self.QHBoxLayout()
        search_options_layout.setSpacing(15)
        
        self.regex_checkbox = self.QCheckBox("Use Regex")
        search_options_layout.addWidget(self.regex_checkbox)
        
        self.case_sensitive_checkbox = self.QCheckBox("Case Sensitive")
        search_options_layout.addWidget(self.case_sensitive_checkbox)
        
        self.whole_word_checkbox = self.QCheckBox("Whole Words Only")
        search_options_layout.addWidget(self.whole_word_checkbox)
        
        search_options_layout.addStretch()
        
        search_form_layout.addRow("⚙️ Options:", search_options_layout)
        
        # Search button
        search_btn = self.QPushButton("🔍 Search")
        search_btn.setFixedHeight(40)
        search_btn.clicked.connect(self.perform_advanced_search)
        search_form_layout.addRow("", search_btn)
        
        layout.addWidget(search_form_group)
        
        # Results area
        results_group = self.QGroupBox("📋 Search Results")
        results_layout = self.QVBoxLayout(results_group)
        results_layout.setContentsMargins(20, 25, 20, 20)
        
        self.search_results_list = self.QListWidget()
        self.search_results_list.itemClicked.connect(self.on_search_result_selected)
        results_layout.addWidget(self.search_results_list)
        
        layout.addWidget(results_group)
    
    def create_analytics_tab(self):
        """Create analytics dashboard tab"""
        analytics_widget = self.QWidget()
        self.tab_widget.addTab(analytics_widget, "📊 Analytics")
        
        layout = self.QVBoxLayout(analytics_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Analytics overview
        overview_group = self.QGroupBox("📈 Analytics Overview")
        overview_layout = self.QFormLayout(overview_group)
        overview_layout.setSpacing(10)
        overview_layout.setContentsMargins(20, 25, 20, 20)
        
        self.total_conversations_label = self.QLabel("0")
        self.total_conversations_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #0078d4;")
        overview_layout.addRow("💬 Total Conversations:", self.total_conversations_label)
        
        self.total_messages_label = self.QLabel("0")
        self.total_messages_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #0078d4;")
        overview_layout.addRow("📝 Total Messages:", self.total_messages_label)
        
        self.unique_bots_label = self.QLabel("0")
        self.unique_bots_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #0078d4;")
        overview_layout.addRow("🤖 Unique Bots:", self.unique_bots_label)
        
        self.avg_messages_per_conv_label = self.QLabel("0")
        self.avg_messages_per_conv_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #0078d4;")
        overview_layout.addRow("📊 Avg Messages/Conv:", self.avg_messages_per_conv_label)
        
        layout.addWidget(overview_group)
        
        # Bot usage stats
        bot_stats_group = self.QGroupBox("🤖 Bot Usage Statistics")
        bot_stats_layout = self.QVBoxLayout(bot_stats_group)
        bot_stats_layout.setContentsMargins(20, 25, 20, 20)
        bot_stats_layout.setSpacing(10)
        
        self.bot_stats_list = self.QListWidget()
        bot_stats_layout.addWidget(self.bot_stats_list)
        
        refresh_analytics_btn = self.QPushButton("🔄 Refresh Analytics")
        refresh_analytics_btn.setFixedHeight(40)
        refresh_analytics_btn.clicked.connect(self.update_analytics)
        bot_stats_layout.addWidget(refresh_analytics_btn)
        
        layout.addWidget(bot_stats_group)
        
        layout.addStretch()
    
    def create_settings_tab(self):
        """Create settings and configuration tab"""
        settings_widget = self.QWidget()
        self.tab_widget.addTab(settings_widget, "⚙️ Settings")
        
        layout = self.QVBoxLayout(settings_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Token configuration
        token_group = self.QGroupBox("🔑 Token Configuration")
        token_layout = self.QVBoxLayout(token_group)
        token_layout.setContentsMargins(20, 25, 20, 20)
        token_layout.setSpacing(15)
        
        # Current token status
        current_token_layout = self.QFormLayout()
        current_token_layout.setSpacing(10)
        
        self.config_token_display = self.QLabel()
        self.update_config_token_display()
        current_token_layout.addRow("📁 Config File Token:", self.config_token_display)
        
        token_layout.addLayout(current_token_layout)
        
        # Token management buttons
        token_buttons_layout = self.QHBoxLayout()
        token_buttons_layout.setSpacing(10)
        
        reload_token_btn = self.QPushButton("🔄 Reload from Config")
        reload_token_btn.setFixedHeight(40)
        reload_token_btn.clicked.connect(self.reload_tokens_from_config)
        token_buttons_layout.addWidget(reload_token_btn)
        
        clear_token_btn = self.QPushButton("🗑️ Clear Config Token")
        clear_token_btn.setFixedHeight(40)
        clear_token_btn.clicked.connect(self.clear_config_token)
        token_buttons_layout.addWidget(clear_token_btn)
        
        token_buttons_layout.addStretch()
        token_layout.addLayout(token_buttons_layout)
        
        instructions = self.QLabel("""
        📋 How to get your Poe token:
        
        1. 🌐 Visit poe.com and log into your account
        2. 🔧 Open Developer Tools (F12 or right-click → Inspect)
        3. 📱 Go to Application tab → Cookies → poe.com
        4. 📋 Find the 'p-b' cookie and copy its value
        5. 🔐 Paste it in the token field above and click "Save Token"
        
        ⚠️ Your token is automatically saved to config/poe_tokens.json (not in git)
        """)
        instructions.setStyleSheet("""
            QLabel {
                font-size: 14px; 
                padding: 20px; 
                color: #ccc; 
                background-color: #2a2a2a; 
                border-radius: 8px; 
                border: 1px solid #404040;
                line-height: 1.5;
            }
        """)
        token_layout.addWidget(instructions)
        
        layout.addWidget(token_group)
        
        # App settings
        app_group = self.QGroupBox("🎛️ Application Settings")
        app_layout = self.QFormLayout(app_group)
        app_layout.setSpacing(10)
        app_layout.setContentsMargins(20, 25, 20, 20)
        
        self.auto_sync_checkbox = self.QCheckBox("Auto-sync on startup")
        app_layout.addRow("🔄 Sync:", self.auto_sync_checkbox)
        
        self.theme_combo = self.QComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme", "Auto"])
        self.theme_combo.setFixedHeight(35)
        app_layout.addRow("🎨 Theme:", self.theme_combo)
        
        self.max_conversations_spin = self.QSpinBox()
        self.max_conversations_spin.setRange(10, 1000)
        self.max_conversations_spin.setValue(100)
        self.max_conversations_spin.setFixedHeight(35)
        app_layout.addRow("📊 Max Conversations:", self.max_conversations_spin)
        
        layout.addWidget(app_group)
        layout.addStretch()
    
    def update_config_token_display(self):
        """Update the config token display in settings"""
        if self.loaded_tokens.get('p-b'):
            masked_token = self.loaded_tokens['p-b'][:12] + "..." + self.loaded_tokens['p-b'][-12:]
            self.config_token_display.setText(f"✅ {masked_token}")
            self.config_token_display.setStyleSheet("color: #00b294; font-weight: bold; font-size: 14px;")
        else:
            self.config_token_display.setText("❌ No token in config file")
            self.config_token_display.setStyleSheet("color: #d13438; font-size: 14px;")
    
    def reload_tokens_from_config(self):
        """Reload tokens from config file"""
        self.loaded_tokens = load_poe_tokens()
        self.update_token_status_display()
        self.update_config_token_display()
        
        if self.loaded_tokens.get('p-b'):
            self.QMessageBox.information(self.window, "Token Reloaded", 
                "✅ Token reloaded from config file successfully!")
            self.status_label.setText("🔑 Token reloaded")
        else:
            self.QMessageBox.warning(self.window, "No Token", 
                "⚠️ No token found in config file.")
    
    def clear_config_token(self):
        """Clear token from config file"""
        reply = self.QMessageBox.question(self.window, "Clear Token", 
            "Are you sure you want to clear the token from the config file?",
            self.QMessageBox.StandardButton.Yes | self.QMessageBox.StandardButton.No)
        
        if reply == self.QMessageBox.StandardButton.Yes:
            self.loaded_tokens = {}
            if save_poe_tokens(self.loaded_tokens):
                self.update_token_status_display()
                self.update_config_token_display()
                self.QMessageBox.information(self.window, "Token Cleared", 
                    "✅ Token cleared from config file.")
                self.status_label.setText("🔴 Token cleared")
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.window.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        sync_action = file_menu.addAction('🔄 &Sync Conversations')
        sync_action.triggered.connect(self.sync_conversations)
        
        file_menu.addSeparator()
        
        export_action = file_menu.addAction('📄 &Export All...')
        export_action.triggered.connect(self.export_all_conversations)
        
        import_action = file_menu.addAction('📥 &Import...')
        import_action.triggered.connect(self.import_conversations)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('❌ E&xit')
        exit_action.triggered.connect(self.window.close)
        
        # Token menu
        token_menu = menubar.addMenu('🔑 &Token')
        
        reload_token_action = token_menu.addAction('🔄 &Reload from Config')
        reload_token_action.triggered.connect(self.reload_tokens_from_config)
        
        save_token_action = token_menu.addAction('💾 &Save Current Token')
        save_token_action.triggered.connect(self.save_current_token)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        refresh_action = view_menu.addAction('🔄 &Refresh')
        refresh_action.triggered.connect(self.refresh_view)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = help_menu.addAction('ℹ️ &About')
        about_action.triggered.connect(self.show_about)
    
    def apply_advanced_styling(self):
        """Apply comprehensive dark theme styling with better layout"""
        self.window.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            
            /* General Widgets */
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 2px solid #404040;
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 5px;
            }
            
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 15px 25px;
                margin-right: 3px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
            
            /* Group Boxes */
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 10px;
                margin-top: 1ex;
                padding-top: 20px;
                background-color: #2a2a2a;
                font-size: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #0078d4;
                font-weight: bold;
                font-size: 15px;
            }
            
            /* Input Fields */
            QLineEdit, QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                min-height: 15px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #0078d4;
                background-color: #404040;
            }
            
            QLineEdit:hover, QComboBox:hover {
                border-color: #666666;
            }
            
            /* Spin Boxes */
            QSpinBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                min-height: 15px;
            }
            
            QSpinBox:focus {
                border-color: #0078d4;
                background-color: #404040;
            }
            
            QSpinBox:hover {
                border-color: #666666;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #106ebe;
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                background-color: #005a9e;
                transform: translateY(0px);
            }
            
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
            }
            
            /* List Widget */
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 10px;
                font-size: 14px;
                alternate-background-color: #323232;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #3a3a3a;
                margin: 2px;
                border-radius: 6px;
            }
            
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
                border-radius: 6px;
            }
            
            QListWidget::item:hover {
                background-color: #404040;
                border-radius: 6px;
            }
            
            /* Text Browser */
            QTextBrowser {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 10px;
                padding: 20px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #2a2a2a;
                color: #ffffff;
                font-size: 13px;
            }
            
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 6px;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #2a2a2a;
                color: #ffffff;
                border-top: 2px solid #404040;
                padding: 8px;
                font-size: 13px;
            }
            
            /* Menu Bar */
            QMenuBar {
                background-color: #2a2a2a;
                color: #ffffff;
                border-bottom: 2px solid #404040;
                padding: 5px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 10px 15px;
                border-radius: 5px;
            }
            
            QMenuBar::item:selected {
                background-color: #0078d4;
                border-radius: 5px;
            }
            
            /* Checkboxes */
            QCheckBox {
                spacing: 10px;
                font-size: 14px;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #3c3c3c;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
                image: none;
            }
            
            QCheckBox::indicator:hover {
                border-color: #666666;
            }
            
            /* Splitter */
            QSplitter::handle {
                background-color: #404040;
                border-radius: 4px;
            }
            
            QSplitter::handle:horizontal {
                width: 8px;
            }
            
            QSplitter::handle:vertical {
                height: 8px;
            }
            
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
            
            /* Form Layout */
            QFormLayout QLabel {
                font-weight: bold;
                color: #cccccc;
                font-size: 14px;
            }
        """)
    
    # Event handlers (keeping the same functionality)
    def toggle_token_visibility(self):
        """Toggle token visibility"""
        if self.token_input.echoMode() == self.QLineEdit.EchoMode.Password:
            self.token_input.setEchoMode(self.QLineEdit.EchoMode.Normal)
        else:
            self.token_input.setEchoMode(self.QLineEdit.EchoMode.Password)
    
    def test_connection(self):
        """Test connection to Poe"""
        token = self.get_current_token()
        if not token:
            self.QMessageBox.warning(self.window, "Warning", "Please configure a Poe token first.")
            return
        
        try:
            # Test client creation
            client = self.PoeAPIClient(token=token, headless=True)
            self.QMessageBox.information(self.window, "Test Successful", 
                "✅ Connection test successful!\n\nReady to sync conversations.")
            self.status_label.setText("🟢 Connection OK")
        except Exception as e:
            self.QMessageBox.warning(self.window, "Connection Error", 
                f"❌ Connection test failed:\n\n{str(e)}")
            self.status_label.setText("🔴 Connection failed")
    
    def sync_conversations(self):
        """Sync conversations from Poe"""
        token = self.get_current_token()
        if not token:
            self.QMessageBox.warning(self.window, "Warning", "Please configure a Poe token first.")
            return
        
        try:
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.sync_button.setEnabled(False)
            self.sync_button.setText("🔄 Syncing...")
            
            # Create client and get conversations
            self.poe_client = self.PoeAPIClient(token=token, headless=self.headless_checkbox.isChecked())
            
            # Get real conversations from Poe.com
            max_conversations = self.max_conversations_spin.value()
            conversations = self.poe_client.get_conversations(max_conversations)
            self.conversations = conversations
            
            # Update UI
            self.populate_conversation_list()
            self.update_bot_filter()
            self.update_stats()
            self.update_analytics()
            
            # Hide progress
            self.progress_bar.setVisible(False)
            self.sync_button.setEnabled(True)
            self.sync_button.setText("🔄 Sync Conversations")
            
            token_source = "config file" if "Config File" in self.token_source_combo.currentText() else "manual entry"
            self.status_bar.showMessage(f"✅ Successfully loaded {len(conversations)} conversations using {token_source}")
            self.status_label.setText("🟢 Connected")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.sync_button.setEnabled(True)
            self.sync_button.setText("🔄 Sync Conversations")
            self.QMessageBox.critical(self.window, "Sync Error", f"Failed to sync conversations:\n\n{str(e)}")
            self.status_label.setText("🔴 Sync failed")
    
    def populate_conversation_list(self):
        """Populate the conversation list"""
        self.conversation_list.clear()
        
        for conv in self.conversations:
            item = self.QListWidgetItem()
            
            # Format conversation preview
            title = conv.title[:60] + "..." if len(conv.title) > 60 else conv.title
            subtitle = f"🤖 {conv.bot} • 💬 {len(conv.messages)} messages • 📅 {conv.created_at.strftime('%Y-%m-%d %H:%M')}"
            
            # Add preview of first message
            first_msg = conv.messages[0] if conv.messages else None
            preview = ""
            if first_msg:
                preview = first_msg.content[:100] + "..." if len(first_msg.content) > 100 else first_msg.content
                preview = f"\n💭 {preview}"
            
            item.setText(f"📝 {title}\n{subtitle}{preview}")
            item.setData(self.Qt.ItemDataRole.UserRole, conv)
            
            self.conversation_list.addItem(item)
    
    def update_bot_filter(self):
        """Update bot filter dropdown"""
        current_selection = self.bot_filter.currentText()
        bots = set(conv.bot for conv in self.conversations)
        
        self.bot_filter.clear()
        self.bot_filter.addItem("All Bots")
        for bot in sorted(bots):
            self.bot_filter.addItem(f"🤖 {bot}")
        
        # Restore selection if possible
        if current_selection in [self.bot_filter.itemText(i) for i in range(self.bot_filter.count())]:
            self.bot_filter.setCurrentText(current_selection)
    
    def update_stats(self):
        """Update statistics display"""
        count = len(self.conversations)
        bots = len(set(conv.bot for conv in self.conversations))
        self.stats_label.setText(f"📊 {count} conversations • 🤖 {bots} bots")
        self.list_stats.setText(f"📊 Showing {self.conversation_list.count()} of {count} conversations")
    
    def update_analytics(self):
        """Update analytics dashboard"""
        if not self.conversations:
            return
        
        total_conversations = len(self.conversations)
        total_messages = sum(len(conv.messages) for conv in self.conversations)
        unique_bots = len(set(conv.bot for conv in self.conversations))
        avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
        
        self.total_conversations_label.setText(str(total_conversations))
        self.total_messages_label.setText(str(total_messages))
        self.unique_bots_label.setText(str(unique_bots))
        self.avg_messages_per_conv_label.setText(f"{avg_messages:.1f}")
        
        # Update bot stats
        bot_stats = {}
        for conv in self.conversations:
            bot = conv.bot
            if bot not in bot_stats:
                bot_stats[bot] = {'conversations': 0, 'messages': 0}
            bot_stats[bot]['conversations'] += 1
            bot_stats[bot]['messages'] += len(conv.messages)
        
        self.bot_stats_list.clear()
        for bot, stats in sorted(bot_stats.items(), key=lambda x: x[1]['conversations'], reverse=True):
            item_text = f"🤖 {bot}: {stats['conversations']} conversations, {stats['messages']} messages"
            self.bot_stats_list.addItem(item_text)
    
    def filter_conversations(self):
        """Filter conversations based on search criteria"""
        # For now, just update the list display
        self.populate_conversation_list()
    
    def perform_advanced_search(self):
        """Perform advanced search"""
        query = self.advanced_search_input.text().strip()
        if not query:
            self.QMessageBox.information(self.window, "Search", "Please enter a search query.")
            return
        
        # Simple search implementation
        results = []
        for conv in self.conversations:
            if query.lower() in conv.title.lower():
                results.append(conv)
            else:
                for msg in conv.messages:
                    if query.lower() in msg.content.lower():
                        results.append(conv)
                        break
        
        # Update search results
        self.search_results_list.clear()
        for conv in results:
            item = self.QListWidgetItem()
            item.setText(f"📝 {conv.title} (🤖 {conv.bot})")
            item.setData(self.Qt.ItemDataRole.UserRole, conv)
            self.search_results_list.addItem(item)
        
        self.status_bar.showMessage(f"🔍 Found {len(results)} matching conversations")
    
    def on_search_result_selected(self, item):
        """Handle search result selection"""
        conversation = item.data(self.Qt.ItemDataRole.UserRole)
        if conversation:
            # Switch to conversations tab and display the conversation
            self.tab_widget.setCurrentIndex(0)
            self.current_conversation = conversation
            self.display_conversation(conversation)
    
    def on_conversation_selected(self, item):
        """Handle conversation selection"""
        conversation = item.data(self.Qt.ItemDataRole.UserRole)
        if conversation:
            self.current_conversation = conversation
            self.display_conversation(conversation)
            self.export_conv_btn.setEnabled(True)
            self.copy_conv_btn.setEnabled(True)
    
    def display_conversation(self, conversation):
        """Display conversation in the message viewer"""
        if not conversation:
            return
        
        # Update header
        self.conv_header.setText(f"💬 {conversation.title}")
        
        # Build HTML content
        html = f"""
        <div style="margin-bottom: 25px; padding: 25px; background-color: #2a2a2a; border-radius: 15px; border: 2px solid #404040;">
            <h2 style="color: #0078d4; margin: 0 0 15px 0; font-size: 28px; font-weight: bold;">📝 {conversation.title}</h2>
            <div style="color: #aaa; font-size: 16px; margin-bottom: 15px; line-height: 1.5;">
                <span style="color: #0078d4; font-weight: bold;">🤖 Bot:</span> {conversation.bot} •
                <span style="color: #0078d4; font-weight: bold;">💬 Messages:</span> {len(conversation.messages)} •
                <span style="color: #0078d4; font-weight: bold;">📅 Created:</span> {conversation.created_at.strftime('%Y-%m-%d at %H:%M')}
            </div>
        </div>
        """
        
        # Add messages
        for i, message in enumerate(conversation.messages):
            role_color = "#0078d4" if message.role == "user" else "#00b294"
            role_icon = "👤" if message.role == "user" else "🤖"
            role_name = "You" if message.role == "user" else (message.bot_name or "Assistant")
            
            html += f"""
            <div style="margin-bottom: 25px; padding: 25px; border-left: 5px solid {role_color}; 
                        background-color: #252525; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                <div style="font-weight: bold; color: {role_color}; margin-bottom: 15px; font-size: 18px;">
                    {role_icon} {role_name} • 🕒 {message.timestamp.strftime('%H:%M:%S')}
                </div>
                <div style="white-space: pre-wrap; line-height: 1.7; font-size: 15px; color: #ffffff;">
                    {message.content}
                </div>
            </div>
            """
        
        self.message_viewer.setHtml(html)
        self.status_bar.showMessage(f"📖 Viewing: {conversation.title}")
    
    def export_current_conversation(self):
        """Export current conversation"""
        if not self.current_conversation:
            return
        
        filename, _ = self.QFileDialog.getSaveFileName(
            self.window, "Export Conversation", 
            f"{self.current_conversation.title}.json",
            "JSON Files (*.json);;Markdown Files (*.md);;Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                import json
                data = self.current_conversation.to_dict()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.QMessageBox.information(self.window, "Export Successful", 
                    f"✅ Conversation exported to:\n{filename}")
            except Exception as e:
                self.QMessageBox.critical(self.window, "Export Error", f"❌ Export failed:\n\n{str(e)}")
    
    def copy_conversation(self):
        """Copy conversation to clipboard"""
        if not self.current_conversation:
            return
        
        # Create text version
        text = f"# {self.current_conversation.title}\n\n"
        text += f"**Bot:** {self.current_conversation.bot}\n"
        text += f"**Created:** {self.current_conversation.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        for message in self.current_conversation.messages:
            role_name = "**You:**" if message.role == "user" else f"**{message.bot_name or 'Assistant'}:**"
            text += f"{role_name} {message.content}\n\n"
        
        # Copy to clipboard
        clipboard = self.QApplication.clipboard()
        clipboard.setText(text)
        
        self.status_bar.showMessage("📋 Conversation copied to clipboard")
    
    def export_all_conversations(self):
        """Export all conversations"""
        if not self.conversations:
            self.QMessageBox.information(self.window, "Info", "No conversations to export.")
            return
        
        filename, _ = self.QFileDialog.getSaveFileName(
            self.window, "Export All Conversations", "all_conversations.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                import json
                data = [conv.to_dict() for conv in self.conversations]
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.QMessageBox.information(self.window, "Export Successful", 
                    f"✅ {len(self.conversations)} conversations exported to:\n{filename}")
            except Exception as e:
                self.QMessageBox.critical(self.window, "Export Error", f"❌ Export failed:\n\n{str(e)}")
    
    def import_conversations(self):
        """Import conversations from file"""
        filename, _ = self.QFileDialog.getOpenFileName(
            self.window, "Import Conversations", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                import json
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert to conversation objects
                imported_conversations = [self.Conversation.from_dict(conv_data) for conv_data in data]
                self.conversations.extend(imported_conversations)
                
                # Update UI
                self.populate_conversation_list()
                self.update_bot_filter()
                self.update_stats()
                self.update_analytics()
                
                self.QMessageBox.information(self.window, "Import Successful", 
                    f"✅ {len(imported_conversations)} conversations imported successfully!")
                
            except Exception as e:
                self.QMessageBox.critical(self.window, "Import Error", f"❌ Import failed:\n\n{str(e)}")
    
    def refresh_view(self):
        """Refresh the current view"""
        self.populate_conversation_list()
        self.update_stats()
        self.update_analytics()
        self.status_bar.showMessage("🔄 View refreshed")
    
    def show_about(self):
        """Show about dialog"""
        self.QMessageBox.about(self.window, "About Poe Search", 
            """🔍 <b>Poe Search - Advanced AI Conversation Manager</b><br><br>
            
            <b>Version:</b> 1.0.0<br>
            <b>Description:</b> A comprehensive tool for searching, organizing, and managing your Poe.com conversations<br><br>
            
            <b>Features:</b><br>
            • 💬 Real Poe.com conversation syncing<br>
            • 🔍 Advanced search and filtering<br>
            • 📊 Analytics and insights<br>
            • 📄 Export/Import capabilities<br>
            • 🔑 Secure token management<br>
            • 🌙 Modern dark theme interface<br><br>
            
            <b>Built with:</b> PyQt6, Python, Selenium, and ❤️<br>
            <b>Repository:</b> github.com/hkevin01/poe-search
            """)

def main():
    """Enhanced main function with full GUI"""
    try:
        print("🚀 Starting Enhanced Poe Search GUI...")
        setup_logging()
        
        # Check dependencies
        missing = check_dependencies()
        if missing:
            print(f"❌ Missing dependencies: {missing}")
            print("Install with: pip install " + " ".join(missing))
            return 1
        
        # Load tokens early to show status
        tokens = load_poe_tokens()
        if tokens.get('p-b'):
            print(f"🔑 Found token in config: {tokens['p-b'][:8]}...{tokens['p-b'][-8:]}")
        else:
            print("⚠️ No token found in config file")
        
        # Import PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Poe Search")
        app.setApplicationDisplayName("Poe Search - Advanced AI Conversation Manager")
        app.setApplicationVersion("1.0.0")
        
        # Set application font
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        print("✅ Creating enhanced GUI interface...")
        
        # Create and show main window
        main_window_factory = FullFeaturedMainWindow()
        window = main_window_factory.create_window()
        window.show()
        
        print("🎉 Enhanced GUI launched successfully!")
        print("💡 Features available:")
        print("   • 🔑 Secure token loading from config file")
        print("   • 💬 Real Poe.com conversation syncing")
        print("   • 📝 Message viewer with rich formatting")  
        print("   • 📤 Export/Import capabilities")
        print("   • 📊 Analytics dashboard")
        print("   • 🔍 Advanced search functionality")
        print("   • ⚙️ Complete settings management")
        print("   • 🌙 Improved dark theme interface")
        
        if tokens.get('p-b'):
            print("✅ Ready to sync conversations immediately!")
        else:
            print("ℹ️ Add your token via the GUI to get started")
        
        # Start event loop
        return app.exec()
        
    except Exception as e:
        print(f"❌ Failed to launch enhanced GUI: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())