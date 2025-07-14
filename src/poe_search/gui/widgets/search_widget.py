"""Search widget for finding and filtering conversations."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QDate, Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class SearchWidget(QWidget):
    """Widget for searching and filtering conversations."""
    
    # Signals
    conversation_selected = pyqtSignal(str)  # conversation_id
    search_requested = pyqtSignal(dict)     # search_params
    
    def __init__(self, parent=None):
        """Initialize the search widget."""
        super().__init__(parent)
        
        self.conversations = []
        self.filtered_conversations = []
        self.database = None
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.setup_connections()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_results)
        
    def set_database(self, database):
        """Set the database instance.
        
        Args:
            database: Database instance
        """
        self.database = database
        self.logger.info("Database set for search widget")
        
        # DEBUG: Try to create a new database connection to ensure we get data
        try:
            from pathlib import Path

            # Use absolute path to ensure we get the right database
            project_root = Path(__file__).parent.parent.parent.parent.parent
            data_db_path = project_root / "data" / "poe_search.db"
            root_db_path = project_root / "poe_search.db" 
            
            self.logger.info(f"DEBUG: project_root = {project_root}")
            self.logger.info(f"DEBUG: data_db_path = {data_db_path}, exists = {data_db_path.exists()}")
            self.logger.info(f"DEBUG: root_db_path = {root_db_path}, exists = {root_db_path.exists()}")
            
            # Test both database paths
            if data_db_path.exists():
                from poe_search.storage.database import Database
                test_db = Database(str(data_db_path))
                test_convs = test_db.get_conversations()
                self.logger.info(f"DEBUG: data database has {len(test_convs)} conversations")
                
                # If the passed database is empty but the data database has conversations, use the data database
                current_convs = self.database.get_conversations() if self.database else []
                if len(current_convs) == 0 and len(test_convs) > 0:
                    self.logger.warning("Passed database is empty, switching to data database")
                    self.database = test_db
                    
            if root_db_path.exists():
                from poe_search.storage.database import Database
                test_db2 = Database(str(root_db_path))
                test_convs2 = test_db2.get_conversations()
                self.logger.info(f"DEBUG: root database has {len(test_convs2)} conversations")
                
        except Exception as e:
            self.logger.error(f"DEBUG: Database path testing failed: {e}")
        
        # Automatically load all conversations when database is set
        if self.database:
            self.show_all_conversations()
    
    def set_client(self, client):
        """Set the Poe Search client (legacy method for compatibility).
        
        Args:
            client: PoeSearchClient instance
        """
        if hasattr(client, 'database'):
            self.database = client.database
            self.logger.info("Database set from client for search widget")
        else:
            self.logger.warning("Client has no database attribute")
    
    def focus_search_input(self):
        """Focus on the search input field."""
        self.search_input.setFocus()
        self.search_input.selectAll()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Search controls
        search_group = self.create_search_controls()
        layout.addWidget(search_group)
        
        # Results table
        results_group = self.create_results_table()
        layout.addWidget(results_group)
        
        # Status and progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def create_search_controls(self) -> QGroupBox:
        """Create the search controls group."""
        group = QGroupBox("Search & Filter")
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
        layout.setSpacing(12)
        
        # Search input row
        search_row = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search conversations, messages, or topics...")
        self.search_input.setMinimumHeight(36)
        search_row.addWidget(QLabel("Search:"), 0)
        search_row.addWidget(self.search_input, 1)
        
        self.search_button = QPushButton("Search")
        self.search_button.setMinimumHeight(36)
        self.search_button.setMinimumWidth(100)
        search_row.addWidget(self.search_button)
        
        layout.addLayout(search_row)
        
        # Filters row
        filters_row = QHBoxLayout()
        
        # Bot filter
        filters_row.addWidget(QLabel("Bot:"))
        self.bot_combo = QComboBox()
        self.bot_combo.addItem("All Bots")
        self.bot_combo.setMinimumWidth(120)
        filters_row.addWidget(self.bot_combo)
        
        # Category filter
        filters_row.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "All Categories", "Technical", "Medical", "Spiritual", 
            "Political", "Educational", "Creative", "Personal", "Other"
        ])
        self.category_combo.setMinimumWidth(120)
        filters_row.addWidget(self.category_combo)
        
        # Date range
        filters_row.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-365))  # 1 year ago
        self.date_from.setMinimumWidth(120)
        filters_row.addWidget(self.date_from)
        
        filters_row.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setMinimumWidth(120)
        filters_row.addWidget(self.date_to)
        
        filters_row.addStretch()
        
        # Clear filters button
        self.clear_filters_button = QPushButton("Clear Filters")
        self.clear_filters_button.setMinimumHeight(32)
        filters_row.addWidget(self.clear_filters_button)
        
        layout.addLayout(filters_row)
        
        # Advanced options
        advanced_row = QHBoxLayout()
        
        self.regex_checkbox = QCheckBox("Use Regular Expressions")
        advanced_row.addWidget(self.regex_checkbox)
        
        self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        advanced_row.addWidget(self.case_sensitive_checkbox)
        
        advanced_row.addStretch()
        
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh (30s)")
        advanced_row.addWidget(self.auto_refresh_checkbox)
        
        layout.addLayout(advanced_row)
        
        return group
    
    def create_results_table(self) -> QGroupBox:
        """Create the results table group."""
        group = QGroupBox("Search Results")
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
        
        # Results info
        self.results_label = QLabel("No results")
        self.results_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.results_label)
        
        # Table
        self.results_table = QTableWidget()
        self.setup_results_table()
        layout.addWidget(self.results_table)
        
        return group
    
    def setup_results_table(self):
        """Set up the results table."""
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Title", "Bot", "Category", "Messages", "Last Updated", "Created"
        ])
        
        # Configure table
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(True)
        
        # Column sizing
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Title
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Bot
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Messages
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Updated
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Created
        
        # Style the table for Windows 11
        self.results_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #404040;
                font-size: 13px;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid #404040;
                font-weight: 600;
                font-size: 12px;
            }
        """)
    
    def setup_connections(self):
        """Set up signal connections."""
        # Search
        self.search_button.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Filters - make date filters trigger new search
        self.bot_combo.currentTextChanged.connect(self.apply_filters)
        self.category_combo.currentTextChanged.connect(self.apply_filters)
        self.date_from.dateChanged.connect(self.perform_search)  # Trigger new search
        self.date_to.dateChanged.connect(self.perform_search)    # Trigger new search
        
        # Clear filters
        self.clear_filters_button.clicked.connect(self.clear_filters)
        
        # Auto-refresh
        self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
        
        # Table selection
        self.results_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.results_table.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def get_search_params(self) -> Dict[str, Any]:
        """Get current search parameters from the widget.
        
        Returns:
            Dictionary of search parameters
        """
        return {
            "query": self.search_input.text().strip(),
            "bot": self.bot_combo.currentText() if self.bot_combo.currentText() != "All Bots" else None,
            "category": self.category_combo.currentText() if self.category_combo.currentText() != "All Categories" else None,
            "date_from": self.date_from.date().toPyDate(),
            "date_to": self.date_to.date().toPyDate(),
            "use_regex": self.regex_checkbox.isChecked(),
            "case_sensitive": self.case_sensitive_checkbox.isChecked()
        }

    def perform_search(self):
        """Perform a search with current parameters."""
        if not self.database:
            return
        
        # Get search query and validate it
        query = self.search_input.text().strip()
        
        # Handle empty queries - show all conversations instead of warning
        if not query:
            logger.info("Empty search query, showing all conversations")
            self.show_all_conversations()
            return
            
        search_params = {
            "query": query,
            "bot": self.bot_combo.currentText() if self.bot_combo.currentText() != "All Bots" else None,
            "category": self.category_combo.currentText() if self.category_combo.currentText() != "All Categories" else None,
            "date_from": self.date_from.date().toPyDate(),
            "date_to": self.date_to.date().toPyDate(),
            "use_regex": self.regex_checkbox.isChecked(),
            "case_sensitive": self.case_sensitive_checkbox.isChecked()
        }
        
        logger.info(f"Performing search with params: {search_params}")
        self.search_requested.emit(search_params)
        self.show_progress(True)
    
    def apply_filters(self):
        """Apply current filters to the results."""
        # For non-date filters, we can filter current results
        # For date filters, we need to perform a new search
        if self.database and self.conversations:
            self.filter_current_results()
    
    def filter_current_results(self):
        """Filter the current results based on UI filters."""
        if not self.conversations:
            return
            
        filtered_conversations = []
        
        for conversation in self.conversations:
            # Bot filter
            selected_bot = self.bot_combo.currentText()
            if selected_bot != "All Bots" and conversation.get("bot") != selected_bot:
                continue
                
            # Category filter
            selected_category = self.category_combo.currentText()
            if selected_category != "All Categories" and conversation.get("category") != selected_category:
                continue
                
            filtered_conversations.append(conversation)
        
        # Update the table with filtered results
        self.populate_table(filtered_conversations)
        
        # Update results label
        count = len(filtered_conversations)
        self.results_label.setText(f"{count} conversation{'s' if count != 1 else ''} found")
    
    def clear_filters(self):
        """Clear all filters."""
        self.bot_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addDays(-365))  # 1 year ago
        self.date_to.setDate(QDate.currentDate())
        self.regex_checkbox.setChecked(False)
        self.case_sensitive_checkbox.setChecked(False)
        
        # Perform a new search with cleared filters
        self.perform_search()
    
    def toggle_auto_refresh(self, enabled: bool):
        """Toggle auto-refresh functionality."""
        if enabled:
            self.refresh_timer.start(30000)  # 30 seconds
        else:
            self.refresh_timer.stop()
    
    def refresh_results(self):
        """Refresh the search results."""
        if self.database:
            # Re-run the last search
            self.perform_search()
    
    def show_progress(self, show: bool):
        """Show or hide progress bar."""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate
        
    def update_results(self, conversations: List[Dict[str, Any]]):
        """Update the results table with conversations."""
        self.conversations = conversations
        self.populate_table(conversations)
        self.update_bot_filter()
        self.show_progress(False)
        
        # Update results label
        count = len(conversations)
        self.results_label.setText(f"{count} conversation{'s' if count != 1 else ''} found")
    
    def populate_table(self, conversations: List[Dict[str, Any]]):
        """Populate the results table."""
        self.results_table.setRowCount(len(conversations))
        
        for row, conversation in enumerate(conversations):
            # Title
            title_item = QTableWidgetItem(conversation.get("title", "Untitled"))
            title_item.setData(Qt.ItemDataRole.UserRole, conversation.get("id"))
            self.results_table.setItem(row, 0, title_item)
            
            # Bot
            bot_item = QTableWidgetItem(conversation.get("bot", "Unknown"))
            self.results_table.setItem(row, 1, bot_item)
            
            # Category
            category = conversation.get("category", "Uncategorized")
            category_item = QTableWidgetItem(category)
            self.results_table.setItem(row, 2, category_item)
            
            # Message count
            msg_count = conversation.get("message_count", 0)
            msg_item = QTableWidgetItem(str(msg_count))
            msg_item.setData(Qt.ItemDataRole.DisplayRole, msg_count)
            self.results_table.setItem(row, 3, msg_item)
            
            # Last updated
            updated_at = conversation.get("updated_at", "")
            if updated_at:
                try:
                    dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    updated_text = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    updated_text = updated_at
            else:
                updated_text = "Unknown"
            updated_item = QTableWidgetItem(updated_text)
            self.results_table.setItem(row, 4, updated_item)
            
            # Created
            created_at = conversation.get("created_at", "")
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_text = dt.strftime("%Y-%m-%d")
                except:
                    created_text = created_at
            else:
                created_text = "Unknown"
            created_item = QTableWidgetItem(created_text)
            self.results_table.setItem(row, 5, created_item)
    
    def update_bot_filter(self):
        """Update the bot filter dropdown with available bots."""
        current_bots = set(conv.get("bot", "Unknown") for conv in self.conversations)
        
        # Save current selection
        current_selection = self.bot_combo.currentText()
        
        # Update items
        self.bot_combo.clear()
        self.bot_combo.addItem("All Bots")
        self.bot_combo.addItems(sorted(current_bots))
        
        # Restore selection if possible
        if current_selection in [self.bot_combo.itemText(i) for i in range(self.bot_combo.count())]:
            self.bot_combo.setCurrentText(current_selection)
    
    def on_selection_changed(self):
        """Handle table selection changes."""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            title_item = self.results_table.item(current_row, 0)
            if title_item:
                conversation_id = title_item.data(Qt.ItemDataRole.UserRole)
                if conversation_id:
                    self.conversation_selected.emit(conversation_id)
    
    def on_item_double_clicked(self, item):
        """Handle double-click on table item."""
        conversation_id = item.data(Qt.ItemDataRole.UserRole) 
        if conversation_id:
            self.conversation_selected.emit(conversation_id)
    
    def get_selected_conversation_id(self) -> Optional[str]:
        """Get the currently selected conversation ID."""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            title_item = self.results_table.item(current_row, 0)
            if title_item:
                return title_item.data(Qt.ItemDataRole.UserRole)
        return None

    def refresh_data(self):
        """Refresh search data (alias for refresh_results)."""
        logger.debug("SearchWidget.refresh_data() called")
        try:
            self.refresh_results()
            logger.debug("SearchWidget.refresh_data() completed successfully")
        except Exception as e:
            logger.error(f"Error in SearchWidget.refresh_data(): {e}")
            raise

    def show_all_conversations(self):
        """Show all conversations respecting current filters."""
        if not self.database:
            logger.error("Database not set in SearchWidget")
            return
        
        try:
            # Get all conversations from database
            all_conversations = self.database.get_conversations()
            logger.info(f"Raw conversations from database: {len(all_conversations)}")
            
            # Apply all current filters including date range
            filtered_conversations = []
            selected_bot = self.bot_combo.currentText()
            selected_category = self.category_combo.currentText()
            
            # Use the actual selected date range from the UI
            user_date_from = self.date_from.date().toPyDate()
            user_date_to = self.date_to.date().toPyDate()
            
            logger.info(f"Filters: bot={selected_bot}, "
                        f"category={selected_category}, "
                        f"date_range={user_date_from} to {user_date_to}")
            
            for conversation in all_conversations:
                # Apply bot filter
                if (selected_bot != "All Bots" and
                        conversation.get("bot") != selected_bot):
                    continue
                
                # Apply category filter
                if (selected_category != "All Categories" and
                        conversation.get("category") != selected_category):
                    continue
                
                # Apply user's selected date filter
                conv_date = conversation.get("created_at")
                if conv_date:
                    try:
                        from datetime import datetime
                        conv_datetime = datetime.fromisoformat(
                            conv_date.replace('Z', '+00:00'))
                        conv_date_only = conv_datetime.date()
                        if not (user_date_from <= conv_date_only <=
                                user_date_to):
                            continue
                    except (ValueError, AttributeError):
                        # Skip conversations with invalid dates
                        continue
                
                filtered_conversations.append(conversation)
            
            # Use existing methods to display results
            self.populate_table(filtered_conversations)
            self.update_bot_filter()
            
            # Update results count
            count = len(filtered_conversations)
            text = f"{count} conversation{'s' if count != 1 else ''} found"
            self.results_label.setText(text)
            logger.info(f"Showing {count} conversations after filters")
            
        except Exception as e:
            logger.error(f"Error showing all conversations: {e}")
