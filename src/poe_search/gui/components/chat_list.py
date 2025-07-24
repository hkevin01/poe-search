from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal

class ChatListWidget(QListWidget):
    chat_selected = pyqtSignal(str)  # conversation_id

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setAlternatingRowColors(True)
        self.itemClicked.connect(self._on_item_clicked)

    def populate_chats(self, conversations):
        self.clear()
        for conv in conversations:
            item = QListWidgetItem(f"{conv.title} - {conv.bot}")
            item.setData(Qt.ItemDataRole.UserRole, conv.id)
            self.addItem(item)

    def _on_item_clicked(self, item):
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        self.chat_selected.emit(conv_id)
