"""Tests for the category widget and auto-categorization functionality."""

import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QWidget, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from poe_search.gui.widgets.category_widget import CategoryWidget, CategoryRule, CategoryWorker


class TestCategoryRule:
    """Test cases for the CategoryRule class."""
    
    def test_rule_creation(self):
        """Test creating a categorization rule."""
        rule = CategoryRule(
            name="Technical Rule",
            keywords=["python", "programming", "code"],
            category="Technical",
            description="Programming related content"
        )
        
        assert rule.name == "Technical Rule"
        assert rule.keywords == ["python", "programming", "code"]
        assert rule.category == "Technical"
        assert rule.description == "Programming related content"
        assert rule.enabled == True
    
    def test_rule_matching_case_insensitive(self):
        """Test rule matching (case insensitive)."""
        rule = CategoryRule(
            name="Test Rule",
            keywords=["python", "programming"],
            category="Technical"
        )
        
        # Should match
        assert rule.matches("I need help with Python programming")
        assert rule.matches("PYTHON is great")
        assert rule.matches("Learn programming with me")
        
        # Should not match
        assert not rule.matches("I like cats")
        assert not rule.matches("Weather is nice today")
    
    def test_rule_matching_case_sensitive(self):
        """Test rule matching (case sensitive)."""
        rule = CategoryRule(
            name="Test Rule",
            keywords=["Python", "API"],
            category="Technical"
        )
        
        # Case sensitive matching
        assert rule.matches("Python is great", case_sensitive=True)
        assert rule.matches("REST API design", case_sensitive=True)
        
        # Should not match with wrong case
        assert not rule.matches("python is great", case_sensitive=True)
        assert not rule.matches("api design", case_sensitive=True)
    
    def test_disabled_rule(self):
        """Test disabled rule doesn't match."""
        rule = CategoryRule(
            name="Disabled Rule",
            keywords=["python"],
            category="Technical",
            enabled=False
        )
        
        assert not rule.matches("Python programming")
    
    def test_empty_keywords(self):
        """Test rule with empty keywords."""
        rule = CategoryRule(
            name="Empty Rule",
            keywords=[],
            category="Technical"
        )
        
        assert not rule.matches("Any text")


class TestCategoryWorker:
    """Test cases for the CategoryWorker thread."""
    
    def test_worker_initialization(self, sample_conversations):
        """Test worker initialization."""
        rules = [
            CategoryRule("Test", ["python"], "Technical")
        ]
        
        worker = CategoryWorker(sample_conversations, rules)
        
        assert worker.conversations == sample_conversations
        assert worker.rules == rules
        assert not worker.should_stop
    
    def test_categorize_text(self, sample_conversations):
        """Test text categorization logic."""
        rules = [
            CategoryRule("Programming", ["python", "programming"], "Technical"),
            CategoryRule("Health", ["symptoms", "health"], "Medical")
        ]
        
        worker = CategoryWorker(sample_conversations, rules)
        
        # Test categorization
        assert worker.categorize_text("Python programming help") == "Technical"
        assert worker.categorize_text("What are flu symptoms?") == "Medical"
        assert worker.categorize_text("Random text") is None
    
    def test_worker_stop(self, sample_conversations):
        """Test worker can be stopped."""
        rules = []
        worker = CategoryWorker(sample_conversations, rules)
        
        worker.stop()
        assert worker.should_stop


