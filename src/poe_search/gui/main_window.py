"""Main window for Poe Search GUI application."""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QProgressBar,
    QStatusBar, QMenuBar, QMenu, QToolBar, QLabel, QComboBox, QTextEdit,
    QSplitter, QGroupBox, QCheckBox, QSpinBox, QDateEdit, QMessageBox,
    QFileDialog, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QDate
from PyQt6.QtGui import QAction, QIcon, QFont, QPixmap

from poe_search import PoeSearchClient
from poe_search.gui.widgets.search_widget import SearchWidget
from poe_search.gui.widgets.conversation_widget import ConversationWidget
from poe_search.gui.widgets.analytics_widget import AnalyticsWidget
from poe_search.gui.workers.search_worker import SearchWorker
from poe_search.gui.workers.sync_worker import SyncWorker

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window for the Poe Search GUI application."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the main window.
        
        Args:
            config: Application configuration
        """
        super().__init__()
        
        self.config = config
        self.client = None
        self.search_worker = None
        self.sync_worker = None
        
        # Window properties
        self.setWindowTitle("Poe Search")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # Initialize UI
        self.setup_ui()
        self.setup_connections()
        self.setup_client()
        
        # Status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    def setup_ui(self):
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
        
        export_action = QAction("&Export...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("Export conversations")
        export_action.triggered.connect(self.export_conversations)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Refresh data")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        sync_action = QAction("&Sync Conversations", self)
        sync_action.setShortcut("Ctrl+S")
        sync_action.setStatusTip("Sync conversations from Poe.com")
        sync_action.triggered.connect(self.sync_conversations)
        tools_menu.addAction(sync_action)
        
        analytics_action = QAction("&Analytics", self)
        analytics_action.setShortcut("Ctrl+A")
        analytics_action.setStatusTip("View analytics")
        analytics_action.triggered.connect(self.show_analytics)
        tools_menu.addAction(analytics_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Poe Search")
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
        self.search_widget = SearchWidget(self.config)
        self.tab_widget.addTab(self.search_widget, "Search")
        
        # Conversations tab
        self.conversation_widget = ConversationWidget(self.config)
        self.tab_widget.addTab(self.conversation_widget, "Conversations")
        
        # Analytics tab
        self.analytics_widget = AnalyticsWidget(self.config)
        self.tab_widget.addTab(self.analytics_widget, "Analytics")
        
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
        """Set up signal connections."""
        # Tab widget
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Search widget connections
        self.search_widget.search_requested.connect(self.perform_search)
        self.search_widget.conversation_selected.connect(self.show_conversation)
        
        # Conversation widget connections
        self.conversation_widget.refresh_requested.connect(self.refresh_conversations)
        
        # Analytics widget connections
        self.analytics_widget.refresh_requested.connect(self.refresh_analytics)
    
    def setup_client(self):
        """Set up the Poe Search client."""
        try:
            token = self.config.get("token")
            if not token:
                self.show_token_setup_dialog()
                return
            
            self.client = PoeSearchClient(
                token=token,
                database_url=self.config.get("database_url")
            )
            
            self.connection_label.setText("Connected")
            self.db_label.setText("DB: Ready")
            self.status_label.setText("Ready - Connected to Poe Search")
            
            # Initialize widgets with client
            self.search_widget.set_client(self.client)
            self.conversation_widget.set_client(self.client)
            self.analytics_widget.set_client(self.client)
            
        except Exception as e:
            logger.error(f"Failed to setup client: {e}")
            self.connection_label.setText("Error")
            self.status_label.setText(f"Error: {e}")
    
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
    
    def perform_search(self, query: str, filters: Dict[str, Any]):
        """Perform a search operation.
        
        Args:
            query: Search query
            filters: Search filters
        """
        if not self.client:
            QMessageBox.warning(self, "Error", "Please configure your Poe token first.")
            return
        
        self.status_label.setText(f"Searching for: {query}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Create and start search worker
        self.search_worker = SearchWorker(self.client, query, filters)
        self.search_worker.results_ready.connect(self.on_search_results)
        self.search_worker.error_occurred.connect(self.on_search_error)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.start()
    
    def on_search_results(self, results: List[Dict[str, Any]]):
        """Handle search results.
        
        Args:
            results: Search results
        """
        self.search_widget.display_results(results)
        self.status_label.setText(f"Found {len(results)} results")
    
    def on_search_error(self, error: str):
        """Handle search error.
        
        Args:
            error: Error message
        """
        QMessageBox.critical(self, "Search Error", f"Search failed: {error}")
        self.status_label.setText("Search failed")
    
    def on_search_finished(self):
        """Handle search completion."""
        self.progress_bar.setVisible(False)
        if self.search_worker:
            self.search_worker.deleteLater()
            self.search_worker = None
    
    def show_conversation(self, conversation_id: str):
        """Show a specific conversation.
        
        Args:
            conversation_id: Conversation ID to show
        """
        self.tab_widget.setCurrentIndex(1)
        self.conversation_widget.show_conversation(conversation_id)
    
    def sync_conversations(self):
        """Sync conversations from Poe.com."""
        if not self.client:
            QMessageBox.warning(self, "Error", "Please configure your Poe token first.")
            return
        
        self.status_label.setText("Syncing conversations...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # Create and start sync worker
        self.sync_worker = SyncWorker(self.client, days=7)
        self.sync_worker.sync_complete.connect(self.on_sync_complete)
        self.sync_worker.error_occurred.connect(self.on_sync_error)
        self.sync_worker.finished.connect(self.on_sync_finished)
        self.sync_worker.start()
    
    def on_sync_complete(self, stats: Dict[str, int]):
        """Handle sync completion.
        
        Args:
            stats: Sync statistics
        """
        message = f"Sync complete! New: {stats['new']}, Updated: {stats['updated']}"
        self.status_label.setText(message)
        QMessageBox.information(self, "Sync Complete", message)
        
        # Refresh data in all widgets
        self.refresh_data()
    
    def on_sync_error(self, error: str):
        """Handle sync error.
        
        Args:
            error: Error message
        """
        QMessageBox.critical(self, "Sync Error", f"Sync failed: {error}")
        self.status_label.setText("Sync failed")
    
    def on_sync_finished(self):
        """Handle sync completion."""
        self.progress_bar.setVisible(False)
        if self.sync_worker:
            self.sync_worker.deleteLater()
            self.sync_worker = None
    
    def refresh_data(self):
        """Refresh data in all widgets."""
        self.refresh_conversations()
        self.refresh_analytics()
        self.status_label.setText("Data refreshed")
    
    def refresh_conversations(self):
        """Refresh conversation data."""
        if self.client:
            self.conversation_widget.refresh_data()
    
    def refresh_analytics(self):
        """Refresh analytics data."""
        if self.client:
            self.analytics_widget.refresh_data()
    
    def export_conversations(self):
        """Export conversations to file."""
        if not self.client:
            QMessageBox.warning(self, "Error", "Please configure your Poe token first.")
            return
        
        from poe_search.gui.dialogs.export_dialog import ExportDialog
        
        dialog = ExportDialog(self)
        if dialog.exec() == ExportDialog.DialogCode.Accepted:
            export_config = dialog.get_export_config()
            self.perform_export(export_config)
    
    def perform_export(self, export_config: Dict[str, Any]):
        """Perform export operation.
        
        Args:
            export_config: Export configuration
        """
        try:
            self.status_label.setText("Exporting conversations...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            self.client.export_conversations(**export_config)
            
            self.progress_bar.setVisible(False)
            self.status_label.setText("Export complete")
            QMessageBox.information(
                self, 
                "Export Complete", 
                f"Conversations exported to {export_config['output_path']}"
            )
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Export Error", f"Export failed: {e}")
            self.status_label.setText("Export failed")
    
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
        from poe_search import __version__
        
        QMessageBox.about(
            self,
            "About Poe Search",
            f"""
            <h3>Poe Search {__version__}</h3>
            <p>A tool for searching and organizing your Poe.com conversations.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Full-text search across conversations</li>
                <li>Local data storage and organization</li>
                <li>Export to multiple formats</li>
                <li>Usage analytics and insights</li>
            </ul>
            <p><b>GitHub:</b> <a href="https://github.com/kevin/poe-search">github.com/kevin/poe-search</a></p>
            <p>Licensed under the MIT License</p>
            """
        )
    
    def update_status(self):
        """Update status information."""
        if self.client:
            try:
                # Update database status
                conversations = self.client.get_conversations(limit=1)
                self.db_label.setText(f"DB: Ready ({len(conversations)} conversations)")
            except Exception:
                self.db_label.setText("DB: Error")
    
    def closeEvent(self, event):
        """Handle close event.
        
        Args:
            event: Close event
        """
        # Stop any running workers
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
        
        if self.sync_worker and self.sync_worker.isRunning():
            self.sync_worker.terminate()
            self.sync_worker.wait()
        
        event.accept()
