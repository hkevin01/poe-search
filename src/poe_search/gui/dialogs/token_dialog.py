"""Token setup dialog."""

from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt


class TokenDialog(QDialog):
    """Dialog for setting up Poe authentication token."""
    
    def __init__(self, parent=None):
        """Initialize the token dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.token = None
        
        self.setWindowTitle("Setup Poe Token")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Poe Authentication Token Setup")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(120)
        instructions.setHtml("""
        <p>To use Poe Search, you need to provide your Poe authentication token:</p>
        <ol>
            <li>Go to <a href="https://poe.com">poe.com</a> and log in</li>
            <li>Open your browser's developer tools (F12)</li>
            <li>Go to Application/Storage → Cookies → https://poe.com</li>
            <li>Find the cookie named <code>p-b</code> and copy its value</li>
        </ol>
        """)
        layout.addWidget(instructions)
        
        # Token input
        token_label = QLabel("Poe Token (p-b cookie value):")
        layout.addWidget(token_label)
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Paste your p-b cookie value here...")
        self.token_input.textChanged.connect(self.validate_input)
        layout.addWidget(self.token_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_token)
        self.ok_button.setEnabled(False)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def validate_input(self):
        """Validate the token input."""
        token = self.token_input.text().strip()
        # Basic validation - token should be reasonably long
        self.ok_button.setEnabled(len(token) > 10)
    
    def accept_token(self):
        """Accept the token and close dialog."""
        token = self.token_input.text().strip()
        
        if not token:
            QMessageBox.warning(self, "Invalid Token", "Please enter a valid token.")
            return
        
        self.token = token
        self.accept()
    
    def get_token(self) -> Optional[str]:
        """Get the entered token.
        
        Returns:
            The entered token or None if cancelled
        """
        return self.token
