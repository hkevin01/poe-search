#!/usr/bin/env python3
"""
Enhanced GUI Launcher for Poe Search - Fixed Layout Version
Fixed overlapping issues with proper layout management
Author: Kevin Hao
Version: 1.2.0
License: MIT
"""

import sys
import os
import json
import asyncio
import logging
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def setup_logging():
    """Setup comprehensive logging for the application."""
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
    """Load Poe authentication tokens from secure config file."""
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
    """Save Poe authentication tokens to secure config file."""
    config_file = project_root / "config" / "poe_tokens.json"
    
    try:
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        print(f"✅ Saved tokens to {config_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")
        return False

def check_dependencies():
    """Check all required dependencies for the application."""
    missing = []
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 found")
    except ImportError:
        missing.append("PyQt6")
        print("❌ PyQt6 not found")
    
    try:
        import selenium
        print("✅ Selenium found")
    except ImportError:
        missing.append("selenium")
        print("❌ Selenium not found")
    
    try:
        from poe_search.api.browser_client import PoeApiClient
        print("✅ Enhanced browser client found")
    except ImportError as e:
        print(f"❌ Enhanced browser client not found: {e}")
        missing.append("poe_search.api.browser_client")
    
    return missing


class ConversationSyncThread:
    """Background thread for syncing conversations without blocking the GUI."""
    
    def __init__(self, token: str, lat_token: str = None, headless: bool = True, limit: int = 50):
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class SyncWorker(QThread):
            progress = pyqtSignal(str, int)
            finished = pyqtSignal(list)
            error = pyqtSignal(str)
            
            def __init__(self, token, lat_token, headless, limit):
                super().__init__()
                self.token = token
                self.lat_token = lat_token
                self.headless = headless
                self.limit = limit
                
            def run(self):
                try:
                    from poe_search.api.browser_client import PoeApiClient
                    
                    client = PoeApiClient(
                        token=self.token,
                        lat_token=self.lat_token,
                        headless=self.headless
                    )
                    
                    def progress_callback(message, percentage):
                        self.progress.emit(message, percentage)
                    
                    if not client.authenticate(progress_callback):
                        self.error.emit("Authentication failed. Please check your tokens.")
                        return
                    
                    conversations = client.get_conversations(
                        limit=self.limit,
                        progress_callback=progress_callback
                    )
                    
                    detailed_conversations = []
                    total = len(conversations)
                    
                    for i, conv_info in enumerate(conversations):
                        try:
                            progress_callback(f"Loading messages {i+1}/{total}...", 80 + (i / total) * 15)
                            
                            messages = client.get_conversation_messages(
                                conv_info['id'],
                                progress_callback
                            )
                            
                            conversation = {
                                'id': conv_info['id'],
                                'title': conv_info['title'],
                                'bot': conv_info.get('bot', 'Assistant'),
                                'url': conv_info['url'],
                                'messages': messages,
                                'created_at': datetime.now() - timedelta(days=i),
                                'extracted_at': conv_info.get('extracted_at'),
                                'method': conv_info.get('method', 'browser_client')
                            }
                            
                            detailed_conversations.append(conversation)
                            
                        except Exception as e:
                            logging.warning(f"Failed to get messages for conversation {conv_info['id']}: {e}")
                            conversation = {
                                'id': conv_info['id'],
                                'title': conv_info['title'],
                                'bot': conv_info.get('bot', 'Assistant'),
                                'url': conv_info['url'],
                                'messages': [],
                                'created_at': datetime.now() - timedelta(days=i),
                                'extracted_at': conv_info.get('extracted_at'),
                                'method': conv_info.get('method', 'browser_client')
                            }
                            detailed_conversations.append(conversation)
                    
                    client.close()
                    self.finished.emit(detailed_conversations)
                    
                except Exception as e:
                    self.error.emit(str(e))
        
        self.worker = SyncWorker(token, lat_token, headless, limit)


