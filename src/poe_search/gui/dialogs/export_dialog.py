"""Export dialog."""

from typing import Dict, Any, List
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QSpinBox, QDateEdit, QTextEdit, QFileDialog, QListWidget,
    QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, QDate


class ExportDialog(QDialog):
    """Dialog for exporting conversations."""
    
    def __init__(self, parent=None):
        """Initialize the export dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.export_config = {}
        
        self.setWindowTitle("Export Conversations")
        self.setModal(True)
        self.resize(650, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Export format group
        format_group = QGroupBox("Export Format")
        format_layout = QFormLayout(format_group)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JSON", "CSV", "Markdown", "HTML", "Text"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addRow("Format:", self.format_combo)
        
        layout.addWidget(format_group)
        
        # Output settings group
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)
        
        # Output path
        output_path_layout = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Choose output file...")
        output_path_layout.addWidget(self.output_path_input)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_output_path)
        output_path_layout.addWidget(browse_button)
        
        output_layout.addRow("Output File:", output_path_layout)
        
        # Compression
        self.compress_check = QCheckBox("Compress output")
        output_layout.addRow("", self.compress_check)
        
        layout.addWidget(output_group)
        
        # Filter settings group
        filter_group = QGroupBox("Filters")
        filter_layout = QFormLayout(filter_group)
        
        # Date range
        self.use_date_filter_check = QCheckBox("Filter by date range")
        self.use_date_filter_check.toggled.connect(self.toggle_date_filter)
        filter_layout.addRow("", self.use_date_filter_check)
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_date_edit.setEnabled(False)
        filter_layout.addRow("Start Date:", self.start_date_edit)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setEnabled(False)
        filter_layout.addRow("End Date:", self.end_date_edit)
        
        # Categories
        self.use_category_filter_check = QCheckBox("Filter by categories")
        self.use_category_filter_check.toggled.connect(self.toggle_category_filter)
        filter_layout.addRow("", self.use_category_filter_check)
        
        self.category_list = QListWidget()
        self.category_list.setMaximumHeight(100)
        self.category_list.setEnabled(False)
        self.populate_categories()
        filter_layout.addRow("Categories:", self.category_list)
        
        # Search query
        self.use_search_filter_check = QCheckBox("Filter by search query")
        self.use_search_filter_check.toggled.connect(self.toggle_search_filter)
        filter_layout.addRow("", self.use_search_filter_check)
        
        self.search_query_input = QLineEdit()
        self.search_query_input.setPlaceholderText("Enter search query...")
        self.search_query_input.setEnabled(False)
        filter_layout.addRow("Search Query:", self.search_query_input)
        
        # Limit
        self.use_limit_check = QCheckBox("Limit number of conversations")
        self.use_limit_check.toggled.connect(self.toggle_limit)
        filter_layout.addRow("", self.use_limit_check)
        
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 100000)
        self.limit_spin.setValue(1000)
        self.limit_spin.setEnabled(False)
        filter_layout.addRow("Limit:", self.limit_spin)
        
        layout.addWidget(filter_group)
        
        # Content options group
        content_group = QGroupBox("Content Options")
        content_layout = QFormLayout(content_group)
        
        self.include_metadata_check = QCheckBox("Include metadata")
        self.include_metadata_check.setChecked(True)
        content_layout.addRow("", self.include_metadata_check)
        
        self.include_timestamps_check = QCheckBox("Include timestamps")
        self.include_timestamps_check.setChecked(True)
        content_layout.addRow("", self.include_timestamps_check)
        
        self.include_categories_check = QCheckBox("Include categories")
        self.include_categories_check.setChecked(True)
        content_layout.addRow("", self.include_categories_check)
        
        self.pretty_format_check = QCheckBox("Pretty format (human-readable)")
        self.pretty_format_check.setChecked(True)
        content_layout.addRow("", self.pretty_format_check)
        
        layout.addWidget(content_group)
        
        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setPlaceholderText("Export preview will appear here...")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.preview_export)
        button_layout.addWidget(self.preview_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.validate_and_export)
        self.export_button.setDefault(True)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        
        # Set initial format
        self.on_format_changed("JSON")
    
    def populate_categories(self):
        """Populate the categories list."""
        categories = [
            "Technical", "Medical", "Spiritual", "Political", 
            "Entertainment", "Education", "Business", "Personal",
            "Creative", "Research"
        ]
        
        for category in categories:
            item = QListWidgetItem(category)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.category_list.addItem(item)
    
    def on_format_changed(self, format_name: str):
        """Handle format change.
        
        Args:
            format_name: New format name
        """
        # Update file extension in output path
        current_path = self.output_path_input.text()
        if current_path:
            path = Path(current_path)
            extensions = {
                "JSON": ".json",
                "CSV": ".csv", 
                "Markdown": ".md",
                "HTML": ".html",
                "Text": ".txt"
            }
            new_path = path.with_suffix(extensions.get(format_name, ".json"))
            self.output_path_input.setText(str(new_path))
        
        # Enable/disable compression based on format
        if format_name in ["JSON", "CSV", "Text"]:
            self.compress_check.setEnabled(True)
        else:
            self.compress_check.setEnabled(False)
            self.compress_check.setChecked(False)
    
    def browse_output_path(self):
        """Browse for output file path."""
        format_name = self.format_combo.currentText()
        extensions = {
            "JSON": "JSON Files (*.json)",
            "CSV": "CSV Files (*.csv)",
            "Markdown": "Markdown Files (*.md)",
            "HTML": "HTML Files (*.html)",
            "Text": "Text Files (*.txt)"
        }
        
        file_filter = extensions.get(format_name, "All Files (*)")
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export as {format_name}",
            str(Path.home() / f"poe_conversations.{format_name.lower()}"),
            f"{file_filter};;All Files (*)"
        )
        
        if path:
            self.output_path_input.setText(path)
    
    def toggle_date_filter(self, enabled: bool):
        """Toggle date filter controls."""
        self.start_date_edit.setEnabled(enabled)
        self.end_date_edit.setEnabled(enabled)
    
    def toggle_category_filter(self, enabled: bool):
        """Toggle category filter controls."""
        self.category_list.setEnabled(enabled)
    
    def toggle_search_filter(self, enabled: bool):
        """Toggle search filter controls."""
        self.search_query_input.setEnabled(enabled)
    
    def toggle_limit(self, enabled: bool):
        """Toggle limit controls."""
        self.limit_spin.setEnabled(enabled)
    
    def preview_export(self):
        """Preview the export configuration."""
        config = self.build_export_config()
        
        preview_text = f"Export Configuration:\n\n"
        preview_text += f"Format: {config['format']}\n"
        preview_text += f"Output: {config['output_path']}\n"
        
        if config.get('filters'):
            preview_text += f"\nFilters:\n"
            filters = config['filters']
            
            if filters.get('date_range'):
                start = filters['date_range']['start']
                end = filters['date_range']['end']
                preview_text += f"  Date Range: {start} to {end}\n"
            
            if filters.get('categories'):
                categories = ", ".join(filters['categories'])
                preview_text += f"  Categories: {categories}\n"
            
            if filters.get('search_query'):
                preview_text += f"  Search: {filters['search_query']}\n"
            
            if filters.get('limit'):
                preview_text += f"  Limit: {filters['limit']} conversations\n"
        
        preview_text += f"\nContent Options:\n"
        preview_text += f"  Include Metadata: {config['include_metadata']}\n"
        preview_text += f"  Include Timestamps: {config['include_timestamps']}\n"
        preview_text += f"  Include Categories: {config['include_categories']}\n"
        preview_text += f"  Pretty Format: {config['pretty_format']}\n"
        preview_text += f"  Compressed: {config['compressed']}\n"
        
        self.preview_text.setText(preview_text)
    
    def build_export_config(self) -> Dict[str, Any]:
        """Build export configuration from UI.
        
        Returns:
            Export configuration dictionary
        """
        config = {
            'format': self.format_combo.currentText().lower(),
            'output_path': self.output_path_input.text(),
            'include_metadata': self.include_metadata_check.isChecked(),
            'include_timestamps': self.include_timestamps_check.isChecked(),
            'include_categories': self.include_categories_check.isChecked(),
            'pretty_format': self.pretty_format_check.isChecked(),
            'compressed': self.compress_check.isChecked(),
            'filters': {}
        }
        
        # Date filter
        if self.use_date_filter_check.isChecked():
            config['filters']['date_range'] = {
                'start': self.start_date_edit.date().toString('yyyy-MM-dd'),
                'end': self.end_date_edit.date().toString('yyyy-MM-dd')
            }
        
        # Category filter
        if self.use_category_filter_check.isChecked():
            selected_categories = []
            for i in range(self.category_list.count()):
                item = self.category_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    selected_categories.append(item.text())
            
            if selected_categories:
                config['filters']['categories'] = selected_categories
        
        # Search filter
        if self.use_search_filter_check.isChecked():
            query = self.search_query_input.text().strip()
            if query:
                config['filters']['search_query'] = query
        
        # Limit filter
        if self.use_limit_check.isChecked():
            config['filters']['limit'] = self.limit_spin.value()
        
        return config
    
    def validate_and_export(self):
        """Validate configuration and accept dialog."""
        output_path = self.output_path_input.text().strip()
        
        if not output_path:
            QMessageBox.warning(
                self, 
                "Invalid Configuration", 
                "Please specify an output file path."
            )
            return
        
        # Check if file already exists
        if Path(output_path).exists():
            reply = QMessageBox.question(
                self,
                "File Exists",
                f"The file '{output_path}' already exists. Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.export_config = self.build_export_config()
        self.accept()
    
    def get_export_config(self) -> Dict[str, Any]:
        """Get the export configuration.
        
        Returns:
            Export configuration dictionary
        """
        return self.export_config
