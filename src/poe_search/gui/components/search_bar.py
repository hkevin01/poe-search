from PyQt6.QtWidgets import QLineEdit, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import pyqtSignal

class SearchBarWidget(QWidget):
    search_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Search:"))
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type to search chats...")
        self.input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.input)
        self.setLayout(layout)