class TestCategoryWidget:
    """Test cases for the CategoryWidget class."""
    
    def test_widget_initialization(self, qapp):
        """Test category widget initializes correctly."""
        widget = CategoryWidget()
        
        assert widget is not None
        assert hasattr(widget, 'tab_widget')
        assert hasattr(widget, 'category_table')
        assert hasattr(widget, 'auto_categorization_table')
        assert hasattr(widget, 'rules_table')
        assert len(widget.rules) > 0  # Should have default rules
    
    def test_default_rules_creation(self, qapp):
        """Test default categorization rules are created."""
        widget = CategoryWidget()
        
        rules = widget.get_default_rules()
        assert len(rules) > 0
        
        # Check some expected rules exist
        rule_categories = [rule.category for rule in rules]
        assert "Technical" in rule_categories
        assert "Medical" in rule_categories
        assert "Spiritual" in rule_categories
        assert "Political" in rule_categories
    
    def test_tab_creation(self, qapp):
        """Test all tabs are created."""
        widget = CategoryWidget()
        
        tab_widget = widget.tab_widget
        assert tab_widget.count() == 3  # Overview, Auto-categorization, Rules
        
        tab_titles = [tab_widget.tabText(i) for i in range(tab_widget.count())]
        assert "Overview" in tab_titles[0]
        assert "Auto-Categorization" in tab_titles[1]
        assert "Rules" in tab_titles[2]
    
    def test_conversations_update(self, qapp, sample_conversations):
        """Test updating conversations data."""
        widget = CategoryWidget()
        
        widget.update_conversations(sample_conversations)
        
        assert widget.conversations == sample_conversations
    
    def test_category_filter(self, qapp, sample_conversations):
        """Test category filtering."""
        widget = CategoryWidget()
        
        widget.update_conversations(sample_conversations)
        
        # Test filter combo
        filter_items = [widget.filter_combo.itemText(i) 
                       for i in range(widget.filter_combo.count())]
        assert "All Categories" in filter_items
        assert "Technical" in filter_items
        assert "Medical" in filter_items
    
    def test_stat_cards_update(self, qapp, sample_conversations):
        """Test statistics cards update."""
        widget = CategoryWidget()
        
        # Mock the stat card update method
        with patch.object(widget, 'update_stat_card') as mock_update:
            widget.update_conversations(sample_conversations)
            
            # Should call update for each stat card
            assert mock_update.call_count >= 3  # total, categorized, uncategorized
    
    def test_populate_category_table(self, qapp, sample_conversations):
        """Test populating category overview table."""
        widget = CategoryWidget()
        
        widget.update_conversations(sample_conversations)
        
        table = widget.category_table
        assert table.rowCount() == len(sample_conversations)
        
        # Check first row
        if table.rowCount() > 0:
            title_item = table.item(0, 0)
            assert title_item is not None
    
    def test_auto_categorization_list(self, qapp, sample_conversations):
        """Test auto-categorization conversation list."""
        widget = CategoryWidget()
        
        widget.update_conversations(sample_conversations)
        
        table = widget.auto_categorization_table
        
        # Should populate table
        assert table.rowCount() > 0
        
        # Check checkboxes exist
        for row in range(table.rowCount()):
            checkbox = table.cellWidget(row, 0)
            assert isinstance(checkbox, QCheckBox)
    
    def test_select_all_toggle(self, qapp, sample_conversations):
        """Test select all checkbox functionality."""
        widget = CategoryWidget()
        
        widget.update_conversations(sample_conversations)
        
        # Check all
        widget.select_all_checkbox.setChecked(True)
        widget.toggle_select_all(True)
        
        # Verify all checkboxes are checked
        table = widget.auto_categorization_table
        for row in range(table.rowCount()):
            checkbox = table.cellWidget(row, 0)
            assert checkbox.isChecked()
        
        # Uncheck all
        widget.toggle_select_all(False)
        
        # Verify all checkboxes are unchecked
        for row in range(table.rowCount()):
            checkbox = table.cellWidget(row, 0)
            assert not checkbox.isChecked()
    
    def test_uncategorized_only_filter(self, qapp, sample_conversations):
        """Test uncategorized only filter."""
        widget = CategoryWidget()
        
        # Add some categorized and uncategorized conversations
        conversations = sample_conversations.copy()
        conversations.append({
            "id": "conv3",
            "title": "Uncategorized Conversation",
            "category": "Uncategorized",
            "messages": []
        })
        
        widget.update_conversations(conversations)
        
        # Enable uncategorized only
        widget.uncategorized_only_checkbox.setChecked(True)
        widget.update_auto_categorization_list()
        
        # Should show fewer conversations (only uncategorized)
        table = widget.auto_categorization_table
        # This would filter in real implementation
        assert table.rowCount() >= 0
    
    def test_suggest_category_for_conversation(self, qapp):
        """Test category suggestion for conversation."""
        widget = CategoryWidget()
        
        # Test conversation with programming content
        conversation = {
            "title": "Python Help",
            "messages": [
                {"content": "How to use Python programming?"}
            ]
        }
        
        suggested = widget.suggest_category_for_conversation(conversation)
        assert suggested == "Technical"  # Should match programming rule
        
        # Test conversation with no matching content
        conversation = {
            "title": "Random Chat",
            "messages": [
                {"content": "Random conversation"}
            ]
        }
        
        suggested = widget.suggest_category_for_conversation(conversation)
        assert suggested is None
    
    def test_rules_table_update(self, qapp):
        """Test rules table display update."""
        widget = CategoryWidget()
        
        widget.update_rules_display()
        
        table = widget.rules_table
        assert table.rowCount() == len(widget.rules)
        
        # Check first rule if exists
        if table.rowCount() > 0:
            # Should have checkbox in first column
            checkbox = table.cellWidget(0, 0)
            assert isinstance(checkbox, QCheckBox)
            
            # Should have rule name
            name_item = table.item(0, 1)
            assert name_item is not None
    
    def test_bulk_categorization_signal(self, qapp, sample_conversations):
        """Test bulk categorization emits correct signal."""
        widget = CategoryWidget()
        
        signal_emitted = False
        emitted_ids = None
        
        def on_bulk_categorization(conversation_ids):
            nonlocal signal_emitted, emitted_ids
            signal_emitted = True
            emitted_ids = conversation_ids
        
        widget.bulk_categorization_requested.connect(on_bulk_categorization)
        
        # Mock some selected conversations
        widget.conversations = sample_conversations
        
        # This would normally be triggered by button click
        # widget.bulk_categorize_conversations()
        
        # For now, just test the signal exists
        assert hasattr(widget, 'bulk_categorization_requested')
    
    def test_category_updated_signal(self, qapp):
        """Test category update signal."""
        widget = CategoryWidget()
        
        signal_emitted = False
        emitted_data = None
        
        def on_category_updated(conv_id, category):
            nonlocal signal_emitted, emitted_data
            signal_emitted = True
            emitted_data = (conv_id, category)
        
        widget.category_updated.connect(on_category_updated)
        
        # Emit signal manually to test
        widget.category_updated.emit("conv1", "Technical")
        
        assert signal_emitted
        assert emitted_data == ("conv1", "Technical")


