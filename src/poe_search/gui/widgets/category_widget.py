"""Category management widget for organizing conversations."""

import logging
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict, Counter

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QPushButton, QLineEdit, QTextEdit, QMessageBox, QSplitter,
    QListWidget, QListWidgetItem, QCheckBox, QProgressBar,
    QTabWidget, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor

logger = logging.getLogger(__name__)


class CategoryRule:
    """Class representing a categorization rule."""
    
    def __init__(self, name: str, keywords: List[str], category: str, 
                 description: str = "", enabled: bool = True):
        self.name = name
        self.keywords = keywords
        self.category = category
        self.description = description
        self.enabled = enabled
    
    def matches(self, text: str, case_sensitive: bool = False) -> bool:
        """Check if text matches this rule."""
        if not self.enabled or not self.keywords:
            return False
        
        search_text = text if case_sensitive else text.lower()
        search_keywords = self.keywords if case_sensitive else [k.lower() for k in self.keywords]
        
        return any(keyword in search_text for keyword in search_keywords)


class CategoryWorker(QThread):
    """Worker thread for categorizing conversations."""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)  # {conversation_id: category}
    error = pyqtSignal(str)
    
    def __init__(self, conversations: List[Dict[str, Any]], rules: List[CategoryRule]):
        super().__init__()
        self.conversations = conversations
        self.rules = rules
        self.should_stop = False
    
    def run(self):
        """Run categorization."""
        try:
            categorized = {}
            total = len(self.conversations)
            
            for i, conversation in enumerate(self.conversations):
                if self.should_stop:
                    break
                
                # Get conversation text (title + messages)
                text_parts = []
                if conversation.get("title"):
                    text_parts.append(conversation["title"])
                
                for message in conversation.get("messages", []):
                    if message.get("content"):
                        text_parts.append(message["content"])
                
                conversation_text = " ".join(text_parts)
                
                # Apply rules
                category = self.categorize_text(conversation_text)
                if category:
                    categorized[conversation.get("id")] = category
                
                # Update progress
                progress_value = int((i + 1) / total * 100)
                self.progress.emit(progress_value)
            
            self.finished.emit(categorized)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def categorize_text(self, text: str) -> Optional[str]:
        """Categorize text using rules."""
        for rule in self.rules:
            if rule.matches(text):
                return rule.category
        return None
    
    def stop(self):
        """Stop categorization."""
        self.should_stop = True