class FixedLayoutMainWindow:
    """Main window with fixed, non-overlapping layout management."""
    
    def __init__(self):
        """Initialize the main window with proper widget management."""
        from PyQt6.QtWidgets import (
            QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
            QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
            QLabel, QProgressBar, QMessageBox, QStatusBar, QMenuBar, QTabWidget,
            QGroupBox, QFormLayout, QComboBox, QCheckBox, QSpinBox, QTextBrowser,
            QFileDialog, QScrollArea, QFrame, QApplication, QSizePolicy
        )
        from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QTimer, QSize
        from PyQt6.QtGui import QFont, QIcon, QAction, QPixmap
        
        # Store PyQt6 classes
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
        self.QSizePolicy = QSizePolicy
        self.Qt = Qt
        self.QSettings = QSettings
        self.QSize = QSize
        
        # Application state
        self.conversations = []
        self.current_conversation = None
        self.loaded_tokens = {}
        self.sync_thread = None
        self.settings = self.QSettings('PoeSearch', 'GUI')
        
    def create_window(self):
        """Create the main window with proper fixed layout."""
        self.window = self.QMainWindow()
        self.window.setWindowTitle("🔍 Poe Search - Enhanced AI Conversation Manager v1.2")
        self.window.setGeometry(100, 100, 1600, 1000)
        self.window.setMinimumSize(1400, 900)
        
        # Load tokens
        self.loaded_tokens = load_poe_tokens()
        
        # Apply styling
        self.apply_fixed_styling()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main central widget with fixed layout
        central_widget = self.QWidget()
        self.window.setCentralWidget(central_widget)
        
        # Main layout with proper spacing
        main_layout = self.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header (fixed height)
        header = self.create_fixed_header()
        main_layout.addWidget(header)
        
        # Tab widget (expandable)
        self.tab_widget = self.QTabWidget()
        self.tab_widget.setMinimumHeight(700)
        main_layout.addWidget(self.tab_widget, 1)  # Give it stretch factor
        
        # Create tabs
        self.create_conversations_tab()
        self.create_search_tab()
        self.create_analytics_tab()
        self.create_settings_tab()
        
        # Status bar (fixed height)
        self.status_bar = self.QStatusBar()
        self.status_bar.setFixedHeight(30)
        self.window.setStatusBar(self.status_bar)
        
        # Set initial status
        if self.loaded_tokens.get('p-b'):
            self.status_bar.showMessage("🔑 Token loaded - Ready to sync!")
        else:
            self.status_bar.showMessage("🚀 Configure your Poe token to begin")
        
        return self.window
    
    def create_fixed_header(self):
        """Create header with fixed dimensions."""
        header_frame = self.QFrame()
        header_frame.setFixedHeight(80)  # Fixed height
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4, stop:1 #106ebe);
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        header_layout = self.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(20)
        
        # Title section
        title_widget = self.QWidget()
        title_layout = self.QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        
        title_label = self.QLabel("🔍 Poe Search")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        title_layout.addWidget(title_label)
        
        subtitle_label = self.QLabel("Enhanced AI Conversation Manager v1.2")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
                background: transparent;
            }
        """)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(title_widget)
        header_layout.addStretch()
        
        # Stats section
        stats_widget = self.QWidget()
        stats_layout = self.QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(2)
        stats_layout.setAlignment(self.Qt.AlignmentFlag.AlignRight)
        
        self.stats_label = self.QLabel("📊 0 conversations")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        stats_layout.addWidget(self.stats_label)
        
        token_status = "🔑 Token loaded" if self.loaded_tokens.get('p-b') else "⚪ No token"
        self.status_label = self.QLabel(token_status)
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 11px;
                background: transparent;
            }
        """)
        stats_layout.addWidget(self.status_label)
        
        self.connection_status_label = self.QLabel("🔘 Not connected")
        self.connection_status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 10px;
                background: transparent;
            }
        """)
        stats_layout.addWidget(self.connection_status_label)
        
        header_layout.addWidget(stats_widget)
        
        return header_frame
    
    def create_conversations_tab(self):
        """Create conversations tab with proper layout management."""
        conv_widget = self.QWidget()
        self.tab_widget.addTab(conv_widget, "💬 Conversations")
        
        # Main layout for conversations tab
        main_layout = self.QVBoxLayout(conv_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Connection toolbar (fixed height)
        toolbar = self.create_connection_toolbar()
        main_layout.addWidget(toolbar)
        
        # Progress section (fixed height, initially hidden)
        progress_widget = self.create_progress_section()
        main_layout.addWidget(progress_widget)
        
        # Content area (expandable)
        content_splitter = self.QSplitter(self.Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(5)
        content_splitter.setMinimumHeight(400)
        
        # Left panel (conversation list)
        left_panel = self.create_conversation_list_panel()
        left_panel.setMinimumWidth(400)
        left_panel.setMaximumWidth(600)
        content_splitter.addWidget(left_panel)
        
        # Right panel (message viewer)
        right_panel = self.create_message_viewer_panel()
        right_panel.setMinimumWidth(600)
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([400, 800])
        content_splitter.setStretchFactor(0, 0)  # Left panel doesn't stretch
        content_splitter.setStretchFactor(1, 1)  # Right panel stretches
        
        main_layout.addWidget(content_splitter, 1)  # Give content area stretch factor
    
    def create_connection_toolbar(self):
        """Create connection toolbar with fixed layout."""
        toolbar_group = self.QGroupBox("🔗 Connection & Sync")
        toolbar_group.setFixedHeight(180)  # Fixed height to prevent overlap
        
        toolbar_layout = self.QVBoxLayout(toolbar_group)
        toolbar_layout.setContentsMargins(15, 20, 15, 15)
        toolbar_layout.setSpacing(8)
        
        # Row 1: Token source
        source_layout = self.QHBoxLayout()
        source_layout.addWidget(self.QLabel("Token Source:"))
        
        self.token_source_combo = self.QComboBox()
        self.token_source_combo.addItem("📁 Use Config File")
        self.token_source_combo.addItem("✏️ Manual Entry")
        self.token_source_combo.setFixedHeight(30)
        self.token_source_combo.currentTextChanged.connect(self.on_token_source_changed)
        source_layout.addWidget(self.token_source_combo)
        source_layout.addStretch()
        
        toolbar_layout.addLayout(source_layout)
        
        # Row 2: Manual token inputs (conditionally visible)
        self.token_input_widget = self.QWidget()
        token_input_layout = self.QHBoxLayout(self.token_input_widget)
        token_input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.token_input = self.QLineEdit()
        self.token_input.setEchoMode(self.QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText("p-b token...")
        self.token_input.setFixedHeight(30)
        token_input_layout.addWidget(self.token_input)
        
        self.lat_token_input = self.QLineEdit()
        self.lat_token_input.setEchoMode(self.QLineEdit.EchoMode.Password)
        self.lat_token_input.setPlaceholderText("p-lat token (optional)...")
        self.lat_token_input.setFixedHeight(30)
        token_input_layout.addWidget(self.lat_token_input)
        
        show_btn = self.QPushButton("👁️")
        show_btn.setFixedSize(30, 30)
        show_btn.clicked.connect(self.toggle_token_visibility)
        token_input_layout.addWidget(show_btn)
        
        toolbar_layout.addWidget(self.token_input_widget)
        
        # Row 3: Token status
        status_layout = self.QHBoxLayout()
        status_layout.addWidget(self.QLabel("Status:"))
        
        self.token_status_label = self.QLabel()
        self.update_token_status_display()
        status_layout.addWidget(self.token_status_label)
        status_layout.addStretch()
        
        toolbar_layout.addLayout(status_layout)
        
        # Row 4: Controls
        controls_layout = self.QHBoxLayout()
        
        self.sync_button = self.QPushButton("🚀 Enhanced Sync")
        self.sync_button.setFixedHeight(35)
        self.sync_button.clicked.connect(self.sync_conversations_enhanced)
        controls_layout.addWidget(self.sync_button)
        
        self.test_connection_btn = self.QPushButton("🧪 Test")
        self.test_connection_btn.setFixedHeight(35)
        self.test_connection_btn.clicked.connect(self.test_browser_connection)
        controls_layout.addWidget(self.test_connection_btn)
        
        self.save_token_btn = self.QPushButton("💾 Save")
        self.save_token_btn.setFixedHeight(35)
        self.save_token_btn.clicked.connect(self.save_current_tokens)
        controls_layout.addWidget(self.save_token_btn)
        
        # Browser options
        self.headless_checkbox = self.QCheckBox("Headless")
        self.headless_checkbox.setChecked(True)
        controls_layout.addWidget(self.headless_checkbox)
        
        controls_layout.addWidget(self.QLabel("Max:"))
        self.max_conversations_spin = self.QSpinBox()
        self.max_conversations_spin.setRange(5, 500)
        self.max_conversations_spin.setValue(50)
        self.max_conversations_spin.setFixedHeight(30)
        self.max_conversations_spin.setFixedWidth(60)
        controls_layout.addWidget(self.max_conversations_spin)
        
        controls_layout.addStretch()
        
        toolbar_layout.addLayout(controls_layout)
        
        # Set initial visibility
        self.on_token_source_changed()
        
        return toolbar_group
    
    def create_progress_section(self):
        """Create progress section with fixed height."""
        progress_widget = self.QWidget()
        progress_widget.setFixedHeight(60)
        
        progress_layout = self.QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(10, 5, 10, 5)
        progress_layout.setSpacing(5)
        
        self.progress_bar = self.QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_status_label = self.QLabel()
        self.progress_status_label.setStyleSheet("color: #0078d4; font-size: 12px;")
        self.progress_status_label.setVisible(False)
        progress_layout.addWidget(self.progress_status_label)
        
        progress_layout.addStretch()
        
        return progress_widget
    
    def create_conversation_list_panel(self):
        """Create conversation list panel with proper sizing."""
        panel_widget = self.QWidget()
        
        panel_layout = self.QVBoxLayout(panel_widget)
        panel_layout.setContentsMargins(5, 5, 5, 5)
        panel_layout.setSpacing(8)
        
        # Search section (fixed height)
        search_group = self.QGroupBox("🔍 Search & Filter")
        search_group.setFixedHeight(200)
        
        search_layout = self.QVBoxLayout(search_group)
        search_layout.setContentsMargins(10, 15, 10, 10)
        search_layout.setSpacing(6)
        
        # Search input
        search_input_layout = self.QHBoxLayout()
        self.search_input = self.QLineEdit()
        self.search_input.setPlaceholderText("Search conversations...")
        self.search_input.setFixedHeight(28)
        self.search_input.textChanged.connect(self.filter_conversations)
        search_input_layout.addWidget(self.search_input)
        
        clear_btn = self.QPushButton("🗑️")
        clear_btn.setFixedSize(28, 28)
        clear_btn.clicked.connect(lambda: self.search_input.clear())
        search_input_layout.addWidget(clear_btn)
        
        search_layout.addLayout(search_input_layout)
        
        # Filters in grid layout
        filter_layout = self.QVBoxLayout()
        
        # Bot filter
        bot_layout = self.QHBoxLayout()
        bot_layout.addWidget(self.QLabel("Bot:"))
        self.bot_filter = self.QComboBox()
        self.bot_filter.addItem("All Bots")
        self.bot_filter.setFixedHeight(28)
        self.bot_filter.currentTextChanged.connect(self.filter_conversations)
        bot_layout.addWidget(self.bot_filter)
        filter_layout.addLayout(bot_layout)
        
        # Date filter
        date_layout = self.QHBoxLayout()
        date_layout.addWidget(self.QLabel("Date:"))
        self.date_filter = self.QComboBox()
        self.date_filter.addItems(["All Time", "Today", "This Week", "This Month"])
        self.date_filter.setFixedHeight(28)
        self.date_filter.currentTextChanged.connect(self.filter_conversations)
        date_layout.addWidget(self.date_filter)
        filter_layout.addLayout(date_layout)
        
        # Messages filter
        msg_layout = self.QHBoxLayout()
        msg_layout.addWidget(self.QLabel("Messages:"))
        self.min_messages_spin = self.QSpinBox()
        self.min_messages_spin.setRange(0, 1000)
        self.min_messages_spin.setFixedHeight(28)
        self.min_messages_spin.setFixedWidth(60)
        msg_layout.addWidget(self.min_messages_spin)
        msg_layout.addWidget(self.QLabel("to"))
        self.max_messages_spin = self.QSpinBox()
        self.max_messages_spin.setRange(0, 1000)
        self.max_messages_spin.setValue(1000)
        self.max_messages_spin.setFixedHeight(28)
        self.max_messages_spin.setFixedWidth(60)
        msg_layout.addWidget(self.max_messages_spin)
        msg_layout.addStretch()
        filter_layout.addLayout(msg_layout)
        
        search_layout.addLayout(filter_layout)
        
        panel_layout.addWidget(search_group)
        
        # Conversation list (expandable)
        list_group = self.QGroupBox("💬 Conversations")
        list_layout = self.QVBoxLayout(list_group)
        list_layout.setContentsMargins(10, 15, 10, 10)
        list_layout.setSpacing(6)
        
        # Sort controls
        sort_layout = self.QHBoxLayout()
        sort_layout.addWidget(self.QLabel("Sort:"))
        self.sort_combo = self.QComboBox()
        self.sort_combo.addItems([
            "📅 Date (Newest)", "📅 Date (Oldest)",
            "🔤 Title (A-Z)", "💬 Messages (Most)"
        ])
        self.sort_combo.setFixedHeight(28)
        self.sort_combo.currentTextChanged.connect(self.sort_conversations)
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addStretch()
        list_layout.addLayout(sort_layout)
        
        # List widget
        self.conversation_list = self.QListWidget()
        self.conversation_list.setAlternatingRowColors(True)
        self.conversation_list.itemClicked.connect(self.on_conversation_selected)
        list_layout.addWidget(self.conversation_list)
        
        # Stats
        self.list_stats = self.QLabel("📊 0 conversations")
        self.list_stats.setStyleSheet("color: #888; font-size: 11px;")
        list_layout.addWidget(self.list_stats)
        
        panel_layout.addWidget(list_group, 1)  # Give list the stretch factor
        
        return panel_widget
    
    def create_message_viewer_panel(self):
        """Create message viewer panel with proper sizing."""
        panel_widget = self.QWidget()
        
        panel_layout = self.QVBoxLayout(panel_widget)
        panel_layout.setContentsMargins(5, 5, 5, 5)
        panel_layout.setSpacing(8)
        
        # Header (fixed height)
        header_layout = self.QHBoxLayout()
        
        self.conv_header = self.QLabel("Select a conversation to view messages")
        self.conv_header.setFixedHeight(40)
        self.conv_header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #0078d4;
                padding: 10px 15px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border: 1px solid #404040;
            }
        """)
        header_layout.addWidget(self.conv_header)
        
        self.open_browser_btn = self.QPushButton("🌐 Open")
        self.open_browser_btn.setFixedSize(80, 40)
        self.open_browser_btn.clicked.connect(self.open_conversation_in_browser)
        self.open_browser_btn.setEnabled(False)
        header_layout.addWidget(self.open_browser_btn)
        
        panel_layout.addLayout(header_layout)
        
        # Message viewer (expandable)
        viewer_group = self.QGroupBox("💬 Messages")
        viewer_layout = self.QVBoxLayout(viewer_group)
        viewer_layout.setContentsMargins(10, 15, 10, 10)
        viewer_layout.setSpacing(6)
        
        # Search within conversation
        msg_search_layout = self.QHBoxLayout()
        self.message_search_input = self.QLineEdit()
        self.message_search_input.setPlaceholderText("Search within conversation...")
        self.message_search_input.setFixedHeight(28)
        msg_search_layout.addWidget(self.message_search_input)
        
        self.copy_msg_btn = self.QPushButton("📋")
        self.copy_msg_btn.setFixedSize(28, 28)
        msg_search_layout.addWidget(self.copy_msg_btn)
        
        viewer_layout.addLayout(msg_search_layout)
        
        # Message browser
        self.message_viewer = self.QTextBrowser()
        self.message_viewer.setOpenExternalLinks(True)
        viewer_layout.addWidget(self.message_viewer)
        
        panel_layout.addWidget(viewer_group, 1)  # Give viewer the stretch factor
        
        # Action buttons (fixed height)
        actions_layout = self.QHBoxLayout()
        
        self.export_conv_btn = self.QPushButton("📄 Export")
        self.export_conv_btn.setFixedHeight(32)
        self.export_conv_btn.clicked.connect(self.export_current_conversation)
        self.export_conv_btn.setEnabled(False)
        actions_layout.addWidget(self.export_conv_btn)
        
        self.copy_conv_btn = self.QPushButton("📋 Copy")
        self.copy_conv_btn.setFixedHeight(32)
        self.copy_conv_btn.clicked.connect(self.copy_conversation)
        self.copy_conv_btn.setEnabled(False)
        actions_layout.addWidget(self.copy_conv_btn)
        
        self.analyze_conv_btn = self.QPushButton("📊 Analyze")
        self.analyze_conv_btn.setFixedHeight(32)
        self.analyze_conv_btn.clicked.connect(self.analyze_current_conversation)
        self.analyze_conv_btn.setEnabled(False)
        actions_layout.addWidget(self.analyze_conv_btn)
        
        actions_layout.addStretch()
        
        panel_layout.addLayout(actions_layout)
        
        return panel_widget
    
    def create_search_tab(self):
        """Create search tab with proper layout."""
        search_widget = self.QWidget()
        self.tab_widget.addTab(search_widget, "🔍 Advanced Search")
        
        layout = self.QVBoxLayout(search_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Search form (fixed height)
        search_form = self.QGroupBox("🔍 Search Options")
        search_form.setFixedHeight(200)
        
        form_layout = self.QVBoxLayout(search_form)
        form_layout.setContentsMargins(15, 20, 15, 15)
        form_layout.setSpacing(8)
        
        # Query input
        query_layout = self.QHBoxLayout()
        query_layout.addWidget(self.QLabel("Query:"))
        self.advanced_search_input = self.QLineEdit()
        self.advanced_search_input.setPlaceholderText("Enter search query...")
        self.advanced_search_input.setFixedHeight(30)
        query_layout.addWidget(self.advanced_search_input)
        
        syntax_btn = self.QPushButton("❓")
        syntax_btn.setFixedSize(30, 30)
        syntax_btn.clicked.connect(self.show_search_syntax_help)
        query_layout.addWidget(syntax_btn)
        
        form_layout.addLayout(query_layout)
        
        # Options
        options_layout = self.QHBoxLayout()
        self.regex_checkbox = self.QCheckBox("Regex")
        self.case_sensitive_checkbox = self.QCheckBox("Case Sensitive")
        self.whole_word_checkbox = self.QCheckBox("Whole Words")
        
        options_layout.addWidget(self.regex_checkbox)
        options_layout.addWidget(self.case_sensitive_checkbox)
        options_layout.addWidget(self.whole_word_checkbox)
        options_layout.addStretch()
        
        form_layout.addLayout(options_layout)
        
        # Scope
        scope_layout = self.QHBoxLayout()
        scope_layout.addWidget(self.QLabel("Scope:"))
        self.search_scope_combo = self.QComboBox()
        self.search_scope_combo.addItems([
            "All Conversations", "User Messages", "Assistant Messages", "Titles Only"
        ])
        self.search_scope_combo.setFixedHeight(30)
        scope_layout.addWidget(self.search_scope_combo)
        scope_layout.addStretch()
        
        form_layout.addLayout(scope_layout)
        
        # Buttons
        btn_layout = self.QHBoxLayout()
        search_btn = self.QPushButton("🔍 Search")
        search_btn.setFixedHeight(35)
        search_btn.clicked.connect(self.perform_advanced_search)
        btn_layout.addWidget(search_btn)
        
        clear_btn = self.QPushButton("🗑️ Clear")
        clear_btn.setFixedHeight(35)
        clear_btn.clicked.connect(self.clear_search_results)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        form_layout.addLayout(btn_layout)
        
        layout.addWidget(search_form)
        
        # Results (expandable)
        results_group = self.QGroupBox("📋 Search Results")
        results_layout = self.QVBoxLayout(results_group)
        results_layout.setContentsMargins(15, 20, 15, 15)
        
        self.search_results_summary = self.QLabel("No search performed yet")
        self.search_results_summary.setStyleSheet("color: #888; font-size: 12px;")
        results_layout.addWidget(self.search_results_summary)
        
        self.search_results_list = self.QListWidget()
        self.search_results_list.itemClicked.connect(self.on_search_result_selected)
        results_layout.addWidget(self.search_results_list)
        
        layout.addWidget(results_group, 1)
    
    def create_analytics_tab(self):
        """Create analytics tab with proper layout."""
        analytics_widget = self.QWidget()
        self.tab_widget.addTab(analytics_widget, "📊 Analytics")
        
        layout = self.QVBoxLayout(analytics_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Overview stats (fixed height)
        overview_group = self.QGroupBox("📈 Overview")
        overview_group.setFixedHeight(200)
        
        overview_layout = self.QVBoxLayout(overview_group)
        overview_layout.setContentsMargins(15, 20, 15, 15)
        
        # Stats grid
        stats_grid = self.QHBoxLayout()
        
        # Create stat cards
        self.total_conv_card = self.create_stat_card("💬", "Conversations", "0")
        self.total_msg_card = self.create_stat_card("📝", "Messages", "0")
        self.unique_bots_card = self.create_stat_card("🤖", "Bots", "0")
        self.avg_msg_card = self.create_stat_card("📊", "Avg/Conv", "0")
        
        stats_grid.addWidget(self.total_conv_card)
        stats_grid.addWidget(self.total_msg_card)
        stats_grid.addWidget(self.unique_bots_card)
        stats_grid.addWidget(self.avg_msg_card)
        
        overview_layout.addLayout(stats_grid)
        
        # Refresh button
        refresh_layout = self.QHBoxLayout()
        refresh_btn = self.QPushButton("🔄 Refresh Analytics")
        refresh_btn.setFixedHeight(35)
        refresh_btn.clicked.connect(self.update_analytics)
        refresh_layout.addWidget(refresh_btn)
        refresh_layout.addStretch()
        overview_layout.addLayout(refresh_layout)
        
        layout.addWidget(overview_group)
        
        # Bot stats (expandable)
        bot_stats_group = self.QGroupBox("🤖 Bot Usage")
        bot_stats_layout = self.QVBoxLayout(bot_stats_group)
        bot_stats_layout.setContentsMargins(15, 20, 15, 15)
        
        self.bot_stats_list = self.QListWidget()
        bot_stats_layout.addWidget(self.bot_stats_list)
        
        layout.addWidget(bot_stats_group, 1)
    
    def create_stat_card(self, icon: str, label: str, value: str):
        """Create a stat card widget."""
        card = self.QFrame()
        card.setFixedSize(120, 80)
        card.setFrameStyle(self.QFrame.Shape.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 6px;
                margin: 2px;
            }
        """)
        
        layout = self.QVBoxLayout(card)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(self.Qt.AlignmentFlag.AlignCenter)
        
        icon_label = self.QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px; color: #0078d4;")
        icon_label.setAlignment(self.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        value_label = self.QLabel(value)
        value_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff;")
        value_label.setAlignment(self.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        label_label = self.QLabel(label)
        label_label.setStyleSheet("font-size: 10px; color: #ccc;")
        label_label.setAlignment(self.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_label)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def create_settings_tab(self):
        """Create settings tab with proper layout."""
        settings_widget = self.QWidget()
        self.tab_widget.addTab(settings_widget, "⚙️ Settings")
        
        # Scroll area for settings
        scroll = self.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(self.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = self.QWidget()
        scroll_layout = self.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(15, 15, 15, 15)
        scroll_layout.setSpacing(15)
        
        # Token config
        token_group = self.QGroupBox("🔑 Token Configuration")
        token_layout = self.QVBoxLayout(token_group)
        token_layout.setContentsMargins(15, 20, 15, 15)
        token_layout.setSpacing(10)
        
        # Current tokens display
        current_layout = self.QVBoxLayout()
        
        self.config_token_display = self.QLabel()
        self.update_config_token_display()
        current_layout.addWidget(self.QLabel("Primary Token (p-b):"))
        current_layout.addWidget(self.config_token_display)
        
        self.config_lat_token_display = self.QLabel()
        self.update_config_lat_token_display()
        current_layout.addWidget(self.QLabel("Secondary Token (p-lat):"))
        current_layout.addWidget(self.config_lat_token_display)
        
        token_layout.addLayout(current_layout)
        
        # Token management buttons
        token_btn_layout = self.QHBoxLayout()
        
        reload_btn = self.QPushButton("🔄 Reload")
        reload_btn.setFixedHeight(35)
        reload_btn.clicked.connect(self.reload_tokens_from_config)
        token_btn_layout.addWidget(reload_btn)
        
        clear_btn = self.QPushButton("🗑️ Clear")
        clear_btn.setFixedHeight(35)
        clear_btn.clicked.connect(self.clear_config_tokens)
        token_btn_layout.addWidget(clear_btn)
        
        validate_btn = self.QPushButton("✅ Validate")
        validate_btn.setFixedHeight(35)
        validate_btn.clicked.connect(self.validate_tokens)
        token_btn_layout.addWidget(validate_btn)
        
        token_btn_layout.addStretch()
        token_layout.addLayout(token_btn_layout)
        
        scroll_layout.addWidget(token_group)
        
        # App settings
        app_group = self.QGroupBox("🎛️ Application Settings")
        app_layout = self.QVBoxLayout(app_group)
        app_layout.setContentsMargins(15, 20, 15, 15)
        app_layout.setSpacing(10)
        
        # Auto-sync
        auto_sync_layout = self.QHBoxLayout()
        self.auto_sync_checkbox = self.QCheckBox("Auto-sync on startup")
        auto_sync_layout.addWidget(self.auto_sync_checkbox)
        auto_sync_layout.addStretch()
        app_layout.addLayout(auto_sync_layout)
        
        # Theme
        theme_layout = self.QHBoxLayout()
        theme_layout.addWidget(self.QLabel("Theme:"))
        self.theme_combo = self.QComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme"])
        self.theme_combo.setFixedHeight(30)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        app_layout.addLayout(theme_layout)
        
        # Default limit
        limit_layout = self.QHBoxLayout()
        limit_layout.addWidget(self.QLabel("Default Limit:"))
        self.default_limit_spin = self.QSpinBox()
        self.default_limit_spin.setRange(10, 1000)
        self.default_limit_spin.setValue(50)
        self.default_limit_spin.setFixedHeight(30)
        limit_layout.addWidget(self.default_limit_spin)
        limit_layout.addStretch()
        app_layout.addLayout(limit_layout)
        
        scroll_layout.addWidget(app_group)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        
        settings_layout = self.QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.addWidget(scroll)
    
    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.window.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        sync_action = file_menu.addAction('🚀 &Sync')
        sync_action.setShortcut('Ctrl+S')
        sync_action.triggered.connect(self.sync_conversations_enhanced)
        
        export_action = file_menu.addAction('📄 &Export All')
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_all_conversations)
        
        file_menu.addSeparator()
        exit_action = file_menu.addAction('❌ E&xit')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.window.close)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        refresh_action = view_menu.addAction('🔄 &Refresh')
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_view)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        about_action = help_menu.addAction('ℹ️ &About')
        about_action.triggered.connect(self.show_about)

    def apply_fixed_styling(self):
        """Apply styling optimized for fixed layouts."""
        self.window.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
                border-radius: 6px;
            }
            
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                min-width: 100px;
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
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 0.5ex;
                padding-top: 15px;
                background-color: #2a2a2a;
                font-size: 13px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #0078d4;
                font-weight: bold;
                background-color: #2a2a2a;
            }
            
            /* Input Fields */
            QLineEdit, QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #0078d4;
                background-color: #404040;
            }
            
            QSpinBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
            
            QSpinBox:focus {
                border-color: #0078d4;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 60px;
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
            
            /* List Widget */
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
                font-size: 12px;
                alternate-background-color: #323232;
            }
            
            QListWidget::item {
                padding: 10px;
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
            
            /* Text Browser */
            QTextBrowser {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 15px;
                font-size: 13px;
                line-height: 1.5;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
                background-color: #2a2a2a;
                color: #ffffff;
                font-size: 11px;
            }
            
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #2a2a2a;
                color: #ffffff;
                border-top: 1px solid #404040;
                font-size: 11px;
            }
            
            /* Menu Bar */
            QMenuBar {
                background-color: #2a2a2a;
                color: #ffffff;
                border-bottom: 1px solid #404040;
                font-size: 12px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 3px;
            }
            
            QMenuBar::item:selected {
                background-color: #0078d4;
            }
            
            /* Checkboxes */
            QCheckBox {
                spacing: 8px;
                font-size: 12px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
            
            /* Splitter */
            QSplitter::handle {
                background-color: #404040;
                border-radius: 2px;
            }
            
            QSplitter::handle:horizontal {
                width: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
            
            /* Scroll Area */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #0078d4;
            }
        """)

    # Event handlers and core functionality
    
    def get_current_token(self) -> str:
        """Get the current primary token."""
        source = self.token_source_combo.currentText()
        if "Config File" in source and self.loaded_tokens.get('p-b'):
            return self.loaded_tokens['p-b']
        else:
            return self.token_input.text().strip()
    
    def get_current_lat_token(self) -> str:
        """Get the current secondary token."""
        source = self.token_source_combo.currentText()
        if "Config File" in source and self.loaded_tokens.get('p-lat'):
            return self.loaded_tokens['p-lat']
        else:
            return self.lat_token_input.text().strip()

    def on_token_source_changed(self):
        """Handle token source selection change."""
        source = self.token_source_combo.currentText()
        
        if "Config File" in source:
            # Hide manual input if we have a config token
            self.token_input_widget.setVisible(not bool(self.loaded_tokens.get('p-b')))
            if self.loaded_tokens.get('p-b'):
                self.status_label.setText("🔑 Using config tokens")
        else:
            # Show manual input
            self.token_input_widget.setVisible(True)
            self.status_label.setText("✏️ Manual entry mode")

    def update_token_status_display(self):
        """Update the token status display."""
        if self.loaded_tokens.get('p-b'):
            masked_token = self.loaded_tokens['p-b'][:8] + "..." + self.loaded_tokens['p-b'][-8:]
            has_lat = " + p-lat" if self.loaded_tokens.get('p-lat') else ""
            status_text = f"✅ {masked_token}{has_lat}"
            self.token_status_label.setText(status_text)
            self.token_status_label.setStyleSheet("color: #00b294; font-weight: bold; font-size: 11px;")
        else:
            self.token_status_label.setText("❌ No token found")
            self.token_status_label.setStyleSheet("color: #d13438; font-weight: bold; font-size: 11px;")

    def update_config_token_display(self):
        """Update config token display in settings."""
        if not hasattr(self, 'config_token_display'):
            return
        if self.loaded_tokens.get('p-b'):
            masked = self.loaded_tokens['p-b'][:12] + "..." + self.loaded_tokens['p-b'][-12:]
            self.config_token_display.setText(f"✅ {masked}")
            self.config_token_display.setStyleSheet("color: #00b294; font-size: 11px;")
        else:
            self.config_token_display.setText("❌ No token in config")
            self.config_token_display.setStyleSheet("color: #d13438; font-size: 11px;")

    def update_config_lat_token_display(self):
        """Update config lat token display in settings."""
        if not hasattr(self, 'config_lat_token_display'):
            return
        if self.loaded_tokens.get('p-lat'):
            masked = self.loaded_tokens['p-lat'][:8] + "..." + self.loaded_tokens['p-lat'][-8:]
            self.config_lat_token_display.setText(f"✅ {masked}")
            self.config_lat_token_display.setStyleSheet("color: #00b294; font-size: 11px;")
        else:
            self.config_lat_token_display.setText("❌ No secondary token")
            self.config_lat_token_display.setStyleSheet("color: #d13438; font-size: 11px;")

    def toggle_token_visibility(self):
        """Toggle token input visibility."""
        if self.token_input.echoMode() == self.QLineEdit.EchoMode.Password:
            self.token_input.setEchoMode(self.QLineEdit.EchoMode.Normal)
            self.lat_token_input.setEchoMode(self.QLineEdit.EchoMode.Normal)
        else:
            self.token_input.setEchoMode(self.QLineEdit.EchoMode.Password)
            self.lat_token_input.setEchoMode(self.QLineEdit.EchoMode.Password)

    def test_browser_connection(self):
        """Test browser connection."""
        token = self.get_current_token()
        if not token:
            self.QMessageBox.warning(self.window, "Warning", 
                "Please configure a Poe token first.")
            return
        
        try:
            from poe_search.api.browser_client import PoeApiClient
            
            lat_token = self.get_current_lat_token()
            client = PoeApiClient(token=token, lat_token=lat_token if lat_token else None, headless=True)
            
            if client.authenticate():
                client.close()
                self.QMessageBox.information(self.window, "Test Successful", 
                    "✅ Browser connection test successful!")
                self.connection_status_label.setText("🟢 Connection OK")
            else:
                client.close()
                self.QMessageBox.warning(self.window, "Test Failed", 
                    "❌ Authentication failed. Check your tokens.")
                self.connection_status_label.setText("🔴 Connection failed")
                
        except Exception as e:
            self.QMessageBox.critical(self.window, "Test Error", 
                f"❌ Connection test error:\n{str(e)}")
            self.connection_status_label.setText("🔴 Connection error")

    def sync_conversations_enhanced(self):
        """Sync conversations with progress tracking."""
        token = self.get_current_token()
        if not token:
            self.QMessageBox.warning(self.window, "Warning", 
                "Please configure a Poe token first.")
            return
        
        # Show progress
        self.sync_button.setEnabled(False)
        self.sync_button.setText("🔄 Syncing...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_status_label.setVisible(True)
        self.progress_status_label.setText("Initializing sync...")
        
        # Get parameters
        lat_token = self.get_current_lat_token()
        headless = self.headless_checkbox.isChecked()
        max_conversations = self.max_conversations_spin.value()
        
        # Create sync thread
        self.sync_thread = ConversationSyncThread(token, lat_token, headless, max_conversations)
        
        # Connect signals
        self.sync_thread.worker.progress.connect(self.on_sync_progress)
        self.sync_thread.worker.finished.connect(self.on_sync_finished)
        self.sync_thread.worker.error.connect(self.on_sync_error)
        
        # Start sync
        self.sync_thread.worker.start()
        self.connection_status_label.setText("🔄 Syncing...")

    def on_sync_progress(self, message: str, percentage: int):
        """Handle sync progress updates."""
        self.progress_bar.setValue(percentage)
        self.progress_status_label.setText(message)
        self.status_bar.showMessage(f"🔄 {message}")

    def on_sync_finished(self, conversations: List[Dict[str, Any]]):
        """Handle successful sync completion."""
        # Convert to simple conversation objects
        converted_conversations = []
        for conv_data in conversations:
            class SimpleConversation:
                def __init__(self, data):
                    self.id = data['id']
                    self.title = data['title']
                    self.bot = data['bot']
                    self.url = data['url']
                    self.messages = data['messages']
                    self.created_at = data['created_at']
                
                def to_dict(self):
                    return {
                        'id': self.id, 'title': self.title, 'bot': self.bot,
                        'url': self.url, 'messages': self.messages,
                        'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at)
                    }
            
            converted_conversations.append(SimpleConversation(conv_data))
        
        self.conversations = converted_conversations
        
        # Update UI
        self.populate_conversation_list()
        self.update_bot_filter()
        self.update_stats()
        self.update_analytics()
        
        # Hide progress
        self.progress_bar.setVisible(False)
        self.progress_status_label.setVisible(False)
        self.sync_button.setEnabled(True)
        self.sync_button.setText("🚀 Enhanced Sync")
        
        self.connection_status_label.setText("🟢 Sync complete")
        self.status_bar.showMessage(f"✅ Successfully synced {len(conversations)} conversations")
        
        self.QMessageBox.information(self.window, "Sync Successful", 
            f"🎉 Successfully synced {len(conversations)} conversations!")

    def on_sync_error(self, error_message: str):
        """Handle sync errors."""
        self.progress_bar.setVisible(False)
        self.progress_status_label.setVisible(False)
        self.sync_button.setEnabled(True)
        self.sync_button.setText("🚀 Enhanced Sync")
        
        self.connection_status_label.setText("🔴 Sync failed")
        self.status_bar.showMessage("❌ Sync failed")
        
        self.QMessageBox.critical(self.window, "Sync Error", 
            f"❌ Sync failed:\n{error_message}")

    # Placeholder implementations for remaining functionality
    def save_current_tokens(self): pass
    def validate_tokens(self): pass
    def clear_config_tokens(self): pass
    def reload_tokens_from_config(self): pass
    def filter_conversations(self): pass
    def sort_conversations(self): pass
    def populate_conversation_list(self): pass
    def update_bot_filter(self): pass
    def update_stats(self): pass
    def update_analytics(self): pass
    def on_conversation_selected(self, item): pass
    def display_conversation(self, conversation): pass
    def open_conversation_in_browser(self): pass
    def export_current_conversation(self): pass
    def copy_conversation(self): pass
    def analyze_current_conversation(self): pass
    def perform_advanced_search(self): pass
    def clear_search_results(self): pass
    def show_search_syntax_help(self): pass
    def on_search_result_selected(self, item): pass
    def export_all_conversations(self): pass
    def refresh_view(self): pass
    def show_about(self): pass


def main():
    """Main function with fixed layout GUI."""
    try:
        print("🚀 Starting Poe Search GUI v1.2 (Fixed Layout)...")
        setup_logging()
        
        missing = check_dependencies()
        if missing:
            print(f"❌ Missing dependencies: {missing}")
            return 1
        
        tokens = load_poe_tokens()
        if tokens.get('p-b'):
            has_lat = " + p-lat" if tokens.get('p-lat') else ""
            print(f"🔑 Found tokens: {tokens['p-b'][:8]}...{tokens['p-b'][-8:]}{has_lat}")
        
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont
        
        app = QApplication(sys.argv)
        app.setApplicationName("Poe Search")
        app.setApplicationDisplayName("Poe Search - Fixed Layout v1.2")
        app.setApplicationVersion("1.2.0")
        
        font = QFont("Segoe UI", 9)
        app.setFont(font)
        
        print("✅ Creating fixed layout GUI...")
        
        main_window = FixedLayoutMainWindow()
        window = main_window.create_window()
        window.show()
        
        print("🎉 Fixed layout GUI launched successfully!")
        print("✨ No more overlapping elements!")
        
        if tokens.get('p-b'):
            print("✅ Ready to sync conversations!")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())