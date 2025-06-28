"""Tests for the main GUI application window."""

import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from poe_search.gui.main_window import MainWindow


class TestMainWindow:
    """Test cases for the MainWindow class."""
    
    def test_main_window_initialization(self, qapp, mock_config):
        """Test main window initializes correctly."""
        window = MainWindow(mock_config)
        
        assert window.windowTitle() == "Poe Search"
        assert window.isVisible() == False  # Window not shown yet
        assert window.config == mock_config
        
        # Check that widgets are created
        assert hasattr(window, 'tab_widget')
        assert hasattr(window, 'search_widget')
        assert hasattr(window, 'conversation_widget')
        assert hasattr(window, 'analytics_widget')
        assert hasattr(window, 'category_widget')
    
    def test_tab_widget_creation(self, qapp, mock_config):
        """Test that all tabs are created correctly."""
        window = MainWindow(mock_config)
        
        tab_widget = window.tab_widget
        assert tab_widget.count() == 4  # Search, Conversation, Categories, Analytics
        
        # Check tab titles
        tab_titles = [tab_widget.tabText(i) for i in range(tab_widget.count())]
        assert "Search" in tab_titles[0]
        assert "Conversation" in tab_titles[1]
        assert "Categories" in tab_titles[2]
        assert "Analytics" in tab_titles[3]
    
    def test_menu_bar_creation(self, qapp, mock_config):
        """Test that menu bar is created with correct items."""
        window = MainWindow(mock_config)
        
        menubar = window.menuBar()
        actions = menubar.actions()
        
        # Check that we have File, Edit, View, Tools, Help menus
        menu_titles = [action.text() for action in actions]
        assert "&File" in menu_titles
        assert "&Edit" in menu_titles
        assert "&View" in menu_titles
        assert "&Tools" in menu_titles
        assert "&Help" in menu_titles
    
    def test_status_bar_creation(self, qapp, mock_config):
        """Test that status bar is created with labels."""
        window = MainWindow(mock_config)
        
        status_bar = window.statusBar()
        assert status_bar is not None
        
        # Check that status labels exist
        assert hasattr(window, 'status_label')
        assert hasattr(window, 'connection_label')
        assert hasattr(window, 'db_label')
    
    @patch('poe_search.gui.main_window.PoeSearchClient')
    def test_client_setup_with_token(self, mock_client_class, qapp, mock_config):
        """Test client setup with valid token."""
        mock_config['token'] = 'valid_token'
        window = MainWindow(mock_config)
        
        # Should attempt to create client
        mock_client_class.assert_called_once()
    
    def test_client_setup_without_token(self, qapp):
        """Test client setup without token."""
        config = {"database_url": "test.db"}  # No token
        
        with patch.object(MainWindow, 'show_token_setup_dialog') as mock_dialog:
            window = MainWindow(config)
            # Should show token setup dialog
            mock_dialog.assert_called_once()
    
    def test_tab_switching(self, qapp, mock_config):
        """Test switching between tabs."""
        window = MainWindow(mock_config)
        
        # Start with first tab
        assert window.tab_widget.currentIndex() == 0
        
        # Switch to analytics tab
        window.tab_widget.setCurrentIndex(3)
        assert window.tab_widget.currentIndex() == 3
    
    def test_search_widget_connection(self, qapp, mock_config):
        """Test that search widget signals are connected."""
        window = MainWindow(mock_config)
        
        # Check that search widget has the right connections
        search_widget = window.search_widget
        assert search_widget is not None
        
        # Test search signal connection (would need to emit signal to test fully)
        assert hasattr(search_widget, 'search_requested')
        assert hasattr(search_widget, 'conversation_selected')
    
    def test_conversation_widget_connection(self, qapp, mock_config):
        """Test that conversation widget signals are connected."""
        window = MainWindow(mock_config)
        
        conversation_widget = window.conversation_widget
        assert conversation_widget is not None
        
        # Check signal existence
        assert hasattr(conversation_widget, 'category_changed')
        assert hasattr(conversation_widget, 'export_requested')
    
    def test_category_widget_connection(self, qapp, mock_config):
        """Test that category widget signals are connected."""
        window = MainWindow(mock_config)
        
        category_widget = window.category_widget
        assert category_widget is not None
        
        # Check signal existence
        assert hasattr(category_widget, 'category_updated')
        assert hasattr(category_widget, 'bulk_categorization_requested')
    
    def test_window_geometry(self, qapp, mock_config):
        """Test window geometry settings."""
        window = MainWindow(mock_config)
        
        # Check initial size
        geometry = window.geometry()
        assert geometry.width() >= 1000  # Minimum width
        assert geometry.height() >= 700   # Minimum height
        
        # Check minimum size
        min_size = window.minimumSize()
        assert min_size.width() == 1000
        assert min_size.height() == 700
    
    def test_progress_bar_initially_hidden(self, qapp, mock_config):
        """Test that progress bar is initially hidden."""
        window = MainWindow(mock_config)
        
        assert hasattr(window, 'progress_bar')
        assert not window.progress_bar.isVisible()
    
    @patch('poe_search.gui.main_window.QMessageBox')
    def test_show_about_dialog(self, mock_msgbox, qapp, mock_config):
        """Test showing about dialog."""
        window = MainWindow(mock_config)
        
        window.show_about()
        
        # Should show message box
        mock_msgbox.about.assert_called_once()
    
    def test_window_close_event(self, qapp, mock_config):
        """Test window close event handling."""
        window = MainWindow(mock_config)
        
        # Should be able to close without errors
        window.close()
        assert True  # If we get here, no exception was raised


class TestMainWindowIntegration:
    """Integration tests for MainWindow with other components."""
    
    def test_search_to_conversation_flow(self, qapp, mock_config, sample_conversations):
        """Test the flow from search to viewing a conversation."""
        window = MainWindow(mock_config)
        
        # Mock search results
        with patch.object(window, 'perform_search') as mock_search:
            window.search_widget.search_requested.emit({"query": "test"})
            mock_search.assert_called_once()
        
        # Mock conversation selection
        with patch.object(window, 'show_conversation') as mock_show:
            window.search_widget.conversation_selected.emit("conv1")
            mock_show.assert_called_once_with("conv1")
    
    def test_category_update_flow(self, qapp, mock_config):
        """Test category update flow."""
        window = MainWindow(mock_config)
        
        # Mock category update
        with patch.object(window, 'update_conversation_category') as mock_update:
            window.category_widget.category_updated.emit("conv1", "Technical")
            mock_update.assert_called_once_with("conv1", "Technical")
    
    def test_analytics_refresh_flow(self, qapp, mock_config):
        """Test analytics refresh flow."""
        window = MainWindow(mock_config)
        
        # Mock analytics refresh
        with patch.object(window, 'refresh_analytics') as mock_refresh:
            window.analytics_widget.refresh_requested.emit()
            mock_refresh.assert_called_once()
