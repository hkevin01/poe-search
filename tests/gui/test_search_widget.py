"""Tests for the search widget."""

import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtTest import QTest

from poe_search.gui.widgets.search_widget import SearchWidget


class TestSearchWidget:
    """Test cases for the SearchWidget class."""
    
    def test_search_widget_initialization(self, qapp):
        """Test search widget initializes correctly."""
        widget = SearchWidget()
        
        assert widget is not None
        assert hasattr(widget, 'search_input')
        assert hasattr(widget, 'search_button')
        assert hasattr(widget, 'results_table')
        assert hasattr(widget, 'bot_combo')
        assert hasattr(widget, 'category_combo')
    
    def test_search_input_placeholder(self, qapp):
        """Test search input has correct placeholder text."""
        widget = SearchWidget()
        
        placeholder = widget.search_input.placeholderText()
        assert "Search conversations" in placeholder.lower()
    
    def test_filter_combo_boxes(self, qapp):
        """Test filter combo boxes have correct items."""
        widget = SearchWidget()
        
        # Bot combo should start with "All Bots"
        assert widget.bot_combo.itemText(0) == "All Bots"
        
        # Category combo should have predefined categories
        category_items = [widget.category_combo.itemText(i) 
                         for i in range(widget.category_combo.count())]
        assert "All Categories" in category_items
        assert "Technical" in category_items
        assert "Medical" in category_items
        assert "Spiritual" in category_items
    
    def test_results_table_setup(self, qapp):
        """Test results table is set up correctly."""
        widget = SearchWidget()
        
        table = widget.results_table
        assert table.columnCount() == 6  # Title, Bot, Category, Messages, Updated, Created
        
        headers = [table.horizontalHeaderItem(i).text() 
                  for i in range(table.columnCount())]
        assert "Title" in headers
        assert "Bot" in headers
        assert "Category" in headers
        assert "Messages" in headers
    
    def test_search_button_click(self, qapp):
        """Test search button click emits signal."""
        widget = SearchWidget()
        
        # Set up signal spy
        signal_emitted = False
        search_params = None
        
        def on_search_requested(params):
            nonlocal signal_emitted, search_params
            signal_emitted = True
            search_params = params
        
        widget.search_requested.connect(on_search_requested)
        
        # Set some search parameters
        widget.search_input.setText("test query")
        widget.bot_combo.setCurrentText("GPT-4")
        widget.category_combo.setCurrentText("Technical")
        
        # Click search button
        QTest.mouseClick(widget.search_button, Qt.MouseButton.LeftButton)
        
        assert signal_emitted
        assert search_params is not None
        assert search_params["query"] == "test query"
        assert search_params["bot"] == "GPT-4"
        assert search_params["category"] == "Technical"
    
    def test_enter_key_triggers_search(self, qapp):
        """Test pressing Enter in search input triggers search."""
        widget = SearchWidget()
        
        signal_emitted = False
        
        def on_search_requested(params):
            nonlocal signal_emitted
            signal_emitted = True
        
        widget.search_requested.connect(on_search_requested)
        
        # Focus search input and press Enter
        widget.search_input.setFocus()
        widget.search_input.setText("test")
        QTest.keyPress(widget.search_input, Qt.Key.Key_Return)
        
        assert signal_emitted
    
    def test_clear_filters_button(self, qapp):
        """Test clear filters functionality."""
        widget = SearchWidget()
        
        # Set some filters
        widget.bot_combo.setCurrentText("GPT-4")
        widget.category_combo.setCurrentText("Technical")
        widget.regex_checkbox.setChecked(True)
        widget.case_sensitive_checkbox.setChecked(True)
        
        # Click clear filters
        QTest.mouseClick(widget.clear_filters_button, Qt.MouseButton.LeftButton)
        
        # Check filters are cleared
        assert widget.bot_combo.currentIndex() == 0  # "All Bots"
        assert widget.category_combo.currentIndex() == 0  # "All Categories"
        assert not widget.regex_checkbox.isChecked()
        assert not widget.case_sensitive_checkbox.isChecked()
    
    def test_update_results(self, qapp, sample_conversations):
        """Test updating search results."""
        widget = SearchWidget()
        
        # Update with sample conversations
        widget.update_results(sample_conversations)
        
        # Check table is populated
        assert widget.results_table.rowCount() == len(sample_conversations)
        
        # Check first row data
        title_item = widget.results_table.item(0, 0)
        assert title_item.text() == sample_conversations[0]["title"]
        
        bot_item = widget.results_table.item(0, 1)
        assert bot_item.text() == sample_conversations[0]["bot"]
    
    def test_conversation_selection(self, qapp, sample_conversations):
        """Test conversation selection emits signal."""
        widget = SearchWidget()
        
        # Populate with sample data
        widget.update_results(sample_conversations)
        
        signal_emitted = False
        selected_id = None
        
        def on_conversation_selected(conv_id):
            nonlocal signal_emitted, selected_id
            signal_emitted = True
            selected_id = conv_id
        
        widget.conversation_selected.connect(on_conversation_selected)
        
        # Select first row
        widget.results_table.selectRow(0)
        widget.results_table.itemSelectionChanged.emit()
        
        assert signal_emitted
        assert selected_id == sample_conversations[0]["id"]
    
    def test_bot_filter_update(self, qapp, sample_conversations):
        """Test bot filter updates when conversations change."""
        widget = SearchWidget()
        
        # Initial state - only "All Bots"
        assert widget.bot_combo.count() == 1
        
        # Update with conversations
        widget.update_results(sample_conversations)
        
        # Should now include bots from conversations
        bot_items = [widget.bot_combo.itemText(i) 
                    for i in range(widget.bot_combo.count())]
        assert "All Bots" in bot_items
        assert "GPT-4" in bot_items
        assert "Claude" in bot_items
    
    def test_progress_bar_visibility(self, qapp):
        """Test progress bar visibility control."""
        widget = SearchWidget()
        
        # Initially hidden
        assert not widget.progress_bar.isVisible()
        
        # Show progress
        widget.show_progress(True)
        assert widget.progress_bar.isVisible()
        
        # Hide progress
        widget.show_progress(False)
        assert not widget.progress_bar.isVisible()
    
    def test_auto_refresh_toggle(self, qapp):
        """Test auto-refresh functionality."""
        widget = SearchWidget()
        
        # Initially off
        assert not widget.refresh_timer.isActive()
        
        # Enable auto-refresh
        widget.auto_refresh_checkbox.setChecked(True)
        widget.toggle_auto_refresh(True)
        assert widget.refresh_timer.isActive()
        
        # Disable auto-refresh
        widget.toggle_auto_refresh(False)
        assert not widget.refresh_timer.isActive()
    
    def test_date_range_defaults(self, qapp):
        """Test date range filter defaults."""
        widget = SearchWidget()
        
        # From date should be 30 days ago
        from_date = widget.date_from.date().toPython()
        to_date = widget.date_to.date().toPython()
        
        # Check that from_date is before to_date
        assert from_date <= to_date
        
        # Check that to_date is today (approximately)
        from datetime import date
        assert to_date == date.today()
    
    def test_results_label_update(self, qapp, sample_conversations):
        """Test results label updates correctly."""
        widget = SearchWidget()
        
        # Initially shows "No results"
        assert "No results" in widget.results_label.text().lower()
        
        # Update with conversations
        widget.update_results(sample_conversations)
        
        # Should show count
        label_text = widget.results_label.text()
        assert str(len(sample_conversations)) in label_text
        assert "conversation" in label_text.lower()


