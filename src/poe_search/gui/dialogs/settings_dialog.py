"""Settings dialog for Poe Search."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from poe_search.utils.config import PoeSearchConfig

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Settings dialog for configuring Poe Search."""
    
    settings_changed = pyqtSignal(PoeSearchConfig)
    
    def __init__(self, config: PoeSearchConfig, parent=None):
        """Initialize the settings dialog.
        
        Args:
            config: Current configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config.copy()
        self.original_config = config
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.tab_widget.addTab(self.create_api_tab(), "API")
        self.tab_widget.addTab(self.create_gui_tab(), "GUI")
        self.tab_widget.addTab(self.create_search_tab(), "Search")
        self.tab_widget.addTab(self.create_sync_tab(), "Sync")
        self.tab_widget.addTab(self.create_export_tab(), "Export")
        self.tab_widget.addTab(self.create_advanced_tab(), "Advanced")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def create_api_tab(self) -> QWidget:
        """Create the API settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API Type Selection
        api_type_group = QGroupBox("API Configuration")
        api_type_layout = QFormLayout(api_type_group)
        
        self.api_type_combo = QComboBox()
        self.api_type_combo.addItems(["Wrapper API", "Official API"])
        self.api_type_combo.currentTextChanged.connect(self.on_api_type_changed)
        api_type_layout.addRow("API Type:", self.api_type_combo)
        
        # API Type Description
        self.api_description = QLabel()
        self.api_description.setWordWrap(True)
        self.api_description.setStyleSheet("color: #888888; font-size: 11px;")
        api_type_layout.addRow("", self.api_description)
        
        layout.addWidget(api_type_group)
        
        # Wrapper API Settings
        self.wrapper_group = QGroupBox("Wrapper API Settings")
        wrapper_layout = QFormLayout(self.wrapper_group)
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your Poe.com token (p-b cookie value)")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        wrapper_layout.addRow("Poe Token:", self.token_input)
        
        self.token_help = QLabel(
            "Get your token from Poe.com browser cookies (p-b value). "
            "This allows access to your conversation history."
        )
        self.token_help.setWordWrap(True)
        self.token_help.setStyleSheet("color: #888888; font-size: 11px;")
        wrapper_layout.addRow("", self.token_help)
        
        layout.addWidget(self.wrapper_group)
        
        # Official API Settings
        self.official_group = QGroupBox("Official API Settings")
        official_layout = QFormLayout(self.official_group)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Poe API key from poe.com/api_key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        official_layout.addRow("API Key:", self.api_key_input)
        
        self.api_key_help = QLabel(
            "Get your API key from poe.com/api_key. "
            "This allows sending new messages but doesn't provide conversation history."
        )
        self.api_key_help.setWordWrap(True)
        self.api_key_help.setStyleSheet("color: #888888; font-size: 11px;")
        official_layout.addRow("", self.api_key_help)
        
        layout.addWidget(self.official_group)
        
        # Test Connection Button
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_button)
        
        layout.addStretch()
        return widget
    
    def create_gui_tab(self) -> QWidget:
        """Create the GUI settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Window Settings
        window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout(window_group)
        
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(400, 2000)
        self.window_width_spin.setSuffix(" px")
        window_layout.addRow("Window Width:", self.window_width_spin)
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(300, 1500)
        self.window_height_spin.setSuffix(" px")
        window_layout.addRow("Window Height:", self.window_height_spin)
        
        self.remember_position_check = QCheckBox("Remember window position")
        window_layout.addRow("", self.remember_position_check)
        
        self.remember_size_check = QCheckBox("Remember window size")
        window_layout.addRow("", self.remember_size_check)
        
        layout.addWidget(window_group)
        
        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout(display_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System"])
        display_layout.addRow("Theme:", self.theme_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setSuffix(" pt")
        display_layout.addRow("Font Size:", self.font_size_spin)
        
        self.show_toolbar_check = QCheckBox("Show toolbar")
        display_layout.addRow("", self.show_toolbar_check)
        
        self.show_status_check = QCheckBox("Show status bar")
        display_layout.addRow("", self.show_status_check)
        
        layout.addWidget(display_group)
        
        # Auto-refresh Settings
        refresh_group = QGroupBox("Auto-refresh Settings")
        refresh_layout = QFormLayout(refresh_group)
        
        self.auto_refresh_spin = QSpinBox()
        self.auto_refresh_spin.setRange(0, 3600)
        self.auto_refresh_spin.setSuffix(" seconds (0 = disabled)")
        refresh_layout.addRow("Auto-refresh Interval:", self.auto_refresh_spin)
        
        layout.addWidget(refresh_group)
        
        layout.addStretch()
        return widget
    
    def create_search_tab(self) -> QWidget:
        """Create the search settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search Behavior
        behavior_group = QGroupBox("Search Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        self.search_limit_spin = QSpinBox()
        self.search_limit_spin.setRange(10, 1000)
        behavior_layout.addRow("Default Search Limit:", self.search_limit_spin)
        
        self.fuzzy_search_check = QCheckBox("Enable fuzzy search")
        behavior_layout.addRow("", self.fuzzy_search_check)
        
        self.regex_search_check = QCheckBox("Enable regex search")
        behavior_layout.addRow("", self.regex_search_check)
        
        self.case_sensitive_check = QCheckBox("Case sensitive search")
        behavior_layout.addRow("", self.case_sensitive_check)
        
        layout.addWidget(behavior_group)
        
        # Search Scope
        scope_group = QGroupBox("Search Scope")
        scope_layout = QFormLayout(scope_group)
        
        self.search_messages_check = QCheckBox("Search in messages")
        scope_layout.addRow("", self.search_messages_check)
        
        self.search_titles_check = QCheckBox("Search in titles")
        scope_layout.addRow("", self.search_titles_check)
        
        self.highlight_results_check = QCheckBox("Highlight search results")
        scope_layout.addRow("", self.highlight_results_check)
        
        layout.addWidget(scope_group)
        
        # Performance
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)
        
        self.auto_search_spin = QSpinBox()
        self.auto_search_spin.setRange(0, 5000)
        self.auto_search_spin.setSuffix(" ms (0 = disabled)")
        perf_layout.addRow("Auto-search Delay:", self.auto_search_spin)
        
        layout.addWidget(perf_group)
        
        layout.addStretch()
        return widget
    
    def create_sync_tab(self) -> QWidget:
        """Create the sync settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Sync Behavior
        sync_group = QGroupBox("Sync Behavior")
        sync_layout = QFormLayout(sync_group)
        
        self.auto_sync_check = QCheckBox("Auto-sync on startup")
        sync_layout.addRow("", self.auto_sync_check)
        
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setRange(1, 168)
        self.sync_interval_spin.setSuffix(" hours")
        sync_layout.addRow("Sync Interval:", self.sync_interval_spin)
        
        self.sync_days_spin = QSpinBox()
        self.sync_days_spin.setRange(1, 365)
        self.sync_days_spin.setSuffix(" days back")
        sync_layout.addRow("Sync Days Back:", self.sync_days_spin)
        
        layout.addWidget(sync_group)
        
        # Batch Settings
        batch_group = QGroupBox("Batch Settings")
        batch_layout = QFormLayout(batch_group)
        
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(10, 1000)
        batch_layout.addRow("Batch Size:", self.batch_size_spin)
        
        self.retry_failed_check = QCheckBox("Retry failed syncs")
        batch_layout.addRow("", self.retry_failed_check)
        
        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(1, 10)
        batch_layout.addRow("Max Retry Attempts:", self.max_retries_spin)
        
        layout.addWidget(batch_group)
        
        layout.addStretch()
        return widget
    
    def create_export_tab(self) -> QWidget:
        """Create the export settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Export Format
        format_group = QGroupBox("Export Format")
        format_layout = QFormLayout(format_group)
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["JSON", "CSV", "Markdown", "TXT"])
        format_layout.addRow("Default Format:", self.export_format_combo)
        
        self.include_metadata_check = QCheckBox("Include metadata")
        format_layout.addRow("", self.include_metadata_check)
        
        self.include_messages_check = QCheckBox("Include messages")
        format_layout.addRow("", self.include_messages_check)
        
        self.compress_exports_check = QCheckBox("Compress exports")
        format_layout.addRow("", self.compress_exports_check)
        
        layout.addWidget(format_group)
        
        # Export Location
        location_group = QGroupBox("Export Location")
        location_layout = QFormLayout(location_group)
        
        location_widget = QWidget()
        location_widget_layout = QHBoxLayout(location_widget)
        location_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        self.export_directory_input = QLineEdit()
        location_widget_layout.addWidget(self.export_directory_input)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_export_directory)
        location_widget_layout.addWidget(self.browse_button)
        
        location_layout.addRow("Default Directory:", location_widget)
        
        self.filename_template_input = QLineEdit()
        self.filename_template_input.setPlaceholderText("{date}_{bot}_{title}")
        location_layout.addRow("Filename Template:", self.filename_template_input)
        
        layout.addWidget(location_group)
        
        layout.addStretch()
        return widget
    
    def create_advanced_tab(self) -> QWidget:
        """Create the advanced settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Rate Limiting
        rate_group = QGroupBox("Rate Limiting")
        rate_layout = QFormLayout(rate_group)
        
        self.enable_rate_limit_check = QCheckBox("Enable rate limiting")
        rate_layout.addRow("", self.enable_rate_limit_check)
        
        self.max_calls_spin = QSpinBox()
        self.max_calls_spin.setRange(1, 100)
        self.max_calls_spin.setSuffix(" calls per minute")
        rate_layout.addRow("Max Calls:", self.max_calls_spin)
        
        self.retry_attempts_spin = QSpinBox()
        self.retry_attempts_spin.setRange(1, 10)
        rate_layout.addRow("Retry Attempts:", self.retry_attempts_spin)
        
        self.base_delay_spin = QSpinBox()
        self.base_delay_spin.setRange(1, 60)
        self.base_delay_spin.setSuffix(" seconds")
        rate_layout.addRow("Base Delay:", self.base_delay_spin)
        
        self.max_delay_spin = QSpinBox()
        self.max_delay_spin.setRange(10, 300)
        self.max_delay_spin.setSuffix(" seconds")
        rate_layout.addRow("Max Delay:", self.max_delay_spin)
        
        self.show_warnings_check = QCheckBox("Show rate limit warnings")
        rate_layout.addRow("", self.show_warnings_check)
        
        self.prompt_costs_check = QCheckBox("Prompt for token costs")
        rate_layout.addRow("", self.prompt_costs_check)
        
        layout.addWidget(rate_group)
        
        # Logging
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        self.debug_mode_check = QCheckBox("Enable debug mode")
        logging_layout.addRow("", self.debug_mode_check)
        
        layout.addWidget(logging_group)
        
        # Cache
        cache_group = QGroupBox("Cache")
        cache_layout = QFormLayout(cache_group)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setSuffix(" MB")
        cache_layout.addRow("Cache Size:", self.cache_size_spin)
        
        layout.addWidget(cache_group)
        
        layout.addStretch()
        return widget
    
    def on_api_type_changed(self, api_type_text: str):
        """Handle API type change."""
        if api_type_text == "Wrapper API":
            self.config.set_api_type("wrapper")
            self.wrapper_group.setVisible(True)
            self.official_group.setVisible(False)
            self.api_description.setText(
                "Wrapper API uses browser cookies to access your conversation history. "
                "No API key required, but limited to existing conversations."
            )
        else:
            self.config.set_api_type("official")
            self.wrapper_group.setVisible(False)
            self.official_group.setVisible(True)
            self.api_description.setText(
                "Official API uses API keys for new bot interactions. "
                "Requires API key from poe.com/api_key, but doesn't provide conversation history."
            )
    
    def load_settings(self):
        """Load current settings into the UI."""
        # API Settings
        api_type = self.config.get_api_type()
        if api_type == "official":
            self.api_type_combo.setCurrentText("Official API")
        else:
            self.api_type_combo.setCurrentText("Wrapper API")
        
        self.token_input.setText(self.config.poe_token)
        self.api_key_input.setText(self.config.poe_api_key)
        
        # GUI Settings
        self.window_width_spin.setValue(self.config.gui.window_width)
        self.window_height_spin.setValue(self.config.gui.window_height)
        self.remember_position_check.setChecked(self.config.gui.remember_window_position)
        self.remember_size_check.setChecked(self.config.gui.remember_window_size)
        self.theme_combo.setCurrentText(self.config.gui.theme)
        self.font_size_spin.setValue(self.config.gui.font_size)
        self.show_toolbar_check.setChecked(self.config.gui.show_toolbar)
        self.show_status_check.setChecked(self.config.gui.show_status_bar)
        self.auto_refresh_spin.setValue(self.config.gui.auto_refresh_interval)
        
        # Search Settings
        self.search_limit_spin.setValue(self.config.search.default_search_limit)
        self.fuzzy_search_check.setChecked(self.config.search.enable_fuzzy_search)
        self.regex_search_check.setChecked(self.config.search.enable_regex_search)
        self.case_sensitive_check.setChecked(self.config.search.case_sensitive)
        self.search_messages_check.setChecked(self.config.search.search_in_messages)
        self.search_titles_check.setChecked(self.config.search.search_in_titles)
        self.highlight_results_check.setChecked(self.config.search.highlight_search_results)
        self.auto_search_spin.setValue(self.config.search.auto_search_delay)
        
        # Sync Settings
        self.auto_sync_check.setChecked(self.config.sync.auto_sync_on_startup)
        self.sync_interval_spin.setValue(self.config.sync.sync_interval)
        self.sync_days_spin.setValue(self.config.sync.sync_days_back)
        self.batch_size_spin.setValue(self.config.sync.sync_batch_size)
        self.retry_failed_check.setChecked(self.config.sync.retry_failed_syncs)
        self.max_retries_spin.setValue(self.config.sync.max_retry_attempts)
        
        # Export Settings
        self.export_format_combo.setCurrentText(self.config.export.default_export_format)
        self.include_metadata_check.setChecked(self.config.export.include_metadata)
        self.include_messages_check.setChecked(self.config.export.include_messages)
        self.compress_exports_check.setChecked(self.config.export.compress_exports)
        self.export_directory_input.setText(self.config.export.default_export_directory)
        self.filename_template_input.setText(self.config.export.export_filename_template)
        
        # Advanced Settings
        self.enable_rate_limit_check.setChecked(self.config.rate_limit.enable_rate_limiting)
        self.max_calls_spin.setValue(self.config.rate_limit.max_calls_per_minute)
        self.retry_attempts_spin.setValue(self.config.rate_limit.retry_attempts)
        self.base_delay_spin.setValue(self.config.rate_limit.base_delay_seconds)
        self.max_delay_spin.setValue(self.config.rate_limit.max_delay_seconds)
        self.show_warnings_check.setChecked(self.config.rate_limit.show_rate_limit_warnings)
        self.prompt_costs_check.setChecked(self.config.rate_limit.prompt_for_token_costs)
        self.log_level_combo.setCurrentText(self.config.log_level)
        self.debug_mode_check.setChecked(self.config.enable_debug_mode)
        self.cache_size_spin.setValue(self.config.cache_size_mb)
        
        # Trigger API type change to update UI
        self.on_api_type_changed(self.api_type_combo.currentText())
    
    def save_settings(self):
        """Save settings from the UI."""
        try:
            # API Settings
            self.config.poe_token = self.token_input.text()
            self.config.poe_api_key = self.api_key_input.text()
            
            # GUI Settings
            self.config.gui.window_width = self.window_width_spin.value()
            self.config.gui.window_height = self.window_height_spin.value()
            self.config.gui.remember_window_position = self.remember_position_check.isChecked()
            self.config.gui.remember_window_size = self.remember_size_check.isChecked()
            self.config.gui.theme = self.theme_combo.currentText()
            self.config.gui.font_size = self.font_size_spin.value()
            self.config.gui.show_toolbar = self.show_toolbar_check.isChecked()
            self.config.gui.show_status_bar = self.show_status_check.isChecked()
            self.config.gui.auto_refresh_interval = self.auto_refresh_spin.value()
            
            # Search Settings
            self.config.search.default_search_limit = self.search_limit_spin.value()
            self.config.search.enable_fuzzy_search = self.fuzzy_search_check.isChecked()
            self.config.search.enable_regex_search = self.regex_search_check.isChecked()
            self.config.search.case_sensitive = self.case_sensitive_check.isChecked()
            self.config.search.search_in_messages = self.search_messages_check.isChecked()
            self.config.search.search_in_titles = self.search_titles_check.isChecked()
            self.config.search.highlight_search_results = self.highlight_results_check.isChecked()
            self.config.search.auto_search_delay = self.auto_search_spin.value()
            
            # Sync Settings
            self.config.sync.auto_sync_on_startup = self.auto_sync_check.isChecked()
            self.config.sync.sync_interval = self.sync_interval_spin.value()
            self.config.sync.sync_days_back = self.sync_days_spin.value()
            self.config.sync.sync_batch_size = self.batch_size_spin.value()
            self.config.sync.retry_failed_syncs = self.retry_failed_check.isChecked()
            self.config.sync.max_retry_attempts = self.max_retries_spin.value()
            
            # Export Settings
            self.config.export.default_export_format = self.export_format_combo.currentText()
            self.config.export.include_metadata = self.include_metadata_check.isChecked()
            self.config.export.include_messages = self.include_messages_check.isChecked()
            self.config.export.compress_exports = self.compress_exports_check.isChecked()
            self.config.export.default_export_directory = self.export_directory_input.text()
            self.config.export.export_filename_template = self.filename_template_input.text()
            
            # Advanced Settings
            self.config.rate_limit.enable_rate_limiting = self.enable_rate_limit_check.isChecked()
            self.config.rate_limit.max_calls_per_minute = self.max_calls_spin.value()
            self.config.rate_limit.retry_attempts = self.retry_attempts_spin.value()
            self.config.rate_limit.base_delay_seconds = self.base_delay_spin.value()
            self.config.rate_limit.max_delay_seconds = self.max_delay_spin.value()
            self.config.rate_limit.show_rate_limit_warnings = self.show_warnings_check.isChecked()
            self.config.rate_limit.prompt_for_token_costs = self.prompt_costs_check.isChecked()
            self.config.log_level = self.log_level_combo.currentText()
            self.config.enable_debug_mode = self.debug_mode_check.isChecked()
            self.config.cache_size_mb = self.cache_size_spin.value()
            
            # Emit signal
            self.settings_changed.emit(self.config)
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = PoeSearchConfig()
            self.load_settings()
    
    def test_connection(self):
        """Test the current API connection."""
        try:
            from poe_search.client import PoeSearchClient

            # Create temporary client with current settings
            temp_config = self.config.copy()
            temp_config.poe_token = self.token_input.text()
            temp_config.poe_api_key = self.api_key_input.text()
            
            if self.api_type_combo.currentText() == "Official API":
                temp_config.set_api_type("official")
            else:
                temp_config.set_api_type("wrapper")
            
            client = PoeSearchClient(config=temp_config)
            result = client.test_api_connection()
            
            if result.get('success'):
                QMessageBox.information(
                    self, "Connection Test",
                    f"✅ Connection successful!\n\n"
                    f"API Type: {result.get('api_type', 'Unknown')}\n"
                    f"Status: Connected"
                )
            else:
                QMessageBox.warning(
                    self, "Connection Test",
                    f"❌ Connection failed!\n\n"
                    f"Error: {result.get('error', 'Unknown error')}\n"
                    f"API Type: {result.get('api_type', 'Unknown')}"
                )
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            QMessageBox.critical(
                self, "Connection Test",
                f"❌ Connection test failed!\n\nError: {e}"
            )
    
    def browse_export_directory(self):
        """Browse for export directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Export Directory"
        )
        if directory:
            self.export_directory_input.setText(directory)
