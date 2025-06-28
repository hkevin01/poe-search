"""Main window for Poe Search GUI application."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QDate, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView,
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
from poe_search.gui.workers.search_worker import SearchWorker
from poe_search.gui.workers.sync_worker import SyncWorker

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window for the Poe Search GUI application."""
    
    def __init__(self, config):
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
        """Set up signal connections."""
        # Tab widget
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Search widget connections
        self.search_widget.search_requested.connect(self.perform_search)
        self.search_widget.conversation_selected.connect(self.show_conversation)
        
        # Conversation widget connections
        self.conversation_widget.category_changed.connect(self.update_conversation_category)
        self.conversation_widget.export_requested.connect(self.export_single_conversation)
        
        # Category widget connections
        self.category_widget.category_updated.connect(self.update_conversation_category)
        self.category_widget.bulk_categorization_requested.connect(self.bulk_categorize_conversations)
        
        # Analytics widget connections
        self.analytics_widget.refresh_requested.connect(self.refresh_analytics)
    
    def setup_client(self):
        """Set up the Poe Search client."""
        try:
            token = self.config.poe_token
            if not token:
                self.show_token_setup_dialog()
                return
            
            self.client = PoeSearchClient(
                token=token,
                database_url=self.config.database_url
            )
            
            # Check if database is empty and populate with sample data
            if self.client.database.is_empty():
                logger.info("Database is empty, populating with sample data...")
                self.client.database.populate_sample_data()
                self.status_label.setText("Sample data loaded - Ready to search")
            else:
                self.status_label.setText("Ready - Connected to Poe Search")
            
            self.connection_label.setText("Connected")
            self.db_label.setText("DB: Ready")
            
            # Initialize widgets with client
            self.search_widget.set_client(self.client)
            self.conversation_widget.set_client(self.client)
            self.analytics_widget.set_client(self.client)
            
        except Exception as e:
            logger.error(f"Failed to setup client: {e}")
            self.connection_label.setText("Error")
            self.status_label.setText(f"Error: {e}")
            QMessageBox.critical(self, "Connection Error", f"Failed to setup client: {e}")
    
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
        """Perform a search operation.
        
        Args:
            search_params: Dictionary containing search query and filters
        """
        try:
            if not self.client:
                QMessageBox.warning(self, "Error", "Please configure your Poe token first.")
                return
            
            if not self.client.database:
                QMessageBox.warning(self, "Error", "Database not initialized.")
                return
            
            # Check if database has conversations
            count = self.client.database.get_conversation_count()
            if count == 0:
                QMessageBox.information(
                    self, 
                    "No Data", 
                    "No conversations found. The database is empty."
                )
                return
            
            query = search_params.get("query", "")
            if not query.strip():
                QMessageBox.information(
                    self, 
                    "Search Query", 
                    "Please enter a search query."
                )
                return
            
            self.status_label.setText(f"Searching for: {query}")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Create and start search worker
            self.search_worker = SearchWorker(search_params, self.client.database)
            self.search_worker.results_ready.connect(self.on_search_results)
            self.search_worker.error.connect(self.on_search_error)
            self.search_worker.finished.connect(self.on_search_finished)
            self.search_worker.start()
            
        except Exception as e:
            logger.error(f"Search initialization failed: {e}")
            QMessageBox.critical(self, "Search Error", f"Failed to start search: {e}")
            self.status_label.setText("Search failed")
            self.progress_bar.setVisible(False)
    
    def on_search_results(self, results: List[Dict[str, Any]]):
        """Handle search results.
        
        Args:
            results: Search results
        """
        self.search_widget.update_results(results)
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
    
    def update_conversation_category(self, conversation_id: str, category: str):
        """Update conversation category.
        
        Args:
            conversation_id: Conversation ID
            category: New category
        """
        if self.client:
            try:
                # Update in database
                self.client.database.update_conversation_category(conversation_id, category)
                self.status_label.setText(f"Updated category for conversation {conversation_id}")
                
                # Refresh widgets
                self.conversation_widget.refresh_data()
                self.analytics_widget.refresh_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update category: {e}")
    
    def export_single_conversation(self, conversation_id: str):
        """Export a single conversation.
        
        Args:
            conversation_id: Conversation ID to export
        """
        if not self.client:
            QMessageBox.warning(self, "Error", "Please configure your Poe token first.")
            return
        
        try:
            # Get conversation data
            conversation = self.client.database.get_conversation(conversation_id)
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
                # Export conversation
                self.client.export_conversations(
                    output_path=file_path,
                    conversation_ids=[conversation_id],
                    format="markdown" if file_path.endswith('.md') else "json"
                )
                
                QMessageBox.information(
                    self, 
                    "Export Complete", 
                    f"Conversation exported to {file_path}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Export failed: {e}")
    
    def bulk_categorize_conversations(self, category_rules: List[Dict[str, Any]]):
        """Perform bulk categorization of conversations.
        
        Args:
            category_rules: List of categorization rules
        """
        if not self.client:
            QMessageBox.warning(self, "Error", "Please configure your Poe token first.")
            return
        
        try:
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
            QMessageBox.critical(self, "Error", f"Bulk categorization failed: {e}")
            self.status_label.setText("Ready")

    def open_import_dialog(self):
        """Open dialog for importing Poe conversation exports."""
        if not self.client:
            QMessageBox.warning(self, "Error", "Please configure your Poe token first.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Poe Conversations",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.import_conversations_from_file(file_path)

    def import_conversations_from_file(self, file_path: str):
        """Import conversations from exported JSON file."""
        try:
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
                    self.client.database.store_conversation(conv)
                    imported_count += 1
                except Exception as e:
                    logger.warning(f"Failed to import conversation {conv.get('id', 'unknown')}: {e}")
            
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Import complete: {imported_count} conversations")
            
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
