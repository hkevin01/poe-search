"""Main window for Poe Search GUI application."""

import json
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from PyQt6.QtCore import QDate, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QBrush, QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QSystemTrayIcon,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from poe_search import PoeSearchClient
from poe_search.gui.widgets.analytics_widget import AnalyticsWidget
from poe_search.gui.widgets.category_widget import CategoryWidget
from poe_search.gui.widgets.conversation_widget import ConversationWidget
from poe_search.gui.widgets.search_widget import SearchWidget
from poe_search.gui.workers.categorization_worker import CategoryWorker
from poe_search.gui.workers.search_worker import SearchWorker
from poe_search.workers.sync_worker import SyncWorker
from poe_search.storage.database import Database
from poe_search.utils.config import load_config

# Setup comprehensive logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window for the Poe Search GUI application."""
    
    def __init__(self):
        """Initialize the main window.
        
        Args:
            config: Application configuration
        """
        super().__init__()
        
        # Initialize logging (don't use basicConfig as it may conflict)
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== MainWindow initialization started ===")
        
        # Load configuration
        self.logger.info("Loading configuration...")
        self.config = load_config()
        self.logger.info("Configuration loaded successfully")
        
        # Initialize database - use data directory for consistency
        try:
            self.logger.info("Starting database initialization...")
            db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
            resolved_db_path = db_path.resolve()
            self.logger.info(f"Database path calculated: {db_path}")
            self.logger.info(f"Database resolved path: {resolved_db_path}")
            self.logger.info(f"Database file exists: {resolved_db_path.exists()}")
            
            self.database = Database(str(db_path))
            self.logger.info("Database object created successfully")
            
            # Test database access immediately
            test_conversations = self.database.get_conversations()
            self.logger.info(f"Database test: {len(test_conversations)} conversations found")
            
            if len(test_conversations) == 0:
                self.logger.warning("Database test found 0 conversations - this may indicate an issue")
                # Try to list tables to see if database is properly initialized
                try:
                    import sqlite3
                    conn = sqlite3.connect(str(resolved_db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    self.logger.info(f"Database tables: {[t[0] for t in tables]}")
                    
                    cursor.execute("SELECT COUNT(*) FROM conversations;")
                    count = cursor.fetchone()[0]
                    self.logger.info(f"Direct SQL query count: {count}")
                    conn.close()
                except Exception as e:
                    self.logger.error(f"Direct SQL test failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Initialize UI components
        self.init_ui()
        
        # Set up system tray
        self.setup_system_tray()
        
        # Set up client with automatic browser extraction
        self.setup_client()
        
        # Set up periodic refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes
        
        # Show welcome message
        self.show_welcome_message()
        
        # Monitor system resources
        self.setup_resource_monitoring()
        
        # Set up database for all widgets
        self.setup_widgets_database()
    
    def setup_resource_monitoring(self):
        """Set up resource monitoring for memory and CPU usage."""
        self.resource_timer = QTimer()
        self.resource_timer.timeout.connect(self.check_system_resources)
        self.resource_timer.start(30000)  # Check every 30 seconds
        
        # Set resource thresholds
        self.memory_threshold = 85.0  # 85% memory usage
        self.cpu_threshold = 90.0     # 90% CPU usage
        
        self.logger.info("Resource monitoring initialized")
    
    def check_system_resources(self):
        """Check system resources and log warnings if thresholds are exceeded."""
        try:
            # Check memory usage
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > self.memory_threshold:
                self.logger.warning(f"High memory usage detected: {memory_percent:.1f}%")
                self.update_status(f"High memory usage: {memory_percent:.1f}%")
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.cpu_threshold:
                self.logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
                self.update_status(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Log resource usage periodically
            if hasattr(self, '_resource_log_counter'):
                self._resource_log_counter += 1
            else:
                self._resource_log_counter = 0
            
            if self._resource_log_counter % 10 == 0:  # Log every 5 minutes
                self.logger.info(f"System resources - Memory: {memory_percent:.1f}%, CPU: {cpu_percent:.1f}%")
                
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
    
    def log_operation_start(self, operation: str):
        """Log the start of a heavy operation with resource info."""
        try:
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.logger.info(f"Starting {operation} - Memory: {memory_percent:.1f}%, CPU: {cpu_percent:.1f}%")
        except Exception as e:
            self.logger.error(f"Error logging operation start: {e}")
    
    def log_operation_end(self, operation: str, success: bool = True):
        """Log the end of a heavy operation with resource info."""
        try:
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=0.1)
            status = "completed" if success else "failed"
            self.logger.info(f"{operation} {status} - Memory: {memory_percent:.1f}%, CPU: {cpu_percent:.1f}%")
        except Exception as e:
            self.logger.error(f"Error logging operation end: {e}")
    
    def init_ui(self):
        """Set up the user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create menu bar
        self.setup_menu_bar()
        
        # Create toolbar
        self.setup_toolbar()
        
        # Create main content area
        self.setup_main_content(main_layout)
        
        # Create status bar
        self.setup_status_bar()
    
    def setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Import action
        import_action = QAction("&Import Conversations...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.open_import_dialog)
        file_menu.addAction(import_action)
        
        # Export action
        export_action = QAction("&Export Conversations...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_conversations)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Refresh action
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        edit_menu.addAction(refresh_action)
        
        # Sync action
        sync_action = QAction("&Sync Conversations", self)
        sync_action.setShortcut("Ctrl+S")
        sync_action.triggered.connect(self.sync_conversations)
        edit_menu.addAction(sync_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Settings action
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        # Analytics action
        analytics_action = QAction("&Analytics", self)
        analytics_action.triggered.connect(self.show_analytics)
        tools_menu.addAction(analytics_action)
        
        tools_menu.addSeparator()
        
        # Session management
        relogin_action = QAction("&Re-login to Poe", self)
        relogin_action.setStatusTip("Force re-login to Poe.com")
        relogin_action.triggered.connect(self.force_relogin)
        tools_menu.addAction(relogin_action)
        
        extract_browser_action = QAction("&Extract from Browser", self)
        extract_browser_action.setStatusTip("Extract tokens from existing browser session")
        extract_browser_action.triggered.connect(self.extract_from_browser)
        tools_menu.addAction(extract_browser_action)
        
        clear_session_action = QAction("&Clear Session Data", self)
        clear_session_action.setStatusTip("Clear saved session data")
        clear_session_action.triggered.connect(self.clear_session_data)
        tools_menu.addAction(clear_session_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Set up the toolbar."""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        
        # Search button
        search_action = QAction("Search", self)
        search_action.setStatusTip("Search conversations")
        search_action.triggered.connect(self.focus_search)
        toolbar.addAction(search_action)
        
        toolbar.addSeparator()
        
        # Sync button
        sync_action = QAction("Sync", self)
        sync_action.setStatusTip("Sync conversations")
        sync_action.triggered.connect(self.sync_conversations)
        toolbar.addAction(sync_action)
        
        # Export button
        export_action = QAction("Export", self)
        export_action.setStatusTip("Export conversations")
        export_action.triggered.connect(self.export_conversations)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Settings button
        settings_action = QAction("Settings", self)
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
    
    def setup_main_content(self, main_layout: QVBoxLayout):
        """Set up the main content area.
        
        Args:
            main_layout: Main layout to add content to
        """
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Search tab
        self.search_widget = SearchWidget()
        self.tab_widget.addTab(self.search_widget, "🔍 Search")
        
        # Conversations tab
        self.conversation_widget = ConversationWidget()
        self.tab_widget.addTab(self.conversation_widget, "💬 Conversation")
        
        # Categories tab
        self.category_widget = CategoryWidget()
        self.tab_widget.addTab(self.category_widget, "🏷️ Categories")
        
        # Analytics tab
        self.analytics_widget = AnalyticsWidget()
        self.tab_widget.addTab(self.analytics_widget, "📊 Analytics")
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status labels
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        self.status_bar.addPermanentWidget(QLabel(""))  # Spacer
        
        # Connection status
        self.connection_label = QLabel("Disconnected")
        self.status_bar.addPermanentWidget(self.connection_label)
        
        # Database status
        self.db_label = QLabel("DB: Not loaded")
        self.status_bar.addPermanentWidget(self.db_label)
    
    def setup_connections(self):
        """Set up signal connections for widgets."""
        # Connect search widget
        self.search_widget.search_requested.connect(self.perform_search)
        self.search_widget.conversation_selected.connect(
            self.show_conversation)
        
        # Tab widget
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Conversation widget connections
        self.conversation_widget.category_changed.connect(self.update_conversation_category)
        self.conversation_widget.export_requested.connect(self.export_single_conversation)
        
        # Category widget connections
        self.category_widget.category_updated.connect(self.update_conversation_category)
        self.category_widget.bulk_categorization_requested.connect(self.bulk_categorize_conversations)
        
        # Analytics widget connections - REMOVED to prevent recursion
        # self.analytics_widget.refresh_requested.connect(self.refresh_analytics)
    
    def setup_client(self):
        """Set up the Poe API client with authentication."""
        try:
            from poe_search.utils.browser_tokens import refresh_tokens_if_needed
            
            self.status_label.setText("Setting up Poe API client...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            # Try to get tokens (will attempt browser extraction first, then manual login if needed)
            tokens = refresh_tokens_if_needed()
            
            if not tokens:
                QMessageBox.critical(
                    self,
                    "Authentication Failed",
                    "Failed to authenticate with Poe.com.\n\n"
                    "Please try logging in again or extracting tokens from your browser."
                )
                self.progress_bar.setVisible(False)
                return
            
            # Initialize the API client
            # Set the tokens in the config for the PoeSearchClient to use
            if tokens:
                # Convert None values to empty strings for type safety
                clean_tokens = {k: v or "" for k, v in tokens.items()}
                self.config.poe_tokens = clean_tokens
        
            # Use consistent database path
            db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
            self.client = PoeSearchClient(config=self.config, database_url=f"sqlite:///{db_path}")
        
            # Get the underlying API client for direct API calls
            self.api_client = self.client.api_client
            
            # Test the connection
            try:
                # Real connection test: fetch user info
                user_info = self.api_client.get_user_info()
                if user_info:
                    self.status_label.setText("Connected to Poe.com")
                    logger.info("Successfully connected to Poe.com (user info fetched)")
                else:
                    self.status_label.setText("Connected to Poe.com (no user info)")
                    logger.warning("Connected to Poe.com but user info not available")
                
                # Enable sync functionality
                self.sync_worker = SyncWorker(self.client)
                self.sync_worker.sync_finished.connect(self.on_sync_finished)
                self.sync_worker.sync_error.connect(self.on_sync_error)
                
                # Note: SearchWorker will be created when needed during actual searches
                # since it requires search_params and database which aren't available here
                
                # Enable categorization
                self.categorization_worker = CategoryWorker(self.client)
                self.categorization_worker.categorization_complete.connect(self.on_categorization_complete)
                
                # Load existing conversations
                self.load_conversations()
                
                # Start initial sync
                self.start_sync()
                
            except Exception as e:
                logger.error(f"Connection test failed: {e}")
                QMessageBox.warning(
                    self,
                    "Connection Warning",
                    f"Connected to Poe.com but encountered an issue: {str(e)}\n\n"
                    "The app may have limited functionality."
                )
                self.status_label.setText("Connected with warnings")
            
            self.progress_bar.setVisible(False)
            
        except Exception as e:
            logger.error(f"Client setup failed: {e}")
            QMessageBox.critical(
                self,
                "Setup Error",
                f"Failed to set up the Poe API client: {str(e)}"
            )
            self.progress_bar.setVisible(False)
    
    def show_token_setup_dialog(self):
        """Show dialog to set up Poe token."""
        from poe_search.gui.dialogs.token_dialog import TokenDialog
        
        dialog = TokenDialog(self)
        if dialog.exec() == TokenDialog.DialogCode.Accepted:
            token = dialog.get_token()
            self.config["token"] = token
            # Save config and retry setup
            from poe_search.utils.config import save_config
            save_config(self.config)
            self.setup_client()
    
    def on_tab_changed(self, index: int):
        """Handle tab change.
        
        Args:
            index: New tab index
        """
        tab_names = ["Search", "Conversations", "Analytics"]
        if 0 <= index < len(tab_names):
            self.status_label.setText(f"Viewing {tab_names[index]}")
    
    def focus_search(self):
        """Focus on the search tab and search input."""
        self.tab_widget.setCurrentIndex(0)
        self.search_widget.focus_search_input()
    
    def perform_search(self, search_params: Dict[str, Any]):
        """Perform a search with the given parameters in background thread.
        
        Args:
            search_params: Search parameters including query, filters, etc.
        """
        try:
            self.log_operation_start("search")
            query = search_params.get("query", "").strip()
            
            # Stop any existing search worker
            if hasattr(self, 'search_worker') and self.search_worker.isRunning():
                self.search_worker.stop()
                self.search_worker.wait()
            
            # If no query and no specific filters, show all conversations
            if not query and not any([
                search_params.get("bot"),
                search_params.get("category"),
                search_params.get("date_from"),
                search_params.get("date_to")
            ]):
                self.status_label.setText("Showing all conversations")
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)
                
                # Get all conversations and apply basic filters
                conversations = self.database.get_conversations()
                self.on_search_results(conversations)
                self.on_search_finished()
                return
            
            # If query is empty but we have filters, show filtered conversations
            if not query:
                self.status_label.setText("Showing filtered conversations")
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)
                
                # Get all conversations and apply filters
                conversations = self.database.get_conversations()
                filtered = self.apply_search_filters(conversations, search_params)
                self.on_search_results(filtered)
                self.on_search_finished()
                return
            
            # Perform text search with filters in background thread
            self.status_label.setText(f"Searching for: {query}")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Create and start search worker
            self.search_worker = SearchWorker(search_params, self.database)
            self.search_worker.progress.connect(self.on_search_progress)
            self.search_worker.results_ready.connect(self.on_search_results)
            self.search_worker.error.connect(self.on_search_error)
            self.search_worker.finished.connect(self.on_search_finished)
            self.search_worker.start()
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            self.log_operation_end("search", success=False)
            import traceback
            tb = traceback.format_exc()
            self.show_detailed_error("Search Error", str(e), tb)
            self.status_label.setText("Search failed")
            self.progress_bar.setVisible(False)
    
    def apply_search_filters(self, conversations: List[Dict[str, Any]], 
                           search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to conversations.
        
        Args:
            conversations: List of conversations to filter
            search_params: Search parameters containing filters
            
        Returns:
            Filtered list of conversations
        """
        filtered = []
        
        for conv in conversations:
            # Bot filter
            bot_filter = search_params.get("bot")
            if bot_filter and conv.get("bot") != bot_filter:
                continue
                
            # Category filter
            category_filter = search_params.get("category")
            if category_filter and conv.get("category", "Uncategorized") != category_filter:
                continue
                
            # Date filters
            date_from = search_params.get("date_from")
            date_to = search_params.get("date_to")
            
            if date_from or date_to:
                created = conv.get("created_at")
                if created:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        conv_date = dt.date()
                        
                        if date_from and conv_date < date_from:
                            continue
                        if date_to and conv_date > date_to:
                            continue
                    except Exception:
                        # If date parsing fails, skip this conversation
                        continue
                else:
                    # If no creation date, skip if date filters are applied
                    if date_from or date_to:
                        continue
            
            filtered.append(conv)
        
        return filtered
    
    def on_search_progress(self, progress: int):
        """Handle search progress updates.
        
        Args:
            progress: Progress percentage (0-100)
        """
        self.progress_bar.setValue(progress)
        self.search_widget.progress_bar.setValue(progress)
    
    def on_search_results(self, results: List[Dict[str, Any]]):
        """Handle search results.
        
        Args:
            results: Search results
        """
        self.search_widget.update_results(results)
        self.status_label.setText(f"Found {len(results)} results")
        self.log_operation_end("search", success=True)
    
    def on_search_error(self, error: str):
        """Handle search error with detailed dialog."""
        self.logger.error(f"Search error: {error}")
        self.log_operation_end("search", success=False)
        import traceback
        tb = traceback.format_exc()
        self.show_detailed_error("Search Error", error, tb)
        self.status_label.setText("Search failed")
    
    def on_search_finished(self):
        """Handle search completion."""
        self.progress_bar.setVisible(False)
        self.search_widget.show_progress(False)
        if hasattr(self, 'search_worker') and self.search_worker:
            self.search_worker.deleteLater()
            self.search_worker = None
    
    def show_conversation(self, conversation_id: str):
        """Show a specific conversation.
        
        Args:
            conversation_id: Conversation ID to show
        """
        try:
            self.tab_widget.setCurrentIndex(1)
            # Fetch the conversation object from the database and load it
            if hasattr(self, 'database') and self.database:
                conversation = self.database.get_conversation(conversation_id)
                if conversation:
                    self.conversation_widget.load_conversation(conversation)
                else:
                    QMessageBox.warning(self, "Not Found", f"Conversation {conversation_id} not found in database.")
            else:
                QMessageBox.warning(self, "Error", "Database not initialized.")
        except Exception as e:
            self.logger.error(f"Error showing conversation {conversation_id}: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show conversation: {e}")
    
    def sync_conversations(self):
        """Sync conversations from Poe.com in background thread."""
        try:
            self.log_operation_start("sync")
            
            if not self.api_client:
                QMessageBox.warning(self, "Error", "Please configure your Poe token first.")
                self.log_operation_end("sync", success=False)
                return
            
            # Stop any existing sync worker
            if hasattr(self, 'sync_worker') and self.sync_worker.isRunning():
                self.sync_worker.stop()
                self.sync_worker.wait()
            
            self.status_label.setText("Syncing conversations...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            # Create and start sync worker with database
            if not hasattr(self, 'config') or not self.config.poe_tokens:
                QMessageBox.warning(self, "Error", "No Poe credentials available.")
                self.progress_bar.setVisible(False)
                return
                
            credentials = {
                'formkey': self.config.poe_tokens.get('formkey', ''),
                'p_b_cookie': self.config.poe_tokens.get('p_b', '')
            }
            
            if not credentials['formkey'] or not credentials['p_b_cookie']:
                QMessageBox.warning(self, "Error", "Missing Poe credentials.")
                self.progress_bar.setVisible(False)
                return
                
            from ..storage.database_manager import DatabaseManager
            db_manager = DatabaseManager(self.database.db_path)
            
            self.sync_worker = SyncWorker(db_manager, credentials)
            self.sync_worker.progress.connect(self.on_sync_progress_new)
            self.sync_worker.status_update.connect(self.on_sync_status_new)
            self.sync_worker.error.connect(self.on_sync_error_new)
            self.sync_worker.finished.connect(self.on_sync_finished_new)
            self.sync_worker.start()
            
        except Exception as e:
            self.logger.error(f"Sync error: {e}")
            self.log_operation_end("sync", success=False)
            QMessageBox.critical(self, "Sync Error", f"Failed to start sync: {e}")
            self.progress_bar.setVisible(False)
    
    def on_sync_progress_new(self, progress: int):
        """Handle new sync worker progress updates."""
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setValue(progress)

    def on_sync_status_new(self, status: str):
        """Handle new sync worker status updates."""
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText(status)
        self.logger.info(f"Sync status: {status}")

    def on_sync_error_new(self, error: str):
        """Handle new sync worker errors."""
        self.logger.error(f"Sync error: {error}")
        self.log_operation_end("sync", success=False)
        QMessageBox.critical(self, "Sync Error", f"Sync failed: {error}")
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setVisible(False)

    def on_sync_finished_new(self):
        """Handle new sync worker completion."""
        self.logger.info("Sync completed successfully")
        self.log_operation_end("sync", success=True)
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText("Sync completed")
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setVisible(False)
        # Refresh the conversation list
        self.load_conversations()
        # Clean up worker
        if hasattr(self, 'sync_worker') and self.sync_worker:
            self.sync_worker.deleteLater()
            self.sync_worker = None

    def refresh_data(self):
        """Refresh all data in the application."""
        try:
            self.log_operation_start("refresh")
            self.logger.info("Starting data refresh...")
            
            if not hasattr(self, 'database') or not self.database:
                self.logger.warning("No database available for data refresh")
                self.log_operation_end("refresh", success=False)
                return
            
            # Fetch conversations from database
            self.logger.info("Fetching conversations from database...")
            conversations = self.database.get_conversations()
            self.logger.info(f"Fetched {len(conversations)} conversations")
            
            # Update status
            self.status_label.setText(f"Loaded {len(conversations)} conversations")
            
            # Refresh individual widgets
            self.refresh_conversations()
            self.refresh_analytics()
            
            self.logger.info("Data refresh completed successfully")
            self.log_operation_end("refresh", success=True)
            
        except Exception as e:
            self.logger.error(f"Data refresh failed: {e}", exc_info=True)
            self.log_operation_end("refresh", success=False)
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.warning(
                self,
                "Refresh Error",
                f"Failed to refresh data: {str(e)}"
            )
    
    def refresh_conversations(self):
        """Refresh conversation data."""
        try:
            self.logger.debug("MainWindow.refresh_conversations() called")
            if hasattr(self, 'conversation_widget') and self.conversation_widget:
                self.conversation_widget.refresh_data()
                self.logger.debug("MainWindow.refresh_conversations() completed successfully")
        except Exception as e:
            self.logger.error(f"Error in MainWindow.refresh_conversations(): {e}")
            raise
    
    def refresh_analytics(self):
        """Refresh analytics data."""
        try:
            self.logger.debug("MainWindow.refresh_analytics() called")
            if hasattr(self, 'analytics_widget') and self.analytics_widget:
                self.analytics_widget.refresh_data()
                self.logger.debug("MainWindow.refresh_analytics() completed successfully")
        except Exception as e:
            self.logger.error(f"Error in MainWindow.refresh_analytics(): {e}")
            raise
    
    def export_conversations(self):
        """Export conversations to file."""
        try:
            self.log_operation_start("export")
            self.logger.debug("MainWindow.export_conversations() called")
            
            if not hasattr(self, 'database') or not self.database:
                QMessageBox.warning(self, "Error", "Database not initialized.")
                self.log_operation_end("export", success=False)
                return
            
            from poe_search.gui.dialogs.export_dialog import ExportDialog
            
            dialog = ExportDialog(self)
            if dialog.exec() == ExportDialog.DialogCode.Accepted:
                export_config = dialog.get_export_config()
                self.perform_export(export_config)
            else:
                self.log_operation_end("export", success=False)
                
            self.logger.debug("MainWindow.export_conversations() completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in MainWindow.export_conversations(): {e}")
            self.log_operation_end("export", success=False)
            raise
    
    def perform_export(self, export_config: Dict[str, Any]):
        """Perform export operation.
        
        Args:
            export_config: Export configuration
        """
        try:
            self.logger.debug("MainWindow.perform_export() called")
            self.status_label.setText("Exporting conversations...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            # Use database for export
            from poe_search.export.exporter import ConversationExporter
            exporter = ConversationExporter(self.database)
            
            # Get conversations to export
            conversations = self.database.get_conversations()
            
            # Export using the exporter
            exporter.export(
                conversations=conversations,
                output_path=export_config['output_path'],
                format=export_config.get('format', 'json')
            )
            
            self.progress_bar.setVisible(False)
            self.status_label.setText("Export complete")
            self.log_operation_end("export", success=True)
            
            QMessageBox.information(
                self, 
                "Export Complete", 
                f"Conversations exported to {export_config['output_path']}"
            )
            self.logger.debug("MainWindow.perform_export() completed successfully")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.logger.error(f"Export error: {e}")
            self.log_operation_end("export", success=False)
            QMessageBox.critical(self, "Export Error", f"Failed to export conversations: {e}")
    
    def open_settings(self):
        """Open settings dialog."""
        from poe_search.gui.dialogs.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            self.config = dialog.get_config()
            # Apply new configuration
            self.setup_client()
    
    def show_analytics(self):
        """Show analytics tab."""
        self.tab_widget.setCurrentIndex(2)
        self.analytics_widget.refresh_data()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Poe Search",
            "Poe Search v0.1.0\n\n"
            "A desktop application for searching and organizing "
            "your Poe.com conversations.\n\n"
            "Built with PyQt6 and Python."
        )
    
    def force_relogin(self):
        """Force re-login to Poe.com."""
        try:
            from poe_search.utils.browser_tokens import force_relogin
            
            reply = QMessageBox.question(
                self,
                "Re-login",
                "This will clear your current session and force a fresh login to Poe.com.\n\n"
                "Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.status_label.setText("Re-logging in to Poe.com...")
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)
                
                # Force re-login
                tokens = force_relogin()
                
                if tokens and tokens.get('p-b'):
                    # Re-setup client with new tokens
                    self.setup_client()
                    QMessageBox.information(
                        self,
                        "Re-login Successful",
                        "Successfully re-logged in to Poe.com!"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Re-login Failed",
                        "Failed to re-login. Please try again."
                    )
                
                self.progress_bar.setVisible(False)
                
        except Exception as e:
            logger.error(f"Force re-login failed: {e}")
            QMessageBox.critical(
                self,
                "Re-login Error",
                f"Failed to re-login: {str(e)}"
            )
            self.progress_bar.setVisible(False)
    
    def clear_session_data(self):
        """Clear saved session data."""
        try:
            from poe_search.utils.browser_tokens import clear_session
            
            reply = QMessageBox.question(
                self,
                "Clear Session",
                "This will clear all saved session data and cookies.\n\n"
                "You will need to log in again on the next startup.\n\n"
                "Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                clear_session()
                QMessageBox.information(
                    self,
                    "Session Cleared",
                    "Session data has been cleared successfully.\n\n"
                    "You will need to log in again on the next startup."
                )
                
        except Exception as e:
            logger.error(f"Clear session failed: {e}")
            QMessageBox.critical(
                self,
                "Clear Session Error",
                f"Failed to clear session: {str(e)}"
            )
    
    def extract_from_browser(self):
        """Extract tokens from existing browser session."""
        try:
            from poe_search.utils.browser_tokens import get_tokens_from_browser
            
            self.status_label.setText("Extracting tokens from browser...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            # Try to extract tokens from browser
            tokens = get_tokens_from_browser()
            
            if tokens and tokens.get('p-b'):
                # Re-setup client with extracted tokens
                self.setup_client()
                QMessageBox.information(
                    self,
                    "Token Extraction Successful",
                    f"Successfully extracted tokens from browser!\n\n"
                    f"Found cookies: {', '.join(tokens.keys())}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Token Extraction Failed",
                    "No valid Poe.com tokens found in your browser.\n\n"
                    "Please make sure you are logged in to Poe.com in Chrome or Firefox."
                )
            
            self.progress_bar.setVisible(False)
            
        except Exception as e:
            logger.error(f"Browser token extraction failed: {e}")
            QMessageBox.critical(
                self,
                "Token Extraction Error",
                f"Failed to extract tokens from browser: {str(e)}\n\n"
                "Make sure you are logged in to Poe.com in Chrome or Firefox."
            )
            self.progress_bar.setVisible(False)
    
    def update_status(self):
        """Update status information."""
        if self.api_client:
            try:
                # Update database status
                conversations = self.api_client.database.get_conversations(limit=1)
                self.db_label.setText(f"DB: Ready ({len(conversations)} conversations)")
            except Exception:
                self.db_label.setText("DB: Error")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Check if system tray is available and icon is visible
        if (hasattr(self, 'tray_icon') and 
            self.tray_icon and 
            self.tray_icon.isVisible()):
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Poe Search",
                "The application will be minimized to the system tray.\n"
                "To quit the application, right-click the tray icon and select 'Exit'.\n\n"
                "Do you want to minimize to tray?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Hide the window instead of closing
                self.hide()
                self.tray_icon.showMessage(
                    "Poe Search",
                    "Application minimized to system tray",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
                event.ignore()  # Don't close the application
                return
            else:
                # User chose to quit
                self.quit_application()
                event.accept()
        else:
            # No system tray available, close normally
            logger.info("No system tray available, closing application normally")
            event.accept()
    
    def update_conversation_category(self, conversation_id: str, category: str):
        """Update conversation category.
        
        Args:
            conversation_id: Conversation ID
            category: New category
        """
        try:
            if hasattr(self, 'database') and self.database:
                # Update in database
                self.database.update_conversation_category(conversation_id, category)
                self.status_label.setText(f"Updated category for conversation {conversation_id}")
                
                # Refresh widgets
                self.conversation_widget.refresh_data()
                self.analytics_widget.refresh_data()
            else:
                QMessageBox.warning(self, "Error", "Database not initialized.")
                
        except Exception as e:
            self.logger.error(f"Failed to update category: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update category: {e}")
    
    def export_single_conversation(self, conversation_id: str):
        """Export a single conversation.
        
        Args:
            conversation_id: Conversation ID to export
        """
        try:
            if not hasattr(self, 'database') or not self.database:
                QMessageBox.warning(self, "Error", "Database not initialized.")
                return
            
            # Get conversation data
            conversation = self.database.get_conversation(conversation_id)
            if not conversation:
                QMessageBox.warning(self, "Error", "Conversation not found.")
                return
            
            # Choose export file
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Conversation",
                f"conversation_{conversation_id}.md",
                "Markdown Files (*.md);;JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                # Export conversation using database
                from poe_search.export.exporter import ConversationExporter
                exporter = ConversationExporter(self.database)
                
                exporter.export(
                    conversations=[conversation],
                    output_path=file_path,
                    format="markdown" if file_path.endswith('.md') else "json"
                )
                
                QMessageBox.information(
                    self, 
                    "Export Complete", 
                    f"Conversation exported to {file_path}"
                )
                
        except Exception as e:
            self.logger.error(f"Export error: {e}")
            QMessageBox.critical(self, "Export Error", f"Export failed: {e}")
    
    def bulk_categorize_conversations(self, category_rules: List[Dict[str, Any]]):
        """Perform bulk categorization of conversations.
        
        Args:
            category_rules: List of categorization rules
        """
        try:
            if not hasattr(self, 'database') or not self.database:
                QMessageBox.warning(self, "Error", "Database not initialized.")
                return
            
            self.status_label.setText("Running bulk categorization...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            # This would be implemented with a categorization worker
            # For now, just show a message
            QMessageBox.information(
                self,
                "Bulk Categorization",
                "Bulk categorization feature will be implemented in a future update."
            )
            
            self.progress_bar.setVisible(False)
            self.status_label.setText("Ready")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.logger.error(f"Bulk categorization failed: {e}")
            QMessageBox.critical(self, "Error", f"Bulk categorization failed: {e}")
            self.status_label.setText("Ready")

    def open_import_dialog(self):
        """Open dialog for importing Poe conversation exports."""
        try:
            if not hasattr(self, 'database') or not self.database:
                QMessageBox.warning(self, "Error", "Database not initialized.")
                return
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Poe Conversations",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                self.import_conversations_from_file(file_path)
                
        except Exception as e:
            self.logger.error(f"Import dialog error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open import dialog: {e}")

    def import_conversations_from_file(self, file_path: str):
        """Import conversations from exported JSON file."""
        try:
            self.log_operation_start("import")
            self.status_label.setText("Importing conversations...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process Poe export format
            conversations = self.parse_poe_export(data)
            
            # Store in database
            imported_count = 0
            for conv in conversations:
                try:
                    self.database.save_conversation(conv)
                    imported_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to import conversation {conv.get('id', 'unknown')}: {e}")
            
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Import complete: {imported_count} conversations")
            self.log_operation_end("import", success=True)
            
            QMessageBox.information(
                self, 
                "Import Complete", 
                f"Successfully imported {imported_count} conversations from {file_path}"
            )
            
            # Refresh widgets individually to avoid recursion
            if hasattr(self, 'search_widget') and self.search_widget:
                self.search_widget.refresh_data()
            if hasattr(self, 'conversation_widget') and self.conversation_widget:
                self.conversation_widget.refresh_data()
            if hasattr(self, 'analytics_widget') and self.analytics_widget:
                self.analytics_widget.refresh_data()
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.logger.error(f"Import failed: {e}")
            self.log_operation_end("import", success=False)
            QMessageBox.critical(self, "Import Error", f"Import failed: {str(e)}")
            self.status_label.setText("Import failed")

    def parse_poe_export(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Poe.com export format into conversation objects."""
        conversations = []
        
        # Handle different export formats
        if isinstance(data, list):
            # Direct list of conversations
            conversations_data = data
        elif isinstance(data, dict):
            # Object with conversations array
            conversations_data = data.get('conversations', [])
            if not conversations_data:
                conversations_data = data.get('data', [])
        else:
            raise ValueError("Invalid export format")
        
        for conv_data in conversations_data:
            try:
                # Extract conversation information
                conversation = {
                    'id': conv_data.get('id', str(len(conversations) + 1)),
                    'title': conv_data.get('title', conv_data.get('name', f"Conversation {len(conversations) + 1}")),
                    'bot': conv_data.get('bot', conv_data.get('model', 'Unknown')),
                    'created_at': conv_data.get('created_at', datetime.now().isoformat()),
                    'updated_at': conv_data.get('updated_at', datetime.now().isoformat()),
                    'message_count': len(conv_data.get('messages', [])),
                    'category': 'Uncategorized',
                    'messages': []
                }
                
                # Process messages
                for msg_data in conv_data.get('messages', []):
                    message = {
                        'id': msg_data.get('id', str(len(conversation['messages']) + 1)),
                        'role': msg_data.get('role', msg_data.get('author', 'unknown')),
                        'content': msg_data.get('content', msg_data.get('text', '')),
                        'timestamp': msg_data.get('timestamp', msg_data.get('created_at', datetime.now().isoformat()))
                    }
                    conversation['messages'].append(message)
                
                conversations.append(conversation)
                
            except Exception as e:
                logger.warning(f"Failed to parse conversation: {e}")
                continue
        
        return conversations

    def setup_system_tray(self):
        """Set up the system tray."""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray is not available on this system")
            return
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Try to load tray icon from file first
        icon_loaded = False
        icon_paths = [
            Path(__file__).parent / "resources" / "icons" / "tray_icon.png",
            Path(__file__).parent / "resources" / "icons" / "tray_icon_32x32.png",
            Path(__file__).parent / "resources" / "icons" / "tray_icon_24x24.png",
            Path(__file__).parent / "resources" / "icons" / "tray_icon_16x16.png",
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                self.tray_icon.setIcon(QIcon(str(icon_path)))
                icon_loaded = True
                logger.info(f"Tray icon loaded from: {icon_path}")
                break
        
        # Fallback to a standard Qt icon if no PNG is found
        if not icon_loaded:
            from PyQt6.QtWidgets import QApplication
            self.tray_icon.setIcon(QIcon.fromTheme("application-exit"))  # Use a standard icon
            logger.warning("No tray icon PNG found, using standard Qt icon.")
        
        self.tray_icon.setToolTip("Poe Search - AI Conversation Manager")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide action
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_window_visibility)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        # Quick actions
        search_action = QAction("Search", self)
        search_action.triggered.connect(self.focus_search)
        tray_menu.addAction(search_action)
        
        sync_action = QAction("Sync Conversations", self)
        sync_action.triggered.connect(self.sync_conversations)
        tray_menu.addAction(sync_action)
        
        tray_menu.addSeparator()
        
        # Settings and exit
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        tray_menu.addAction(settings_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Connect double-click to show window
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Only show the tray icon if system tray is available
        if QSystemTrayIcon.isSystemTrayAvailable():
            try:
                if self.tray_icon.show():
                    logger.info("System tray icon created successfully")
                else:
                    logger.warning("System tray icon show() returned False - tray may not be supported")
            except Exception as e:
                logger.warning(f"Failed to show system tray icon: {e}")
                # Don't fail the application if tray icon fails
                self.tray_icon = None
        else:
            logger.warning("System tray is not available on this system. Tray icon will not be shown.")

    def create_poe_search_icon(self) -> QPixmap:
        """Create a Poe-themed search icon."""
        # Create a 32x32 pixmap
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create a painter to draw the icon
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Poe brand colors: Purple (#7C3AED) and gradient
        poe_purple = QColor("#7C3AED")
        poe_dark = QColor("#5B21B6")
        poe_light = QColor("#A78BFA")
        
        # Draw magnifying glass (search symbol)
        # Glass circle
        painter.setPen(QPen(poe_purple, 2))
        painter.setBrush(QBrush(poe_light))
        painter.drawEllipse(8, 8, 16, 16)
        
        # Handle
        painter.setPen(QPen(poe_purple, 3))
        painter.drawLine(20, 20, 26, 26)
        
        # Add a small "P" for Poe in the center
        painter.setPen(QPen(poe_dark, 1))
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "P")
        
        painter.end()
        return pixmap

    def toggle_window_visibility(self):
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "Poe Search",
                "Application minimized to system tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_window_visibility()

    def quit_application(self):
        """Quit the application completely."""
        # Stop any running workers
        if hasattr(self, 'search_worker') and self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
        
        if hasattr(self, 'sync_worker') and self.sync_worker and self.sync_worker.isRunning():
            self.sync_worker.terminate()
            self.sync_worker.wait()
        
        # Hide tray icon
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.hide()
        
        # Close the application
        QApplication.quit()

    def show_welcome_message(self):
        """Show a welcome message to the user."""
        QMessageBox.information(
            self,
            "Welcome to Poe Search",
            "Welcome to Poe Search! We're glad you're here.\n\n"
            "This is a new version of Poe Search, with a focus on improving the user experience.\n\n"
            "We'd love to hear your feedback. Please let us know what you think!"
        )

    def show_detailed_error(self, title, message, details):
        """Show a detailed error dialog with a Show Details button."""
        dlg = QMessageBox(self)
        dlg.setIcon(QMessageBox.Icon.Critical)
        dlg.setWindowTitle(title)
        dlg.setText(message)
        dlg.setDetailedText(details)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()

    def setup_widgets_database(self):
        """Set up database access for all widgets."""
        try:
            if hasattr(self, 'search_widget') and self.search_widget:
                self.search_widget.set_database(self.database)
                self.logger.info("Database set for search widget")
            
            if hasattr(self, 'conversation_widget') and self.conversation_widget:
                if hasattr(self.conversation_widget, 'set_database'):
                    self.conversation_widget.set_database(self.database)
                    self.logger.info("Database set for conversation widget")
            
            if hasattr(self, 'category_widget') and self.category_widget:
                if hasattr(self.category_widget, 'set_database'):
                    self.category_widget.set_database(self.database)
                    self.logger.info("Database set for category widget")
            
            if hasattr(self, 'analytics_widget') and self.analytics_widget:
                if hasattr(self.analytics_widget, 'set_database'):
                    self.analytics_widget.set_database(self.database)
                    self.logger.info("Database set for analytics widget")
                    
        except Exception as e:
            self.logger.error(f"Error setting up database for widgets: {e}")
    
    def on_categorization_complete(self, stats: dict):
        """Handle categorization completion.
        
        Args:
            stats: Categorization statistics
        """
        self.logger.info(f"Categorization completed: {stats}")
        if hasattr(self, 'categorization_worker') and self.categorization_worker:
            self.categorization_worker.deleteLater()
            self.categorization_worker = None

    def load_conversations(self):
        """Load existing conversations from database.
        
        This method loads conversations and populates the conversation widget.
        """
        try:
            self.logger.info("Loading existing conversations...")
            
            if not hasattr(self, 'database') or not self.database:
                self.logger.warning("No database available for loading conversations")
                return
                
            # Get conversations from database
            conversations = self.database.get_conversations()
            self.logger.info(f"Loaded {len(conversations)} conversations from database")
            
            # Update conversation widget if available
            if hasattr(self, 'conversation_widget') and self.conversation_widget:
                self.conversation_widget.load_conversations(conversations)
                
        except Exception as e:
            self.logger.error(f"Error loading conversations: {e}")
    
    def start_sync(self):
        """Start initial sync of conversations.
        
        This method starts the background sync process.
        """
        try:
            self.logger.info("Starting initial sync...")
            
            # Check if we have credentials available
            if not hasattr(self, 'config') or not self.config.poe_tokens:
                self.logger.warning("No Poe tokens available for sync")
                return
                
            # Get credentials from config
            credentials = {
                'formkey': self.config.poe_tokens.get('formkey', ''),
                'p_b_cookie': self.config.poe_tokens.get('p_b', '')
            }
            
            # Validate credentials
            if not credentials['formkey'] or not credentials['p_b_cookie']:
                self.logger.warning("Missing required credentials for sync")
                return
                
            # Check if database is available
            if not hasattr(self, 'database') or not self.database:
                self.logger.warning("No database available for sync")
                return
                
            # Stop any existing sync worker
            if hasattr(self, 'initial_sync_worker') and self.initial_sync_worker.isRunning():
                self.initial_sync_worker.stop()
                self.initial_sync_worker.wait()
                
            # Create and start new sync worker
            from ..storage.database_manager import DatabaseManager
            db_manager = DatabaseManager(self.database.db_path)
            
            self.initial_sync_worker = SyncWorker(db_manager, credentials)
            self.initial_sync_worker.progress.connect(self.on_initial_sync_progress)
            self.initial_sync_worker.status_update.connect(self.on_initial_sync_status)
            self.initial_sync_worker.error.connect(self.on_initial_sync_error)
            self.initial_sync_worker.finished.connect(self.on_initial_sync_finished)
            self.initial_sync_worker.conversation_synced.connect(self.on_conversation_synced)
            
            self.logger.info("Starting initial sync worker...")
            self.initial_sync_worker.start()
            
        except Exception as e:
            self.logger.error(f"Error starting sync: {e}")
            
    def on_initial_sync_progress(self, progress: int):
        """Handle initial sync progress updates."""
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setValue(progress)
            
    def on_initial_sync_status(self, status: str):
        """Handle initial sync status updates."""
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText(status)
        self.logger.info(f"Sync status: {status}")
        
    def on_initial_sync_error(self, error: str):
        """Handle initial sync errors."""
        self.logger.error(f"Initial sync error: {error}")
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText(f"Sync error: {error}")
            
    def on_initial_sync_finished(self):
        """Handle initial sync completion."""
        self.logger.info("Initial sync completed")
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText("Sync completed")
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setVisible(False)
        # Refresh the conversation list
        self.load_conversations()
        
    def on_conversation_synced(self, conversation: dict):
        """Handle individual conversation sync completion."""
        self.logger.debug(f"Conversation synced: {conversation.get('title', 'Unknown')}")