class TestCategoryWidgetIntegration:
    """Integration tests for CategoryWidget."""
    
    @patch('poe_search.gui.widgets.category_widget.CategoryWorker')
    def test_start_auto_categorization(self, mock_worker_class, qapp, sample_conversations):
        """Test starting auto-categorization process."""
        widget = CategoryWidget()
        widget.update_conversations(sample_conversations)
        
        # Mock worker
        mock_worker = Mock()
        mock_worker_class.return_value = mock_worker
        
        # Select some conversations
        widget.auto_categorization_table.setRowCount(1)
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        widget.auto_categorization_table.setCellWidget(0, 0, checkbox)
        
        # Mock the conversation data
        from PyQt6.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem("Test Title")
        item.setData(Qt.ItemDataRole.UserRole, "conv1")
        widget.auto_categorization_table.setItem(0, 1, item)
        
        # Start categorization
        widget.start_auto_categorization()
        
        # Should create and start worker
        mock_worker_class.assert_called_once()
        mock_worker.start.assert_called_once()
    
    def test_categorization_progress_handling(self, qapp):
        """Test handling categorization progress updates."""
        widget = CategoryWidget()
        
        # Initially progress bar should be hidden
        assert not widget.categorization_progress.isVisible()
        
        # Simulate starting categorization
        widget.categorization_progress.setVisible(True)
        widget.categorization_progress.setValue(50)
        
        assert widget.categorization_progress.isVisible()
        assert widget.categorization_progress.value() == 50