class CategoryWidget(QWidget):
    """Widget for managing conversation categories and auto-categorization."""
    
    # Signals
    category_updated = pyqtSignal(str, str)  # conversation_id, category
    bulk_categorization_requested = pyqtSignal(list)  # conversation_ids
    
    def __init__(self, parent=None):
        """Initialize the category widget."""
        super().__init__(parent)
        
        self.conversations = []
        self.rules = self.get_default_rules()
        self.categorization_worker = None
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        
        # Categories overview tab
        overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(overview_tab, "Categories Overview")
        
        # Auto-categorization tab
        auto_cat_tab = self.create_auto_categorization_tab()
        self.tab_widget.addTab(auto_cat_tab, "Auto-Categorization")
        
        # Rules management tab
        rules_tab = self.create_rules_tab()
        self.tab_widget.addTab(rules_tab, "Categorization Rules")
        
        layout.addWidget(self.tab_widget)
    
    def create_overview_tab(self) -> QWidget:
        """Create the categories overview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Categories", "Technical", "Medical", "Spiritual",
            "Political", "Educational", "Creative", "Personal", 
            "Other", "Uncategorized"
        ])
        controls_layout.addWidget(QLabel("Filter:"))
        controls_layout.addWidget(self.filter_combo)
        
        controls_layout.addStretch()
        
        self.bulk_categorize_button = QPushButton("Bulk Categorize Selected")
        self.bulk_categorize_button.setMinimumHeight(32)
        controls_layout.addWidget(self.bulk_categorize_button)
        
        layout.addLayout(controls_layout)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        self.total_card = self.create_stat_card("Total Conversations", "0")
        self.categorized_card = self.create_stat_card("Categorized", "0 (0%)")
        self.uncategorized_card = self.create_stat_card("Uncategorized", "0 (0%)")
        
        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.categorized_card)
        stats_layout.addWidget(self.uncategorized_card)
        
        layout.addLayout(stats_layout)
        
        # Conversations table
        table_group = QGroupBox("Conversations by Category")
        table_layout = QVBoxLayout(table_group)
        
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(5)
        self.category_table.setHorizontalHeaderLabels([
            "Title", "Current Category", "Bot", "Messages", "Last Updated"
        ])
        
        # Configure table
        self.category_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.category_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.category_table.setAlternatingRowColors(True)
        self.category_table.setSortingEnabled(True)
        
        # Column sizing
        header = self.category_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Title
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Bot
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Messages
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Updated
        
        # Style
        self.category_table.setStyleSheet("""
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
        
        table_layout.addWidget(self.category_table)
        layout.addWidget(table_group)
        
        return widget
    
    def create_auto_categorization_tab(self) -> QWidget:
        """Create the auto-categorization tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        
        # Instructions
        instructions = QLabel("""
        Auto-categorization uses predefined rules to automatically assign categories to conversations.
        Select conversations below and click "Categorize Selected" to apply rules.
        """)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 12px;
                color: #cccccc;
                font-size: 13px;
            }
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.select_all_checkbox = QCheckBox("Select All")
        controls_layout.addWidget(self.select_all_checkbox)
        
        self.uncategorized_only_checkbox = QCheckBox("Uncategorized Only")
        self.uncategorized_only_checkbox.setChecked(True)
        controls_layout.addWidget(self.uncategorized_only_checkbox)
        
        controls_layout.addStretch()
        
        self.categorize_selected_button = QPushButton("Categorize Selected")
        self.categorize_selected_button.setMinimumHeight(36)
        self.categorize_selected_button.setMinimumWidth(150)
        controls_layout.addWidget(self.categorize_selected_button)
        
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.categorization_progress = QProgressBar()
        self.categorization_progress.setVisible(False)
        layout.addWidget(self.categorization_progress)
        
        # Conversations list
        list_group = QGroupBox("Conversations to Categorize")
        list_layout = QVBoxLayout(list_group)
        
        self.auto_categorization_table = QTableWidget()
        self.auto_categorization_table.setColumnCount(4)
        self.auto_categorization_table.setHorizontalHeaderLabels([
            "Select", "Title", "Current Category", "Suggested Category"
        ])
        
        # Configure table
        self.auto_categorization_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.auto_categorization_table.setAlternatingRowColors(True)
        
        # Column sizing
        header = self.auto_categorization_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Select
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Title
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Current
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Suggested
        
        # Style
        self.auto_categorization_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #404040;
                font-size: 13px;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
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
        
        list_layout.addWidget(self.auto_categorization_table)
        layout.addWidget(list_group)
        
        return widget
    
    def create_rules_tab(self) -> QWidget:
        """Create the rules management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        
        # Rules list
        rules_group = QGroupBox("Categorization Rules")
        rules_layout = QVBoxLayout(rules_group)
        
        # Controls
        rules_controls = QHBoxLayout()
        
        self.add_rule_button = QPushButton("Add Rule")
        self.add_rule_button.setMinimumHeight(32)
        rules_controls.addWidget(self.add_rule_button)
        
        self.edit_rule_button = QPushButton("Edit Rule")
        self.edit_rule_button.setMinimumHeight(32)
        rules_controls.addWidget(self.edit_rule_button)
        
        self.delete_rule_button = QPushButton("Delete Rule")
        self.delete_rule_button.setMinimumHeight(32)
        rules_controls.addWidget(self.delete_rule_button)
        
        rules_controls.addStretch()
        
        self.export_rules_button = QPushButton("Export Rules")
        self.export_rules_button.setMinimumHeight(32)
        rules_controls.addWidget(self.export_rules_button)
        
        self.import_rules_button = QPushButton("Import Rules")
        self.import_rules_button.setMinimumHeight(32)
        rules_controls.addWidget(self.import_rules_button)
        
        rules_layout.addLayout(rules_controls)
        
        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels([
            "Enabled", "Rule Name", "Category", "Keywords", "Description"
        ])
        
        # Configure table
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.rules_table.setAlternatingRowColors(True)
        
        # Column sizing
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Enabled
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Keywords
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Description
        
        # Style
        self.rules_table.setStyleSheet("""
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
        
        rules_layout.addWidget(self.rules_table)
        layout.addWidget(rules_group)
        
        return widget
    
    def create_stat_card(self, title: str, value: str) -> QFrame:
        """Create a statistics card."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        card.setFixedHeight(80)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #888888;
                font-weight: 500;
            }
        """)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #ffffff;
                font-weight: 600;
            }
        """)
        layout.addWidget(value_label)
        
        return card
    
    def setup_connections(self):
        """Set up signal connections."""
        # Overview tab
        self.filter_combo.currentTextChanged.connect(self.filter_conversations)
        self.bulk_categorize_button.clicked.connect(self.bulk_categorize_selected)
        
        # Auto-categorization tab
        self.select_all_checkbox.toggled.connect(self.toggle_select_all)
        self.uncategorized_only_checkbox.toggled.connect(self.update_auto_categorization_list)
        self.categorize_selected_button.clicked.connect(self.start_auto_categorization)
        
        # Rules tab
        self.add_rule_button.clicked.connect(self.add_rule)
        self.edit_rule_button.clicked.connect(self.edit_rule)
        self.delete_rule_button.clicked.connect(self.delete_rule)
        self.export_rules_button.clicked.connect(self.export_rules)
        self.import_rules_button.clicked.connect(self.import_rules)
    
    def get_default_rules(self) -> List[CategoryRule]:
        """Get default categorization rules."""
        return [
            CategoryRule(
                "Technical Programming",
                ["python", "javascript", "code", "programming", "software", "algorithm", "debugging", "api"],
                "Technical",
                "Programming and software development topics"
            ),
            CategoryRule(
                "Medical Health",
                ["health", "medical", "doctor", "symptoms", "medicine", "treatment", "diagnosis", "therapy"],
                "Medical",
                "Health and medical related questions"
            ),
            CategoryRule(
                "Spiritual Religious",
                ["god", "religion", "spiritual", "prayer", "faith", "bible", "meditation", "soul"],
                "Spiritual",
                "Religious and spiritual discussions"
            ),
            CategoryRule(
                "Political Current Events",
                ["politics", "government", "election", "policy", "president", "congress", "law", "voting"],
                "Political",
                "Political and governmental topics"
            ),
            CategoryRule(
                "Educational Learning",
                ["learn", "study", "education", "school", "university", "homework", "research", "academic"],
                "Educational",
                "Learning and educational content"
            ),
            CategoryRule(
                "Creative Arts",
                ["art", "creative", "design", "music", "writing", "story", "poem", "draw", "painting"],
                "Creative",
                "Creative and artistic pursuits"
            ),
            CategoryRule(
                "Personal Life",
                ["personal", "relationship", "family", "friend", "advice", "help", "life", "feeling"],
                "Personal",
                "Personal life and relationships"
            )
        ]
    
    def update_conversations(self, conversations: List[Dict[str, Any]]):
        """Update conversations data."""
        self.conversations = conversations
        self.update_overview()
        self.update_auto_categorization_list()
        self.update_rules_display()
    
    def update_overview(self):
        """Update the overview tab."""
        if not self.conversations:
            return
        
        # Update stats cards
        total = len(self.conversations)
        categorized = sum(1 for conv in self.conversations 
                         if conv.get("category") and conv["category"] != "Uncategorized")
        uncategorized = total - categorized
        
        self.update_stat_card(self.total_card, str(total))
        self.update_stat_card(self.categorized_card, f"{categorized} ({categorized/total*100:.1f}%)" if total > 0 else "0 (0%)")
        self.update_stat_card(self.uncategorized_card, f"{uncategorized} ({uncategorized/total*100:.1f}%)" if total > 0 else "0 (0%)")
        
        # Update table
        self.populate_category_table()
    
    def update_stat_card(self, card: QFrame, value: str):
        """Update a stat card value."""
        labels = card.findChildren(QLabel)
        if len(labels) >= 2:
            labels[1].setText(value)  # Value label
    
    def populate_category_table(self):
        """Populate the category overview table."""
        filtered_conversations = self.get_filtered_conversations()
        
        self.category_table.setRowCount(len(filtered_conversations))
        
        for row, conversation in enumerate(filtered_conversations):
            # Title
            title_item = QTableWidgetItem(conversation.get("title", "Untitled"))
            title_item.setData(Qt.ItemDataRole.UserRole, conversation.get("id"))
            self.category_table.setItem(row, 0, title_item)
            
            # Category
            category = conversation.get("category", "Uncategorized")
            category_item = QTableWidgetItem(category)
            self.category_table.setItem(row, 1, category_item)
            
            # Bot
            bot_item = QTableWidgetItem(conversation.get("bot", "Unknown"))
            self.category_table.setItem(row, 2, bot_item)
            
            # Messages
            msg_count = conversation.get("message_count", 0)
            msg_item = QTableWidgetItem(str(msg_count))
            msg_item.setData(Qt.ItemDataRole.DisplayRole, msg_count)
            self.category_table.setItem(row, 3, msg_item)
            
            # Last updated
            updated_at = conversation.get("updated_at", "")
            if updated_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    updated_text = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    updated_text = updated_at
            else:
                updated_text = "Unknown"
            updated_item = QTableWidgetItem(updated_text)
            self.category_table.setItem(row, 4, updated_item)
    
    def get_filtered_conversations(self) -> List[Dict[str, Any]]:
        """Get conversations filtered by current filter."""
        filter_category = self.filter_combo.currentText()
        
        if filter_category == "All Categories":
            return self.conversations
        
        return [conv for conv in self.conversations 
                if conv.get("category", "Uncategorized") == filter_category]
    
    def filter_conversations(self):
        """Filter conversations based on current selection."""
        self.populate_category_table()
    
    def bulk_categorize_selected(self):
        """Bulk categorize selected conversations."""
        selected_rows = set()
        for item in self.category_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select conversations to categorize.")
            return
        
        conversation_ids = []
        for row in selected_rows:
            title_item = self.category_table.item(row, 0)
            if title_item:
                conversation_id = title_item.data(Qt.ItemDataRole.UserRole)
                if conversation_id:
                    conversation_ids.append(conversation_id)
        
        if conversation_ids:
            self.bulk_categorization_requested.emit(conversation_ids)
    
    def update_auto_categorization_list(self):
        """Update the auto-categorization list."""
        conversations = self.conversations
        
        if self.uncategorized_only_checkbox.isChecked():
            conversations = [conv for conv in conversations 
                           if not conv.get("category") or conv["category"] == "Uncategorized"]
        
        self.auto_categorization_table.setRowCount(len(conversations))
        
        for row, conversation in enumerate(conversations):
            # Checkbox
            checkbox = QCheckBox()
            self.auto_categorization_table.setCellWidget(row, 0, checkbox)
            
            # Title
            title_item = QTableWidgetItem(conversation.get("title", "Untitled"))
            title_item.setData(Qt.ItemDataRole.UserRole, conversation.get("id"))
            self.auto_categorization_table.setItem(row, 1, title_item)
            
            # Current category
            current_category = conversation.get("category", "Uncategorized")
            current_item = QTableWidgetItem(current_category)
            self.auto_categorization_table.setItem(row, 2, current_item)
            
            # Suggested category (would be calculated based on rules)
            suggested_category = self.suggest_category_for_conversation(conversation)
            suggested_item = QTableWidgetItem(suggested_category or "No suggestion")
            self.auto_categorization_table.setItem(row, 3, suggested_item)
    
    def suggest_category_for_conversation(self, conversation: Dict[str, Any]) -> Optional[str]:
        """Suggest a category for a conversation based on rules."""
        # Get conversation text
        text_parts = []
        if conversation.get("title"):
            text_parts.append(conversation["title"])
        
        for message in conversation.get("messages", []):
            if message.get("content"):
                text_parts.append(message["content"])
        
        conversation_text = " ".join(text_parts)
        
        # Apply rules
        for rule in self.rules:
            if rule.matches(conversation_text):
                return rule.category
        
        return None
    
    def toggle_select_all(self, checked: bool):
        """Toggle select all checkboxes."""
        for row in range(self.auto_categorization_table.rowCount()):
            checkbox = self.auto_categorization_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(checked)
    
    def start_auto_categorization(self):
        """Start auto-categorization process."""
        # Get selected conversations
        selected_conversations = []
        for row in range(self.auto_categorization_table.rowCount()):
            checkbox = self.auto_categorization_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                title_item = self.auto_categorization_table.item(row, 1)
                if title_item:
                    conversation_id = title_item.data(Qt.ItemDataRole.UserRole)
                    conversation = next(
                        (conv for conv in self.conversations if conv.get("id") == conversation_id),
                        None
                    )
                    if conversation:
                        selected_conversations.append(conversation)
        
        if not selected_conversations:
            QMessageBox.information(self, "No Selection", "Please select conversations to categorize.")
            return
        
        # Start categorization worker
        self.categorization_progress.setVisible(True)
        self.categorization_progress.setRange(0, 100)
        self.categorization_progress.setValue(0)
        
        self.categorization_worker = CategoryWorker(selected_conversations, self.rules)
        self.categorization_worker.progress.connect(self.categorization_progress.setValue)
        self.categorization_worker.finished.connect(self.on_categorization_finished)
        self.categorization_worker.error.connect(self.on_categorization_error)
        self.categorization_worker.start()
        
        self.categorize_selected_button.setEnabled(False)
    
    def on_categorization_finished(self, categorized: Dict[str, str]):
        """Handle categorization completion."""
        self.categorization_progress.setVisible(False)
        self.categorize_selected_button.setEnabled(True)
        
        # Emit updates for each categorized conversation
        for conversation_id, category in categorized.items():
            self.category_updated.emit(conversation_id, category)
        
        QMessageBox.information(
            self, "Categorization Complete", 
            f"Successfully categorized {len(categorized)} conversations."
        )
        
        # Refresh displays
        self.update_auto_categorization_list()
    
    def on_categorization_error(self, error_message: str):
        """Handle categorization error."""
        self.categorization_progress.setVisible(False)
        self.categorize_selected_button.setEnabled(True)
        
        QMessageBox.critical(self, "Categorization Error", f"Error during categorization: {error_message}")
    
    def update_rules_display(self):
        """Update the rules table display."""
        self.rules_table.setRowCount(len(self.rules))
        
        for row, rule in enumerate(self.rules):
            # Enabled checkbox
            enabled_checkbox = QCheckBox()
            enabled_checkbox.setChecked(rule.enabled)
            self.rules_table.setCellWidget(row, 0, enabled_checkbox)
            
            # Rule name
            name_item = QTableWidgetItem(rule.name)
            self.rules_table.setItem(row, 1, name_item)
            
            # Category
            category_item = QTableWidgetItem(rule.category)
            self.rules_table.setItem(row, 2, category_item)
            
            # Keywords
            keywords_text = ", ".join(rule.keywords)
            keywords_item = QTableWidgetItem(keywords_text)
            self.rules_table.setItem(row, 3, keywords_item)
            
            # Description
            description_item = QTableWidgetItem(rule.description)
            self.rules_table.setItem(row, 4, description_item)
    
    def add_rule(self):
        """Add a new categorization rule."""
        # This would open a dialog to create a new rule
        QMessageBox.information(self, "Add Rule", "Rule creation dialog would open here.")
    
    def edit_rule(self):
        """Edit selected rule."""
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            QMessageBox.information(self, "Edit Rule", f"Edit rule dialog would open for rule {current_row}.")
    
    def delete_rule(self):
        """Delete selected rule."""
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Delete Rule", 
                "Are you sure you want to delete this rule?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                del self.rules[current_row]
                self.update_rules_display()
    
    def export_rules(self):
        """Export categorization rules."""
        QMessageBox.information(self, "Export Rules", "Rules export dialog would open here.")
    
    def import_rules(self):
        """Import categorization rules."""
        QMessageBox.information(self, "Import Rules", "Rules import dialog would open here.")