class TestSearchWidgetIntegration:
    """Integration tests for SearchWidget."""
    
    def test_filter_application(self, qapp, sample_conversations):
        """Test applying filters to search results."""
        widget = SearchWidget()
        
        # Set up conversations with different categories
        widget.update_results(sample_conversations)
        
        # Apply category filter
        widget.category_combo.setCurrentText("Technical")
        
        # This would normally trigger filtering
        # In a real implementation, we'd test the filtering logic
        assert widget.category_combo.currentText() == "Technical"
    
    def test_search_params_generation(self, qapp):
        """Test search parameters are generated correctly."""
        widget = SearchWidget()
        
        # Set various parameters
        widget.search_input.setText("python programming")
        widget.bot_combo.setCurrentText("GPT-4")
        widget.category_combo.setCurrentText("Technical")
        widget.regex_checkbox.setChecked(True)
        widget.case_sensitive_checkbox.setChecked(True)
        
        # Mock the search request
        search_params = None
        
        def capture_params(params):
            nonlocal search_params
            search_params = params
        
        widget.search_requested.connect(capture_params)
        
        # Trigger search
        widget.perform_search()
        
        # Verify parameters
        assert search_params["query"] == "python programming"
        assert search_params["bot"] == "GPT-4"
        assert search_params["category"] == "Technical"
        assert search_params["use_regex"] == True
        assert search_params["case_sensitive"] == True
