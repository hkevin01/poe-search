"""Settings dialog."""

from typing import Dict, Any
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox,
    QComboBox, QFileDialog, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    def __init__(self, config: Dict[str, Any], parent=None):
        """Initialize the settings dialog.
        
        Args:
            config: Current configuration
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.config = config.copy()
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # General tab
        self.setup_general_tab()
        
        # Database tab
        self.setup_database_tab()
        
        # Search tab
        self.setup_search_tab()
        
        # Advanced tab
        self.setup_advanced_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def setup_general_tab(self):
        """Set up the general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Authentication group
        auth_group = QGroupBox("Authentication")
        auth_layout = QFormLayout(auth_group)
        
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        auth_layout.addRow("Poe Token:", self.token_input)
        
        layout.addWidget(auth_group)
        
        # UI preferences group
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Auto"])
        ui_layout.addRow("Theme:", self.theme_combo)
        
        self.auto_refresh_check = QCheckBox("Auto-refresh data")
        ui_layout.addRow("", self.auto_refresh_check)
        
        self.confirm_delete_check = QCheckBox("Confirm before deleting")
        ui_layout.addRow("", self.confirm_delete_check)
        
        layout.addWidget(ui_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "General")
    
    def setup_database_tab(self):
        """Set up the database settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Database group
        db_group = QGroupBox("Database")
        db_layout = QFormLayout(db_group)
        
        # Database path
        db_path_layout = QHBoxLayout()
        self.db_path_input = QLineEdit()
        db_path_layout.addWidget(self.db_path_input)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_database_path)
        db_path_layout.addWidget(browse_button)
        
        db_layout.addRow("Database Path:", db_path_layout)
        
        # Backup settings
        self.auto_backup_check = QCheckBox("Enable automatic backups")
        db_layout.addRow("", self.auto_backup_check)
        
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 30)
        self.backup_interval_spin.setSuffix(" days")
        db_layout.addRow("Backup Interval:", self.backup_interval_spin)
        
        layout.addWidget(db_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "Database")
    
    def setup_search_tab(self):
        """Set up the search settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search group
        search_group = QGroupBox("Search")
        search_layout = QFormLayout(search_group)
        
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(10, 10000)
        self.max_results_spin.setValue(100)
        search_layout.addRow("Max Results:", self.max_results_spin)
        
        self.case_sensitive_check = QCheckBox("Case sensitive search")
        search_layout.addRow("", self.case_sensitive_check)
        
        self.regex_check = QCheckBox("Enable regex search")
        search_layout.addRow("", self.regex_check)
        
        self.highlight_results_check = QCheckBox("Highlight search terms")
        search_layout.addRow("", self.highlight_results_check)
        
        layout.addWidget(search_group)
        
        # Indexing group
        index_group = QGroupBox("Indexing")
        index_layout = QFormLayout(index_group)
        
        self.auto_index_check = QCheckBox("Auto-index new conversations")
        index_layout.addRow("", self.auto_index_check)
        
        self.index_interval_spin = QSpinBox()
        self.index_interval_spin.setRange(1, 60)
        self.index_interval_spin.setSuffix(" minutes")
        index_layout.addRow("Index Interval:", self.index_interval_spin)
        
        layout.addWidget(index_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "Search")
    
    def setup_advanced_tab(self):
        """Set up the advanced settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Logging group
        log_group = QGroupBox("Logging")
        log_layout = QFormLayout(log_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        log_layout.addRow("Log Level:", self.log_level_combo)
        
        self.log_to_file_check = QCheckBox("Log to file")
        log_layout.addRow("", self.log_to_file_check)
        
        layout.addWidget(log_group)
        
        # Performance group
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setSuffix(" MB")
        perf_layout.addRow("Cache Size:", self.cache_size_spin)
        
        self.parallel_requests_spin = QSpinBox()
        self.parallel_requests_spin.setRange(1, 10)
        perf_layout.addRow("Parallel Requests:", self.parallel_requests_spin)
        
        layout.addWidget(perf_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "Advanced")
    
    def browse_database_path(self):
        """Browse for database path."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose Database Path",
            str(Path.home() / "poe_search.db"),
            "Database Files (*.db);;All Files (*)"
        )
        
        if path:
            self.db_path_input.setText(path)
    
    def load_config(self):
        """Load configuration into UI."""
        # General
        self.token_input.setText(self.config.get("token", ""))
        theme = self.config.get("theme", "Dark")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.auto_refresh_check.setChecked(self.config.get("auto_refresh", True))
        self.confirm_delete_check.setChecked(self.config.get("confirm_delete", True))
        
        # Database
        self.db_path_input.setText(self.config.get("database_url", ""))
        self.auto_backup_check.setChecked(self.config.get("auto_backup", False))
        self.backup_interval_spin.setValue(self.config.get("backup_interval", 7))
        
        # Search
        self.max_results_spin.setValue(self.config.get("max_results", 100))
        self.case_sensitive_check.setChecked(self.config.get("case_sensitive", False))
        self.regex_check.setChecked(self.config.get("regex_enabled", False))
        self.highlight_results_check.setChecked(self.config.get("highlight_results", True))
        self.auto_index_check.setChecked(self.config.get("auto_index", True))
        self.index_interval_spin.setValue(self.config.get("index_interval", 15))
        
        # Advanced
        log_level = self.config.get("log_level", "INFO")
        index = self.log_level_combo.findText(log_level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
        
        self.log_to_file_check.setChecked(self.config.get("log_to_file", False))
        self.cache_size_spin.setValue(self.config.get("cache_size", 100))
        self.parallel_requests_spin.setValue(self.config.get("parallel_requests", 3))
    
    def get_config(self) -> Dict[str, Any]:
        """Get the updated configuration.
        
        Returns:
            Updated configuration dictionary
        """
        # Update config with UI values
        self.config["token"] = self.token_input.text()
        self.config["theme"] = self.theme_combo.currentText()
        self.config["auto_refresh"] = self.auto_refresh_check.isChecked()
        self.config["confirm_delete"] = self.confirm_delete_check.isChecked()
        
        self.config["database_url"] = self.db_path_input.text()
        self.config["auto_backup"] = self.auto_backup_check.isChecked()
        self.config["backup_interval"] = self.backup_interval_spin.value()
        
        self.config["max_results"] = self.max_results_spin.value()
        self.config["case_sensitive"] = self.case_sensitive_check.isChecked()
        self.config["regex_enabled"] = self.regex_check.isChecked()
        self.config["highlight_results"] = self.highlight_results_check.isChecked()
        self.config["auto_index"] = self.auto_index_check.isChecked()
        self.config["index_interval"] = self.index_interval_spin.value()
        
        self.config["log_level"] = self.log_level_combo.currentText()
        self.config["log_to_file"] = self.log_to_file_check.isChecked()
        self.config["cache_size"] = self.cache_size_spin.value()
        self.config["parallel_requests"] = self.parallel_requests_spin.value()
        
        return self.config
